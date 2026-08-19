import numpy as np
import xarray as xr
from matplotlib import animation as mpl_animation
from matplotlib import pyplot as plt
from matplotlib.colors import BoundaryNorm
import matplotlib as mpl
import pandas as pd
from pathlib import Path

_fonts_dir = Path(__file__).parent / ".." / ".." / "data" / "fonts"

for font_file in _fonts_dir.glob("*.ttf"):
    mpl.font_manager.fontManager.addfont(str(font_file))


try:
    import contextily as ctx
except ImportError:
    ctx = None

XBEACH_CRS = "EPSG:32629"
MINIMUM_WATER_DEPTH_M = 0.05
MAXIMUM_ANIMATION_FRAMES = 92


# ------------------------------------------------------------
# Small numeric helpers
# ------------------------------------------------------------

def _clean_values(values, absolute_limit=1e10):
    """Replace non-finite or implausibly large values with NaN.

    xarray decodes each variable's ``_FillValue``/``missing_value`` metadata
    into NaN automatically on load, so this only needs to catch sentinel
    values that are finite but fall outside ``absolute_limit``.
    """
    values = np.asarray(values, dtype=float)
    invalid = ~np.isfinite(values) | (np.abs(values) > absolute_limit)
    return np.where(invalid, np.nan, values)


def sample_indices(total_count, maximum_count):
    """Return at most ``maximum_count`` regularly spaced indices into ``range(total_count)``."""
    if total_count <= 0:
        raise ValueError("The selected variable contains no time records.")
    number_of_samples = min(total_count, maximum_count)
    return np.unique(np.linspace(0, total_count - 1, number_of_samples, dtype=int))


def align_runup_time_indices(depth_indices, depth_time_count, runup_time_count):
    """Map depth-frame indices onto the runup time axis.

    XBeach can write ``hh`` and ``runup`` at different output frequencies, so
    each depth index is mapped to the runup index at the same relative
    position in time.
    """
    if runup_time_count <= 0:
        raise ValueError("The runup variable contains no time records.")
    if depth_time_count <= 1:
        return np.zeros(len(depth_indices), dtype=int)

    relative_position = np.asarray(depth_indices, dtype=float) / float(depth_time_count - 1)
    runup_indices = np.rint(relative_position * float(runup_time_count - 1)).astype(int)
    return np.clip(runup_indices, 0, runup_time_count - 1)

def _estimate_cell_size(x, y):
    """Estimate the (dx, dy) grid spacing in metres from the curvilinear grid."""
    horizontal_distance = np.hypot(np.diff(x, axis=1), np.diff(y, axis=1))
    vertical_distance = np.hypot(np.diff(x, axis=0), np.diff(y, axis=0))
    dx = float(np.nanmedian(horizontal_distance)) if np.isfinite(horizontal_distance).any() else 0.0
    dy = float(np.nanmedian(vertical_distance)) if np.isfinite(vertical_distance).any() else 0.0
    return dx, dy


def _compute_flooded_area_km2(water_depths, dx, dy):
    """Flooded area per animation frame, in square kilometres."""
    flooded_cell_count = np.isfinite(water_depths).sum(axis=(1, 2))
    return flooded_cell_count * dx * dy / 1e6


def _compute_depth_vmax(water_depths, minimum_water_depth_m):
    """99.5th-percentile water depth, used as the animation colour-scale ceiling."""
    finite_depths = water_depths[np.isfinite(water_depths)]
    depth_vmax = (
        float(np.nanpercentile(finite_depths, 99.5))
        if finite_depths.size
        else minimum_water_depth_m + 0.20
    )
    return max(depth_vmax, minimum_water_depth_m + 0.05)


# ------------------------------------------------------------
# Data loader
# ------------------------------------------------------------

