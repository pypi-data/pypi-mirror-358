from itertools import chain, zip_longest
from pathlib import Path
from typing import Dict, List, Tuple

import astropy.constants as const
import astropy.units as u
import corner
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from dynesty import DynamicNestedSampler, NestedSampler
from dynesty import plotting as dyplot
from matplotlib.axes import Axes
from matplotlib.gridspec import GridSpec
from matplotlib.legend import Legend

from .base import FourierComponent
from .fitting import compute_observables, get_best_fit
from .options import OPTIONS, get_colormap
from .utils import (
    compare_angles,
    get_band_indices,
    transform_coordinates,
)


def get_best_plot_arrangement(nplots):
    """Gets the best plot arrangement for a given number of plots."""
    sqrt_nplots = np.sqrt(nplots)
    cols = int(np.ceil(sqrt_nplots))
    rows = int(np.floor(sqrt_nplots))

    while rows * cols < nplots:
        if cols < rows:
            cols += 1
        else:
            rows += 1

    while (rows - 1) * cols >= nplots:
        rows -= 1

    return rows, cols


def set_axes_color(
    ax: Axes,
    background_color: str,
    set_label: bool = True,
    direction: str | None = None,
) -> None:
    """Sets all the axes' facecolor."""
    opposite_color = "white" if background_color == "black" else "black"
    ax.set_facecolor(background_color)
    ax.spines["bottom"].set_color(opposite_color)
    ax.spines["top"].set_color(opposite_color)
    ax.spines["right"].set_color(opposite_color)
    ax.spines["left"].set_color(opposite_color)

    if set_label:
        ax.xaxis.label.set_color(opposite_color)
        ax.yaxis.label.set_color(opposite_color)

    ax.tick_params(axis="both", colors=opposite_color, direction=direction)


def set_legend_color(legend: Legend, background_color: str) -> None:
    """Sets the legend's facecolor."""
    opposite_color = "white" if background_color == "black" else "black"
    plt.setp(legend.get_texts(), color=opposite_color)
    legend.get_frame().set_facecolor(background_color)


def format_labels(
    labels: List[str], units: List[str] | None = None, split: bool = False
) -> List[str]:
    """Formats the labels in LaTeX.

    Parameters
    ----------
    labels : list of str
        The labels.
    units : list of str, optional
        The units. The default is None.
    split : bool, optional
        If True, splits into labels, units, and uncertainties.
        The default is False.

    Returns
    -------
    labels : list of str
        The formatted labels.
    units : list of str, optional
        The formatted units. If split is True
    """
    nice_labels = {
        "rin": {"letter": "R", "indices": [r"\text{in}"]},
        "rout": {"letter": "R", "indices": [r"\text{out}"]},
        "p": {"letter": "p"},
        "q": {"letter": "q"},
        "rho": {"letter": r"\rho"},
        "theta": {"letter": r"\theta"},
        "logsigma0": {"letter": r"\Sigma", "indices": ["0"]},
        "sigma0": {"letter": r"\Sigma", "indices": ["0"]},
        "weight_cont": {"letter": "w", "indices": [r"\text{cont}"]},
        "pa": {"letter": r"\theta", "indices": []},
        "cinc": {"letter": r"\cos\left(i\right)"},
        "temp0": {"letter": "T", "indices": ["0"]},
        "tempc": {"letter": "T", "indices": [r"\text{c}"]},
        "f": {"letter": "f"},
        "fr": {"letter": "fr"},
        "fwhm": {"letter": r"\sigma"},
        "r": {"letter": "r"},
        "phi": {"letter": r"\phi"},
    }

    formatted_labels = []
    for label in labels:
        if "-" in label:
            name, index = label.split("-")
        else:
            name, index = label, ""

        if name in nice_labels or name[-1].isdigit():
            if ".t" in name:
                name, time_index = name.split(".")
            else:
                time_index = None

            if name not in nice_labels and name[-1].isdigit():
                letter = nice_labels[name[:-1]]["letter"]
                indices = [name[-1]]
                if index:
                    indices.append(index)
            else:
                letter = nice_labels[name]["letter"]
                if name in ["temp0", "tempc"]:
                    indices = nice_labels[name].get("indices", [])
                else:
                    indices = [*nice_labels[name].get("indices", [])]
                    if index:
                        indices.append(rf"\mathrm{{{index}}}")

            if time_index is not None:
                indices.append(rf"\mathrm{{{time_index}}}")

            indices = r",\,".join(indices)
            formatted_label = f"{letter}_{{{indices}}}"
            if "log" in label:
                formatted_label = rf"\log_{{10}}\left({formatted_label}\right)"

            formatted_labels.append(f"$ {formatted_label} $")
        else:
            if "weight" in name:
                name, letter = name.replace("weight", ""), "w"

                indices = []
                if "small" in name:
                    name = name.replace("small", "")
                    indices = [r"\text{small}"]
                elif "large" in name:
                    name = name.replace("large", "")
                    indices = [r"\text{large}"]
                name = name.replace("_", "")
                indices.append(rf"\text{{{name}}}")

                indices = r",\,".join(indices)
                formatted_label = f"{letter}_{{{indices}}}"
                if "log" in label:
                    formatted_label = rf"\log_{{10}}\left({formatted_label}\right)"
            elif "scale" in name:
                formatted_label = rf"w_{{\text{{{name.replace('scale_', '')}}}}}"
            elif "lnf" in name:
                formatted_label = (
                    rf"\ln\left(f\right)_{{\text{{{name.split('_')[0]}}}}}"
                )
            else:
                formatted_label = label

            formatted_labels.append(f"$ {formatted_label} $")

    if units is not None:
        reformatted_units = []
        for unit in units:
            if unit == u.g / u.cm**2:
                unit = r"\si{\gram\per\square\centi\metre}"
            elif unit == u.au:
                unit = r"\si{\astronomicalunit}"
            elif unit == u.deg:
                unit = r"\si{\degree}"
            elif unit == u.pct:
                unit = r"\si{\percent}"

            reformatted_units.append(unit)

        reformatted_units = [
            rf"$ (\text{{{str(unit).strip()}}}) $" if str(unit) else ""
            for unit in reformatted_units
        ]
        if split:
            return formatted_labels, reformatted_units

        formatted_labels = [
            rf"{label} {unit}"
            for label, unit in zip(formatted_labels, reformatted_units)
        ]
    return formatted_labels


