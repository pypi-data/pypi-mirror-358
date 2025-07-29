import sys
from multiprocessing import Pool
from pathlib import Path
from typing import Any, List, Tuple

import dynesty.utils as dyutils
import numpy as np
from dynesty import DynamicNestedSampler
from numpy.typing import NDArray

from .base import Component
from .data import get_weights
from .options import OPTIONS
from .parameter import Parameter
from .utils import compare_angles, compute_t3, compute_vis, get_band_indices

CURRENT_MODULE = sys.modules[__name__]


def get_fit_params(components: List[Component], key: str | None = None) -> NDArray[Any]:
    """Gets the fit params from the components.

    Parameters
    ----------
    components : list of Component
        The components to be used in the model.
    key : str, optional
        If a key is provided, a field of the parameter will be returned.

    Returns
    -------
    params : numpy.typing.NDArray
    """
    params = []
    [
        params.extend(component.get_params(free=True, shared=False).values())
        for component in components
    ]
    params.extend(
        [
            component.get_params(free=True, shared=True).values()
            for component in components
        ][-1]
    )

    if key is not None:
        return np.array([getattr(param, key, None) for param in params])

    return np.array(params)


def get_labels(components: List[Component]) -> NDArray[Any]:
    """Sets theta from the components.

    Parameters
    ----------
    components : list of Component
        The components to be used in the model.

    Returns
    -------
    theta : numpy.typing.NDArray
    """
    labels, labels_shared = [], []
    for index, component in enumerate(components):
        component_labels = [key for key in component.get_params(free=True)]
        labels.extend([f"{label}-{index}" for label in component_labels])
        labels_shared.append(
            [
                rf"{key}-\mathrm{{sh}}"
                for key in component.get_params(free=True, shared=True)
            ]
        )

    labels.extend(labels_shared[-1])
    return labels


def get_priors(components: List[Component]) -> NDArray[Any]:
    """Gets the priors from the model parameters."""
    return np.array([param.get_limits() for param in get_fit_params(components)])


def get_units(components: List[Component]) -> NDArray[Any]:
    """Sets the units from the components."""
    return get_fit_params(components, "unit")


def get_theta(components: List[Component]) -> NDArray[Any]:
    """Sets the theta vector from the components."""
    return get_fit_params(components, "value")


def set_components_from_theta(
    theta: NDArray[Any], uniform: NDArray[Any] = np.array([])
) -> List[Component]:
    """Sets the components from theta."""
    components = [component.copy() for component in OPTIONS.model.components]
    nshared = len(components[-1].get_params(free=True, shared=True))
    if nshared != 0:
        theta_list, shared_params = theta[:-nshared], theta[-nshared:]
        uniforms, shared_uniforms = uniform[:-nshared], uniform[-nshared:]
    else:
        theta_list, shared_params = theta, np.array([])
        uniforms, shared_uniforms = uniform, np.array([])

    theta_list, uniform_list = theta_list.copy().tolist(), uniforms.copy().tolist()
    shared_params_labels = [
        label.split("-")[0] for label in get_labels(components) if "sh" in label
    ]

    for component in components:
        for param in component.get_params(free=True).values():
            param.value = theta_list.pop(0)
            param.free = True
            if uniforms.size != 0:
                param.uniform = uniform_list.pop(0)

        for index, (param_name, value) in enumerate(
            zip(shared_params_labels, shared_params)
        ):
            if hasattr(component, param_name):
                param = getattr(component, param_name)
                param.value = value
                param.free = param.shared = True

                if shared_uniforms.size != 0:
                    param.uniform = shared_uniforms[index]

    return components


def compute_residuals(
    data: NDArray[Any], model_data: NDArray[Any], kind: str = "linear"
) -> NDArray[Any]:
    """Computes the residuals from data vs. model."""
    if kind == "periodic":
        return np.rad2deg(compare_angles(np.deg2rad(data), np.deg2rad(model_data)))
    return data - model_data


