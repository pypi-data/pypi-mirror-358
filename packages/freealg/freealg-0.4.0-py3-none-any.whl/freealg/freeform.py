# SPDX-FileCopyrightText: Copyright 2025, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import numpy
from scipy.stats import gaussian_kde
# from statsmodels.nonparametric.kde import KDEUnivariate
from functools import partial
from ._util import compute_eig, beta_kde, force_density
from ._jacobi import jacobi_sample_proj, jacobi_kernel_proj, jacobi_approx, \
    jacobi_stieltjes
from ._chebyshev import chebyshev_sample_proj, chebyshev_kernel_proj, \
    chebyshev_approx, chebyshev_stieltjes
from ._damp import jackson_damping, lanczos_damping, fejer_damping, \
    exponential_damping, parzen_damping
from ._plot_util import plot_fit, plot_density, plot_hilbert, plot_stieltjes
from ._pade import fit_pade, eval_pade
from ._decompress import decompress
from ._sample import qmc_sample
from ._support import detect_support

# Fallback to previous API
if not hasattr(numpy, 'trapezoid'):
    numpy.trapezoid = numpy.trapz

__all__ = ['FreeForm']


# =========
# Free Form
# =========

class FreeForm(object):
    """
    Free probability for large matrices.

    Parameters
    ----------

    A : numpy.ndarray
        The 2D symmetric :math:`\\mathbf{A}`. The eigenvalues of this will be
        computed upon calling this class. If a 1D array provided, it is
        assumed to be the eigenvalues of :math:`\\mathbf{A}`.

    support : tuple, default=None
        The support of the density of :math:`\\mathbf{A}`. If `None`, it is
        estimated from the minimum and maximum of the eigenvalues.

    delta: float, default=1e-6
        Size of perturbations into the upper half plane for Plemelj's
        formula.

    **kwargs : dict, optional
        Parameters for the ``detect_support`` function can also be prescribed
        here when ``support=None``.

    Notes
    -----

    TBD

    References
    ----------

    .. [1] Reference.

    Attributes
    ----------

    eig : numpy.array
        Eigenvalues of the matrix

    support: tuple
        The predicted (or given) support :math:`(\\lambda_{\\min},
        \\lambda_{\\max})` of the eigenvalue density.

    psi : numpy.array
        Jacobi coefficients.

    n : int
      Initial array size (assuming a square matrix when :math:`\\mathbf{A}` is
      2D).

    Methods
    -------

    fit
        Fit the Jacobi polynomials to the empirical density.

    density
        Compute the spectral density of the matrix.

    hilbert
        Compute Hilbert transform of the spectral density

    stieltjes
        Compute Stieltjes transform of the spectral density

    decompress
        Free decompression of spectral density

    eigvalsh
        Estimate the eigenvalues

    cond
        Estimate the condition number

    trace
        Estimate the trace of a matrix power

    slogdet
        Estimate the sign and logarithm of the determinant

    norm
        Estimate the Schatten norm

    Examples
    --------

    .. code-block:: python

        >>> from freealg import FreeForm
    """

    # ====
    # init
    # ====

    def __init__(self, A, support=None, delta=1e-6, **kwargs):
        """
        Initialization.
        """

        self.A = None
        self.eig = None
        self.delta = delta

        # Eigenvalues
        if A.ndim == 1:
            # When A is a 1D array, it is assumed A is the eigenvalue array.
            self.eig = A
            self.n = len(A)
        elif A.ndim == 2:
            # When A is a 2D array, it is assumed A is the actual array,
            # and its eigenvalues will be computed.
            self.A = A
            self.n = A.shape[0]
            assert A.shape[0] == A.shape[1], \
                'Only square matrices are permitted.'
            self.eig = compute_eig(A)

        # Support
        if support is None:
            self.lam_m, self.lam_p = detect_support(self.eig, **kwargs)
        else:
            self.lam_m = support[0]
            self.lam_p = support[1]
        self.support = (self.lam_m, self.lam_p)

        # Initialize
        self.method = None
        self.psi = None
        self.alpha = None
        self.beta = None
        self._pade_sol = None

    # ===
    # fit
    # ===

    def fit(self, method='jacobi', K=10, alpha=0.0, beta=0.0, reg=0.0,
            projection='gaussian', kernel_bw=None, damp=None, force=False,
            pade_p=0, pade_q=1, odd_side='left', pade_reg=0.0, optimizer='ls',
            plot=False, latex=False, save=False):
        """
        Fit model to eigenvalues.

        Parameters
        ----------

        method : {``'jacobi'``, ``'chebyshev'``}, default= ``'jacobi'``
            Method of approximation, either by Jacobi polynomials or Chebyshev
            polynomials of the second kind.

        K : int, default=10
            Highest polynomial degree

        alpha : float, default=0.0
            Jacobi parameter :math:`\\alpha`. Determines the slope of the
            fitting model on the right side of interval. This should be greater
            then -1. This option is only applicable when ``method='jacobi'``.

        beta : float, default=0.0
            Jacobi parameter :math:`\\beta`. Determines the slope of the
            fitting model on the left side of interval. This should be greater
            then -1. This option is only applicable when ``method='jacobi'``.

        reg : float, default=0.0
            Tikhonov regularization coefficient.

        projection : {``'sample'``, ``'gaussian'``, ``'beta'``}, \
                default= ``'beta'``
            The method of Galerkin projection:

            * ``'sample'``: directly project samples (eigenvalues) to the
              orthogonal polynomials. This method is highly unstable as it
              treats each sample as a delta Dirac function.
            * ``'gaussian'``: computes Gaussian-Kernel KDE from the samples and
              project a smooth KDE to the orthogonal polynomials. This method
              is stable.
            * ``'beta'``: computes Beta-Kernel KDE from the samples and
              project a smooth KDE to the orthogonal polynomials. This method
              is stable.

        kernel_bw : float, default=0.001
            Kernel band-wdth. See scipy.stats.gaussian_kde. This argument is
            relevant if ``projection='kernel'`` is set.

        damp : {``'jackson'``, ``'lanczos'``, ``'fejer``, ``'exponential'``,\
                ``'parzen'``}, default=None
            Damping method to eliminate Gibbs oscillation.

        force : bool, default=False
            If `True`, it forces the density to have unit mass and to be
            strictly positive.

        pade_p : int, default=0
            Degree of polynomial :math:`P(z)` is :math:`q+p` where :math:`p`
            can only be ``-1``, ``0``, or ``1``. See notes below.

        pade_q : int, default=1
            Degree of polynomial :math:`Q(z)` is :math:`q`. See notes below.

        odd_side : {``'left'``, ``'right'``}, default= ``'left'``
            In case of odd number of poles (when :math:`q` is odd), the extra
            pole is set to the left or right side of the support interval,
            while all other poles are split in half to the left and right. Note
            that this is only for the initialization of the poles. The
            optimizer will decide best location by moving them to the left or
            right of the support.

        pade_reg : float, default=0.0
            Regularization for Pade approximation.

        optimizer : {``'ls'``, ``'de'``}, default= ``'ls'``
            Optimizer for Pade approximation, including:

            * ``'ls'``: least square (local, fast)
            * ``'de'``: differential evolution (global, slow)

        plot : bool, default=False
            If `True`, the approximation coefficients and Pade approximation to
            the Hilbert transform are plotted.

        latex : bool, default=False
            If `True`, the plot is rendered using LaTeX. This option is
            relevant only if ``plot=True``.

        save : bool, default=False
            If not `False`, the plot is saved. If a string is given, it is
            assumed to the save filename (with the file extension). This option
            is relevant only if ``plot=True``.

        Returns
        -------

        psi : (K+1, ) numpy.ndarray
            Coefficients of fitting Jacobi polynomials

        Notes
        -----

        The Pade approximation for the glue function :math:`G(z)` is

        .. math::

            G(z) = \\frac{P(z)}{Q(z)},

        where :math:`P(z)` and :math:`Q(z)` are polynomials of order
        :math:`p+q` and :math:`q` respectively. Note that :math:`p` can only
        be -1, 0, or 1, effectively making Pade approximation of order
        :math:`q-1:q`, :math:`q:q`, or :math:`q-1:q`.

        Examples
        --------

        .. code-block:: python

            >>> from freealg import FreeForm
        """

        if alpha <= -1:
            raise ValueError('"alpha" should be greater then "-1".')

        if beta <= -1:
            raise ValueError('"beta" should be greater then "-1".')

        if not (method in ['jacobi', 'chebyshev']):
            raise ValueError('"method" is invalid.')

        if not (projection in ['sample', 'gaussian', 'beta']):
            raise ValueError('"projection" is invalid.')

        # Project eigenvalues to Jacobi polynomials basis
        if method == 'jacobi':

            if projection == 'sample':
                psi = jacobi_sample_proj(self.eig, support=self.support, K=K,
                                         alpha=alpha, beta=beta, reg=reg)
            else:
                # smooth KDE on a fixed grid
                xs = numpy.linspace(self.lam_m, self.lam_p, 2000)

                if projection == 'gaussian':
                    pdf = gaussian_kde(self.eig, bw_method=kernel_bw)(xs)
                else:
                    pdf = beta_kde(self.eig, xs, self.lam_m, self.lam_p,
                                   kernel_bw)

                # Adaptive KDE
                # k = KDEUnivariate(self.eig)
                # k.fit(bw="silverman", fft=False, weights=None, gridsize=1024,
                #       adaptive=True)
                # pdf = k.evaluate(xs)

                # TEST
                # import matplotlib.pyplot as plt
                # plt.plot(xs, pdf)
                # plt.grid(True)
                # plt.show()

                psi = jacobi_kernel_proj(xs, pdf, support=self.support, K=K,
                                         alpha=alpha, beta=beta, reg=reg)

        elif method == 'chebyshev':

            if projection == 'sample':
                psi = chebyshev_sample_proj(self.eig, support=self.support,
                                            K=K, reg=reg)
            else:
                # smooth KDE on a fixed grid
                xs = numpy.linspace(self.lam_m, self.lam_p, 2000)

                if projection == 'gaussian':
                    pdf = gaussian_kde(self.eig, bw_method=kernel_bw)(xs)
                else:
                    pdf = beta_kde(self.eig, xs, self.lam_m, self.lam_p,
                                   kernel_bw)

                # Adaptive KDE
                # k = KDEUnivariate(self.eig)
                # k.fit(bw="silverman", fft=False, weights=None, gridsize=1024,
                #       adaptive=True)
                # pdf = k.evaluate(xs)

                psi = chebyshev_kernel_proj(xs, pdf, support=self.support,
                                            K=K, reg=reg)
        else:
            raise ValueError('"method" is invalid.')

        # Damping
        if damp is not None:
            if damp == 'jackson':
                g = jackson_damping(K+1)
            elif damp == 'lanczos':
                g = lanczos_damping(K+1)
            elif damp == 'fejer':
                g = fejer_damping(K+1)
            elif damp == 'exponential':
                g = exponential_damping(K+1)
            elif damp == 'parzen':
                g = parzen_damping(K+1)

            psi = psi * g

        if force:
            # A grid to check and enforce positivity and unit mass on it
            grid = numpy.linspace(self.lam_m, self.lam_p, 500)

            if method == 'jacobi':
                approx = partial(jacobi_approx, support=self.support,
                                 alpha=alpha, beta=beta)
            elif method == 'chebyshev':
                approx = partial(chebyshev_approx, support=self.support)
            else:
                raise RuntimeError('"method" is invalid.')

            # Enforce positivity, unit mass, and zero at edges
            psi = force_density(psi, support=self.support, approx=approx,
                                grid=grid, alpha=alpha, beta=beta)

        # Update attributes
        self.method = method
        self.psi = psi
        self.alpha = alpha
        self.beta = beta

        # Fit a pade approximation
        if method != 'chebyshev' or projection != 'sample':
            # For holomorphic continuation for the lower half-plane
            x_supp = numpy.linspace(self.lam_m, self.lam_p, 1000)
            g_supp = 2.0 * numpy.pi * self.hilbert(x_supp)
            self._pade_sol = fit_pade(x_supp, g_supp, self.lam_m, self.lam_p,
                                      p=pade_p, q=pade_q, odd_side=odd_side,
                                      pade_reg=pade_reg, safety=1.0,
                                      max_outer=40, xtol=1e-12, ftol=1e-12,
                                      optimizer=optimizer, verbose=0)

        if plot:
            g_supp_approx = eval_pade(x_supp[None, :], self._pade_sol)[0, :]
            plot_fit(psi, x_supp, g_supp, g_supp_approx, support=self.support,
                     latex=latex, save=save)

        return self.psi

    # =======
    # density
    # =======

    def _grid(self, scale, extend=1.0, N=500):
        """
        Return a grid of points to evaluate density / Hilbert / Stieltjes
        transforms.
        """

        radius = 0.5 * (self.lam_p - self.lam_m)
        center = 0.5 * (self.lam_p + self.lam_m)

        x_min = numpy.floor(extend * (center - extend * radius * scale))
        x_max = numpy.ceil(extend * (center + extend * radius * scale))

        x_min /= extend
        x_max /= extend

        return numpy.linspace(x_min, x_max, N)

    # =======
    # density
    # =======

    def density(self, x=None, plot=False, latex=False, save=False):
        """
        Evaluate spectral density.

        Parameters
        ----------

        x : numpy.array, default=None
            Positions where density to be evaluated at. If `None`, an interval
            slightly larger than the support interval will be used.

        plot : bool, default=False
            If `True`, density is plotted.

        latex : bool, default=False
            If `True`, the plot is rendered using LaTeX. This option is
            relevant only if ``plot=True``.

        save : bool, default=False
            If not `False`, the plot is saved. If a string is given, it is
            assumed to the save filename (with the file extension). This option
            is relevant only if ``plot=True``.

        Returns
        -------

        rho : numpy.array
            Density at locations x.

        See Also
        --------
        hilbert
        stieltjes

        Examples
        --------

        .. code-block:: python

            >>> from freealg import FreeForm
        """

        if self.psi is None:
            raise RuntimeError('The spectral density needs to be fit using ' +
                               'the .fit() function.')

        # Create x if not given
        if x is None:
            x = self._grid(1.25)

        # Preallocate density to zero
        rho = numpy.zeros_like(x)

        # Compute density only inside support
        mask = numpy.logical_and(x >= self.lam_m, x <= self.lam_p)

        if self.method == 'jacobi':
            rho[mask] = jacobi_approx(x[mask], self.psi, self.support,
                                      self.alpha, self.beta)
        elif self.method == 'chebyshev':
            rho[mask] = chebyshev_approx(x[mask], self.psi, self.support)
        else:
            raise RuntimeError('"method" is invalid.')

        # Check density is unit mass
        mass = numpy.trapezoid(rho, x)
        if not numpy.isclose(mass, 1.0, atol=1e-2):
            print(f'"rho" is not unit mass. mass: {mass:>0.3f}. Set ' +
                  r'"force=True".')

        # Check density is positive
        min_rho = numpy.min(rho)
        if min_rho < 0.0 - 1e-3:
            print(f'"rho" is not positive. min_rho: {min_rho:>0.3f}. Set ' +
                  r'"force=True".')

        if plot:
            plot_density(x, rho, eig=self.eig, support=self.support,
                         label='Estimate', latex=latex, save=save)

        return rho

    # =======
    # hilbert
    # =======

    def hilbert(self, x=None, rho=None, plot=False, latex=False, save=False):
        """
        Compute Hilbert transform of the spectral density.

        Parameters
        ----------

        x : numpy.array, default=None
            The locations where Hilbert transform is evaluated at. If `None`,
            an interval slightly larger than the support interval of the
            spectral density is used.

        rho : numpy.array, default=None
            Density. If `None`, it will be computed.

        plot : bool, default=False
            If `True`, density is plotted.

        latex : bool, default=False
            If `True`, the plot is rendered using LaTeX. This option is
            relevant only if ``plot=True``.

        save : bool, default=False
            If not `False`, the plot is saved. If a string is given, it is
            assumed to the save filename (with the file extension). This option
            is relevant only if ``plot=True``.

        Returns
        -------

        hilb : numpy.array
            The Hilbert transform on the locations `x`.

        See Also
        --------
        density
        stieltjes

        Examples
        --------

        .. code-block:: python

            >>> from freealg import FreeForm
        """

        if self.psi is None:
            raise RuntimeError('The spectral density needs to be fit using ' +
                               'the .fit() function.')

        # Create x if not given
        if x is None:
            x = self._grid(1.25)

        # if (numpy.min(x) > self.lam_m) or (numpy.max(x) < self.lam_p):
        #     raise ValueError('"x" does not encompass support interval.')

        # Preallocate density to zero
        if rho is None:
            rho = self.density(x)

        # mask of support [lam_m, lam_p]
        mask = numpy.logical_and(x >= self.lam_m, x <= self.lam_p)
        x_s = x[mask]
        rho_s = rho[mask]

        # Form the matrix of integrands: rho_s / (t - x_i)
        # Here, we have diff[i,j] = x[i] - x_s[j]
        diff = x[:, None] - x_s[None, :]
        D = rho_s[None, :] / diff

        # Principal‐value: wherever t == x_i, then diff == 0, zero that entry
        # (numpy.isclose handles floating‐point exactly)
        D[numpy.isclose(diff, 0.0)] = 0.0

        # Integrate each row over t using trapezoid rule on x_s
        # Namely, hilb[i] = int rho_s(t)/(t - x[i]) dt
        hilb = numpy.trapezoid(D, x_s, axis=1) / numpy.pi

        # We use negative sign convention
        hilb = -hilb

        if plot:
            plot_hilbert(x, hilb, support=self.support, latex=latex,
                         save=save)

        return hilb

    # ====
    # glue
    # ====

    def _glue(self, z):
        # Glue function
        if self._pade_sol is None:
            return numpy.zeros_like(z)
        g = eval_pade(z, self._pade_sol)
        return g

    # =========
    # stieltjes
    # =========

    def stieltjes(self, x=None, y=None, plot=False, latex=False, save=False):
        """
        Compute Stieltjes transform of the spectral density on a grid.

        This function evaluates Stieltjes transform on an array of points, or
        over a 2D Cartesian grid on the complex plane.

        Parameters
        ----------

        x : numpy.array, default=None
            The x axis of the grid where the Stieltjes transform is evaluated.
            If `None`, an interval slightly larger than the support interval of
            the spectral density is used.

        y : numpy.array, default=None
            The y axis of the grid where the Stieltjes transform is evaluated.
            If `None`, a grid on the interval ``[-1, 1]`` is used.

        plot : bool, default=False
            If `True`, density is plotted.

        latex : bool, default=False
            If `True`, the plot is rendered using LaTeX. This option is
            relevant only if ``plot=True``.

        save : bool, default=False
            If not `False`, the plot is saved. If a string is given, it is
            assumed to the save filename (with the file extension). This option
            is relevant only if ``plot=True``.

        Returns
        -------

        m_p : numpy.ndarray
            The Stieltjes transform on the principal branch.

        m_m : numpy.ndarray
            The Stieltjes transform continued to the secondary branch.

        See Also
        --------
        density
        hilbert

        Notes
        -----

        Notes.

        References
        ----------

        .. [1] tbd

        Examples
        --------

        .. code-block:: python

            >>> from freealg import FreeForm
        """

        if self.psi is None:
            raise RuntimeError('The spectral density needs to be fit using ' +
                               'the .fit() function.')

        # Determine whether the Stieltjes transform is to be computed on a
        # Cartesian grid
        cartesian = plot | (y is not None)

        # Create x if not given
        if x is None:
            x = self._grid(2.0, extend=2.0)

            if not cartesian:
                # Evaluate slightly above the real line
                x = x.astype(complex)
                x += self.delta * 1j

        # Create y if not given
        if cartesian:
            if y is None:
                y = numpy.linspace(-1, 1, 400)
            x_grid, y_grid = numpy.meshgrid(x.real, y.real)
            z = x_grid + 1j * y_grid              # shape (Ny, Nx)
        else:
            z = x

        m1, m2 = self._eval_stieltjes(z, branches=True)

        if plot:
            plot_stieltjes(x, y, m1, m2, self.support, latex=latex, save=save)

        return m1, m2

    # ==============
    # eval stieltjes
    # ==============

    def _eval_stieltjes(self, z, branches=False):
        """
        Compute Stieltjes transform of the spectral density.

        Parameters
        ----------

        z : numpy.array
            The z values in the complex plan where the Stieltjes transform is
            evaluated.

        branches : bool, default = False
            Return both the principal and secondary branches of the Stieltjes
            transform. The default ``branches=False`` will return only
            the secondary branch.


        Returns
        -------

        m_p : numpy.ndarray
            The Stieltjes transform on the principal branch if
            ``branches=True``.

        m_m : numpy.ndarray
            The Stieltjes transform continued to the secondary branch.
        """

        assert self.psi is not None, "The fit function has not been called."

        # Allow for arbitrary input shapes
        z = numpy.asarray(z)
        shape = z.shape
        if len(shape) == 0:
            shape = (1,)
        z = z.reshape(-1, 1)

        # # Set the number of bases as the number of x points insides support
        # mask_sup = numpy.logical_and(z.real >= self.lam_m,
        #                              z.real <= self.lam_p)
        # n_base = 2 * numpy.sum(mask_sup)

        # Stieltjes function
        if self.method == 'jacobi':
            stieltjes = partial(jacobi_stieltjes, psi=self.psi,
                                support=self.support, alpha=self.alpha,
                                beta=self.beta)  # n_base = n_base
        elif self.method == 'chebyshev':
            stieltjes = partial(chebyshev_stieltjes, psi=self.psi,
                                support=self.support)

        mask_p = z.imag >= 0.0
        mask_m = z.imag < 0.0

        m1 = numpy.zeros_like(z)
        m2 = numpy.zeros_like(z)

        if self._pade_sol is not None:
            # Upper half-plane
            m1[mask_p] = stieltjes(z[mask_p].reshape(-1, 1)).ravel()

            # Lower half-plane, use Schwarz reflection
            z_conj = numpy.conjugate(z[mask_m].reshape(-1, 1))
            m1[mask_m] = numpy.conjugate(stieltjes(z_conj)).ravel()

            # Second Riemann sheet
            m2[mask_p] = m1[mask_p]
            m2[mask_m] = -m1[mask_m] + self._glue(
                z[mask_m].reshape(-1, 1)).ravel()

        else:
            m2[:] = stieltjes(z.reshape(-1, 1)).reshape(*m2.shape)
            if branches:
                m1[mask_p] = m2[mask_p]
                m1[mask_m] = numpy.conjugate(
                    stieltjes(numpy.conjugate(z[mask_m].reshape(-1, 1)))
                ).ravel()

        if not branches:
            return m2.reshape(*shape)
        else:
            m1, m2 = m1.reshape(*shape), m2.reshape(*shape)
            return m1, m2

    # ==========
    # decompress
    # ==========

    def decompress(self, size, x=None, max_iter=500, eigvals=True,
                   tolerance=1e-9, plot=False,
                   latex=False, save=False):
        """
        Free decompression of spectral density.

        Parameters
        ----------

        size : int
            Size of the decompressed matrix.

        x : numpy.array, default=None
            Positions where density to be evaluated at. If `None`, an interval
            slightly larger than the support interval will be used.

        max_iter: int, default=500
            Maximum number of secant method iterations.

        eigvals: bool, default=True
            Return estimated (sampled) eigenvalues as well as the density.

        tolerance: float, default=1e-9
            Tolerance for the solution obtained by the Newton solver. Also
            used for the finite difference approximation to the derivative.

        plot : bool, default=False
            If `True`, density is plotted.

        latex : bool, default=False
            If `True`, the plot is rendered using LaTeX. This option is
            relevant only if ``plot=True``.

        save : bool, default=False
            If not `False`, the plot is saved. If a string is given, it is
            assumed to the save filename (with the file extension). This option
            is relevant only if ``plot=True``.

        Returns
        -------

        x : numpy.array
            Locations where the spectral density is estimated

        rho : numpy.array
            Estimated spectral density at locations x

        eigs : numpy.array
            Estimated eigenvalues as low-discrepancy samples of the estimated
            spectral density. Only returns if ``eigvals=True``.

        See Also
        --------

        density
        stieltjes

        Notes
        -----

        Work in progress.

        References
        ----------

        .. [1] tbd

        Examples
        --------

        .. code-block:: python

            >>> from freealg import FreeForm
        """

        size = int(size)

        rho, x, (lb, ub) = decompress(self, size, x=x, delta=self.delta,
                                      max_iter=max_iter, tolerance=tolerance)
        x, rho = x.ravel(), rho.ravel()

        if plot:
            plot_density(x, rho, support=(lb, ub),
                         label='Decompression', latex=latex, save=save)

        return x, rho

    # ========
    # eigvalsh
    # ========

    def eigvalsh(self, size=None, seed=None, **kwargs):
        """
        Estimate the eigenvalues.

        This function estimates the eigenvalues of the freeform matrix
        or a larger matrix containing it using free decompression.

        Parameters
        ----------

        size : int, default=None
            The size of the matrix containing :math:`\\mathbf{A}` to estimate
            eigenvalues of. If None, returns estimates of the eigenvalues of
            :math:`\\mathbf{A}` itself.

        seed : int, default=None
            The seed for the Quasi-Monte Carlo sampler.

        **kwargs : dict, optional
            Pass additional options to the underlying
            :func:`FreeForm.decompress` function.

        Returns
        -------

        eigs : numpy.array
            Eigenvalues of decompressed matrix

        See Also
        --------

        FreeForm.decompress
        FreeForm.cond

        Notes
        -----

        All arguments to the `.decompress()` procedure can be provided.

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 1

            >>> from freealg import FreeForm
        """

        if size is None:
            x = self._grid(1.25)
            rho = self.density(x)
            size = self.n
        else:
            x, rho = self.decompress(size, **kwargs)
        eigs = numpy.sort(qmc_sample(x, rho, size, seed=seed))
        return eigs

    # ====
    # cond
    # ====

    def cond(self, size=None, seed=None, **kwargs):
        """
        Estimate the condition number.

        This function estimates the condition number of the matrix
        :math:`\\mathbf{A}` or a larger matrix containing :math:`\\mathbf{A}`
        using free decompression.

        Parameters
        ----------

        size : int, default=None
            The size of the matrix containing :math:`\\mathbf{A}` to estimate
            eigenvalues of. If None, returns estimates of the eigenvalues of
            :math:`\\mathbf{A}` itself.

        **kwargs : dict, optional
            Pass additional options to the underlying
            :func:`FreeForm.decompress` function.

        Returns
        -------

        c : float
            Condition number

        See Also
        --------

        FreeForm.eigvalsh
        FreeForm.norm
        FreeForm.slogdet
        FreeForm.trace

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 1

            >>> from freealg import FreeForm
        """

        eigs = self.eigvalsh(size=size, **kwargs)
        return eigs.max() / eigs.min()

    # =====
    # trace
    # =====

    def trace(self, size=None, p=1.0, seed=None, **kwargs):
        """
        Estimate the trace of a power.

        This function estimates the trace of the matrix power
        :math:`\\mathbf{A}^p` of the freeform or that of a larger matrix
        containing it.

        Parameters
        ----------

        size : int, default=None
            The size of the matrix containing :math:`\\mathbf{A}` to estimate
            eigenvalues of. If None, returns estimates of the eigenvalues of
            :math:`\\mathbf{A}` itself.

        p : float, default=1.0
            The exponent :math:`p` in :math:`\\mathbf{A}^p`.

        seed : int, default=None
            The seed for the Quasi-Monte Carlo sampler.

        **kwargs : dict, optional
            Pass additional options to the underlying
            :func:`FreeForm.decompress` function.

        Returns
        -------

        trace : float
            matrix trace

        See Also
        --------

        FreeForm.eigvalsh
        FreeForm.cond
        FreeForm.slogdet
        FreeForm.norm

        Notes
        -----

        The trace is highly amenable to subsampling: under free decompression
        the average eigenvalue is assumed constant, so the trace increases
        linearly. Traces of powers fall back to :func:`eigvalsh`.
        All arguments to the `.decompress()` procedure can be provided.

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 6

            >>> ...
        """
        if numpy.isclose(p, 1.0):
            return numpy.mean(self.eig) * (size / self.n)

        eig = self.eigvalsh(size=size, seed=seed, **kwargs)
        return numpy.sum(eig ** p)

    # =======
    # slogdet
    # =======

    def slogdet(self, size=None, seed=None, **kwargs):
        """
        Estimate the sign and logarithm of the determinant.

        This function estimates the *slogdet* of the freeform or that of
        a larger matrix containing it using free decompression.

        Parameters
        ----------

        size : int, default=None
            The size of the matrix containing :math:`\\mathbf{A}` to estimate
            eigenvalues of. If None, returns estimates of the eigenvalues of
            :math:`\\mathbf{A}` itself.

        seed : int, default=None
            The seed for the Quasi-Monte Carlo sampler.

        Returns
        -------

        sign : float
            Sign of determinant

        ld : float
            natural logarithm of the absolute value of the determinant

        See Also
        --------

        FreeForm.eigvalsh
        FreeForm.cond
        FreeForm.trace
        FreeForm.norm

        Notes
        -----

        All arguments to the `.decompress()` procedure can be provided.

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 6

            >>> ...
        """

        eigs = self.eigvalsh(size=size, seed=seed, **kwargs)
        sign = numpy.prod(numpy.sign(eigs))
        ld = numpy.sum(numpy.log(numpy.abs(eigs)))
        return sign, ld

    # ====
    # norm
    # ====

    def norm(self, size=None, order=2, seed=None, **kwargs):
        """
        Estimate the Schatten norm.

        This function estimates the norm of the freeform or a larger
        matrix containing it using free decompression.

        Parameters
        ----------

        size : int, default=None
            The size of the matrix containing :math:`\\mathbf{A}` to estimate
            eigenvalues of. If None, returns estimates of the eigenvalues of
            :math:`\\mathbf{A}` itself.

        order : {float, ``''inf``, ``'-inf'``, ``'fro'``, ``'nuc'``}, default=2
            Order of the norm.

            * float :math:`p`: Schatten p-norm.
            * ``'inf'``: Largest absolute eigenvalue
            :math:`\\max \\vert \\lambda_i \\vert)`
            * ``'-inf'``: Smallest absolute eigenvalue
            :math:`\\min \\vert \\lambda_i \\vert)`
            * ``'fro'``: Frobenius norm corresponding to :math:`p=2`
            * ``'nuc'``: Nuclear (or trace) norm corresponding to :math:`p=1`

        seed : int, default=None
            The seed for the Quasi-Monte Carlo sampler.

        **kwargs : dict, optional
            Pass additional options to the underlying
            :func:`FreeForm.decompress` function.

        Returns
        -------

        norm : float
            matrix norm

        See Also
        --------

        FreeForm.eigvalsh
        FreeForm.cond
        FreeForm.slogdet
        FreeForm.trace

        Notes
        -----

        Thes Schatten :math:`p`-norm is defined by

        .. math::

            \\Vert \\mathbf{A} \\Vert_p = \\left(
            \\sum_{i=1}^N \\vert \\lambda_i \\vert^p \\right)^{1/p}.

        Examples
        --------

        .. code-block:: python
            :emphasize-lines: 6

            >>> ...
        """

        eigs = self.eigvalsh(size, seed=seed, **kwargs)

        # Check order type and convert to float
        if order == 'nuc':
            order = 1
        elif order == 'fro':
            order = 2
        elif order == 'inf':
            order = float('inf')
        elif order == '-inf':
            order = -float('inf')
        elif not isinstance(order,
                            (int, float, numpy.integer, numpy.floating)) \
                and not isinstance(order, (bool, numpy.bool_)):
            raise ValueError('"order" is invalid.')

        # Compute norm
        if numpy.isinf(order) and not numpy.isneginf(order):
            norm_ = max(numpy.abs(eigs))

        elif numpy.isneginf(order):
            norm_ = min(numpy.abs(eigs))

        elif isinstance(order, (int, float, numpy.integer, numpy.floating)) \
                and not isinstance(order, (bool, numpy.bool_)):
            norm_q = numpy.sum(numpy.abs(eigs)**order)
            norm_ = norm_q**(1.0 / order)

        return norm_
