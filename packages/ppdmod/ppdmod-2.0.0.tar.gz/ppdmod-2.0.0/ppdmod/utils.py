import shutil
import time as time
from pathlib import Path
from typing import Any, Callable, List, Tuple

import astropy.units as u
import numpy as np
from astropy.io import fits
from numpy.typing import NDArray
from scipy.interpolate import interp1d
from scipy.stats import linregress

from .options import OPTIONS


def save_model_to_fits(
    components: List, fits_files: List[Path], save_dir: Path, suffix: str = ".fits"
) -> None:
    """Calculates the model and saves it into the corresponding fits files."""
    for fits_file in fits_files:
        for t in range(OPTIONS.data.nt):
            shutil.copy(fits_file, save_dir / f"{fits_file.stem}_MODEL_t{t}{suffix}")
            with fits.open(
                save_dir / f"{fits_file.stem}_MODEL_t{t}{suffix}", "update"
            ) as hdul:
                instrument = hdul[0].header.get("instrume", "unknown").lower()
                sci_index = (
                    OPTIONS.data.gravity.index if instrument == "gravity" else None
                )
                wavelength = (
                    hdul["oi_wavelength", sci_index].data["eff_wave"] * u.m
                ).to(u.um)
                for extension in ["oi_vis", "oi_vis2", "oi_t3"]:
                    if extension in ["oi_vis", "oi_vis2"]:
                        ucoord = np.insert(
                            hdul[extension, sci_index].data["ucoord"], 0, 0
                        )
                        vcoord = np.insert(
                            hdul[extension, sci_index].data["vcoord"], 0, 0
                        )
                    elif extension == "oi_t3":
                        u1 = hdul[extension, sci_index].data["u1coord"]
                        u2 = hdul[extension, sci_index].data["u2coord"]
                        v1 = hdul[extension, sci_index].data["v1coord"]
                        v2 = hdul[extension, sci_index].data["v2coord"]
                        u123 = np.insert([u1, u2, u1 + u2], 0, 0, axis=1)
                        v123 = np.insert([v1, v2, v1 + v2], 0, 0, axis=1)
                        ucoord, vcoord, i123 = get_t3_indices(u123, v123)

                    complex_vis = np.sum(
                        [
                            comp.compute_complex_vis(ucoord, vcoord, t, wavelength)
                            for comp in components
                        ],
                        axis=0,
                    )

                    if extension in ["oi_vis", "oi_vis2"]:
                        model_flux = complex_vis[:, 0].reshape(-1, 1)
                        if extension == "oi_vis2":
                            val, err = "vis2data", "vis2err"
                            complex_vis /= model_flux
                            complex_vis *= complex_vis
                        else:
                            val, err = "visamp", "visamperr"
                            hdul["oi_flux", sci_index].data["fluxdata"] = np.abs(
                                model_flux.squeeze(-1)
                            )
                            hdul["oi_flux", sci_index].data["fluxerr"] = np.nan
                            hdul["oi_flux", sci_index].data["flag"] = False

                            if (
                                "visphi".upper()
                                in hdul[extension, sci_index].columns.names
                            ):
                                diff_phases = []
                                for phase in np.angle(complex_vis, deg=True).T[1:]:
                                    res = linregress(1 / wavelength.value, phase)
                                    diff_phases.append(
                                        phase
                                        - (
                                            res.slope * 1 / wavelength.value
                                            + res.intercept
                                        )
                                    )

                                hdul[extension, sci_index].data["visphi"] = np.array(
                                    diff_phases
                                )
                                hdul[extension, sci_index].data["visphierr"] = np.nan

                        hdul[extension, sci_index].data[val] = compute_vis(
                            complex_vis[:, 1:]
                        ).T
                        hdul[extension, sci_index].data[err] = np.nan
                        hdul[extension, sci_index].data["flag"] = False

                    elif extension == "oi_t3":
                        hdul[extension, sci_index].data["t3phi"] = compute_t3(
                            complex_vis, i123
                        )[:, 1:].T
                        hdul[extension, sci_index].data["t3phierr"] = np.nan
                        hdul[extension, sci_index].data["flag"] = False

                hdul.flush()


def get_binning_windows(wavelength: NDArray[Any]) -> u.Quantity[u.um]:
    """Gets all the binning windows."""
    skip_set = set()
    all_binning_windows = []
    for band in list(map(get_band, wavelength)):
        windows = getattr(OPTIONS.data.binning, band).value
        if band in skip_set:
            continue

        if isinstance(windows, (list, tuple, np.ndarray)):
            all_binning_windows.extend(windows)
            skip_set.add(band)
        else:
            all_binning_windows.append(windows)
    return all_binning_windows * u.um