def compute_chi_sq(
    data: NDArray[Any],
    sigma_sq: NDArray[Any],
    model: NDArray[Any],
    kind: str = "linear",
) -> float:
    """Computes the chi sq from."""
    return np.sum(compute_residuals(data, model, kind) ** 2 / sigma_sq)


def compute_loglike(
    data: NDArray[Any],
    error: NDArray[Any],
    model: NDArray[Any],
    kind: str = "linear",
    lnf: float | None = None,
):
    """Computes the chi square minimisation.

    Parameters
    ----------
    data : numpy.typing.NDArray
        The real data.
    error : numpy.typing.NDArray
        The real data's error.
    model : numpy.typing.NDArray
        The model data.
    kind : str, optional
        The method to determine the residuals of the dataset.
        Either "linear" or "periodic". Default is "linear".

    Returns
    -------
    chi_sq : float
    """
    sn = error**2
    if lnf is not None:
        sn += model**2 * np.exp(2 * lnf)

    chi_sq = compute_chi_sq(data, sn, model, kind)
    lnorm = np.sum(data.size * np.log(2 * np.pi) + np.log(sn))
    return -0.5 * (chi_sq + lnorm)


def compute_observables(
    components: List[Component],
    time: NDArray[Any] | None = None,
    wavelength: NDArray[Any] | None = None,
) -> Tuple[NDArray[Any], NDArray[Any], NDArray[Any]]:
    """Calculates the observables from the model.

    Parameters
    ----------
    components : list of Component
        The components to be used in the model.
    time : numpy.typing.NDArray, optional
        The time to be used in the model.
    wavelength : numpy.typing.NDArray, optional
        The wavelength to be used in the model.
    """
    wavelength = OPTIONS.fit.wls if wavelength is None else wavelength
    times = range(time if time is not None else OPTIONS.data.nt)
    vis = OPTIONS.data.vis2 if "vis2" in OPTIONS.fit.data else OPTIONS.data.vis
    t3 = OPTIONS.data.t3
    complex_vis, complex_t3 = [], []
    for t in times:
        complex_vis.append(
            np.sum(
                [
                    comp.compute_complex_vis(vis.u[t], vis.v[t], t, wavelength)
                    for comp in components
                ],
                axis=0,
            )
        )
        complex_t3.append(
            np.sum(
                [
                    comp.compute_complex_vis(t3.u[t], t3.v[t], t, wavelength)
                    for comp in components
                ],
                axis=0,
            )
        )

    complex_vis, complex_t3 = np.array(complex_vis), np.array(complex_t3)
    t3_model = np.array(
        [compute_t3(complex_t3[t], OPTIONS.data.t3.i123[t])[:, 1:] for t in times]
    )
    flux_model = np.array([complex_vis[t, :, 0].reshape(-1, 1) for t in times])
    vis_model = np.array([compute_vis(complex_vis[t, :, 1:]) for t in times])
    if flux_model.size > 0:
        flux_model = np.array(
            [
                np.tile(flux_model[t], OPTIONS.data.flux.val.shape[-1]).real
                for t in times
            ]
        )

    return flux_model, vis_model, t3_model


def compute_nband_fit_chi_sq(
    model_data: NDArray[Any],
    ndim: int,
    reduced: bool = False,
) -> float:
    """Calculates the sed model's chi square.

    Parameters
    ----------
    flux_model : numpy.typing.NDArray
        The model's total flux.
    ndim : int, optional
        The number of (parameter) dimensions.
    reduced : bool, optional
        Whether to return the reduced chi square.

    Returns
    -------
    chi_sq : float
        The chi square.
    """
    # NOTE: The -1 here indicates that one of the parameters is actually fixed
    flux, ndim = OPTIONS.data.flux, ndim - 1
    val, err = map(lambda x: x.squeeze(), [flux.val, flux.err])
    chi_sq = compute_loglike(
        val.compressed(),
        err.compressed(),
        model_data.squeeze()[~val.mask],
    )

    if reduced:
        return chi_sq / (flux.val.size - ndim)

    return chi_sq