def needs_sci_notation(ax):
    """Checks if scientific notation is needed"""
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    return (
        abs(x_min) <= 1e-3
        or abs(x_max) <= 1e-3
        or abs(y_min) <= 1e-3
        or abs(y_max) <= 1e-3
    )


def get_exponent(num: float) -> int:
    """Gets the exponent of a number for scientific notation"""
    if num == 0:
        raise ValueError("Number must be non-zero")

    exponent_10 = np.floor(np.log10(abs(num)))
    normalized_num = num / (10**exponent_10)
    return np.floor(np.log10(normalized_num) - np.log10(10**exponent_10)).astype(int)


def plot_corner(
    sampler,
    labels: List[str],
    units: List[str] | None = None,
    fontsize: int = 12,
    discard: int = 0,
    savefig: Path | None = None,
    **kwargs,
) -> None:
    """Plots the corner of the posterior spread.

    Parameters
    ----------
    sampler :
    labels : list of str
        The parameter labels.
    units : list of str, optional
    discard : int, optional
    fontsize : int, optional
        The fontsize. The default is 12.
    savefig : pathlib.Path, optional
        The save path. The default is None.
    """
    labels = format_labels(labels, units)
    quantiles = [x / 100 for x in OPTIONS.fit.quantiles]
    if OPTIONS.fit.fitter == "dynesty":
        results = sampler.results
        _, axarr = dyplot.cornerplot(
            results,
            color="blue",
            labels=labels,
            show_titles=True,
            max_n_ticks=3,
            title_quantiles=quantiles,
            quantiles=quantiles,
        )

        theta, uncertainties = get_best_fit(sampler)
        for index, row in enumerate(axarr):
            for ax in row:
                if ax is not None:
                    if needs_sci_notation(ax):
                        if "Sigma" in ax.get_xlabel():
                            ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
                            ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))

                        if "Sigma" in ax.get_ylabel():
                            ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
                            ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
                            ax.yaxis.get_offset_text().set_position((-0.2, 0))

                    title = ax.get_title()
                    if title and np.abs(theta[index]) <= 1e-3:
                        exponent = get_exponent(theta[index])
                        factor = 10.0**exponent
                        formatted_title = (
                            rf"${theta[index] * factor:.2f}_{{-{uncertainties[index][0] * factor:.2f}}}"
                            rf"^{{+{uncertainties[index][1] * factor:.2f}}}\,1\mathrm{{e}}-{exponent}$"
                        )
                        ax.set_title(
                            f"{labels[index]} = {formatted_title}",
                            fontsize=fontsize - 2,
                        )
    else:
        samples = sampler.get_chain(discard=discard, flat=True)
        corner.corner(samples, labels=labels)

    if savefig is not None:
        plt.savefig(savefig, format=Path(savefig).suffix[1:], dpi=OPTIONS.plot.dpi)
    plt.close()


def plot_chains(
    sampler: NestedSampler | DynamicNestedSampler,
    labels: List[str],
    units: List[str] | None = None,
    savefig: Path | None = None,
    **kwargs,
) -> None:
    """Plots the fitter's chains.

    Parameters
    ----------
    sampler : dynesty.NestedSampler or dynesty.DynamicNestedSampler
        The sampler.
    labels : list of str
        The parameter labels.
    units : list of str, optional
    discard : int, optional
    savefig : pathlib.Path, optional
        The save path. The default is None.
    """
    labels = format_labels(labels, units)
    quantiles = [x / 100 for x in OPTIONS.fit.quantiles]
    results = sampler.results
    dyplot.traceplot(
        results,
        labels=labels,
        truths=np.zeros(len(labels)),
        quantiles=quantiles,
        truth_color="black",
        show_titles=True,
        trace_cmap="viridis",
        connect=True,
        connect_highlight=range(5),
    )

    if savefig:
        plt.savefig(savefig, format=Path(savefig).suffix[1:], dpi=OPTIONS.plot.dpi)
    else:
        plt.show()
    plt.close()


