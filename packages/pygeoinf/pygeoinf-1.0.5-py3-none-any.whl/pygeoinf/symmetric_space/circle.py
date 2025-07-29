"""
 Sobolev spaces for functions on a circle. 
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import rfft, irfft
from scipy.sparse import diags
from pygeoinf.hilbert_space import (
    LinearOperator,
    LinearForm,
    EuclideanSpace,
)
from pygeoinf.gaussian_measure import GaussianMeasure
from pygeoinf.symmetric_space.symmetric_space import SymmetricSpaceSobolev


class Sobolev(SymmetricSpaceSobolev):
    """
    Implementation of the Sobolev space H^s on a circle.
    """

    def __init__(
        self,
        kmax,
        order,
        scale,
        /,
        *,
        radius=1,
    ):
        """
        Args:
            kmax (float): The maximum Fourier degree.
            order (float): Sobolev order.
            scale (float): Sobolev length-scale.
            radius (float): Radius of the circle. Default is 1.
        """

        self._kmax = kmax
        self._radius = radius

        super().__init__(
            order,
            scale,
            2 * kmax,
            self._to_componets,
            self._from_componets,
            self._inner_product,
            self._to_dual,
            self._from_dual,
            vector_multiply=lambda u1, u2: u1 * u2,
        )

        self._fft_factor = np.sqrt(2 * np.pi * radius) / self.dim
        self._inverse_fft_factor = 1 / self._fft_factor

        values = np.zeros(self.kmax + 1)
        values[0] = 1
        for k in range(1, self.kmax + 1):
            values[k] = 2 * self._sobolev_function(k)

        self._metric = diags([values], [0])
        self._inverse_metric = diags([np.reciprocal(values)], [0])

    @staticmethod
    def from_sobolev_parameters(
        order, scale, /, *, radius=1, rtol=1e-8, power_of_two=False
    ):
        """
        Returns a instance of the class with the maximum Fourier degree
        chosen based on the Sobolev parameters. The method is based on
        an estimate of truncation error for the Dirac measure, and is
        only applicable in spaces with orders > 0.5.

        Args:
            order (float): The Sobolev order.
            scale (float): The Sobolev length-scale.
            radius (float): The radius for the circle. Default is 1.
            rtol (float): Relative tolerance used in assessing
                truncation error. Default is 1e-8
            power_of_two (bool): If True, truncation degree set to optimal
                power of two.

        Raises:
            ValueError: If order is <= 0.5.
        """

        if order <= 0.5:
            raise ValueError("This method is only applicable for orders > 0.5")

        summation = 1
        k = 0
        err = 1
        while err > rtol:
            k += 1
            term = (1 + (scale * k / radius) ** 2) ** -order
            summation += term
            err = term / summation

        if power_of_two:
            n = int(np.log2(k))
            k = 2 ** (n + 1)

        return Sobolev(k, order, scale, radius=radius)

    @property
    def kmax(self):
        """
        Return the maximum Fourier degree.
        """
        return self._kmax

    @property
    def radius(self):
        """
        Return the radius.
        """
        return self._radius

    @property
    def angle_spacing(self):
        """
        Return the angle spacing.
        """
        return 2 * np.pi / self.dim

    def random_point(self):
        return np.random.uniform(0, 2 * np.pi)

    def angles(self):
        """
        Returns a numpy array of the angles.
        """
        return np.fromiter(
            [i * self.angle_spacing for i in range(self.dim)],
            float,
        )

    def project_function(self, f):
        """
        Returns an element of the space formed by projecting a given function.
        """
        return np.fromiter([f(theta) for theta in self.angles()], float)

    def plot(self, u, fig=None, ax=None, **kwargs):
        """
        Make a simple plot of an element of the space on the computational domain.

        Args:
            u (vector): The element of the space to be plotted.
            fig (Figure): An existing Figure object to use. Default is None.
            ax (Axes): An existing Axes object to use. Default is None.
            kwargs: Keyword arguments forwarded to plot.

        Returns
            Figure: The figure object, either that given or newly created.
            Axes: The axes object, either that given or newly created.
        """

        figsize = kwargs.pop("figsize", (10, 8))

        if fig is None:
            fig = plt.figure(figsize=figsize)
        if ax is None:
            ax = fig.add_subplot()

        ax.plot(self.angles(), u, **kwargs)

        return fig, ax

    def plot_error_bounds(self, u, u_bound, fig=None, ax=None, **kwargs):
        """
        Make a plot of an element of the space bounded above and below by a standard
        deviation curve.

        Args:
            u (vector): The element of the space to be plotted.
            u_bounds (vector): A second element giving point-wise bounds.
            fig (Figure): An existing Figure object to use. Default is None.
            ax (Axes): An existing Axes object to use. Default is None.
            kwargs: Keyword arguments forwarded to plot.

        Returns
            Figure: The figure object, either that given or newly created.
            Axes: The axes object, either that given or newly created.
        """

        figsize = kwargs.pop("figsize", (10, 8))

        if fig is None:
            fig = plt.figure(figsize=figsize)
        if ax is None:
            ax = fig.add_subplot()

        ax.fill_between(self.angles(), u - u_bound, u + u_bound, **kwargs)

        return fig, ax

    def invariant_automorphism(self, f):
        values = np.fromiter(
            [f(k * k / self.radius**2) for k in range(self.kmax + 1)], dtype=float
        )
        matrix = diags([values], [0])

        def mapping(u):
            coeff = self.to_coefficient(u)
            coeff = matrix @ coeff
            return self.from_coefficient(coeff)

        return LinearOperator.formally_self_adjoint(self, mapping)

    def invariant_gaussian_measure(self, f, /, *, expectation=None):
        values = np.fromiter(
            [np.sqrt(f(k * k / self.radius**2)) for k in range(self.kmax + 1)],
            dtype=float,
        )
        matrix = diags([values], [0])

        domain = EuclideanSpace(self.dim)
        codomain = self

        def mapping(c):
            coeff = self._component_to_coefficient(c)
            coeff = matrix @ coeff
            return self.from_coefficient(coeff)

        def formal_adjoint(u):
            coeff = self.to_coefficient(u)
            coeff = matrix @ coeff
            return self._coefficient_to_component(coeff)

        covariance_factor = LinearOperator.from_formal_adjoint(
            domain, codomain, mapping, formal_adjoint
        )

        return GaussianMeasure(
            covariance_factor=covariance_factor,
            expectation=expectation,
        )

    def dirac(self, point):
        coeff = np.zeros(self.kmax + 1, dtype=complex)
        fac = np.exp(-1j * point)
        coeff[0] = 1
        for k in range(1, coeff.size):
            coeff[k] = coeff[k - 1] * fac
        coeff *= 1 / np.sqrt(2 * np.pi * self.radius)
        coeff[1:] *= 2
        cp = self._coefficient_to_component(coeff)
        return LinearForm(self, components=cp)

    def to_coefficient(self, u):
        """
        Maps an element to its Fourier coefficients.
        """
        return rfft(u) * self._fft_factor

    def from_coefficient(self, coeff):
        """
        Maps Fourier coefficients to an element.
        """
        return irfft(coeff, n=self.dim) * self._inverse_fft_factor

    # ================================================================#
    #                         Private methods                         #
    # ================================================================#

    def _sobolev_function(self, k):
        return (1 + (self.scale * k) ** 2) ** self.order

    def _coefficient_to_component(self, coeff):
        return np.concatenate([coeff.real, coeff.imag[1 : self.kmax]])

    def _component_to_coefficient(self, c):
        coeff_real = c[: self.kmax + 1]
        coeff_imag = np.concatenate([[0], c[self.kmax + 1 :], [0]])
        return coeff_real + 1j * coeff_imag

    def _to_componets(self, u):
        coeff = self.to_coefficient(u)
        return self._coefficient_to_component(coeff)

    def _from_componets(self, c):
        coeff = self._component_to_coefficient(c)
        return self.from_coefficient(coeff)

    def _inner_product(self, u1, u2):
        coeff1 = self.to_coefficient(u1)
        coeff2 = self.to_coefficient(u2)
        return np.real(np.vdot(self._metric @ coeff1, coeff2))

    def _to_dual(self, u):
        coeff = self.to_coefficient(u)
        cp = self._coefficient_to_component(self._metric @ coeff)
        return self.dual.from_components(cp)

    def _from_dual(self, up):
        cp = self.dual.to_components(up)
        coeff = self._component_to_coefficient(cp)
        c = self._coefficient_to_component(self._inverse_metric @ coeff)
        return self.from_components(c)


class Lebesgue(Sobolev):
    """
    Implementation of the Lebesgue space L2 on a circle.
    """

    def __init__(
        self,
        kmax,
        /,
        *,
        radius=1,
    ):
        """
        Args:
            kmax (float): The maximum Fourier degree.
            radius (float): Radius of the circle. Default is 1.
        """
        super().__init__(kmax, 0, 1, radius=radius)
