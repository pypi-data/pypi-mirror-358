import copy
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple

import astropy.units as u
import numpy as np
from astropy.io import fits
from numpy.typing import NDArray
from scipy.stats import circmean, circstd

from .options import OPTIONS
from .utils import (
    get_band,
    get_binning_windows,
    get_indices,
    get_t3_indices,
)


def mean_and_err(key: str):
    """Gets the mean and std functions."""
    t3_kwargs, axis = {"low": -180, "high": 180, "nan_policy": "omit"}, -1
    if key == "t3":
        mean_func = partial(circmean, axis=axis, **t3_kwargs)
        err_func = lambda x: np.sqrt(
            np.ma.sum(x**2, axis=axis).filled(np.nan)
            + circstd(x, axis=axis, **t3_kwargs) ** 2
        )
    else:
        mean_func = lambda x: np.ma.mean(x, axis=axis).filled(np.nan)
        err_func = lambda x: np.ma.sqrt(
            np.ma.sum(x**2, axis=axis) + np.ma.std(x, axis=axis) ** 2
        ).filled(np.nan)

    return mean_func, err_func


class ReadoutFits:
    """All functionality to work with (.fits) or flux files.

    Parameters
    ----------
    fits_file : pathlib.Path
        The path to the (.fits) or flux file.
    """

    def __init__(self, fits_file: Path) -> None:
        """The class's constructor."""
        self.fits_file = Path(fits_file)
        self.name = self.fits_file.name
        self.band = "unknown"
        self.read_file()

    def read_file(self) -> None:
        """Reads the data of the (.fits)-files into vectors."""
        with fits.open(self.fits_file) as hdul:
            instrument = None
            if "instrume" in hdul[0].header:
                instrument = hdul[0].header["instrume"].lower()
            sci_index = OPTIONS.data.gravity.index if instrument == "gravity" else None
            self.wl = (hdul["oi_wavelength", sci_index].data["eff_wave"] * u.m).to(u.um)
            self.band = get_band(self.wl)
            self.array = (
                "ats" if "AT" in hdul["oi_array"].data["tel_name"][0] else "uts"
            )
            self.flux = self.read_into_namespace(hdul, "flux", sci_index)
            self.t3 = self.read_into_namespace(hdul, "t3", sci_index)
            self.vis = self.read_into_namespace(hdul, "vis", sci_index)
            self.vis2 = self.read_into_namespace(hdul, "vis2", sci_index)

    def read_into_namespace(
        self,
        hdul: fits.HDUList,
        key: str,
        sci_index: int | None = None,
    ) -> SimpleNamespace:
        """Reads a (.fits) card into a namespace."""
        try:
            hdu = hdul[f"oi_{key}", sci_index]
            data = hdu.data
        except KeyError:
            return SimpleNamespace(
                val=np.array([]),
                err=np.array([]),
                u=np.array([]).reshape(1, -1),
                v=np.array([]).reshape(1, -1),
            )

        if key == "flux":
            try:
                return SimpleNamespace(
                    val=np.ma.masked_array(data["fluxdata"], mask=data["flag"]),
                    err=np.ma.masked_array(data["fluxerr"], mask=data["flag"]),
                )
            except KeyError:
                return SimpleNamespace(
                    val=np.array([]), err=np.array([]), flag=np.array([])
                )

        # TODO: Might err if vis is not included in datasets
        if key in ["vis", "vis2"]:
            if key == "vis":
                val_key, err_key = "visamp", "visamperr"
            else:
                val_key, err_key = "vis2data", "vis2err"

            ucoord = data["ucoord"].reshape(1, -1).astype(OPTIONS.data.dtype.real)
            vcoord = data["vcoord"].reshape(1, -1).astype(OPTIONS.data.dtype.real)
            return SimpleNamespace(
                val=np.ma.masked_array(data[val_key], mask=data["flag"]),
                err=np.ma.masked_array(data[err_key], mask=data["flag"]),
                u=np.round(ucoord, 2),
                v=np.round(vcoord, 2),
            )

        u1, u2 = map(lambda x: data[f"u{x}coord"], ["1", "2"])
        v1, v2 = map(lambda x: data[f"v{x}coord"], ["1", "2"])
        u123 = np.array([u1, u2, u1 + u2]).astype(OPTIONS.data.dtype.real)
        v123 = np.array([v1, v2, v1 + v2]).astype(OPTIONS.data.dtype.real)
        return SimpleNamespace(
            val=np.ma.masked_array(data["t3phi"], mask=data["flag"]),
            err=np.ma.masked_array(data["t3phierr"], mask=data["flag"]),
            u123=np.round(u123, 2),
            v123=np.round(v123, 2),
        )

    def get_data_for_wavelength(
        self,
        wavelength: u.Quantity,
        key: str,
        do_bin: bool = True,
        min_err: Dict[str, float] | None = None,
    ) -> Tuple[NDArray[Any], NDArray[Any]]:
        """Gets the data for the given wavelengths.

        If there is no data for the given wavelengths,
        a np.nan array is returned of the shape
        (wavelength.size, data.shape[0]).

        Parameters
        ----------
        wavelength : astropy.units.um
            The wavelengths to be returned.
        key : str
            The key (header) of the data to be returned.
        do_bin : bool, optional
            If the data should be binned or not.
        min_err : dict, optional
            A dictionary containing the minimum error for the data.
            Will be applied to the data before binning.

        Returns
        -------
        numpy.typing.NDArray
            The values for the given wavelengths.
        numpy.typing.NDArray
            The errors for the given wavelengths.
        """
        if do_bin:
            # TODO: Check if binning is done correctly -> No duplicates, etc.
            # Should there be an error if the bins overlap? -> Maybe a good idea
            # Or at least a warning
            windows = get_binning_windows(wavelength)
            indices = get_indices(wavelength, array=self.wl, windows=windows)
        else:
            indices = [np.where(wl == self.wl)[0] for wl in wavelength]

        val, err = getattr(self, key).val, getattr(self, key).err
        if all(index.size == 0 for index in indices):
            nan_val = np.full((wavelength.size, val.shape[0]), np.nan)
            nan_err = np.full((wavelength.size, err.shape[0]), np.nan)
            if "flux":
                wl_val, wl_err = nan_val, nan_err
            else:
                wl_val, wl_err = nan_val[:, :1], nan_err[:, :1]

            return wl_val, wl_err

        if min_err is not None:
            error_floor = min_err.get(key, 0.0)
            if key == "t3":
                err[err < error_floor] = error_floor
            else:
                ind = np.where(err < val * error_floor)
                err[ind] = val[ind] * error_floor

        mean_func, err_func = mean_and_err(key)
        if do_bin:
            wl_val = [mean_func(val[:, index]) for index in indices]
            wl_err = [err_func(err[:, index]) for index in indices]
        else:
            wl_val = [
                (
                    val[:, index].filled(np.nan).squeeze(-1)
                    if index.size != 0
                    else np.full((val.shape[0],), np.nan)
                )
                for index in indices
            ]
            wl_err = [
                (
                    err[:, index].filled(np.nan).squeeze(-1)
                    if index.size != 0
                    else np.full((err.shape[0],), np.nan)
                )
                for index in indices
            ]

        wl_val = np.array(wl_val, dtype=OPTIONS.data.dtype.real)
        wl_err = np.array(wl_err, dtype=OPTIONS.data.dtype.real)
        return wl_val, wl_err


