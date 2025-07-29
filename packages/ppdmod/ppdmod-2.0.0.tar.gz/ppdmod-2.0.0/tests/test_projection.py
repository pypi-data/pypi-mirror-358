from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from ppdmod.utils import transform_coordinates


def get_normal(polar: float, azimuth: float) -> NDArray[Any]:
    """Gets the normal vector for a polar and azimuth angle.

    Parameters
    ----------
    pola: float, optional
        The polar angle (radians).
    pa: float, optional
        The azimuth angle (radians).

    Returns
    -------
    normal : numpy.typing.NDArray
    """
    return np.array(
        [
            -np.sin(polar) * np.sin(azimuth),
            np.sin(polar) * np.cos(azimuth),
            np.cos(polar),
        ]
    )


def ring_model(rin, dim, pixel_size, i, pa):
    """A ring model."""
    x = np.linspace(-0.5, 0.5, dim, endpoint=False) * dim * pixel_size
    xt, yt = transform_coordinates(*np.meshgrid(x, x), np.cos(i), pa, axis="x")
    dx = np.max(
        [
            np.abs(1.0 * (xt[0, 1] - xt[0, 0])),
            np.abs(1.0 * (yt[1, 0] - yt[0, 0])),
        ]
    )
    grid = np.hypot(xt, yt)
    return ((grid <= (rin + dx)) & (grid >= (rin / 2))).astype(float)


def compare_angles(i, pa):
    au_to_mas = 1e3 / 158.51
    dim, pixel_size = 2048, 0.01
    i, pa = np.deg2rad(i), np.deg2rad(pa)
    image = ring_model(au_to_mas, dim, pixel_size, i, pa)

    # NOTE: Compare the projection to the 3D case
    normal = get_normal(i, pa)
    assert np.isclose(normal[-1], np.cos(i))
    assert np.isclose(np.tan((pa - np.pi / 2) % (2 * np.pi)), normal[1] / normal[0])

    extent = np.array([-0.5, 0.5, -0.5, 0.5]) * dim * pixel_size
    _, ax = plt.subplots()
    ax.imshow(image, label="2D inc. + rot.", extent=extent, origin="lower", cmap="Greys")
    ax.set_ylim([-8, 8])
    ax.set_xlim([-8, 8])
    ax.set_xlabel(r"$\Delta\alpha$ (mas)")
    ax.set_ylabel(r"$\Delta\delta$ (mas)")
    ax.set_aspect("equal")
    ax.invert_xaxis()

    # NOTE: Transform back to display in degrees
    i, pa = np.rad2deg(i), np.rad2deg(pa)
    plt.title(rf"Angle Check - i: {i:.2f}, $\theta$: {pa:.2f}")
    plt.savefig(f"angle_check_{i:.0f}_{pa:.0f}.png", dpi=300)


if __name__ == "__main__":
    for i, pa in zip([46.39, 46.39, 23.76, 60], [352, 172, 15.44, 45]):
        compare_angles(i, pa)