class LogNorm(mcolors.Normalize):
    """Gets the log norm."""

    def __init__(self, vmin=None, vmax=None, clip=False):
        super().__init__(vmin, vmax, clip)

    def __call__(self, value, clip=None):
        normalized_value = np.log1p(value - self.vmin) / np.log1p(self.vmax - self.vmin)
        return np.ma.masked_array(normalized_value, np.isnan(normalized_value))

    def inverse(self, value):
        return np.expm1(value * np.log1p(self.vmax - self.vmin)) + self.vmin


def set_axis_information(
    axarr: Dict[str, List[Axes]],
    key: str,
    cinc=None,
) -> Tuple[Axes, Axes]:
    """Sets the axis labels and limits for the different keys."""
    if isinstance(axarr[key], (tuple, list, np.ndarray)):
        upper_ax, lower_ax = axarr[key]
        # set_axes_color(lower_ax, OPTIONS.plot.color.background)
    else:
        upper_ax, lower_ax = axarr[key], None

    tick_params = {
        "axis": "x",
        "which": "both",
        "bottom": True,
        "top": False,
        "labelbottom": False if lower_ax is not None else True,
    }

    if key == "flux":
        xlabel = r"$ \lambda (\mathrm{\mu}\text{m}) $"
        residual_label = "Residuals (Jy)"
        ylabel = r"$ F_{\nu} $ (Jy)"

    elif key in ["vis", "vis2"]:
        xlabel = r"$ B (\text{M}\lambda)$"
        if cinc is not None:
            xlabel = r"$ B_{\text{eff}} (\text{M}\lambda) $"

        if key == "vis":
            ylabel = r"$ F_{\nu,\,\text{corr}} $ (Jy)"
            residual_label = "Residuals (Jy)"
        else:
            ylabel = "$ V^{2} $ (a.u.)"
            residual_label = "Residuals (a.u.)"
            upper_ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))

    elif key == "t3":
        xlabel = r"$ B_{\text{max}} (\text{M}\lambda) $"
        ylabel = r"$ \Phi_{\text{cp}} (^{\circ}) $"
        residual_label = r"Residuals $ (^{\circ}) $"

    upper_ax.tick_params(**tick_params)
    upper_ax.set_ylabel(ylabel)
    if lower_ax is not None:
        lower_ax.set_xlabel(xlabel)
        lower_ax.set_ylabel(residual_label)
    else:
        upper_ax.set_xlabel(xlabel)

    return upper_ax, lower_ax


def plot_data_vs_model(
    axarr,
    wavelengths: np.ndarray,
    val: np.ndarray,
    err: np.ndarray,
    key: str,
    baselines: np.ndarray | None = None,
    model_val: np.ndarray | None = None,
    colormap: str = OPTIONS.plot.color.colormap,
    bands: List[str] | str = "all",
    cinc: float | None = None,
    ylims: Dict = {},
    norm=None,
):
    """Plots the data versus the model or just the data if not model data given."""
    upper_ax, lower_ax = set_axis_information(axarr, key, cinc)
    colormap, alpha = get_colormap(colormap), 1 if lower_ax is None else 0.55
    hline_color = "gray" if OPTIONS.plot.color.background == "white" else "white"
    errorbar_params, scatter_params = OPTIONS.plot.errorbar, OPTIONS.plot.scatter
    if OPTIONS.plot.color.background == "black":
        errorbar_params.markeredgecolor = "white"
        scatter_params.edgecolor = "white"

    if model_val is not None:
        model_val = np.ma.masked_array(model_val, mask=val.mask)

    if bands == "all" or bands is None:
        band_indices = np.where(np.ones_like(wavelengths.value).astype(bool))[0]
    else:
        band_indices = get_band_indices(wavelengths.value, bands)

    wavelengths = wavelengths[band_indices]
    val, err = val[band_indices], err[band_indices]
    if model_val is not None:
        model_val = model_val[band_indices]

    set_axes_color(upper_ax, OPTIONS.plot.color.background)
    color = colormap(norm(wavelengths.value))
    if baselines is None:
        grid = [wl.repeat(val.shape[-1]) for wl in wavelengths.value]
    else:
        grid = baselines / wavelengths.value[:, np.newaxis]

    ymin, ymax = 0, 0
    ymin_res, ymax_res = 0, 0
    for index, _ in enumerate(wavelengths.value):
        errorbar_params.color = scatter_params.color = color[index]
        upper_ax.errorbar(
            grid[index],
            val[index],
            err[index],
            fmt="o",
            **vars(errorbar_params),
        )

        ymin = min(ymin, np.nanmin(val[index]))
        ymax = max(ymax, np.nanmax(val[index]))
        if model_val is not None and lower_ax is not None:
            upper_ax.scatter(
                grid[index],
                model_val[index],
                marker="X",
                alpha=alpha,
                **vars(scatter_params),
            )

            if key == "t3":
                upper_ax.axhline(0, color="grey", linestyle="--")
                residuals = np.rad2deg(
                    compare_angles(
                        np.deg2rad(val[index]),
                        np.deg2rad(model_val[index]),
                    )
                )
            else:
                residuals = val[index] - model_val[index]

            residual_errs = err[index]

            ymin = min(ymin, np.nanmin(model_val[index]))
            ymax = max(ymax, np.nanmax(model_val[index]))
            ymin_res = min(ymin_res, np.nanmin(residuals))
            ymax_res = max(ymax_res, np.nanmax(residuals))

            lower_ax.errorbar(
                grid[index],
                residuals,
                residual_errs,
                fmt="o",
                **vars(errorbar_params),
            )
            lower_ax.axhline(y=0, color=hline_color, linestyle="--")

    ymin, ymax = ymin - np.abs(ymin) * 0.25, ymax + ymax * 0.25
    if key in ["flux", "vis"]:
        ylim = ylims.get(key, [0, ymax])
    elif key == "vis2":
        ylim = ylims.get(key, [0, 1])
    else:
        ylim = ylims.get("t3", [ymin, ymax])

    upper_ax.set_ylim(ylim)
    # TODO: Improve the residual plots
    if lower_ax is not None:
        upper_ax.tick_params(axis="x", which="both", direction="in")
        ymin_res, ymax_res = (
            ymin_res - np.abs(ymin_res) * 0.25,
            ymax_res + ymax_res * 0.25,
        )
        tick_diff = np.diff(upper_ax.get_yticks())[0]
        lower_ax.set_ylim((ymin_res, ymax_res))

    if not len(axarr) > 1:
        label_color = "lightgray" if OPTIONS.plot.color.background == "black" else "k"
        dot_label = mlines.Line2D(
            [],
            [],
            color=label_color,
            marker="o",
            linestyle="None",
            label="Data",
            alpha=0.6,
        )
        x_label = mlines.Line2D(
            [], [], color=label_color, marker="X", linestyle="None", label="Model"
        )
        legend = upper_ax.legend(handles=[dot_label, x_label])
        set_legend_color(legend, OPTIONS.plot.color.background)

    errorbar_params.color = scatter_params.color = None


