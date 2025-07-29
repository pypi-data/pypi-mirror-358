import copy
from typing import Dict, Tuple

import astropy.units as u
import numpy as np

from .options import OPTIONS
from .parameter import MultiParam, Parameter
from .utils import transform_coordinates, translate_image, translate_vis


class Component:
    """The base class for the component."""

    name = "GenComp"
    label = None
    description = "This is base component are derived."

    def __init__(self, **kwargs):
        """The class's constructor."""
        self.flux_lnf = Parameter(name="flux_lnf", base="lnf")
        self.t3_lnf = Parameter(name="t3_lnf", base="lnf")
        self.vis_lnf = Parameter(name="vis_lnf", base="lnf")

    def eval(self, **kwargs) -> None:
        """Sets the parameters (values) from the keyword arguments."""
        for key, val in kwargs.items():
            if hasattr(self, key):
                if isinstance(val, (Parameter, MultiParam)):
                    setattr(self, key, val.copy())
                else:
                    if isinstance(getattr(self, key), Parameter):
                        getattr(self, key).value = val
                    else:
                        setattr(self, key, val)

    def copy(self) -> "Component":
        """Copies the component."""
        return copy.deepcopy(self)

    def get_params(
        self, free: bool = False, shared: bool = False, time: bool = False
    ) -> Dict[str, Parameter]:
        """Gets all the parameters of a component.

        Parameters
        ----------
        component : Component
            The component for which the parameters should be fetched.
        free : bool, optional
            If free parameters should be returned, by default False.
        shared : bool, optional
            If shared parameters should be returned, by default False.
        time: bool, optional
            If time-dependent parameters should be returned, by default False.

        Returns
        -------
        params : dict of Parameter
        """
        params = {}
        for attribute in dir(self):
            param = getattr(self, attribute)
            if isinstance(param, Parameter):
                if shared and free:
                    if not (param.shared and param.free):
                        continue
                elif free:
                    if not param.free or param.shared:
                        continue
                elif shared:
                    if not param.shared or param.free:
                        continue

                params[attribute] = param
            elif isinstance(param, MultiParam):
                for p in param.params:
                    if shared and free:
                        if not (p.shared and p.free):
                            continue
                    elif free:
                        if not p.free or p.shared:
                            continue
                    elif shared:
                        if not p.shared or p.free:
                            continue

                    params[p.name] = p
        return params

    def flux_func(self, t: int, wl: u.um, **kwargs) -> np.ndarray:
        """Calculates the flux."""
        return np.array([]).astype(OPTIONS.data.dtype.real)

    def compute_flux(self, t: int, wl: u.um, **kwargs) -> np.ndarray:
        """Computes the fluxes."""
        return np.abs(self.flux_func(t, wl, **kwargs)).astype(OPTIONS.data.dtype.real)