def load_xbeach_animation_frames(
    path,
    site_name,
    max_frames=MAXIMUM_ANIMATION_FRAMES,
    minimum_water_depth_m=MINIMUM_WATER_DEPTH_M,
):
    """Load a sampled set of XBeach water-depth frames with their runup time series.

    Reads water depth (``hh``), bed level (``zb``), the curvilinear grid
    (``globalx``/``globaly``), model time (``globaltime``), and shoreline
    runup (``runup``) from an XBeach output netCDF file, sampling at most
    ``max_frames`` regularly spaced time steps. Depths below
    ``minimum_water_depth_m`` are treated as dry land (NaN).

    Parameters
    ----------
    path : str or Path
        Path to the XBeach output netCDF file.
    site_name : str
        Human-readable site label to attach to the result, e.g. "Costa da Caparica".
    max_frames : int
        Maximum number of animation frames to sample.
    minimum_water_depth_m : float
        Water depths below this threshold are masked as dry.

    Returns
    -------
    dict
        Animation-ready grid, depth, and runup arrays plus derived metadata
        (shoreline coordinates, flooded area per frame, colour-scale bounds).
    """
    required_variables = {"hh", "zb", "globalx", "globaly", "globaltime", "point_zs"}

    with xr.open_dataset(path) as dataset:
        missing = required_variables - set(dataset.variables)
        if missing:
            raise ValueError(f"XBeach variables missing in {path}: {sorted(missing)}")

        depth_var = dataset["hh"]
        bed_var = dataset["zb"]
        time_var = dataset["globaltime"]
        pointtime_var = dataset["pointtime"]
        runup_var = dataset["point_zs"][:,-1]
        x_runup_point = dataset["point_xz"][:,-1]
        y_runup_point = dataset["point_yz"][:,-1]

        # ----------------------------------------------------
        # Water depth
        # ----------------------------------------------------

        depth_time_dim = depth_var.dims[0]
        depth_time_count = int(depth_var.sizes[depth_time_dim])
        depth_indices = sample_indices(depth_time_count, max_frames)

        water_depths = _clean_values(
            depth_var.isel({depth_time_dim: depth_indices}).values,
            absolute_limit=1e6,
        ).astype(np.float32)
        water_depths[water_depths < minimum_water_depth_m] = np.nan

        # ----------------------------------------------------
        # Runup
        # ----------------------------------------------------

        runup_time_dim = runup_var.dims[0]
        runup_time_count = int(runup_var.sizes[runup_time_dim])

        runup_time = pd.to_datetime(pointtime_var.values, unit='s', 
                                    origin=pd.Timestamp('2026-02-02 12:00:00'))
        runup_time_series = pd.Series(runup_var.values, index=runup_time)
        runup_98th_percentile = runup_time_series.resample('15min').quantile(0.98)

        aligned_depth_runup_indices = align_runup_time_indices(depth_indices, depth_time_count, 
                                                               runup_time_count)

        # ----------------------------------------------------
        # Horizontal grid and bed level
        # ----------------------------------------------------

        x = _clean_values(dataset["globalx"].values)
        y = _clean_values(dataset["globaly"].values)

        if bed_var.ndim >= 3:
            bed = _clean_values(
                bed_var.isel({bed_var.dims[0]: 0}).values, absolute_limit=1e6
            ).astype(np.float32)
        else:
            bed = _clean_values(bed_var.values, absolute_limit=1e6).astype(np.float32)

        times_15m_s = _clean_values(
            time_var.isel({depth_time_dim: depth_indices}).values,
            absolute_limit=1e20,
        )

    dx, dy = _estimate_cell_size(x, y)

    return {
        "site": site_name,
        "x_m": x,
        "y_m": y,
        "bed_level_m": bed,
        "frame_indices": depth_indices,
        "aligned_indices": aligned_depth_runup_indices,
        "water_depths_m": water_depths,
        "runup_values_m":  runup_var.values,
        "times_15m": times_15m_s,
        "times_1s": pointtime_var.values,
        "runup_98th_m": runup_98th_percentile.values,
        "x_runup_point": x_runup_point,
        "y_runup_point": y_runup_point,
        "minimum_water_depth_m": minimum_water_depth_m,
        "vmax_m": _compute_depth_vmax(water_depths, minimum_water_depth_m),
        "water_area_km2": _compute_flooded_area_km2(water_depths, dx, dy),
        "model_frame_count": depth_time_count,
    }

# ------------------------------------------------------------
# Animation
# ------------------------------------------------------------

def _mask_dry_cells(depth_frame, minimum_water_depth_m):
    """Mask cells that are dry (NaN) or below the minimum water depth."""
    depth_frame = np.asarray(depth_frame, dtype=float)
    return np.ma.masked_where(
        ~np.isfinite(depth_frame) | (depth_frame < minimum_water_depth_m),
        depth_frame,
    )