def plot_fit(
    components: List | None = None,
    data_to_plot: List[str | None] | None = None,
    cmap: str = OPTIONS.plot.color.colormap,
    ylims: Dict[str, List[float]] = {},
    bands: List[str] | str = "all",
    title: str | None = None,
    ax: List[List[Axes]] | None = None,
    colorbar: bool = True,
    savefig: Path | None = None,
):
    """Plots the deviation of a model from real data of an object for
    total flux, visibilities and closure phases.

    Parameters
    ----------
    inclination : astropy.units.one
        The axis ratio.
    pos_angle : astropy.units.deg
        The position angle.
    data_to_plot : list of str, optional
        The data to plot. The default is OPTIONS.fit.data.
    ylimits : dict of list of float, optional
        The ylimits for the individual keys.
    bands : list of str or str, optional
        The bands to be plotted. The default is "all".
    cmap : str, optional
        The colormap.
    title : str, optional
        The title. The default is None.
    savefig : pathlib.Path, optional
        The save path. The default is None.
    """
    data_to_plot = OPTIONS.fit.data if data_to_plot is None else data_to_plot
    flux, t3 = OPTIONS.data.flux, OPTIONS.data.t3
    vis = OPTIONS.data.vis if "vis" in data_to_plot else OPTIONS.data.vis2
    nts, wls = range(OPTIONS.data.nt), OPTIONS.fit.wls
    norm = LogNorm(vmin=wls[0].value, vmax=wls[-1].value)

    data_types, nplots = [], 0
    for key in data_to_plot:
        if key in ["vis", "vis2"] and "vis" not in data_types:
            data_types.append("vis")
        else:
            data_types.append(key)
        nplots += 1

    for t in nts:
        model_flux, model_vis, model_t3 = compute_observables(components)

        # NOTE: This won't work with differing cinc and pa
        cinc, pa = components[0].cinc(), components[0].pa()
        figsize = (16, 5) if nplots == 3 else ((12, 5) if nplots == 2 else None)
        fig = plt.figure(figsize=figsize, facecolor=OPTIONS.plot.color.background)
        if ax is None:
            gs = GridSpec(2, nplots, height_ratios=[2.5, 1.5], hspace=0.00)
            axarr = [
                [
                    fig.add_subplot(gs[j, i], facecolor=OPTIONS.plot.color.background)
                    for j in range(2)
                ]
                for i in range(nplots)
            ]
        else:
            axarr = ax

        axarr = dict(zip(data_types, axarr))
        plot_kwargs = {"norm": norm, "colormap": cmap}
        if "flux" in data_to_plot:
            plot_data_vs_model(
                axarr,
                wls,
                flux.val[t],
                flux.err[t],
                "flux",
                ylims=ylims,
                bands=bands,
                model_val=model_flux[t],
                cinc=cinc,
                **plot_kwargs,
            )

        if "vis" in data_to_plot or "vis2" in data_to_plot:
            baselines = np.hypot(*transform_coordinates(vis.u[t], vis.v[t], cinc, pa))
            plot_data_vs_model(
                axarr,
                wls,
                vis.val[t],
                vis.err[t],
                "vis" if "vis" in data_to_plot else "vis2",
                ylims=ylims,
                bands=bands,
                baselines=baselines[:, 1:],
                model_val=model_vis[t],
                cinc=cinc,
                **plot_kwargs,
            )

        if "t3" in data_to_plot:
            baselines = np.hypot(*transform_coordinates(t3.u[t], t3.v[t], cinc, pa))
            baselines = baselines[t3.i123[t]].T.max(1).reshape(1, -1)
            plot_data_vs_model(
                axarr,
                wls,
                t3.val[t],
                t3.err[t],
                "t3",
                ylims=ylims,
                bands=bands,
                baselines=baselines[:, 1:],
                model_val=model_t3[t],
                cinc=cinc,
                **plot_kwargs,
            )

        if colorbar:
            sm = cm.ScalarMappable(cmap=get_colormap(cmap), norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=axarr[data_types[-1]])
            cbar.set_ticks(OPTIONS.plot.ticks)
            cbar.set_ticklabels(
                [f"{wavelength:.1f}" for wavelength in OPTIONS.plot.ticks]
            )

            if OPTIONS.plot.color.background == "black":
                cbar.ax.yaxis.set_tick_params(color="white")
                plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")
                for spine in cbar.ax.spines.values():
                    spine.set_edgecolor("white")

            text_color = (
                "white" if OPTIONS.plot.color.background == "black" else "black"
            )
            cbar.set_label(label=r"$\lambda$ ($\mathrm{\mu}$m)", color=text_color)

        if title is not None:
            plt.title(title)

        if savefig is not None:
            plt.savefig(
                savefig.parent / f"{savefig.stem}_t{t}{savefig.suffix}",
                format=Path(savefig).suffix[1:],
                dpi=OPTIONS.plot.dpi,
                bbox_inches="tight",
            )

        if ax is None:
            plt.show()

        # TODO: Implement plt.close() again here


