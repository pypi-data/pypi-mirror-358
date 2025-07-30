#!/usr/bin/env python3

import math
import unittest
from unittest.mock import MagicMock, patch

import linear_operator
import torch
from torch import optim

import qpytorch
from qpytorch.likelihoods import BernoulliLikelihood
from qpytorch.models import ApproximateQEP
from qpytorch.test import BaseTestCase
from qpytorch.variational import CholeskyVariationalDistribution, VariationalStrategy

POWER = 1.0

def train_data(cuda=False):
    train_x = torch.linspace(0, 1, 150)
    train_y = torch.cos(train_x * (2 * math.pi)).gt(0).float()
    if cuda:
        return train_x.cuda(), train_y.cuda()
    else:
        return train_x, train_y


class SVQEPClassificationModel(ApproximateQEP):
    def __init__(self, inducing_points):
        self.power = torch.tensor(POWER)
        variational_distribution = CholeskyVariationalDistribution(inducing_points.size(-1), power=self.power)
        variational_strategy = VariationalStrategy(
            self, inducing_points, variational_distribution, learn_inducing_locations=True, jitter_val=1e-4
        )
        super(SVQEPClassificationModel, self).__init__(variational_strategy)
        self.mean_module = qpytorch.means.ConstantMean()
        self.covar_module = qpytorch.kernels.ScaleKernel(
            qpytorch.kernels.RBFKernel(lengthscale_prior=qpytorch.priors.SmoothedBoxPrior(0.001, 1.0, sigma=0.1))
        )

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        latent_pred = qpytorch.distributions.MultivariateQExponential(mean_x, covar_x, power=self.power)
        return latent_pred


class TestSVQEPClassification(BaseTestCase, unittest.TestCase):
    seed = 1

    def test_classification_error(self, cuda=False, mll_cls=qpytorch.mlls.VariationalELBO):
        train_x, train_y = train_data(cuda=cuda)
        likelihood = BernoulliLikelihood()
        model = SVQEPClassificationModel(torch.linspace(0, 1, 64))
        mll = mll_cls(likelihood, model, num_data=len(train_y))
        if cuda:
            likelihood = likelihood.cuda()
            model = model.cuda()
            mll = mll.cuda()

        # Find optimal model hyperparameters
        model.train()
        likelihood.train()
        optimizer = optim.Adam([{"params": model.parameters()}, {"params": likelihood.parameters()}], lr=0.03)

        _wrapped_cg = MagicMock(wraps=linear_operator.utils.linear_cg)
        _cg_mock = patch("linear_operator.utils.linear_cg", new=_wrapped_cg)
        with _cg_mock as cg_mock:
            for _ in range(100):
                optimizer.zero_grad()
                output = model(train_x)
                loss = -mll(output, train_y)
                loss.backward()
                optimizer.step()

            for param in model.parameters():
                self.assertTrue(param.grad is not None)
                self.assertGreater(param.grad.norm().item(), 0)
            for param in likelihood.parameters():
                self.assertTrue(param.grad is not None)
                self.assertGreater(param.grad.norm().item(), 0)

            # Set back to eval mode
            model.eval()
            likelihood.eval()
            test_preds = likelihood(model(train_x)).mean.squeeze().round().float()
            mean_abs_error = torch.mean(torch.ne(train_y, test_preds).float())
            self.assertLess(mean_abs_error.item(), 2e-1)

            self.assertFalse(cg_mock.called)

    def test_predictive_ll_classification_error(self):
        return self.test_classification_error(mll_cls=qpytorch.mlls.PredictiveLogLikelihood)


if __name__ == "__main__":
    unittest.main()