def get_all_wavelengths(readouts: List[ReadoutFits] | None = None) -> NDArray[Any]:
    """Gets all wavelengths from the readouts."""
    readouts = OPTIONS.data.readouts if readouts is None else readouts
    return np.sort(np.unique(np.concatenate(list(map(lambda x: x.wl, readouts)))))


def set_fit_wavelengths(
    wavelengths: u.Quantity[u.um] | None = None,
) -> str | NDArray[Any]:
    """Sets the wavelengths to be fitted for as a global option.

    If called without a wavelength and all set to False, it will clear
    the fit wavelengths.

    Parameters
    ----------
    wavelengths : numpy.typing.NDArray, optional
        The wavelengths to be fitted.

    Returns
    -------
    str or numpy.typing.NDArray
        The wavelengths to be fitted as a numpy array or "all" if all are to be
        fitted.
    """
    OPTIONS.fit.wls = None
    if wavelengths is None:
        return

    wavelengths = u.Quantity(wavelengths, u.um)
    if wavelengths.shape == ():
        wavelengths = wavelengths.reshape((wavelengths.size,))
    OPTIONS.fit.wls = wavelengths.flatten()
    return OPTIONS.fit.wls


def get_counts_data() -> np.ndarray:
    """Gets the number of data points for the flux,
    visibilities and closure phases."""
    counts = []
    for key in OPTIONS.fit.data:
        counts.append(getattr(OPTIONS.data, key).val[0].compressed().size)

    return np.array(counts)