def plot_overview(
    data_to_plot: List[str | None] = None,
    colormap: str = OPTIONS.plot.color.colormap,
    ylims: Dict[str, List[float]] = {},
    title: str | None = None,
    cinc: float | None = None,
    pa: float | None = None,
    bands: List[str] | str = "all",
    colorbar: bool = True,
    axarr: Axes | None = None,
    savefig: Path | None = None,
) -> None:
    """Plots an overview over the total data for baselines [Mlambda].

    Parameters
    ----------
    data_to_plot : list of str, optional
        The data to plot. The default is OPTIONS.fit.data.
    savefig : pathlib.Path, optional
        The save path. The default is None.
    """
    data_to_plot = OPTIONS.fit.data if data_to_plot is None else data_to_plot
    nts, wls = range(OPTIONS.data.nt), OPTIONS.fit.wls
    norm = LogNorm(vmin=wls[0].value, vmax=wls[-1].value)

    data_types, nplots = [], 0
    for key in data_to_plot:
        if key in ["vis", "vis2"] and "vis" not in data_types:
            data_types.append("vis")
        else:
            data_types.append(key)
        nplots += 1

    for t in nts:
        if axarr is None:
            figsize = (15, 5) if nplots == 3 else ((12, 5) if nplots == 2 else None)
            _, axarr = plt.subplots(
                1,
                nplots,
                figsize=figsize,
                tight_layout=True,
                facecolor=OPTIONS.plot.color.background,
            )

        axarr = axarr.flatten() if isinstance(axarr, np.ndarray) else [axarr]
        axarr = dict(zip(data_types, axarr))

        flux, t3 = OPTIONS.data.flux, OPTIONS.data.t3
        vis = OPTIONS.data.vis if "vis" in OPTIONS.fit.data else OPTIONS.data.vis2

        errorbar_params = OPTIONS.plot.errorbar
        if OPTIONS.plot.color.background == "black":
            errorbar_params.markeredgecolor = "white"

        plot_kwargs = {"norm": norm, "colormap": colormap}
        if "flux" in data_to_plot:
            plot_data_vs_model(
                axarr,
                wls,
                flux.val[t],
                flux.err[t],
                "flux",
                ylims=ylims,
                bands=bands,
                cinc=cinc,
                **plot_kwargs,
            )

        if "vis" in data_to_plot or "vis2" in data_to_plot:
            baselines = np.hypot(*transform_coordinates(vis.u[t], vis.v[t], cinc, pa))
            plot_data_vs_model(
                axarr,
                wls,
                vis.val[t],
                vis.err[t],
                "vis" if "vis" in data_to_plot else "vis2",
                ylims=ylims,
                bands=bands,
                baselines=baselines[:, 1:],
                cinc=cinc,
                **plot_kwargs,
            )

        if "t3" in data_to_plot:
            baselines = np.hypot(*transform_coordinates(t3.u[t], t3.v[t], cinc, pa))
            baselines = baselines[t3.i123[t]].T.max(1).reshape(1, -1)
            plot_data_vs_model(
                axarr,
                wls,
                t3.val[t],
                t3.err[t],
                "t3",
                ylims=ylims,
                bands=bands,
                baselines=baselines[:, 1:],
                cinc=cinc,
                **plot_kwargs,
            )

        if colorbar:
            sm = cm.ScalarMappable(cmap=colormap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=axarr[data_types[-1]])

            # TODO: Set the ticks, but make it so that it is flexible for the band
            cbar.set_ticks(OPTIONS.plot.ticks)
            cbar.set_ticklabels(
                [f"{wavelength:.1f}" for wavelength in OPTIONS.plot.ticks]
            )

            if OPTIONS.plot.color.background == "black":
                cbar.ax.yaxis.set_tick_params(color="white")
                plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")
                for spine in cbar.ax.spines.values():
                    spine.set_edgecolor("white")
            opposite_color = (
                "white" if OPTIONS.plot.color.background == "black" else "black"
            )
            cbar.set_label(label=r"$\lambda$ ($\mathrm{\mu}$m)", color=opposite_color)

        if title is not None:
            plt.title(title)

        if savefig is not None:
            plt.savefig(
                savefig.parent / f"{savefig.stem}_t{t}{savefig.suffix}",
                format=Path(savefig).suffix[1:],
                dpi=OPTIONS.plot.dpi,
            )

        if savefig is None:
            if axarr is not None:
                return

            plt.show()
            plt.close()