def create_adaptive_bins(
    wavelength_range: List[float],
    wavelength_range_fine: List[float],
    bin_window_fine: float,
    bin_window_coarse: float,
) -> Tuple[NDArray[Any], NDArray[Any]]:
    """Create an adaptive binning wavelength grid.

    Parameters
    ----------
    wavelength_range : list of float
        The wavlenength range where bins with corresponding windows are to be created.
    wavelength_range_fine : list of float
        The wavelength range where the bins are to be fine.
    bin_window_fine : float
        The fine binning window (left and right of the bin).
    bin_window_coarse : float
        The coarse binning window (left and right of the bin).

    Returns
    -------
    bins : numpy.ndarray
    windows : numpy.ndarray
    """
    range_min, range_max = wavelength_range
    range_min_fine, range_max_fine = wavelength_range_fine

    if range_min >= range_max or range_min_fine >= range_max_fine:
        raise ValueError("Invalid wavelength ranges.")
    if not (range_min <= range_min_fine and range_max_fine <= range_max):
        raise ValueError("Wavelength range must be within the full wavelength range.")

    fine_bins = np.arange(range_min_fine, range_max_fine, bin_window_fine)
    lower_coarse_bins = np.arange(
        range_min, fine_bins[0] - bin_window_fine / 2, bin_window_coarse
    )
    upper_coarse_bins = np.arange(
        fine_bins[-1] + (bin_window_fine + bin_window_coarse) / 2,
        range_max,
        bin_window_coarse,
    )
    bins = np.unique(np.concatenate((lower_coarse_bins, fine_bins, upper_coarse_bins)))
    windows = np.concatenate(
        (
            np.full(lower_coarse_bins.shape, bin_window_coarse),
            np.full(fine_bins.shape, bin_window_fine),
            np.full(upper_coarse_bins.shape, bin_window_coarse),
        )
    )
    return bins, windows


def compare_angles(phi: float, psi: float) -> float:
    """Subtracts two angles [-π, π].

    Parameters
    ----------
    phi : float
        Angle (rad).
    psi : float
        Angle (rad).

    Returns
    -------
    float
        Difference of angles (rad).
    """
    diff = phi - psi
    diff = np.where(diff > np.pi, diff - 2 * np.pi, diff)
    diff = np.where(diff < -np.pi, diff + 2 * np.pi, diff)
    return diff