def compute_interferometric_loglike(
    components: List[Component],
) -> Tuple:
    """Calculates the disc model's chi square.

    Parameters
    ----------
    components : list of Component
        The components to be used in the model.
    method : bool
        The method used to calculate the chi square.
        Either "linear" or "logarithmic".
        Default is "logarithmic".

    Returns
    -------
    chi_sq : Tuple of floats
        The total and the individual chi squares.
    """
    observables = ["flux", "vis", "t3"]
    model_data = dict(zip(observables, compute_observables(components)))
    wls = OPTIONS.fit.wls.value

    loglikes = []
    for key in OPTIONS.fit.data:
        data = getattr(OPTIONS.data, key)
        key = key if key != "vis2" else "vis"

        loglikes_bands = []
        for band in OPTIONS.fit.bands:
            band_indices = get_band_indices(wls, [band])
            mask = data.val[:, band_indices].mask
            loglikes_bands.append(
                compute_loglike(
                    data.val[:, band_indices].compressed(),
                    data.err[:, band_indices].compressed(),
                    model_data[key][:, band_indices][~mask],
                    kind="linear" if key != "t3" else "periodic",
                )
            )
        loglikes.append(loglikes_bands)

    loglikes = np.array(loglikes).astype(float)
    weights_general = get_weights(kind="general")
    weights_bands = get_weights(kind="bands")
    return np.sum((weights_bands * loglikes).sum(1) * weights_general), loglikes


def sample_uniform(
    param: Parameter | None = None,
    theta: float | None = None,
    prior: List[float] | None = None,
) -> float:
    """Samples from a uniform prior."""
    if param is not None:
        return param.min + (param.max - param.min) * param.uniform
    return prior[0] + (prior[1] - prior[0]) * theta


def transform_uniform_prior(theta: NDArray[Any], priors: NDArray[Any]) -> float:
    """Prior transform for uniform priors."""
    return priors[:, 0] + (priors[:, 1] - priors[:, 0]) * theta


def nband(params: NDArray[Any], labels: List[str], theta: NDArray[Any]) -> NDArray[Any]:
    """Transform that soft constrains successive radii to be smaller than the one before."""
    indices = list(map(labels.index, filter(lambda x: "weight" in x, labels)))
    remainder = 100
    for index in indices[:-1]:
        params[index] = remainder * theta[index]
        remainder -= params[index]

    params[indices[-1]] = remainder
    return params


# NOTE: This ignores the first component (that being the star) -> Not generalised.
# Also only works if all the other components are based on the Ring class
def radii(components: List[Component]) -> List[Component]:
    """Forces the radii to be sequential."""
    for index, component in enumerate(components[1:], start=1):
        if not any(name in component.name for name in ["Ring", "TempGrad", "GreyBody"]):
            continue

        if component.rin.free and not component.rin.shared:
            if index > 1:
                component.rin.min = components[index - 1].rout.value

            component.rin.value = sample_uniform(component.rin)
            component.rout.min = component.rin.value
            component.rout.value = sample_uniform(component.rout)

    return components


def shift():
    """Forces the shift to be within bounds."""
    # NOTE: Removes overlap caused by photosphere shift
    # TODO: This does not account for direction -> Problem? Try in a fit.
    # Subtract the distance also from the centre?
    for index, comp in enumerate(components):
        bounds = np.array([np.nan, np.nan])
        if index != 0:
            prev_comp = components[index - 1]
            try:
                bounds[0] = min(
                    comp.rin.value - prev_comp.rout.value, prev_comp.rout.value
                )
            except AttributeError:
                bounds[0] = comp.r.value

        if index != len(components) - 1:
            next_comp = components[index + 1]
            try:
                bounds[1] = next_comp.rin.value - comp.rout.value
            except AttributeError:
                bounds[1] = next_comp.rin.value

        upper = np.min(bounds[~np.isnan(bounds)])
        if f"r-{index}" in labels:
            r_ind = labels.index(f"r-{index}")
            lower = priors[r_ind][0]
            params[r_ind] = lower + (upper - lower) * theta[r_ind]


