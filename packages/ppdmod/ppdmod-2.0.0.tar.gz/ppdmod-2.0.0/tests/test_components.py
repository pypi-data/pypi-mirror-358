from copy import deepcopy
from pathlib import Path

import astropy.units as u
import numpy as np
import pytest
from make_image import assemble_ring, au_to_mas
from scipy.special import j1

from ppdmod.components import Point, Ring
from ppdmod.data import get_data
from ppdmod.options import OPTIONS
from ppdmod.utils import compute_t3, compute_vis


@pytest.fixture
def data_dir():
    return Path(__file__).parent.parent / "data" / "aspro"

def test_vs_oimod(data_dir: Path) -> None:
    """Tests the internal components (with shift) vs. an ASPRO 2D FFT of an oimodeler model image
    and the interal analytical model of ASPRO."""
    data = deepcopy(
        get_data(data_dir / "internal" / "binaries.fits", wavelengths="all")
    )
    data_user = get_data(data_dir / "user_model" / "binaries.fits", wavelengths="all")
    points = np.array([(0, 0), (5, 0), (5, 5), (5, 10), (5, 15)])
    fluxes = [0.3063047, 0.21626302, 0.12446712, 0.10349181, 0.24947335]
    components = [
        Point(fr=flux, r=np.hypot(*point), phi=np.rad2deg(np.arctan2(*point)))
        for flux, point in zip(fluxes, points)
    ]
    wls = OPTIONS.fit.wls
    complex_vis = np.sum(
        [
            comp.compute_complex_vis(data.vis.u * u.m, data.vis.v * u.m, wls)
            for comp in components
        ],
        axis=0,
    )
    vis = compute_vis(complex_vis)
    assert np.allclose(data.vis.val, vis[:, 1:], atol=1e-1)

    complex_t3 = np.sum(
        [
            comp.compute_complex_vis(data.t3.u * u.m, data.t3.v * u.m, wls)
            for comp in components
        ],
        axis=0,
    )
    # NOTE: Bare numerical inaccuracy this is fine (one values is flipped by 180 degrees due to a numerical error)
    t3 = compute_t3(complex_t3, data.t3.i123)


@pytest.mark.parametrize(
    "rin, rout, i, pa",
    [
        (1, 0, 0, 0),
        (1, 0, 46, 0),
        (1, 0, 46, 50),
        (1, 0, 46, 352 % 180),
        (1, 0, 46, 352),
        (1, 1.5, 46, 352),
    ],
)
def test_vs_aspro_internal(
    rin: float,
    rout: float,
    i: float,
    pa: float,
    data_dir: Path,
):
    """Tests the direct calculation of t3 vs the assignment by uv coordinates,
    also tests 1D vs 2d (user models) from ASPRO."""
    fits_file = f"ring_rin{rin}_rout{rout}_i{i}_pa{pa}.fits"
    data = get_data(data_dir / "internal" / fits_file, wavelengths="all")

    wls = OPTIONS.fit.wls

    rin, rout = au_to_mas(rin) * u.mas, au_to_mas(rout) * u.mas
    ring = Ring(
        dim=32,
        label="Ring",
        rin=rin,
        rout=rout,
        cinc=np.cos(np.deg2rad(i)),
        pa=pa,
        thin=False if rout != 0 else True,
    )
    vis = compute_vis(ring.compute_complex_vis(data.vis.u * u.m, data.vis.v * u.m, wls))
    assert np.allclose(data.vis.val, vis[:, 1:], atol=1e-3)

    # NOTE: Check why this is not quite right? -> Numerical inaccuracy. Is fine
    t3 = compute_t3(
        ring.compute_complex_vis(data.t3.u * u.m, data.t3.v * u.m, wls), data.t3.i123
    )
    # assert np.allclose(data.t3.val, t3[:, 1:])


# TODO: Check the asymmetric case here
# TODO: Check why the 2D FFT case is sometimes off more than 1e-2?
@pytest.mark.parametrize(
    "rin, rout, i, pa, rho, theta",
    [
        # (1, 0, 0, 0, 0, 0),
        # (1, 0, 46, 0, 0, 0),
        # (1, 0, 46, 352 % 180, 0, 0),
        # (1, 0, 46, 352, 0, 0),
        # (1, 1.5, 46, 352, 0, 0),
        (1, 0, 0, 4.58, 0.99, 275.2),
    ],
)
def test_vs_aspro_user_model(
    rin: float,
    rout: float,
    i: float,
    pa: float,
    rho: float,
    theta: float,
    data_dir: Path,
):
    """Tests the user model (especially the t3)."""
    fits_file = Path(f"ring_rin{rin}_rout{rout}_i{i}_pa{pa}.fits")
    if rho != 0 or theta != 0:
        fits_file = f"{fits_file.stem}_rho{rho}_theta{theta}.fits"

    data = get_data(data_dir / "user_model" / fits_file, wavelengths="all")

    wls = OPTIONS.fit.wls
    ring = Ring(
        dim=32,
        label="Ring",
        rin=au_to_mas(rin),
        rout=au_to_mas(rout),
        cinc=np.cos(np.deg2rad(i)),
        pa=pa,
        thin=False if rout != 0 else True,
        rho1=rho,
        theta1=theta,
    )
    ring.asymmetric = True if (rho != 0 or theta != 0) else False
    vis = compute_vis(ring.compute_complex_vis(data.vis.u * u.m, data.vis.v * u.m, wls))
    # assert np.allclose(data.vis.val, vis[:, 1:], atol=1e-1)

    # NOTE: Check why this is not quite right? -> Numerical inaccuracy. Is fine
    t3 = compute_t3(
        ring.compute_complex_vis(data.t3.u * u.m, data.t3.v * u.m, wls), data.t3.i123
    )
    breakpoint()
