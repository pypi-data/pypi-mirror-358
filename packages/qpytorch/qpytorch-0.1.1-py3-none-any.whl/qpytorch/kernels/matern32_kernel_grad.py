#!/usr/bin/env python3

import math

import torch
from linear_operator.operators import KroneckerProductLinearOperator

from gpytorch.kernels.matern_kernel import MaternKernel

sqrt3 = math.sqrt(3)


class Matern32KernelGrad(MaternKernel):
    r"""
    Computes a covariance matrix of the Matern32 kernel that models the covariance
    between the values and partial derivatives for inputs :math:`\mathbf{x_1}`
    and :math:`\mathbf{x_2}`.

    See :class:`qpytorch.kernels.Kernel` for descriptions of the lengthscale options.

    .. note::

        This kernel does not have an `outputscale` parameter. To add a scaling parameter,
        decorate this kernel with a :class:`gpytorch.kernels.ScaleKernel`.

    :param ard_num_dims: Set this if you want a separate lengthscale for each input
        dimension. It should be `d` if x1 is a `n x d` matrix. (Default: `None`.)
    :param batch_shape: Set this if you want a separate lengthscale for each batch of input
        data. It should be :math:`B_1 \times \ldots \times B_k` if :math:`\mathbf x1` is
        a :math:`B_1 \times \ldots \times B_k \times N \times D` tensor.
    :param active_dims: Set this if you want to compute the covariance of only
        a few input dimensions. The ints corresponds to the indices of the
        dimensions. (Default: `None`.)
    :param lengthscale_prior: Set this if you want to apply a prior to the
        lengthscale parameter. (Default: `None`)
    :param lengthscale_constraint: Set this if you want to apply a constraint
        to the lengthscale parameter. (Default: `Positive`.)
    :param eps: The minimum value that the lengthscale can take (prevents
        divide by zero errors). (Default: `1e-6`.)

    :ivar torch.Tensor lengthscale: The lengthscale parameter. Size/shape of parameter depends on the
        ard_num_dims and batch_shape arguments.

    Example:
        >>> x = torch.randn(10, 5)
        >>> # Non-batch: Simple option
        >>> covar_module = qpytorch.kernels.ScaleKernel(qpytorch.kernels.Matern32KernelGrad())
        >>> covar = covar_module(x)  # Output: LinearOperator of size (60 x 60), where 60 = n * (d + 1)
        >>>
        >>> batch_x = torch.randn(2, 10, 5)
        >>> # Batch: Simple option
        >>> covar_module = qpytorch.kernels.ScaleKernel(qpytorch.kernels.Matern32KernelGrad())
        >>> # Batch: different lengthscale for each batch
        >>> covar_module = qpytorch.kernels.ScaleKernel(qpytorch.kernels.Matern32KernelGrad(batch_shape=torch.Size([2]))) # noqa: E501
        >>> covar = covar_module(x)  # Output: LinearOperator of size (2 x 60 x 60)
    """

    def __init__(self, **kwargs):

        # remove nu in case it was set
        kwargs.pop("nu", None)
        super(Matern32KernelGrad, self).__init__(nu=1.5, **kwargs)
        self._interleaved = kwargs.pop('interleaved', True)

    def forward(self, x1, x2, diag=False, **params):

        lengthscale = self.lengthscale

        batch_shape = x1.shape[:-2]
        n_batch_dims = len(batch_shape)
        n1, d = x1.shape[-2:]
        n2 = x2.shape[-2]

        if not diag:

            K = torch.zeros(*batch_shape, n1 * (d + 1), n2 * (d + 1), device=x1.device, dtype=x1.dtype)

            distance_matrix = self.covar_dist(x1.div(lengthscale), x2.div(lengthscale), diag=diag, **params)
            exp_neg_sqrt3r = torch.exp(-sqrt3 * distance_matrix)

            # differences matrix in each dimension to be used for derivatives
            # shape of n1 x n2 x d
            outer = x1.view(*batch_shape, n1, 1, d) - x2.view(*batch_shape, 1, n2, d)
            outer = outer / lengthscale.unsqueeze(-2) ** 2
            # shape of n1 x d x n2
            outer = torch.transpose(outer, -1, -2).contiguous()

            # 1) Kernel block, cov(f^m, f^n)
            # shape is n1 x n2
            # exp_component = torch.exp(-sqrt3 * distance_matrix)
            constant_component = (sqrt3 * distance_matrix).add(1)

            K[..., :n1, :n2] = constant_component * exp_neg_sqrt3r #exp_component

            # 2) First gradient block, cov(f^m, omega^n_i)
            outer1 = outer.view(*batch_shape, n1, n2 * d)
            # the - signs on -outer1 and -five_thirds cancel out
            K[..., :n1, n2:] = 3 * outer1 * exp_neg_sqrt3r.repeat(
                [*([1] * (n_batch_dims + 1)), d]
            )

            # 3) Second gradient block, cov(omega^m_j, f^n)
            outer2 = outer.transpose(-1, -3).reshape(*batch_shape, n2, n1 * d)
            outer2 = outer2.transpose(-1, -2)
            K[..., n1:, :n2] = -3 * outer2 * exp_neg_sqrt3r.repeat(
                [*([1] * n_batch_dims), d, 1]
            )

            # 4) Hessian block, cov(omega^m_j, omega^n_i)
            outer3 = outer1.repeat([*([1] * n_batch_dims), d, 1]) * outer2.repeat([*([1] * (n_batch_dims + 1)), d])
            kp = KroneckerProductLinearOperator(
                torch.eye(d, d, device=x1.device, dtype=x1.dtype).repeat(*batch_shape, 1, 1) / lengthscale**2,
                torch.ones(n1, n2, device=x1.device, dtype=x1.dtype).repeat(*batch_shape, 1, 1),
            )

            # part1 = -3 * exp_neg_sqrt3r
            # part2 = sqrt3 * invrdd * outer3
            invrdd = (distance_matrix+self.eps).pow(-1)
            # invrdd[torch.arange(min(n1,n2)),torch.arange(min(n1,n2))] = distance_matrix.diagonal()
            invrdd = invrdd.repeat([*([1] * (n_batch_dims)), d, d])
            # invrdd = distance_matrix.pow(-1).fill_diagonal_(0).repeat([*([1] * (n_batch_dims)), d, d]).fill_diagonal_(1)

            K[..., n1:, n2:] = -3 * exp_neg_sqrt3r.repeat([*([1] * n_batch_dims), d, d]).mul_(
                (sqrt3*invrdd * outer3).sub_(kp.to_dense())
            )

            # Symmetrize for stability
            if n1 == n2 and torch.eq(x1, x2).all():
                K = 0.5 * (K.transpose(-1, -2) + K)

            # Apply a perfect shuffle permutation to match the MutiTask ordering
            if self._interleaved:
                pi1 = torch.arange(n1 * (d + 1)).view(d + 1, n1).t().reshape((n1 * (d + 1)))
                pi2 = torch.arange(n2 * (d + 1)).view(d + 1, n2).t().reshape((n2 * (d + 1)))
                K = K[..., pi1, :][..., :, pi2]

            return K
        else:
            if not (n1 == n2 and torch.eq(x1, x2).all()):
                raise RuntimeError("diag=True only works when x1 == x2")

            # nu is set to 2.5
            kernel_diag = super(Matern32KernelGrad, self).forward(x1, x2, diag=True)
            grad_diag = (
                3 * torch.ones(*batch_shape, n2, d, device=x1.device, dtype=x1.dtype)
            ) / lengthscale**2
            grad_diag = grad_diag.transpose(-1, -2).reshape(*batch_shape, n2 * d)
            k_diag = torch.cat((kernel_diag, grad_diag), dim=-1)
            if self._interleaved:
                pi = torch.arange(n2 * (d + 1)).view(d + 1, n2).t().reshape((n2 * (d + 1)))
                k_diag = k_diag[..., pi]
            return k_diag

    def num_outputs_per_input(self, x1, x2):
        return x1.size(-1) + 1
