#!/usr/bin/env python3

import unittest

import torch

import qpytorch
from qpytorch.models import ApproximateQEP
from qpytorch.test import VariationalModelTestCase
from qpytorch.variational import CholeskyVariationalDistribution, VariationalStrategy

POWER = 1.0

class QEPClassificationModel(ApproximateQEP):
    def __init__(self, train_x, use_inducing=False):
        variational_distribution = CholeskyVariationalDistribution(train_x.size(-2), batch_shape=train_x.shape[:-2])
        inducing_points = torch.randn(50, train_x.size(-1)) if use_inducing else train_x
        strategy_cls = VariationalStrategy
        variational_strategy = strategy_cls(
            self, inducing_points, variational_distribution, learn_inducing_locations=use_inducing
        )
        super(QEPClassificationModel, self).__init__(variational_strategy)
        self.mean_module = qpytorch.means.ConstantMean()
        self.covar_module = qpytorch.kernels.ScaleKernel(qpytorch.kernels.RBFKernel())

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        latent_pred = qpytorch.distributions.MultivariateQExponential(mean_x, covar_x, power=torch.tensor(POWER))
        return latent_pred


class TestVariationalQEP(VariationalModelTestCase, unittest.TestCase):
    def create_model(self, train_x, train_y, likelihood):
        model = QEPClassificationModel(train_x)
        return model

    def create_test_data(self):
        return torch.randn(50, 1)

    def create_likelihood_and_labels(self):
        likelihood = qpytorch.likelihoods.QExponentialLikelihood(power=torch.tensor(POWER))
        labels = torch.randn(50) + 2
        return likelihood, labels

    def create_batch_test_data(self, batch_shape=torch.Size([3])):
        return torch.randn(*batch_shape, 50, 1)

    def create_batch_likelihood_and_labels(self, batch_shape=torch.Size([3])):
        likelihood = qpytorch.likelihoods.QExponentialLikelihood(batch_shape=batch_shape, power=torch.tensor(POWER))
        labels = torch.randn(*batch_shape, 50) + 2
        return likelihood, labels


class TestSVQEPVariationalQEP(TestVariationalQEP):
    def create_model(self, train_x, train_y, likelihood):
        model = QEPClassificationModel(train_x, use_inducing=True)
        return model

    def test_backward_train_nochol(self):
        with qpytorch.settings.max_cholesky_size(0):
            self.test_backward_train()

    def test_batch_backward_train_nochol(self):
        with qpytorch.settings.max_cholesky_size(0):
            self.test_batch_backward_train()

    def test_multi_batch_backward_train_nochol(self):
        with qpytorch.settings.max_cholesky_size(0):
            self.test_multi_batch_backward_train()


if __name__ == "__main__":
    unittest.main()