def plot_sed(
    wavelength_range: u.um,
    components: List[FourierComponent | None] = None,
    scaling: str = "nu",
    no_model: bool = False,
    ax: plt.Axes | None = None,
    savefig: Path | None = None,
):
    """Plots the observables of the model.

    Parameters
    ----------
    wavelength_range : astropy.units.m
    scaling : str, optional
        The scaling of the SED. "nu" for the flux to be
        in Jy times Hz. If "lambda" the flux is in Jy times m.
        If "none" the flux is in Jy.
        The default is "nu".
    """
    color = OPTIONS.plot.color
    savefig = Path.cwd() if savefig is None else savefig
    wavelength = np.linspace(wavelength_range[0], wavelength_range[1], OPTIONS.plot.dim)

    if not no_model:
        wavelength = OPTIONS.fit.wls if wavelength is None else wavelength
        components = [comp for comp in components if comp.name != "Point Source"]
        flux = np.sum([comp.compute_flux(0, wavelength) for comp in components], axis=0)
        if flux.size > 0:
            flux = np.tile(flux, (len(OPTIONS.data.readouts))).real

    if ax is None:
        fig = plt.figure(facecolor=color.background, tight_layout=True)
        ax = plt.axes(facecolor=color.background)
        set_axes_color(ax, color.background)
    else:
        fig = None

    if len(OPTIONS.data.readouts) > 1:
        names = [
            re.findall(r"(\d{4}-\d{2}-\d{2})", readout.fits_file.name)[0]
            for readout in OPTIONS.data.readouts
        ]
    else:
        names = [OPTIONS.data.readouts[0].fits_file.name]

    cmap = plt.get_cmap(color.colormap)
    norm = mcolors.LogNorm(vmin=1, vmax=len(set(names)))
    colors = [cmap(norm(i)) for i in range(1, len(set(names)) + 1)]
    date_to_color = {date: color for date, color in zip(set(names), colors)}
    sorted_readouts = np.array(OPTIONS.data.readouts.copy())[np.argsort(names)].tolist()

    values = []
    for name, readout in zip(np.sort(names), sorted_readouts):
        if readout.flux.val.size == 0:
            continue

        readout_wl = readout.wl.value
        readout_flux, readout_err = (
            readout.flux.val.flatten(),
            readout.flux.err.flatten(),
        )
        readout_err_percentage = readout_err / readout_flux

        if scaling == "nu":
            readout_flux = (readout_flux * u.Jy).to(u.W / u.m**2 / u.Hz)
            readout_flux = (
                readout_flux * (const.c / ((readout_wl * u.um).to(u.m))).to(u.Hz)
            ).value

        readout_err = readout_err_percentage * readout_flux
        lower_err, upper_err = readout_flux - readout_err, readout_flux + readout_err
        if "HAW" in readout.fits_file.name:
            indices_high = np.where((readout_wl >= 4.55) & (readout_wl <= 4.9))
            indices_low = np.where((readout_wl >= 3.1) & (readout_wl <= 3.9))
            for indices in [indices_high, indices_low]:
                line = ax.plot(
                    readout_wl[indices],
                    readout_flux[indices],
                    color=date_to_color[name],
                )
                ax.fill_between(
                    readout_wl[indices],
                    lower_err[indices],
                    upper_err[indices],
                    color=line[0].get_color(),
                    alpha=0.5,
                )
            value_indices = np.hstack([indices_high, indices_low])
            lim_values = readout_flux[value_indices].flatten()
        else:
            line = ax.plot(readout_wl, readout_flux, color=date_to_color[name])
            ax.fill_between(
                readout_wl,
                lower_err,
                upper_err,
                color=line[0].get_color(),
                alpha=0.5,
            )
            lim_values = readout_flux
        values.append(lim_values)

    flux_label = r"$F_{\nu}$ (Jy)"
    if not no_model:
        flux = flux[:, 0]
        if scaling == "nu":
            flux = (flux * u.Jy).to(u.W / u.m**2 / u.Hz)
            flux = (flux * (const.c / (wavelength.to(u.m))).to(u.Hz)).value
            flux_label = r"$\nu F_{\nu}$ (W m$^{-2}$)"

    if not no_model:
        ax.plot(wavelength, flux, label="Model", color="red")
        values.append(flux)

    if fig is not None:
        ax.set_xlabel(r"$\lambda$ ($\mathrm{\mu}$m)")
        ax.set_ylabel(flux_label)
        ax.legend()

        max_value = np.concatenate(values).max()
        ax.set_ylim([0, max_value + 0.2 * max_value])

        if savefig is not None:
            plt.savefig(savefig, format=Path(savefig).suffix[1:], dpi=OPTIONS.plot.dpi)
        plt.close()