def clear_data() -> List[str]:
    """Clears data and returns the keys of the cleared data."""
    OPTIONS.fit.wls = None
    OPTIONS.data.readouts = []

    for key in ["flux", "vis", "vis2", "t3"]:
        data = getattr(OPTIONS.data, key)
        data.val, data.err = [np.array([]) for _ in range(2)]
        if key in ["vis", "vis2"]:
            data.u, data.v = [np.array([]).reshape(1, -1) for _ in range(2)]
        elif key in "t3":
            data.u123, data.v123 = [np.array([]) for _ in range(2)]

    return ["flux", "vis", "vis2", "t3"]


def read_data(
    data_to_read: List[str], wavelengths: u.um, min_err: Dict[str, float] | None = None
) -> None:
    """Reads in the data from the keys."""
    for readout in OPTIONS.data.readouts:
        for key in data_to_read:
            data = getattr(OPTIONS.data, key)
            data_readout = getattr(readout, key)
            val, err = readout.get_data_for_wavelength(
                wavelengths, key, OPTIONS.data.do_bin, min_err
            )
            if data.val.size == 0:
                data.val, data.err = val, err
            else:
                data.val = np.hstack((data.val, val))
                data.err = np.hstack((data.err, err))

            if key in ["vis", "vis2"]:
                if data.u.size == 0:
                    data.u = np.insert(data_readout.u, 0, 0, axis=1)
                    data.v = np.insert(data_readout.v, 0, 0, axis=1)
                else:
                    data.u = np.hstack((data.u, data_readout.u))
                    data.v = np.hstack((data.v, data_readout.v))

            elif key == "t3":
                if data.u123.size == 0:
                    tmp_u123 = np.insert(data_readout.u123, 0, 0, axis=1)
                    tmp_v123 = np.insert(data_readout.v123, 0, 0, axis=1)
                    data.u123, data.v123 = tmp_u123, tmp_v123
                    data.u, data.v, data.i123 = get_t3_indices(data.u123, data.v123)
                else:
                    ucoord, vcoord, i123 = get_t3_indices(
                        data_readout.u123, data_readout.v123
                    )
                    data.u123 = np.hstack((data.u123, data_readout.u123))
                    data.v123 = np.hstack((data.v123, data_readout.v123))
                    data.u = np.hstack((data.u, ucoord))
                    data.v = np.hstack((data.v, vcoord))
                    data.i123 = np.hstack((data.i123, i123 + data.i123.max() + 1))

    # NOTE: Make this work with no time input files again
    nt = OPTIONS.data.nt
    for key in data_to_read:
        data = getattr(OPTIONS.data, key)
        data.val = np.tile(
            np.ma.masked_invalid(data.val).filled(np.nan),
            (nt,) + (1,) * len(data.val.shape),
        ).tolist()
        data.err = np.tile(
            np.ma.masked_invalid(data.err).filled(np.nan), (nt,) + (1,) * len(data.err.shape)
        ).tolist()
        if key in ["vis", "vis2", "t3"]:
            data.u = np.tile(data.u, (nt,) + (1,) * len(data.u.shape)).tolist()
            data.v = np.tile(data.v, (nt,) + (1,) * len(data.v.shape)).tolist()
        if key == "t3":
            data.u123 = np.tile(data.u123, (nt,) + (1,) * len(data.u123.shape)).tolist()
            data.v123 = np.tile(data.v123, (nt,) + (1,) * len(data.v123.shape)).tolist()
            data.i123 = np.tile(data.i123, (nt,) + (1,) * len(data.i123.shape)).tolist()

    # NOTE: This only works if all the time datasets have the same amount of (u, v)-coordinates
    # and also if there is the same number of them.
    for index, readout in enumerate(OPTIONS.data.readouts_t):
        for key in data_to_read:
            data = getattr(OPTIONS.data, key)
            data_readout = getattr(readout, key)
            val, err = readout.get_data_for_wavelength(
                wavelengths, key, OPTIONS.data.do_bin, min_err
            )
            data.val[index] = np.hstack((data.val[index], val))
            data.err[index] = np.hstack((data.err[index], err))

            if key in ["vis", "vis2"]:
                data.u[index] = np.hstack((data.u[index], data_readout.u))
                data.v[index] = np.hstack((data.v[index], data_readout.v))
            elif key == "t3":
                ucoord, vcoord, i123 = get_t3_indices(
                    data_readout.u123, data_readout.v123
                )
                data.u[index] = np.hstack((data.u[index], ucoord))
                data.v[index] = np.hstack((data.v[index], vcoord))
                data.u123[index] = np.hstack((data.u123[index], data_readout.u123))
                data.v123[index] = np.hstack((data.v123[index], data_readout.v123))
                data.i123[index] = np.hstack(
                    (data.i123[index], i123 + np.max(data.i123[index]) + 1)
                )

    for key in data_to_read:
        data = getattr(OPTIONS.data, key)
        data.val = np.ma.masked_invalid(data.val)
        data.err = np.ma.masked_invalid(data.err)

        if key in ["vis", "vis2", "t3"]:
            data.u, data.v = np.array(data.u), np.array(data.v)
        if key == "t3":
            data.u123, data.v123 = np.array(data.u123), np.array(data.v123)
            data.i123 = np.array(data.i123)


