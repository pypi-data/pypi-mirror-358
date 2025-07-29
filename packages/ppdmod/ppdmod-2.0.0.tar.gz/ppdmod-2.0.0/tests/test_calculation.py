from pathlib import Path
from typing import List

import astropy.units as u
import numpy as np
import pytest
from make_image import assemble_ring, au_to_mas
from scipy.special import j0

from ppdmod.data import get_data
from ppdmod.options import OPTIONS
from ppdmod.utils import compute_t3


@pytest.fixture
def data_dir():
    return Path(__file__).parent.parent / "data" / "aspro"


@pytest.fixture
def fits_files(data_dir: Path) -> List[Path]:
    return list((data_dir / "internal").glob("*0.fits"))


def vis_func(rin: u.mas, spf: 1 / u.rad) -> complex:
    return j0(2 * np.pi * rin.to(u.rad) * spf).astype(complex)


def test_t3_indexing(fits_files: List[Path]):
    """Tests the assigning of the t3 coordinates and the t3 calculation."""
    data = get_data(fits_files, wavelengths="all")
    assert np.array_equal(data.t3.u[data.t3.i123], data.t3.u123)
    assert np.array_equal(data.t3.v[data.t3.i123], data.t3.v123)

    wls = OPTIONS.fit.wls
    spf = (
        np.hypot(data.t3.u123, data.t3.v123)[np.newaxis, ...]
        / wls.to(u.m).value[:, np.newaxis, np.newaxis]
        / u.rad
    )
    spf_manual = (
        np.hypot(data.t3.u, data.t3.v)[np.newaxis, :]
        / wls.to(u.m).value[:, np.newaxis]
        / u.rad
    )
    t3 = vis_func(au_to_mas(1) * u.mas, spf)
    t3_assembled = vis_func(au_to_mas(1) * u.mas, spf_manual)[:, data.t3.i123]

    assert np.array_equal(t3_assembled, t3)

    t3[-1] = t3[-1].conj()
    t3 = np.angle(np.prod(t3, axis=1).value, deg=True)
    t3_assembled[-1] = t3_assembled[-1].conj()
    t3_assembled = np.angle(np.prod(t3_assembled, axis=1).value, deg=True)

    assert np.array_equal(t3_assembled, t3)


def test_t3_norm(fits_files: List[Path]):
    """Tests if there is a difference between the normed
    and non-normed bispectrum for the phase calculation."""
    data = get_data(fits_files, wavelengths="all")
    wls = OPTIONS.fit.wls
    spf = (
        np.hypot(data.t3.u, data.t3.v)[np.newaxis, :]
        / wls.to(u.m).value[:, np.newaxis]
        / u.rad
    )
    complex_t3 = vis_func(au_to_mas(1) * u.mas, spf)[:, data.t3.i123]
    bispectrum = complex_t3[:, 0] * complex_t3[:, 1] * complex_t3[:, 2].conj()
    t3 = np.angle(bispectrum.value, deg=True)

    normed_t3 = complex_t3 / np.abs(complex_t3[..., 0][..., np.newaxis])
    normed_bispectrum = normed_t3[:, 0] * normed_t3[:, 1] * normed_t3[:, 2].conj()
    nt3 = np.angle(normed_bispectrum.value, deg=True)
    assert np.allclose(nt3, t3)


def test_analytical_vs_component(fits_files: List[Path]):
    """Tests the analytical (direct bessel function) t3 calculation vs. the ring component's internal one."""
    data = get_data(fits_files, wavelengths="all")
    wls = OPTIONS.fit.wls
    spf = (
        np.hypot(data.t3.u123, data.t3.v123)[np.newaxis, ...]
        / wls.to(u.m).value[:, np.newaxis, np.newaxis]
        / u.rad
    )

    complex_t3 = vis_func(au_to_mas(1) * u.mas, spf)
    ring = assemble_ring(0, 0, 1, 0, 0, 0, 0, 0)
    complex_t3_comp = ring.compute_complex_vis(data.t3.u * u.m, data.t3.v * u.m, wls)

    assert np.allclose(complex_t3, complex_t3_comp[:, data.t3.i123])

    bispectrum = complex_t3[:, 0] * complex_t3[:, 1] * complex_t3[:, 2].conj()
    t3 = np.angle(bispectrum.value, deg=True)
    t3_comp = compute_t3(complex_t3_comp, data.t3.i123)
    assert np.array_equal(t3_comp, t3)


# TODO: Make sure phases are still correct
# def test_added_vs_bispectrum(fits_files: List[Path]):
#     """Tests calculating the t3 from the bispectrum vs. adding arguments of the three baselines directly."""
#     data = get_data(fits_files, wavelengths="all")
#     ring = assemble_ring(0, 0, 1, 0, 0, 0, 0, 0)
#     complex_t3 = ring.compute_complex_vis(
#         data.t3.u * u.m, data.t3.v * u.m, OPTIONS.fit.wls
#     )
#     t3 = compute_t3(complex_t3, data.t3.i123)
#     t3_added = np.angle(
#         [
#             (
#                 complex_t3[:, data.t3.i123][:, index]
#                 if index != 2
#                 else complex_t3[:, data.t3.i123][:, index].conj()
#             )
#             for index in range(3)
#         ],
#         deg=True,
#     )
#
#     assert np.allclose(t3, t3_added)