def plot_product(
    points,
    product,
    xlabel,
    ylabel,
    save_path=None,
    ax=None,
    colorbar=False,
    cmap: str = OPTIONS.plot.color.colormap,
    scale=None,
    label=None,
):
    norm = None
    if label is not None:
        if isinstance(label, (np.ndarray, u.Quantity)):
            norm = mcolors.Normalize(vmin=label[0].value, vmax=label[-1].value)

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    if product.ndim > 1:
        for lb, prod in zip(label, product):
            color = None
            if norm is not None:
                colormap = get_colormap(cmap)
                color = colormap(norm(lb.value))
            ax.plot(points, prod, label=lb, color=color)
        if not colorbar:
            ax.legend()
    else:
        ax.plot(points, product, label=label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if scale == "log":
        ax.set_yscale("log")
    elif scale == "loglog":
        ax.set_yscale("log")
        ax.set_xscale("log")
    elif scale == "sci":
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

    if colorbar:
        sm = cm.ScalarMappable(cmap=get_colormap(cmap), norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_ticks(OPTIONS.plot.ticks)
        cbar.set_ticklabels([f"{wavelength:.1f}" for wavelength in OPTIONS.plot.ticks])
        cbar.set_label(label=r"$\lambda$ ($\mathrm{\mu}$m)")

    if save_path is not None:
        fig.savefig(save_path, format=Path(save_path).suffix[1:], dpi=OPTIONS.plot.dpi)
        plt.close(fig)


# TODO: Clean and split this function into multiple ones
def plot_products(
    dim: int,
    components: List[FourierComponent],
    component_labels: List[str],
    save_dir: Path | None = None,
) -> None:
    """Plots the intermediate products of the model (temperature, density, etc.)."""
    component_labels = [
        " ".join(map(str.title, label.split("_"))) for label in component_labels
    ]
    for t in range(OPTIONS.data.nt):
        wls = np.linspace(OPTIONS.fit.wls[0], OPTIONS.fit.wls[-1], dim)
        radii, surface_density, optical_depth = [], [], []
        fluxes, emissivity, intensity = [], [], []
        _, ax = plt.subplots(figsize=(5, 5))
        for label, component in zip(component_labels, components):
            component.dim.value = dim
            flux = component.fr(t, wls) * component.compute_flux(t, wls).squeeze()
            plot_product(
                wls,
                flux,
                r"$\lambda$ ($\mathrm{\mu}$m)",
                r"$F_{\nu}$ (Jy)",
                scale="log",
                ax=ax,
                label=label,
            )
            fluxes.append(flux)
            if component.name in ["Point", "Gauss", "BBGauss"]:
                continue

            radius = component.compute_internal_grid(t, wls)
            radii.append(radius)

            surface_density.append(component.compute_surface_density(radius, t, wls))
            optical_depth.append(
                component.compute_optical_depth(radius, t, wls[:, np.newaxis])
            )
            emissivity.append(
                component.compute_emissivity(radius, t, wls[:, np.newaxis])
            )
            intensity.append(component.compute_intensity(radius, t, wls[:, np.newaxis]))

        surface_density = u.Quantity(surface_density)
        optical_depth = u.Quantity(optical_depth)
        emissivity = u.Quantity(emissivity)
        intensity = u.Quantity(intensity)

        total_flux = np.sum(fluxes, axis=0)
        ax.plot(wls, total_flux, label="Total")
        ax.set_yscale("log")
        ax.set_ylim([1e-1, None])
        ax.legend()
        plt.savefig(save_dir / f"fluxes_t{t}.png", format="png", dpi=OPTIONS.plot.dpi)
        plt.close()

        _, ax = plt.subplots(figsize=(5, 5))
        for label, flux_ratio in zip(component_labels, np.array(fluxes) / total_flux):
            plot_product(
                wls,
                flux_ratio * 100,
                r"$\lambda$ ($\mathrm{\mu}$m)",
                r"$F_{\nu}$ / $F_{\nu,\,\mathrm{tot}}$ (%)",
                ax=ax,
                label=label,
            )

        ax.legend()
        ax.set_ylim([0, 100])
        plt.savefig(
            save_dir / f"flux_ratios_t{t}.png", format="png", dpi=OPTIONS.plot.dpi
        )
        plt.close()

        radii_bounds = [
            (prev[-1], current[0]) for prev, current in zip(radii[:-1], radii[1:])
        ]
        fill_radii = [np.linspace(lower, upper, dim) for lower, upper in radii_bounds]
        merged_radii = list(chain.from_iterable(zip_longest(radii, fill_radii)))[:-1]
        merged_radii = u.Quantity(np.concatenate(merged_radii, axis=0))
        fill_zeros = np.zeros((len(fill_radii), wls.size, dim))
        disc_component = [
            comp for comp in components if comp.name not in ["Point", "Gauss"]
        ][0]

        # TODO: Make it so that the temperatures are somehow continous in the plot? (Maybe check for self.temps in the models?)
        # or interpolate smoothly somehow (see the one youtube video?) :D
        temperature = disc_component.compute_temperature(merged_radii, t, wls)
        surface_density = u.Quantity(
            list(
                chain.from_iterable(
                    zip_longest(surface_density, fill_zeros[:, 0, :] * u.g / u.cm**2)
                )
            )[:-1]
        )
        surface_density = np.concatenate(surface_density, axis=0)
        optical_depth = u.Quantity(
            list(chain.from_iterable(zip_longest(optical_depth, fill_zeros)))[:-1]
        )
        optical_depth = np.hstack(optical_depth)
        emissivity = u.Quantity(
            list(chain.from_iterable(zip_longest(emissivity, fill_zeros)))[:-1]
        )
        emissivity = np.hstack(emissivity)
        intensity = u.Quantity(
            list(
                chain.from_iterable(
                    zip_longest(
                        intensity, fill_zeros * u.erg / u.cm**2 / u.s / u.Hz / u.sr
                    )
                )
            )[:-1]
        )
        intensity = np.hstack(intensity)
        intensity = intensity.to(u.W / u.m**2 / u.Hz / u.sr)
        merged_radii_mas = (
            (merged_radii.to(u.au) / components[1].dist().to(u.pc)).value * 1e3 * u.mas
        )

        # TODO: Code this in a better manner
        wls = [1.7, 2.15, 3.4, 8, 11.3, 13] * u.um
        cumulative_intensity = (
            np.zeros((wls.size, merged_radii_mas.size))
            * u.erg
            / u.s
            / u.Hz
            / u.cm**2
            / u.sr
        )
        # for index, wl in enumerate(wls):
        #     tmp_intensity = [
        #         component.compute_intensity(radius, t, wl)
        #         for radius, component in zip(radii, components[1:])
        #     ]
        #     tmp_intensity = u.Quantity(
        #         list(
        #             chain.from_iterable(
        #                 zip_longest(
        #                     tmp_intensity,
        #                     fill_zeros[0, 0][np.newaxis, :]
        #                     * u.erg
        #                     / u.cm**2
        #                     / u.s
        #                     / u.Hz
        #                     / u.sr,
        #                 )
        #             )
        #         )[:-1]
        #     )
        #     cumulative_intensity[index, :] = np.hstack(tmp_intensity)
        #
        # cumulative_intensity = cumulative_intensity.to(
        #     u.erg / u.s / u.Hz / u.cm**2 / u.mas**2
        # )
        # cumulative_total_flux = (
        #     2
        #     * np.pi
        #     * disc_component.cinc(t, wls)
        #     * np.trapz(merged_radii_mas * cumulative_intensity, merged_radii_mas).to(
        #         u.Jy
        #     )[:, np.newaxis]
        # )
        #
        # cumulative_flux = np.zeros((wls.size, merged_radii.size)) * u.Jy
        # for index, _ in enumerate(merged_radii):
        #     cumulative_flux[:, index] = (
        #         2
        #         * np.pi
        #         * disc_component.cinc(t, wls)
        #         * np.trapz(
        #             merged_radii_mas[:index] * cumulative_intensity[:, :index],
        #             merged_radii_mas[:index],
        #         ).to(u.Jy)
        #     )
        # cumulative_flux_ratio = cumulative_flux / cumulative_total_flux
        # plot_product(
        #     merged_radii.value,
        #     cumulative_flux_ratio.value,
        #     "$R$ (AU)",
        #     r"$F_{\nu}\left(r\right)/F_{\nu,\,\mathrm{{tot}}}$ (a.u.)",
        #     label=wls,
        #     save_path=save_dir / f"cumulative_flux_ratio_t{t}.png",
        # )

        plot_product(
            merged_radii.value,
            temperature.value,
            "$R$ (AU)",
            "$T$ (K)",
            scale="log",
            save_path=save_dir / f"temperature_t{t}.png",
        )
        plot_product(
            merged_radii.value,
            surface_density.value,
            "$R$ (au)",
            r"$\Sigma$ (g cm$^{-2}$)",
            save_path=save_dir / f"surface_density_t{t}.png",
            scale="sci",
        )
        plot_product(
            merged_radii.value,
            optical_depth.value,
            "$R$ (AU)",
            r"$\tau_{\nu}$",
            save_path=save_dir / f"optical_depths_t{t}.png",
            scale="log",
            colorbar=True,
            label=wls,
        )
        # plot_product(merged_radii.value, emissivities.value,
        #              "$R$ (AU)", r"$\epsilon_{\nu}$",
        #              save_path=save_dir / "emissivities.png",
        #              label=wavelength)
        # plot_product(merged_radii.value, brightnesses.value,
        #              "$R$ (AU)", r"$I_{\nu}$ (W m$^{-2}$ Hz$^{-1}$ sr$^{-1}$)",
        #              save_path=save_dir / "brightnesses.png",
        #              scale="log", label=wavelength)