def param_transform(theta: List[float]) -> NDArray[Any]:
    """Transform that soft constrains successive radii to be smaller than the one before."""
    params = transform_uniform_prior(theta, get_priors(OPTIONS.model.components))
    if OPTIONS.fit.type == "nband":
        return nband(params, get_labels(OPTIONS.model.components), theta)

    components = set_components_from_theta(params, theta)
    for option in OPTIONS.fit.conditions:
        components = getattr(CURRENT_MODULE, option)(components)

    return get_theta(components)


def lnprob(theta: NDArray[Any]) -> float:
    """Takes theta vector returns a number corresponding to how good of a fit
    the model is to your data for a given set of parameters.

    Parameters
    ----------
    theta: numpy.typing.NDArray
        The parameters that ought to be fitted.

    Returns
    -------
    float
        The log of the probability.
    """
    components = set_components_from_theta(theta)
    if OPTIONS.fit.type == "nband":
        return compute_nband_fit_chi_sq(
            components[0].compute_flux(0, OPTIONS.fit.wls),
            ndim=theta.size,
        )
    return compute_interferometric_loglike(components)[0]


def run_fit(
    sample: str = "rwalk",
    bound: str = "multi",
    ncores: int = 6,
    debug: bool = False,
    save_dir: Path | None = None,
    **kwargs,
) -> DynamicNestedSampler:
    """Runs the dynesty nested sampler.

    Parameters
    ----------
    sample : str, optional
        The sampling method. Either "rwalk" or "unif".
    bound : str, optional
        The bounding method. Either "multi" or "single".
    ncores : int, optional
        The number of cores to use.
    debug : bool, optional
        Whether to run the sampler in debug mode.
        This will not use multiprocessing.
    save_dir : Path, optional
        The directory to save the sampler.

    Returns
    -------
    sampler : dynesty.DynamicNestedSampler
    """
    if save_dir is not None:
        checkpoint_file = save_dir / "sampler.save"
    else:
        checkpoint_file = None

    components = OPTIONS.model.components
    periodic = [
        index
        for index, param in enumerate(get_fit_params(components))
        if param.periodic
    ]
    periodic = None if not periodic else periodic
    reflective = [
        index
        for index, param in enumerate(get_fit_params(components))
        if param.reflective
    ]
    reflective = None if not reflective else reflective

    pool = Pool(processes=ncores) if not debug else None
    queue_size = 2 * ncores if not debug else None

    general_kwargs = {
        "bound": bound,
        "queue_size": queue_size,
        "sample": sample,
        "periodic": periodic,
        "reflective": reflective,
        "pool": pool,
    }

    run_kwargs = {
        "nlive_batch": kwargs.pop("nlive_batch", 500),
        "dlogz_init": kwargs.pop("dlogz_init", 0.01),
        "nlive_init": kwargs.pop("nlive_init", 1000),
    }

    print(f"Executing Dynesty.\n{'':-^50}")
    labels = get_labels(OPTIONS.model.components)
    ptform = kwargs.pop("ptform", param_transform)
    sampler = DynamicNestedSampler(
        kwargs.pop("lnprob", lnprob),
        ptform,
        len(labels),
        **general_kwargs,
    )
    sampler.run_nested(
        **run_kwargs, print_progress=True, checkpoint_file=str(checkpoint_file)
    )

    if not debug:
        pool.close()
        pool.join()

    return sampler


def get_best_fit(
    sampler: DynamicNestedSampler,
    method: str = "max",
) -> Tuple[NDArray[Any], NDArray[Any]]:
    """Gets the best fit from the sampler."""
    results = sampler.results
    samples, logl = results.samples, results.logl
    weights = results.importance_weights()
    quantiles = np.array(
        [
            dyutils.quantile(
                samps, np.array(OPTIONS.fit.quantiles) / 100, weights=weights
            )
            for samps in samples.T
        ]
    )

    if method == "max":
        quantiles[:, 1] = samples[logl.argmax()]

    return quantiles[:, 1], np.diff(quantiles.T, axis=0).T