def get_weights(kind="general") -> NDArray[Any]:
    """Gets the weights either for the indiviudal band or the general ones for the observables."""
    if kind == "general":
        return np.array(
            [getattr(OPTIONS.fit.weights, key).general for key in OPTIONS.fit.data]
        )

    return np.array(
        [
            [
                getattr(getattr(OPTIONS.fit.weights, key), band)
                for band in OPTIONS.fit.bands
            ]
            for key in OPTIONS.fit.data
        ]
    )


def set_weights(weights, weights_bands) -> None:
    """Sets the weights from the input."""
    if weights is not None:
        if weights == "ndata":
            ndata = get_counts_data()
            weights = dict(zip(OPTIONS.fit.data, (ndata / ndata.max()) ** -1))

        for key, weight in weights.items():
            getattr(OPTIONS.fit.weights, key).general = weight

    if weights_bands is not None:
        for key, band_values in weights_bands.items():
            for band, value in band_values.items():
                setattr(getattr(OPTIONS.fit.weights, key), band, value)


def get_data(
    fits_files: Path | List[Path] | None = [],
    fits_files_t: Path | List[Path] | None = [],
    wavelengths: str | u.Quantity[u.um] | None = None,
    fit_data: List[str] = ["flux", "vis", "t3"],
    weights: Dict[str, float] | str | None = None,
    weights_bands: Dict[str, float] | None = None,
    min_err: Dict[str, float] | None = None,
    **kwargs,
) -> SimpleNamespace:
    """Sets the data as a global variable from the input files.

    If called without parameters or recalled, it will clear the data.

    Parameters
    ----------
    fits_files : list of pathlib.Path
        Paths to (.fits)-files.
    fits_files_t : list of pathlib.Path
        Paths to time-dependent (.fits)-files.
    wavelengts : str or numpy.ndarray
        The wavelengths to be fitted as a numpy array or "all" if all are to be
        fitted.
    fit_data : list of str, optional
        The data to be fitted.
    weights : list of float, optional
        The fitting weights of the interferometric datasets.
    weights_band : list of float, optional
        The fitting weights of the interferometric datasets individual bands.
    set_std_err : list of str, optional
        The data to be set the standard error from the variance of the datasets from.
    min_err : float, optional
        The error floor for the datasets. The keys of the dictionary need to correspond to the
        entries for the fit data argument.
    """
    data_to_read = clear_data()
    if fits_files is None:
        return OPTIONS.data

    if not isinstance(fits_files, (list, tuple, np.ndarray)):
        fits_files = [fits_files]

    if not isinstance(fits_files_t, (list, tuple, np.ndarray)):
        fits_files_t = [fits_files_t]

    OPTIONS.fit.data = fit_data
    hduls = [fits.open(fits_file) for fits_file in fits_files]
    hduls_t = [fits.open(fits_file) for fits_file in fits_files_t]
    OPTIONS.data.hduls = [copy.deepcopy(hdul) for hdul in hduls]
    OPTIONS.data.hduls_t = [copy.deepcopy(hdul) for hdul in hduls_t]
    [hdul.close() for hdul in [*hduls, *hduls_t]]
    OPTIONS.data.nt = len(hduls_t) if len(hduls_t) != 0 else 1

    OPTIONS.data.readouts = list(map(ReadoutFits, fits_files))
    OPTIONS.data.readouts_t = list(map(ReadoutFits, fits_files_t))

    OPTIONS.data.bands = list(map(lambda x: x.band, OPTIONS.data.readouts))
    if wavelengths == "all":
        wavelengths = get_all_wavelengths(
            [*OPTIONS.data.readouts, *OPTIONS.data.readouts_t]
        )
        OPTIONS.data.do_bin = False

    if wavelengths is None:
        raise ValueError("No wavelengths given and/or not 'all' specified!")

    wavelengths = set_fit_wavelengths(wavelengths)
    read_data(data_to_read, wavelengths, min_err)

    for key in OPTIONS.fit.data:
        for band in OPTIONS.fit.bands:
            setattr(getattr(OPTIONS.fit.weights, key), band, 1)

    set_weights(weights, weights_bands)
    return OPTIONS.data