class FourierComponent(Component):
    """The base class for the Fourier (analytical) component.

    Parameters
    ----------
    xx : float
        The x-coordinate of the component.
    yy : float
        The x-coordinate of the component.
    dim : float
        The dimension (px).
    """

    name = "FourierComp"
    description = "The component from which all analytical components are derived."
    _asymmetric = False

    def __init__(self, **kwargs):
        """The class's constructor."""
        super().__init__(**kwargs)
        self.fr = Parameter(base="fr")
        self.r = Parameter(base="r")
        self.phi = Parameter(base="phi")
        self.pa = Parameter(base="pa")
        self.cinc = Parameter(base="cinc")
        self.dim = Parameter(base="dim")
        self.modulation = Parameter(base="modulation")

        self.eval(**kwargs)

        for i in range(1, self.modulation.value + 1):
            rho_str, theta_str = f"rho{i}", f"theta{i}"
            rho = Parameter(name=rho_str, free=self.asymmetric, base="rho")
            theta = Parameter(name=theta_str, free=self.asymmetric, base="theta")
            setattr(self, rho_str, rho)
            setattr(self, theta_str, theta)

    def x(self, t, wl) -> u.Quantity:
        r = self.r(t, wl)
        if self.r(t, wl).unit == u.au:
            r = (r.to(u.au) / self.dist(t, wl).to(u.pc)).value * 1e3 * u.mas
        return r * np.sin(self.phi(t, wl).to(u.rad))

    def y(self, t, wl) -> u.Quantity:
        r = self.r(t, wl)
        if self.r(t, wl).unit == u.au:
            r = (r.to(u.au) / self.dist(t, wl).to(u.pc)).value * 1e3 * u.mas
        return r * np.cos(self.phi(t, wl).to(u.rad))

    @property
    def asymmetric(self) -> bool:
        """Gets if the component is asymmetric."""
        return self._asymmetric

    @asymmetric.setter
    def asymmetric(self, value: bool) -> None:
        """Sets the position angle and the parameters to free or false
        if asymmetry is set."""
        self._asymmetric = value
        for i in range(1, self.modulation.value + 1):
            getattr(self, f"rho{i}").free = value
            getattr(self, f"theta{i}").free = value

    def compute_internal_grid(self) -> Tuple[u.Quantity[u.au], u.Quantity[u.au]]:
        """Calculates the model grid.

        Parameters
        ----------

        Returns
        -------
        xx : astropy.units.au
            The x-coordinate grid.
        yy : astropy.units.au
            The y-coordinate grid.
        """
        return np.array([]) * u.au, np.array([]) * u.au

    def vis_func(self, spf: 1 / u.rad, psi: u.rad, wl: u.um, **kwargs) -> np.ndarray:
        """Computes the correlated fluxes."""
        return np.array([]).astype(OPTIONS.data.dtype.complex)

    def compute_complex_vis(
        self, ucoord: u.m, vcoord: u.m, t: int, wl: u.um, **kwargs
    ) -> np.ndarray:
        """Computes the correlated fluxes."""
        ut, vt = transform_coordinates(
            ucoord, vcoord, self.cinc(t, wl), self.pa(t, wl).to(u.rad)
        )
        wl = wl.reshape(-1, 1)
        utb = (ut / wl.to(u.m)).value[..., np.newaxis] / u.rad
        vtb = (vt / wl.to(u.m)).value[..., np.newaxis] / u.rad
        spf, psi = np.hypot(utb, vtb), np.arctan2(utb, vtb)

        shift = translate_vis(
            utb.value,
            vtb.value,
            self.x(t, wl).to(u.rad).value,
            self.y(t, wl).to(u.rad).value,
        )
        shift = shift.reshape(shift.shape[:-1]) if shift.shape[-1] == 1 else shift
        vis = self.vis_func(spf, psi, t, wl, **kwargs)
        vis = vis.reshape(vis.shape[:-1]) if vis.shape[-1] == 1 else vis
        return (self.fr(t, wl).value * vis * shift).astype(OPTIONS.data.dtype.complex)

    def image_func(
        self, xx: u.mas, yy: u.mas, pixel_size: u.mas, t: int, wl: u.um
    ) -> np.ndarray:
        """Calculates the image."""
        return np.array([]).astype(OPTIONS.data.dtype.real)

    def compute_image(
        self, dim: int, pixel_size: u.mas, t: int, wl: u.um
    ) -> np.ndarray:
        """Computes the image."""
        wl = wl[np.newaxis, np.newaxis]
        xx = np.linspace(-0.5, 0.5, dim, endpoint=False) * pixel_size * dim
        xxt, yyt = transform_coordinates(
            *np.meshgrid(xx, xx, sparse=True),
            self.cinc(t, wl),
            self.pa(t, wl).to(u.rad),
            axis="x",
        )
        xxs, yys = translate_image(xxt, yyt, self.x(t, wl), self.y(t, wl))
        image = self.image_func(xxs, yys, pixel_size, t, wl)
        return (self.fr(t, wl) * image).value.astype(OPTIONS.data.dtype.real)