def windowed_linspace(start: float, end: float, window: float) -> NDArray[Any]:
    """Creates a numpy.linspace with a number of points so that the windowing doesn't overlap"""
    return np.linspace(start, end, int((end - start) // (2 * window / 2)) + 1)


def get_band_limits(band: str) -> Tuple[float, float]:
    """Gets the limits of the respective band"""
    match band:
        case "hband":
            return 1.5, 1.8
        case "kband":
            return 1.9, 2.5
        case "lband":
            return 2.6, 3.99
        case "mband":
            return 4.0, 6.0
        case "nband":
            return 7.5, 16.0
    return 0, 0


def get_band(wavelength: u.um) -> str:
    """Gets the band of the (.fits)-file."""
    wavelength = wavelength.value if isinstance(wavelength, u.Quantity) else wavelength
    wl_min, wl_max = wavelength.min(), wavelength.max()
    if wl_min > 1.5 and wl_max < 1.8:
        return "hband"
    if wl_min > 1.9 and wl_max < 2.5:
        return "kband"
    if wl_min > 2.6 and wl_max < 4.0:
        return "lband"
    if wl_min >= 4.0 and wl_max < 6.0:
        return "mband"
    if wl_min > 2.6 and wl_max < 6:
        return "lmband"
    if wl_min > 7.5 and wl_max < 16.0:
        return "nband"
    return "unknown"


def get_band_indices(grid: NDArray[Any], bands: List[str]) -> NDArray[Any]:
    """Gets the indices for a 1D grid that is matched to the bands."""
    indices = []
    for band in bands:
        limits = get_band_limits(band)
        indices.append(np.where((grid >= limits[0]) & (grid <= limits[1]))[0])

    return np.concatenate(indices)


def smooth_interpolation(
    interpolation_points: NDArray[Any],
    grid: NDArray[Any],
    values: NDArray[Any],
    kind: str | None = None,
    fill_value: str | None = None,
) -> NDArray[Any]:
    """Rebins the grid to a higher factor and then interpolates and averages
    to the original grid.

    Parameters
    ----------
    interpolation_points : numpy.ndarray
        The points to interpolate to.
    points : numpy.ndarray
        The points to interpolate from.
    values : numpy.ndarray
        The values to interpolate.
    """
    kind = OPTIONS.data.interpolation.kind if kind is None else kind
    fill_value = (
        OPTIONS.data.interpolation.fill_value if fill_value is None else fill_value
    )
    points = interpolation_points.flatten()
    windows = get_binning_windows(points).value
    interpolation_grid = (
        np.linspace(-1, 1, OPTIONS.data.interpolation.dim) * windows[:, np.newaxis] / 2
    ).T + points
    return (
        np.interp(interpolation_grid, grid, values)
        .mean(axis=0)
        .reshape(interpolation_points.shape)
    )


def get_indices(
    values: NDArray[Any],
    array: NDArray[Any],
    windows: NDArray[Any] | float | None = None,
) -> List[np.ndarray]:
    """Gets the indices of values occurring in a numpy array
    and returns it in a list corresponding to the input values.

    Parameters
    ----------
    values : numpy.typing.NDArray
        The values to find.
    array : numpy.typing.NDArray
        The array to search in.
    window : numpy.typing.NDArray or float, optional
        The window around the value to search in.
    """
    array = array.value if isinstance(array, u.Quantity) else array
    values = values.value if isinstance(values, u.Quantity) else values
    values = [values] if not isinstance(values, (list, tuple, np.ndarray)) else values
    windows = windows.value if isinstance(windows, u.Quantity) else windows

    if windows is not None:
        if isinstance(windows, (list, tuple, np.ndarray)):
            indices = [
                np.where(((v - w / 2) < array) & ((v + w / 2) > array))[0]
                for v, w in zip(values, windows)
            ]
        else:
            indices = [
                np.where(((v - windows / 2) < array) & ((v + windows / 2) > array))[0]
                for v in values
            ]
    else:
        indices = []
        for value in values:
            index = np.where(array == value)[0]
            if index.size == 0:
                if value < array[0] or value > array[-1]:
                    indices.append(index.astype(int).flatten())
                    continue

                index = np.where(array == min(array, key=lambda x: abs(x - value)))[0]

            indices.append(index.astype(int).flatten())
    return indices


def transform_coordinates(
    x: float | np.ndarray,
    y: float | np.ndarray,
    cinc: float | None = None,
    pa: float | None = None,
    axis: str = "y",
) -> Tuple[float | np.ndarray, float | np.ndarray]:
    """Stretches and rotates the coordinate space depending on the
    cosine of inclination and the positional angle.

    Parameters
    ----------
    x: float or numpy.ndarray or astropy.units.Quantity
        The x-coordinate.
    y: float or numpy.ndarray or astropy.units.Quantity
        The y-coordinate.
    cinc: float, optional
        The cosine of the inclination.
    pa: float, optional
        The positional angle of the object (in degree).
    axis: str, optional
        The axis to stretch the coordinates on.

    Returns
    -------
    xt: float or numpy.ndarray
        Transformed x coordinate.
    yt: float or numpy.ndarray
        Transformed y coordinate.
    """
    if pa is not None:
        xt = x * np.cos(pa) - y * np.sin(pa)
        yt = x * np.sin(pa) + y * np.cos(pa)
    else:
        xt, yt = x, y

    if cinc is not None:
        if axis == "x":
            xt /= cinc
        elif axis == "y":
            xt *= cinc

    return xt, yt


def translate_vis(
    ucoord: np.ndarray, vcoord: np.ndarray, x: float, y: float
) -> np.ndarray:
    """Translates a coordinate shift in image space to Fourier space.

    Parameters
    ----------
    """
    translation = np.exp(-2j * np.pi * (x * ucoord + y * vcoord))
    return translation.astype(OPTIONS.data.dtype.complex)


def translate_image(
    xx: np.ndarray, yy: np.ndarray, x: float, y: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Shifts the coordinates in image space according to an offset."""
    xxs = (xx - x).astype(OPTIONS.data.dtype.real)
    yys = (yy - y).astype(OPTIONS.data.dtype.real)
    return xxs, yys


def qval_to_opacity(qval_file: Path) -> u.cm**2 / u.g:
    """Reads a qval file, then calculates and returns the
    opacity.

    Parameters
    ----------
    qval_file : pathlib.Path

    Returns
    -------
    opacity : astropy.units.cm**2/u.g

    Notes
    -----
    The qval-files give the grain size in microns and the
    density in g/cm^3.
    """
    with open(qval_file, "r+", encoding="utf8") as file:
        _, grain_size, density = map(float, file.readline().strip().split())
    wavelength_grid, qval = np.loadtxt(
        qval_file, skiprows=1, unpack=True, usecols=(0, 1)
    )
    return wavelength_grid * u.um, 3 * qval / (
        4 * (grain_size * u.um).to(u.cm) * (density * u.g / u.cm**3)
    )


def get_opacity(
    source_dir: Path,
    weights: np.ndarray,
    names: List[str],
    method: str,
    individual: bool = False,
    **kwargs,
) -> Tuple[np.ndarray, np.ndarray]:
    """Gets the opacity from input parameters."""
    grf_dict = {
        "olivine": "Olivine",
        "pyroxene": "MgPyroxene",
        "forsterite": "Forsterite",
        "enstatite": "Enstatite",
        "silica": "Silica",
    }

    files = []
    for name in names:
        name = name.lower()
        for size in ["small", "large"]:
            if method == "grf":
                size = 0.1 if size == "small" else 2
                file_name = f"{grf_dict[name]}{size:.1f}.Combined.Kappa"
            else:
                size = "Big" if size == "large" else size.title()
                file_name = f"{size}{name.title()}.kappa"

            files.append(source_dir / method / file_name)

    usecols = (0, 2) if method == "grf" else (0, 1)
    wl, opacity = load_data(files, usecols=usecols, **kwargs)

    if individual:
        return wl, opacity

    opacity = (opacity * weights[:, np.newaxis]).sum(axis=0)
    return wl, opacity


def load_data(
    files: Path | List[Path],
    load_func: Callable | None = None,
    comments: str = "#",
    skiprows: int = 1,
    usecols: Tuple[int, int] = (0, 1),
    method: str = "shortest",
    kind: str | None = None,
    fill_value: str | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Loads data from a file.

    Can either be one or multiple files, but in case
    of multiple files they need to have the same structure

    and size (as they will be converted to numpy.ndarrays).

    Parameters
    ----------
    files : list of pathlib.Path
        The files to load the data from.
    load_func : callable, optional
        The function to load the data with.
    comments : str, optional
        Comment identifier.
    skiprows : str, optional
        The rows to skip.
    usecols : tuple of int, optional
        The columns to use.
    method : str, optional
        The grid to interpolate/extrapolate the data on.
        Default is 'shortest'. Other option is 'longest' or
        'median'.
    kind : str, optional
        The interpolation kind.
        Default is 'cubic'.
    fill_value : str, optional
        If "extrapolate", the data is extrapolated.
        Default is None.

    Returns
    -------
    wavelength_grid : numpy.ndarray
    data : numpy.ndarray
    """
    kind = OPTIONS.data.interpolation.kind if kind is None else kind
    fill_value = (
        OPTIONS.data.interpolation.fill_value if fill_value is None else fill_value
    )

    files = files if isinstance(files, list) else [files]
    wavelength_grids, contents = [], []
    for file in files:
        if load_func is not None:
            wavelengths, content = load_func(file)
        else:
            wavelengths, content = np.loadtxt(
                file, skiprows=skiprows, usecols=usecols, comments=comments, unpack=True
            )

        if isinstance(wavelengths, u.Quantity):
            wavelengths = wavelengths.value
            content = content.value

        wavelength_grids.append(wavelengths)
        contents.append(content)

    sizes = [np.size(wl) for wl in wavelength_grids]
    if method == "longest":
        wavelength_grid = wavelength_grids[np.argmax(sizes)]
    elif method == "shortest":
        wavelength_grid = wavelength_grids[np.argmin(sizes)]
    else:
        wavelength_grid = wavelength_grids[
            np.median(sizes).astype(int) == wavelength_grids
        ]

    data = []
    for wavelengths, content in zip(wavelength_grids, contents):
        if np.array_equal(wavelengths, wavelength_grid):
            data.append(content)
            continue

        data.append(
            interp1d(wavelengths, content, kind=kind, fill_value=fill_value)(
                wavelength_grid
            )
        )

    return wavelength_grid.squeeze(), np.array(data).squeeze()


def get_t3_indices(x: np.ndarray, y: np.ndarray):
    """Gets the unique indices of t3 so it can be quickly calcualted as a 1D array."""
    unique_coords = np.unique(np.column_stack((x.ravel(), y.ravel())), axis=0)
    ucoord, vcoord = unique_coords[:, 0], unique_coords[:, 1]
    index123 = np.vectorize(lambda x: np.where(ucoord == x)[0][0])(x)
    return ucoord, vcoord, index123


def compute_vis(vis: np.ndarray) -> np.ndarray:
    """Computes the visibilities from the visibility function."""
    return np.abs(vis).astype(OPTIONS.data.dtype.real)


def compute_t3(vis: np.ndarray, indices: List[float]) -> np.ndarray:
    """Computes the closure phase from the visibility function."""
    if vis.size == 0:
        return np.array([])

    vis = vis[..., indices]
    return np.angle(vis[:, 0] * vis[:, 1] * vis[:, 2].conj(), deg=True)