def _plot_flood_map(map_axis, surface, x, y, bed, shoreline_x, shoreline_y):
    """Draw the static map layers and the first water-depth frame.

    Returns the artists that need to be mutated per animation frame:
    ``depth_image`` and ``map_title``.
    """

    x_min, x_max = float(np.nanmin(x)), float(np.nanmax(x))
    y_min, y_max = float(np.nanmin(y)), float(np.nanmax(y))
    map_axis.set_xlim(x_min, x_max)
    map_axis.set_ylim(y_min, y_max)
    map_axis.set_facecolor("#e8edf1")

    if ctx is not None:
        try:
            ctx.add_basemap(
                map_axis,
                crs=XBEACH_CRS,
                source=ctx.providers.Esri.WorldImagery,
                attribution=False,
                reset_extent=False,
            )
        except Exception:
            pass

    levels = np.linspace(surface["minimum_water_depth_m"], surface["vmax_m"], 15)
    cmap = plt.get_cmap("RdYlBu").copy()
    cmap.set_bad(alpha=0.0)
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

    initial_depth = _mask_dry_cells(surface["water_depths_m"][0], surface["minimum_water_depth_m"])

    depth_image = map_axis.pcolormesh(
        x, y, initial_depth, norm=norm, cmap=cmap, shading="auto",
        alpha=0.86, antialiased=True, zorder=2, rasterized=True,
    )

    if np.isfinite(bed).any() and np.nanmin(bed) <= 0 and np.nanmax(bed) >= 0:
        map_axis.contour(x, y, bed, levels=[0], colors="black", linewidths=0.9, zorder=3)

    # Zero-metre shoreline
    #map_axis.plot(shoreline_x, shoreline_y, color="black", linewidth=0.8, alpha=0.8, zorder=4)

    # Selected point along shoreline
    current_runup_position = map_axis.scatter(
        [surface["x_runup_point"][0]], [surface["y_runup_point"][0]], s=60, marker="o",
        facecolor="white", edgecolor="k", linewidth=1.2, zorder=6,
    )

    # map_axis.annotate(
    #     f"Point {shoreline_point_index}",
    #     xy=(selected_x, selected_y),
    #     xytext=(7, 7),
    #     textcoords="offset points",
    #     fontsize=8,
    #     bbox={"facecolor": "white", "edgecolor": "red", "alpha": 0.85},
    #     zorder=7,
    # )

    colorbar = map_axis.figure.colorbar(
        depth_image, ax=map_axis, orientation='horizontal',
        boundaries=levels, fraction=0.04, pad=0.12
    )
    colorbar.set_label("Water depth [m]")

    map_title = map_axis.set_title("", fontsize=12, fontweight="bold")
    map_axis.set_xlabel("X UTM [m]")
    map_axis.set_ylabel("Y UTM [m]")
    map_axis.ticklabel_format(style="plain", useOffset=False)
    map_axis.set_aspect("equal")

    return {"depth_image": depth_image, "map_title": map_title, "current_runup_position":current_runup_position}


def _plot_runup_series(series_axis, times_full, runup_full, times_98th, runup_98th):
    """Draw the runup time series and the initial time cursor.

    Returns the artists that need to be mutated per animation frame:
    ``current_time_line`` and ``current_runup_point``.
    """

    series_axis.plot(times_full, runup_full, color="#cac4cb", linewidth=1.8, label="Runup")
    #series_axis.plot(times_98th, runup_98th[:-1], color="#e27406", linewidth=1.8, label="R2")

    current_time_line = series_axis.axvline(
        times_98th[0], color="#d32f2f", linewidth=1.5, linestyle="--", label="Current time"
    )

    current_runup_point = series_axis.scatter(
        [times_98th[0]], [runup_98th[0]], s=45,
        facecolor="#fefefe", edgecolor="k", linewidth=0.8, zorder=4,
    )

    series_axis.set_title(
        f"Runup at a shoreline point",
        fontsize=12, fontweight="bold",
    )
    series_axis.set_xlabel("Model time [s]")
    series_axis.set_ylabel("Runup [m]")
    series_axis.grid(alpha=0.25)
    series_axis.legend(loc="best")

    return {"current_time_line": current_time_line, "current_runup_point": current_runup_point}


def _make_frame_updater(surface, times_s, runup_15m_s, map_artists, series_artists):
    """Build the per-frame callback used by ``FuncAnimation``.

    Mutates the depth image, map title, and runup time cursor in place for
    the given frame index.
    """
    minimum_water_depth_m = surface["minimum_water_depth_m"]

    def update(frame_number):
        depth_frame = _mask_dry_cells(surface["water_depths_m"][frame_number], minimum_water_depth_m)
        map_artists["depth_image"].set_array(depth_frame.ravel())


        pointtime_index = surface["aligned_indices"][frame_number]

        map_artists["current_runup_position"].remove()
        map_artists["current_runup_position"] = map_artists["depth_image"].axes.scatter(
            [surface["x_runup_point"][pointtime_index]], [surface["y_runup_point"][pointtime_index]], s=60, marker="o",
            facecolor="white", edgecolor="k", linewidth=1.2, zorder=6,
        )

        current_time = float(times_s[frame_number])
        current_runup = float(runup_15m_s[frame_number])

        map_artists["map_title"].set_text(
            f"XBeach — {surface['site']}\nWater depth at t = {current_time:.0f} s"
        )

        series_artists["current_time_line"].set_xdata([current_time, current_time])

        if np.isfinite(current_runup):
            series_artists["current_runup_point"].set_offsets(np.asarray([[current_time, current_runup]]))
        else:
            series_artists["current_runup_point"].set_offsets(np.empty((0, 2)))

        return (
            map_artists["depth_image"],
            map_artists["map_title"],
            map_artists["current_runup_position"],
            series_artists["current_time_line"],
            series_artists["current_runup_point"],
        )

    return update


def make_xbeach_animation(surface, interval_ms=250):
    """Render an animated flood map paired with a runup time series.

    Builds a two-panel Matplotlib animation: an animated water-depth map
    (with an optional satellite basemap) showing the selected shoreline
    point, and a runup time series at that point with a moving time cursor.

    Parameters
    ----------
    surface : dict
        Output of :func:`load_xbeach_animation_frames`.
    interval_ms : int
        Delay between animation frames, in milliseconds.

    Returns
    -------
    str
        HTML representation of the animation, ready for ``IPython.display.HTML``.
    """
    x = np.asarray(surface["x_m"], dtype=float)
    y = np.asarray(surface["y_m"], dtype=float)
    bed = np.asarray(surface["bed_level_m"], dtype=float)
    times_15m_s = np.asarray(surface["times_15m"], dtype=float)
    times_1s = np.asarray(surface["times_1s"], dtype=float)
    runup_98th_15m_s = np.asarray(surface["runup_98th_m"], dtype=float)
    runup_1s = np.asarray(surface["runup_values_m"], dtype=float)


    # fig, (map_axis, series_axis) = plt.subplots(
    #     nrows=1, ncols=2, figsize=(10, 5),
    #     gridspec_kw={"width_ratios": [1.2, 1]},
    #     constrained_layout=True,
    # )

    if surface['site'] == 'Costa da Caparica':
        fig = plt.figure(figsize=(12, 7))
        map_axis = fig.add_axes([-0.08, 0.1, 0.7, 0.8])    
        series_axis = fig.add_axes([0.5, 0.35, 0.4, 0.3])
    elif surface['site'] == 'Oeiras':
        fig = plt.figure(figsize=(12, 6))
        map_axis = fig.add_axes([0.08, 0.1, 0.45, 0.8])
        series_axis = fig.add_axes([0.57, 0.35, 0.4, 0.3])
    else:
        pass

    map_artists = _plot_flood_map(map_axis, surface, x, y, bed,3,3)
    series_artists = _plot_runup_series(series_axis, times_1s, runup_1s, times_15m_s, runup_98th_15m_s)

    update = _make_frame_updater(surface, times_15m_s, runup_98th_15m_s, map_artists, series_artists)
    update(0)

    player = mpl_animation.FuncAnimation(
        fig, update, frames=len(surface["frame_indices"]),
        interval=interval_ms, blit=False, repeat=True,
    )

    try:
        with plt.rc_context({"animation.embed_limit": 100.0}):
            html = player.to_jshtml(fps=1000 / interval_ms, embed_frames=True, default_mode="loop")
    finally:
        plt.close(fig)

    return html
