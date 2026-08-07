# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: FOCCUS Demonstrator (.venv)
#     language: python
#     name: foccus-demonstrator
# ---

# %% [markdown] tags=["overview"]
# <div style="display:flex;gap:18px;align-items:stretch;margin-bottom:18px">
#   <div style="flex:0 0 285px;background:white;border:1px solid #d9e2e6;border-radius:10px;padding:16px;display:flex;align-items:center;justify-content:center">
#     <img src="../../data/images/logos/FOCCUS_Logo_1.0.png" alt="FOCCUS project logo" style="width:255px;max-width:100%">
#   </div>
#   <div style="flex:1;background:linear-gradient(120deg,#073b4c,#0b6e75);color:white;padding:28px 32px;border-radius:10px;display:flex;align-items:center;gap:26px;flex-wrap:wrap">
#     <div style="flex:1 1 520px;min-width:0">
#       <div style="font-size:14px;letter-spacing:.08em;text-transform:uppercase;opacity:.85">FOCCUS · ESC 3.2.3 · natural and anthropogenic hazards and resilience to climate change</div>
#       <div style="font-size:17px;margin-top:10px;opacity:.92">Natural Hazards and Extreme Events</div>
#       <div style="font-size:30px;font-weight:700;line-height:1.2;margin-top:8px">Improve storm surge and extreme water levels forecast in Portuguese Estuaries</div>
#     </div>
#   </div>
#   <div style="flex:0 0 285px;background:white;border:1px solid #d9e2e6;border-radius:20px;padding:16px;display:flex;align-items:center;justify-content:center">
#     <img src="../../data/images/logos/Logo_+ATL_blue.png" alt="+ATLANTIC CoLAB logo" style="width:285px;max-width:60%">
#   </div>
# </div>
#
# This demonstrator showcases the implementation and results of Application 3.2.3, presented in Deliverable [D8.1](https://drive.google.com/file/d/1QH0eUeoo3pzQ7cVb4bc-Yg9cs8pDam6h/view?usp=sharing), addressing the Environmental and Societal Challenge related to natural and anthropogenic hazards and resilience to climate change (ESC 3), with a particular focus on natural hazards and extreme coastal events.
#
#

# %% [markdown]
# ## WHY
#
# Coastal flooding is one of the most damaging natural hazards affecting low-lying coastal urban areas. The combined effects of storm surge, astronomical tides, and energetic waves can generate extreme sea-level events capable of causing wave overtopping and coastal flooding. This demonstrator presents a multi-scale forecasting framework developed to support coastal risk management and improve preparedness for extreme coastal events.
#
# ### Objective and Framework
#
# The objective of this application is to develop a short-term coastal forecasting service based on a two-tier modelling approach for predicting and assessing the impacts of extreme sea-level events, particularly coastal overtopping, suported by circulation and wave operational models for the Portuguese coast that capture the large-scale oceanographic processes that drive extreme coastal events.
#
# Tier 1 operates at the national scale, providing a Flooding Hazard Index based on Total Water Level (TWL) forecasts along the Portuguese coast (Stockdon et al., 2023; Turner et al., 2024).
#
# Tier 2 focuses on two high-risk coastal areas within the Tagus estuarine and coastal region that are particularly vulnerable to wave overtopping and flooding. In these local demonstrators, high-resolution coastal models are used to produce event-specific forecasts with enhanced spatial detail.
#
# By combining national- and local-scale modelling, the application supports early warning systems, operational coastal risk management, and the development of climate resilience and adaptation strategies tailored to both regional and site-specific needs.
#
# ### Extreme Sea Level Events
#
# Extreme sea-level events occur when high tides, storm surges, and energetic wave conditions combine to produce exceptionally high coastal water levels. These events can result in coastal flooding and overtopping, shoreline erosion, and damage to infrastructure, posing significant risks to coastal communities, economic activities, and critical assets.
#
# Climate change is expected to increase both the frequency and severity of these events through mean sea-level rise and changes in storm intensity and patterns. Accurate forecasting is therefore essential to support early warning systems, coastal management, emergency response, and long-term climate adaptation strategies.
#
# ### Target Audience
#
# This application is aimed at coastal managers, decision-makers, and stakeholders involved in coastal risk management, including Civil Protection authorities, the Portuguese Environment Agency (APA), the Port of Lisbon Authority, the municipalities of Almada and Oeiras, and the wider scientific and research community.

# %% [markdown] tags=["why-visual"]
# <figure style="margin:18px 0 22px;background:#f6f9fa;border:1px solid #d9e2e6;border-radius:10px;overflow:hidden">
#   <img src="../../data/images/eslevents.png" alt="Extreme sea-level event exposure at Costa da Caparica and Cruz Quebrada" style="display:block;width:100%;height:auto">
#   <figcaption style="padding:9px 14px;color:#455a64;font-size:13px">Coastal application use cases: Costa da Caparica (Almada) and Cruz Quebrada (Oeiras), two coastal areas with distinct geomorphological settings and hydrodynamic conditions, both highly vulnerable to extreme sea-level events.</figcaption>
# </figure>

# %% [markdown] tags=["navigation"]
# ### Structure of the Notebook
#
# <div style="display:grid;grid-template-columns:repeat(3,minmax(190px,1fr));gap:12px;margin:10px 0 24px">
#   <div style="border-top:5px solid #0b6e75;background:#eef8f8;padding:15px;border-radius:8px"><b style="font-size:18px;color:#073b4c">WHY</b><br><span style="color:#455a64">Objective and Framework · Extreme Sea-Level Events · Target Audience · Structure of the Notebook</span></div>
#   <div style="border-top:5px solid #e18b2d;background:#fff7ec;padding:15px;border-radius:8px"><b style="font-size:18px;color:#8a4b08">WHAT</b><br><span style="color:#455a64">Product · Geographical Context · Flooding Maps · Interactive Time Teries</span></div>
#   <div style="border-top:5px solid #5b4b9a;background:#f4f1fb;padding:15px;border-radius:8px"><b style="font-size:18px;color:#3f326f">HOW</b><br><span style="color:#455a64">Technical Description · Integration within FOCCUS WP · Schematic Workflow</span></div>
# </div>

# %% [markdown]
# ## WHAT
#
# ### Product: Coastal Flooding Impact Maps
#
# The final product consists of coastal flooding impact maps generated from the modelling chain. These maps are designed to help users quickly identify where wave overtopping and coastal flooding may occur, assess the expected severity of the impacts, and understand the hydrodynamic and wave conditions that triggered the hazard.
#
# The user-facing product is an interactive coastal flooding application supported by three modelling components:
#
# 1. **National forcing:** MOHID Water providing Sea Surface Hight (SSH) together with Wave Watch III (WW3) providing wave conditions for the Portuguese coast
# 2. **Tier 1 - National first layer forecasting:** a first-layer forecast providing coastal overtopping indicators and risk classes along the Portuguese coastline
# 3. **Tier 2 - Local flooding:** high-resolution XBeach simulations providing detailed information of coastal flooding and wave overtopping in selected hotspot areas in the AML
# <!-- 4. **Product view:** peak conditions, and flood-map layers for each site. -->
#
# The circulation models for the Portuguese coast, together with the higher-resolution models for the Lisbon Metropolitan Area (AML) and adjacent coast, are run operationally every day. The first-layer overtopping forecasts are also produced operationally, and all outputs are available through the [Atlantic SENSE](https://atlanticsense.com/) platform.
#
# ### Geographical Context
# This demonstrator is applied to two study areas located within the Tagus estuary and its adjacent coastline:
#
# **Costa da Caparica (Almada Municipality)**: a low-lying sandy coast located downdrift of the Tagus estuary, highly exposed to wave overtopping and coastal flooding.
#
# **Cruz Quebrada (Oeiras Municipality)**: an urbanised shoreline located inside the Tagus estuary, characterised by artificial coastal structures and exposure to extreme water levels.
#
# These locations were selected because of their high vulnerability to coastal hazards, their socio-economic importance, and their contrasting geomorphological and hydrodynamic settings.
#
# The regional domain represents the large-scale forcing provided by the operational forecasting system, while the two local domains correspond to the high-resolution modelling areas used to simulate coastal flooding and wave overtopping.

# %% hide_input=true jupyter={"source_hidden": true}
from pathlib import Path
import base64
import warnings

import matplotlib.dates as mdates
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib import animation as mpl_animation
from IPython.display import HTML, clear_output, display
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from pyproj import Transformer
import ipywidgets as widgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xarray as xr
import yaml

from demonstrator.tier1 import load_tier1_event_summary, make_study_area_map

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="Pandas requires version.*")

plt.rcParams.update(
    {
        "figure.figsize": (11, 5),
        "axes.grid": True,
        "grid.alpha": 0.22,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
    }
)

CONFIG_PATH = Path("../data") / "config.yaml"
with CONFIG_PATH.open() as config_file:
    CONFIG = yaml.safe_load(config_file)

DATA_ROOT = Path(CONFIG["data_root"])
DATA_DIRS = {name: DATA_ROOT / rel for name, rel in CONFIG["data_dirs"].items()}
HERCULES_FILES = {
    name: DATA_DIRS[entry["dir"]] / entry["filename"]
    for name, entry in CONFIG["hercules_files"].items()
}
missing_data_files = [path for path in HERCULES_FILES.values() if not path.is_file()]
if missing_data_files:
    missing_list = "\n".join(f"- {path.as_posix()}" for path in missing_data_files)
    raise FileNotFoundError(f"Required demonstrator data files are missing:\n{missing_list}")

TIER1_HAZARD_CLASSES = CONFIG["tier1_hazard_classes"]
REGIONAL_DOMAIN = CONFIG["regional_domain"]
SITE_CONFIG = CONFIG["site_config"]
RISK_CLASSES = pd.DataFrame(CONFIG["risk_classes"])[
    ["risk_class", "lower", "upper", "color", "interpretation"]
]

# %% hide_input=true jupyter={"source_hidden": true}
study_area_output = widgets.Output()
study_area_button = widgets.Button(
    description="Refresh map", icon="map", button_style="info",
    layout=widgets.Layout(width="260px"),
)

def render_study_area_map(_=None):
    global study_area_map
    study_area_map = make_study_area_map(REGIONAL_DOMAIN, SITE_CONFIG, HERCULES_FILES["Tier1"], TIER1_HAZARD_CLASSES)
    with study_area_output:
        clear_output(wait=True)
        display(study_area_map)

study_area_button.on_click(render_study_area_map)
display(widgets.VBox([study_area_button, study_area_output]))

# %% [markdown]
# ## Flooding Maps
#
# This product provides an interactive visualisation tool for analysing XBeach simulation results in coastal environments. Users can select one of the two study areas and display animated maps showing either the evolution of water depth (flood extent) or wave runup. Water depths below 5 cm are excluded from the flood maps to highlight the most relevant inundated areas.
#
# The flooding panel includes a municipality selector, allowing users to choose between Costa da Caparica (Almada) and Cruz Quebrada (Oeiras), and a map-layer selector to display either water depth or wave runup. These interactive maps support the interpretation of coastal flooding processes, wave runup dynamics, and the spatial extent of potential impacts during extreme sea-level events.
#

# %%
# try:
#     import contextily as ctx
# except ImportError:
#     ctx = None


# # Minimum water depth shown in the flooding gif
# MINIMUM_WATER_DEPTH_M = 0.05

# # Point index to track if point_yz/runup contain several points
# # TRACKED_POINT_INDEX = 0


# XBEACH_ANIMATION_FILES = {
#     "caparica": HERCULES_FILES["XBeach_Caparica"],
#     "oeiras": HERCULES_FILES["XBeach_Oeiras"],
# }

# XBEACH_ANIMATION_NAMES = {
#     "caparica": "Costa da Caparica",
#     "oeiras": "Oeiras",
# }

# def clean_netcdf_values(variable, values, absolute_limit=1e10):
#     """
#     Convert NetCDF values to float and replace fill/invalid values by NaN.
#     """
#     values = np.asarray(values, dtype=float)

#     invalid = (
#         ~np.isfinite(values)
#         | (np.abs(values) > absolute_limit)
#     )

#     fill_value = getattr(variable, "_FillValue", None)

#     if fill_value is not None:
#         invalid |= np.isclose(
#             values,
#             float(fill_value),
#             equal_nan=False,
#         )

#     missing_value = getattr(variable, "missing_value", None)

#     if missing_value is not None:
#         try:
#             invalid |= np.isclose(
#                 values,
#                 float(np.asarray(missing_value).ravel()[0]),
#                 equal_nan=False,
#             )
#         except (TypeError, ValueError):
#             pass

#     return np.where(invalid, np.nan, values)


# def get_frame_value(values, frame_number, point_index=0):
#     """
#     Obtain a scalar value from arrays such as:

#         (time,)
#         (time, point)
#         (time, point, 1)

#     The value for point_index is returned when a point dimension exists.
#     """
#     if values is None:
#         return np.nan

#     frame = np.asarray(
#         values[frame_number],
#         dtype=float,
#     ).squeeze()

#     if frame.ndim == 0:
#         return float(frame)

#     flattened = frame.ravel()

#     if point_index >= flattened.size:
#         return np.nan

#     return float(flattened[point_index])


# # def get_point_yz_at_frame(
# #     point_zs,
# #     frame_number,
# #     point_index=0,
# # ):
# #     """
# #     Extract the y and z coordinates of point_yz.

# #     Supported examples:

# #         point_yz(time, 2)
# #         point_yz(time, point, 2)
# #         point_yz(time, 2, point)

# #     Returns
# #     -------
# #     point_y, point_z
# #     """
# #     if point_zs is None:
# #         return np.nan, np.nan

# #     frame = np.asarray(
# #         point_zs[frame_number],
# #         dtype=float,
# #     ).squeeze()

# #     if frame.ndim == 1:
# #         if frame.size < 2:
# #             return np.nan, np.nan

# #         return float(frame[0]), float(frame[1])

# #     if frame.ndim == 2:

# #         # Most likely structure: (point, yz)
# #         if frame.shape[-1] >= 2:
# #             if point_index >= frame.shape[0]:
# #                 return np.nan, np.nan

# #             return (
# #                 float(frame[point_index, 0]),
# #                 float(frame[point_index, 1]),
# #             )

# #         # Alternative structure: (yz, point)
# #         if frame.shape[0] >= 2:
# #             if point_index >= frame.shape[1]:
# #                 return np.nan, np.nan

# #             return (
# #                 float(frame[0, point_index]),
# #                 float(frame[1, point_index]),
# #             )

# #     return np.nan, np.nan


# # def point_yz_to_horizontal_map(
# #     surface,
# #     frame_number,
# #     point_index=0,
# # ):
# #     """
# #     Convert the y coordinate stored in point_yz into a position on the
# #     horizontal globalx/globaly grid.

# #     point_yz normally contains y and z, while the map uses globalx/globaly.
# #     Therefore, point_y is matched to the closest horizontal grid coordinate.

# #     The closest point is selected preferably along the shoreline.
# #     """
# #     point_y, point_z = get_point_yz_at_frame(
# #         surface.get("point_yz"),
# #         frame_number,
# #         point_index,
# #     )

# #     if not np.isfinite(point_y):
# #         return np.nan, np.nan, point_z

# #     shoreline_x = np.asarray(
# #         surface["shoreline_x_m"],
# #         dtype=float,
# #     )

# #     shoreline_y = np.asarray(
# #         surface["shoreline_y_m"],
# #         dtype=float,
# #     )

# #     valid = (
# #         np.isfinite(shoreline_x)
# #         & np.isfinite(shoreline_y)
# #     )

# #     if not np.any(valid):
# #         return np.nan, np.nan, point_z

# #     valid_indices = np.flatnonzero(valid)

# #     # First try to interpret point_y as an absolute UTM Y coordinate
# #     distance_absolute = np.abs(
# #         shoreline_y[valid] - point_y
# #     )

# #     selected_local_index = int(
# #         np.nanargmin(distance_absolute)
# #     )

# #     selected_index = valid_indices[
# #         selected_local_index
# #     ]

# #     tracker_x = float(
# #         shoreline_x[selected_index]
# #     )

# #     tracker_y = float(
# #         shoreline_y[selected_index]
# #     )

# #     return tracker_x, tracker_y, point_z

# def load_xbeach_animation_frames(
#     case_id,
#     max_frames=60,
#     minimum_water_depth_m=MINIMUM_WATER_DEPTH_M,
# ):
#     """
#     Read sampled XBeach frames.

#     Water depths below minimum_water_depth_m are masked and are not shown.
#     """
#     path = XBEACH_ANIMATION_FILES[case_id]

#     with Dataset(path) as dataset:
#         dataset.set_auto_mask(False)

#         required = {
#             "hh",
#             "zb",
#             "globalx",
#             "globaly",
#             "globaltime",
#         }

#         missing = required - set(dataset.variables)

#         if missing:
#             raise ValueError(
#                 f"XBeach variables missing in {path}: "
#                 f"{sorted(missing)}"
#             )

#         depth_var = dataset.variables["hh"]
#         bed_var = dataset.variables["zb"]
#         time_var = dataset.variables["globaltime"]

#         model_frame_count = int(
#             depth_var.shape[0]
#         )

#         frame_count = min(
#             max_frames,
#             model_frame_count,
#         )

#         frame_indices = np.unique(
#             np.linspace(
#                 0,
#                 model_frame_count - 1,
#                 frame_count,
#                 dtype=int,
#             )
#         )

#         # Water depth
#         water_depths = clean_netcdf_values(
#             depth_var,
#             depth_var[frame_indices, ...],
#             absolute_limit=1e6,
#         ).astype(np.float32)

#         # Do not plot water depths below 5 cm
#         water_depths[
#             water_depths < minimum_water_depth_m
#         ] = np.nan

#         # Runup
#         runup_var = dataset.variables.get("runup")

#         if runup_var is not None:
#             runup_values = clean_netcdf_values(
#                 runup_var,
#                 runup_var[frame_indices, ...],
#                 absolute_limit=1e6,
#             ).astype(np.float32)
#         else:
#             runup_values = None

#         # point_yz
#         # point_yz_var = dataset.variables.get("point_yz")

#         # if point_yz_var is not None:
#         #     point_yz = clean_netcdf_values(
#         #         point_yz_var,
#         #         point_yz_var[frame_indices, ...],
#         #         absolute_limit=1e10,
#         #     ).astype(np.float64)
#         # else:
#         #     point_yz = None

#         # Horizontal grid
#         x = clean_netcdf_values(
#             dataset.variables["globalx"],
#             dataset.variables["globalx"][:],
#         )

#         y = clean_netcdf_values(
#             dataset.variables["globaly"],
#             dataset.variables["globaly"][:],
#         )

#         # Bed level
#         if bed_var.ndim >= 3:
#             bed = clean_netcdf_values(
#                 bed_var,
#                 bed_var[0, ...],
#                 absolute_limit=1e6,
#             ).astype(np.float32)
#         else:
#             bed = clean_netcdf_values(
#                 bed_var,
#                 bed_var[:],
#                 absolute_limit=1e6,
#             ).astype(np.float32)

#         times_s = clean_netcdf_values(
#             time_var,
#             time_var[frame_indices],
#             absolute_limit=1e20,
#         )


#     # Shoreline: grid cell closest to zb = 0 for each model row

#     shoreline_columns = []

#     for row in bed:
#         if np.isfinite(row).any():
#             shoreline_columns.append(
#                 int(np.nanargmin(np.abs(row)))
#             )
#         else:
#             shoreline_columns.append(0)

#     shoreline_columns = np.asarray(
#         shoreline_columns,
#         dtype=int,
#     )

#     shoreline_rows = np.arange(
#         bed.shape[0],
#         dtype=int,
#     )

#     shoreline_x = x[
#         shoreline_rows,
#         shoreline_columns,
#     ]

#     shoreline_y = y[
#         shoreline_rows,
#         shoreline_columns,
#     ]

#     # --------------------------------------------------------
#     # Approximate cell dimensions
#     # --------------------------------------------------------

#     horizontal_distance = np.hypot(
#         np.diff(x, axis=1),
#         np.diff(y, axis=1),
#     )

#     vertical_distance = np.hypot(
#         np.diff(x, axis=0),
#         np.diff(y, axis=0),
#     )

#     dx = (
#         float(np.nanmedian(horizontal_distance))
#         if np.isfinite(horizontal_distance).any()
#         else 0.0
#     )

#     dy = (
#         float(np.nanmedian(vertical_distance))
#         if np.isfinite(vertical_distance).any()
#         else 0.0
#     )

#     # Only cells with depth >= 0.05 m remain finite
#     water_cells = np.isfinite(
#         water_depths
#     ).sum(axis=(1, 2))

#     water_area_km2 = (
#         water_cells * dx * dy / 1e6
#     )

#     finite_depths = water_depths[
#         np.isfinite(water_depths)
#     ]

#     vmax = (
#         float(np.nanpercentile(finite_depths, 99.5))
#         if finite_depths.size
#         else minimum_water_depth_m + 0.20
#     )

#     if runup_values is not None:
#         finite_runup = runup_values[
#             np.isfinite(runup_values)
#         ]
#     else:
#         finite_runup = np.array([], dtype=float)

#     runup_vmax = (
#         float(np.nanpercentile(finite_runup, 99.5))
#         if finite_runup.size
#         else 0.10
#     )

#     return {
#         "case_id": case_id,
#         "site": XBEACH_ANIMATION_NAMES[case_id],

#         "x_m": x,
#         "y_m": y,
#         "bed_level_m": bed,

#         "water_depths_m": water_depths,
#         "runup_values_m": runup_values,

#         "shoreline_x_m": shoreline_x,
#         "shoreline_y_m": shoreline_y,

#         "frame_indices": frame_indices,
#         "times_s": times_s,

#         "minimum_water_depth_m": minimum_water_depth_m,

#         "vmax_m": max(
#             vmax,
#             minimum_water_depth_m + 0.05,
#         ),

#         "runup_vmax_m": max(
#             runup_vmax,
#             0.10,
#         ),

#         "water_area_km2": water_area_km2,
#         "model_frame_count": model_frame_count,
#     }

# def make_xbeach_animation(
#     surface,
#     interval_ms=250,
#     view_mode="water_extent",
#     tracked_point_index=0,
# ):
#     fig, ax = plt.subplots(
#         figsize=(8, 6),
#         constrained_layout=True,
#     )

#     x = surface["x_m"]
#     y = surface["y_m"]

#     ax.set_xlim(
#         float(np.nanmin(x)),
#         float(np.nanmax(x)),
#     )
#     ax.set_ylim(
#         float(np.nanmin(y)),
#         float(np.nanmax(y)),
#     )

#     ax.set_facecolor("#e8edf1")

#     if ctx is not None:
#         try:
#             ctx.add_basemap(
#                 ax,
#                 crs="EPSG:32629",
#                 source=ctx.providers.Esri.WorldImagery,
#                 attribution=False,
#                 reset_extent=False,
#             )
#         except Exception:
#             pass

#     is_runup = view_mode == "runup"

#     levels = np.linspace(
#         0.0,
#         (
#             surface["runup_vmax_m"]
#             if is_runup
#             else surface["vmax_m"]
#         ),
#         15,
#     )

#     cmap = plt.get_cmap(
#         "magma" if is_runup else "RdYlBu"
#     ).copy()

#     if not is_runup:
#         cmap.set_bad(alpha=0.0)

#     norm = BoundaryNorm(
#         levels,
#         ncolors=cmap.N,
#         clip=True,
#     )

#     if is_runup:
#         initial_runup = np.asarray(
#             surface["runup_values_m"][0],
#             dtype=float,
#         )

#         image = ax.scatter(
#             surface["shoreline_x_m"],
#             surface["shoreline_y_m"],
#             c=np.nan_to_num(
#                 initial_runup,
#                 nan=0.0,
#             ),
#             norm=norm,
#             cmap=cmap,
#             s=13,
#             edgecolor="white",
#             linewidth=0.25,
#             zorder=3,
#         )

#     else:
#         initial_depth = np.asarray(
#             surface["water_depths_m"][0],
#             dtype=float,
#         )

#         initial_depth = np.ma.masked_where(
#             (~np.isfinite(initial_depth))
#             | (initial_depth < 0.05),
#             initial_depth,
#         )

#         image = ax.pcolormesh(
#             x,
#             y,
#             initial_depth,
#             norm=norm,
#             cmap=cmap,
#             shading="auto",
#             alpha=0.86,
#             antialiased=True,
#             zorder=2,
#             rasterized=True,
#         )

#     bed = surface["bed_level_m"]

#     if (
#         np.nanmin(bed) <= 0
#         and np.nanmax(bed) >= 0
#     ):
#         ax.contour(
#             x,
#             y,
#             bed,
#             levels=[0],
#             colors="black",
#             linewidths=0.9,
#             zorder=3,
#         )

#     tracked_point = ax.scatter(
#         [],
#         [],
#         s=70,
#         marker="o",
#         facecolor="red",
#         edgecolor="white",
#         linewidth=1.0,
#         zorder=6,
#     )

#     tracked_point_text = ax.annotate(
#         "",
#         xy=(0, 0),
#         xytext=(7, 7),
#         textcoords="offset points",
#         fontsize=8,
#         color="black",
#         bbox={
#             "facecolor": "white",
#             "edgecolor": "red",
#             "alpha": 0.85,
#         },
#         zorder=7,
#     )

#     tracked_point_text.set_visible(False)

#     colorbar = fig.colorbar(
#         image,
#         ax=ax,
#         boundaries=levels,
#         fraction=0.04,
#         pad=0.03,
#     )

#     colorbar.set_label(
#         "Wave runup (m)"
#         if is_runup
#         else "Water depth (m)"
#     )

#     title = ax.set_title(
#         "",
#         fontsize=13,
#         fontweight="bold",
#     )

#     stats = ax.text(
#         0.02,
#         0.02,
#         "",
#         transform=ax.transAxes,
#         va="bottom",
#         zorder=4,
#         bbox={
#             "facecolor": "white",
#             "edgecolor": "#666",
#             "alpha": 0.9,
#         },
#     )

#     ax.set_xlabel("X UTM (m)")
#     ax.set_ylabel("Y UTM (m)")
#     ax.ticklabel_format(
#         style="plain",
#         useOffset=False,
#     )
#     ax.tick_params(
#         axis="y",
#         labelrotation=90,
#     )
#     ax.set_aspect("equal")

#     def update_tracked_point(frame_number):
#         point_yz = surface.get("point_yz")
#         runup_values = surface.get("runup_values_m")

#         if point_yz is None:
#             tracked_point.set_offsets(
#                 np.empty((0, 2))
#             )
#             tracked_point_text.set_visible(False)
#             return

#         point_frame = np.asarray(
#             point_yz[frame_number],
#             dtype=float,
#         ).squeeze()

#         if point_frame.ndim == 1:
#             if point_frame.size < 2:
#                 tracked_point.set_offsets(
#                     np.empty((0, 2))
#                 )
#                 tracked_point_text.set_visible(False)
#                 return

#             point_y = float(point_frame[0])
#             point_z = float(point_frame[1])

#         elif (
#             point_frame.ndim == 2
#             and point_frame.shape[-1] >= 2
#         ):
#             if tracked_point_index >= point_frame.shape[0]:
#                 tracked_point.set_offsets(
#                     np.empty((0, 2))
#                 )
#                 tracked_point_text.set_visible(False)
#                 return

#             point_y = float(
#                 point_frame[
#                     tracked_point_index,
#                     0,
#                 ]
#             )
#             point_z = float(
#                 point_frame[
#                     tracked_point_index,
#                     1,
#                 ]
#             )

#         elif (
#             point_frame.ndim == 2
#             and point_frame.shape[0] >= 2
#         ):
#             if tracked_point_index >= point_frame.shape[1]:
#                 tracked_point.set_offsets(
#                     np.empty((0, 2))
#                 )
#                 tracked_point_text.set_visible(False)
#                 return

#             point_y = float(
#                 point_frame[
#                     0,
#                     tracked_point_index,
#                 ]
#             )
#             point_z = float(
#                 point_frame[
#                     1,
#                     tracked_point_index,
#                 ]
#             )

#         else:
#             tracked_point.set_offsets(
#                 np.empty((0, 2))
#             )
#             tracked_point_text.set_visible(False)
#             return

#         if not np.isfinite(point_y):
#             tracked_point.set_offsets(
#                 np.empty((0, 2))
#             )
#             tracked_point_text.set_visible(False)
#             return

#         shoreline_x = np.asarray(
#             surface["shoreline_x_m"],
#             dtype=float,
#         )

#         shoreline_y = np.asarray(
#             surface["shoreline_y_m"],
#             dtype=float,
#         )

#         valid_shoreline = (
#             np.isfinite(shoreline_x)
#             & np.isfinite(shoreline_y)
#         )

#         if not np.any(valid_shoreline):
#             tracked_point.set_offsets(
#                 np.empty((0, 2))
#             )
#             tracked_point_text.set_visible(False)
#             return

#         valid_indices = np.flatnonzero(
#             valid_shoreline
#         )

#         closest_local_index = np.nanargmin(
#             np.abs(
#                 shoreline_y[valid_shoreline]
#                 - point_y
#             )
#         )

#         closest_index = valid_indices[
#             closest_local_index
#         ]

#         point_x_map = float(
#             shoreline_x[closest_index]
#         )

#         point_y_map = float(
#             shoreline_y[closest_index]
#         )

#         tracked_point.set_offsets(
#             np.array([
#                 [point_x_map, point_y_map]
#             ])
#         )

#         runup_at_point = np.nan

#         if runup_values is not None:
#             runup_frame = np.asarray(
#                 runup_values[frame_number],
#                 dtype=float,
#             ).squeeze()

#             if runup_frame.ndim == 0:
#                 runup_at_point = float(
#                     runup_frame
#                 )
#             else:
#                 runup_flat = runup_frame.ravel()

#                 if tracked_point_index < runup_flat.size:
#                     runup_at_point = float(
#                         runup_flat[
#                             tracked_point_index
#                         ]
#                     )

#         tracked_point_text.xy = (
#             point_x_map,
#             point_y_map,
#         )

#         if np.isfinite(runup_at_point):
#             tracked_point_text.set_text(
#                 f"Runup: {runup_at_point:.2f} m"
#             )
#         elif np.isfinite(point_z):
#             tracked_point_text.set_text(
#                 f"z: {point_z:.2f} m"
#             )
#         else:
#             tracked_point_text.set_text("")

#         tracked_point_text.set_visible(True)

#     def update(frame_number):
#         if is_runup:
#             frame = np.asarray(
#                 surface["runup_values_m"][frame_number],
#                 dtype=float,
#             )

#             image.set_array(
#                 np.nan_to_num(
#                     frame,
#                     nan=0.0,
#                 )
#             )

#         else:
#             frame = np.asarray(
#                 surface["water_depths_m"][frame_number],
#                 dtype=float,
#             )

#             frame = np.ma.masked_where(
#                 (~np.isfinite(frame))
#                 | (frame < 0.05),
#                 frame,
#             )

#             image.set_array(
#                 frame.ravel()
#             )

#         update_tracked_point(
#             frame_number
#         )

#         title.set_text(
#             f"XBeach — {surface['site']}\n"
#             + (
#                 f"Short-wave runup at "
#                 f"t = {surface['times_s'][frame_number]:.0f} s"
#                 if is_runup
#                 else
#                 f"Water-column depth at "
#                 f"t = {surface['times_s'][frame_number]:.0f} s"
#             )
#         )

#         return (
#             image,
#             tracked_point,
#             tracked_point_text,
#             title,
#             stats,
#         )

#     update(0)

#     player = mpl_animation.FuncAnimation(
#         fig,
#         update,
#         frames=len(surface["frame_indices"]),
#         interval=interval_ms,
#         blit=False,
#     )

#     try:
#         with plt.rc_context({
#             "animation.embed_limit": 100.0
#         }):
#             html = player.to_jshtml(
#                 fps=1000 / interval_ms,
#                 embed_frames=True,
#                 default_mode="loop",
#             )
#     finally:
#         plt.close(fig)

#     return html

# %%

# try:
#     # print("Loading XBeach data...")

#     surface = load_xbeach_animation_frames(
#         case_id="caparica",
#         max_frames=60,
#     )

#     # print(
#     #     f"Loaded {len(surface['frame_indices'])} frames "
#     #     f"for {surface['site']}."
#     # )

#     animation_html = make_xbeach_animation(
#         surface=surface,
#         interval_ms=250,
#         view_mode="water_extent",
#         tracked_point_index=0,
#     )
    
#     _xbeach_animation_cache = {}


#     # ------------------------------------------------------------
#     # Seletores
#     # ------------------------------------------------------------
    
#     xbeach_municipality_selector = widgets.Dropdown(
#         options=[
#             ("Costa da Caparica — Almada", "caparica"),
#             ("Cruz Quebrada — Oeiras", "oeiras"),
#         ],
#         value="caparica",
#         description="Study area:",
#         style={"description_width": "110px"},
#         layout=widgets.Layout(width="370px"),
#     )
    
#     xbeach_layer_selector = widgets.Dropdown(
#         options=[
#             ("Water depth / inundation extent", "water_extent"),
#             ("Wave runup", "runup"),
#         ],
#         value="water_extent",
#         description="Map layer:",
#         style={"description_width": "110px"},
#         layout=widgets.Layout(width="370px"),
#     )
    
#     xbeach_frame_selector = widgets.IntSlider(
#         value=60,
#         min=10,
#         max=100,
#         step=10,
#         description="Frames:",
#         continuous_update=False,
#         style={"description_width": "110px"},
#         layout=widgets.Layout(width="370px"),
#     )
    
#     xbeach_interval_selector = widgets.IntSlider(
#         value=250,
#         min=100,
#         max=1000,
#         step=50,
#         description="Interval (ms):",
#         continuous_update=False,
#         style={"description_width": "110px"},
#         layout=widgets.Layout(width="370px"),
#     )
    
#     xbeach_point_selector = widgets.BoundedIntText(
#         value=0,
#         min=0,
#         max=1000,
#         step=1,
#         description="Point index:",
#         style={"description_width": "110px"},
#         layout=widgets.Layout(width="220px"),
#     )
    
#     xbeach_generate_button = widgets.Button(
#         description="Generate animation",
#         button_style="primary",
#         icon="play",
#         layout=widgets.Layout(width="200px"),
#     )
    
#     xbeach_clear_cache_button = widgets.Button(
#         description="Clear cache",
#         button_style="",
#         icon="trash",
#         layout=widgets.Layout(width="150px"),
#     )
    
#     xbeach_animation_status = widgets.HTML(
#         value="<i>Select the study area and map layer.</i>"
#     )
    
#     xbeach_animation_output = widgets.Output(
#         layout=widgets.Layout(
#             width="100%",
#             min_height="200px",
#         )
#     )
    
    
#     def render_xbeach_animation(change=None):
#         case_id = xbeach_municipality_selector.value
#         view_mode = xbeach_layer_selector.value
#         max_frames = xbeach_frame_selector.value
#         interval_ms = xbeach_interval_selector.value
#         tracked_point_index = xbeach_point_selector.value
    
#         cache_key = (
#             case_id,
#             view_mode,
#             max_frames,
#             interval_ms,
#             tracked_point_index,
#             MINIMUM_WATER_DEPTH_M,
#         )
    
#         xbeach_generate_button.disabled = True
    
#         xbeach_animation_status.value = (
#             "<b>Loading XBeach data and generating animation...</b>"
#         )
    
#         try:
#             if cache_key in _xbeach_animation_cache:
#                 animation_html = _xbeach_animation_cache[cache_key]
#                 source_message = "Animation loaded from cache."
#             else:
#                 surface = load_xbeach_animation_frames(
#                     case_id=case_id,
#                     max_frames=max_frames,
#                     minimum_water_depth_m=MINIMUM_WATER_DEPTH_M,
#                 )
    
#                 if (
#                     view_mode == "runup"
#                     and surface["runup_values_m"] is None
#                 ):
#                     raise ValueError(
#                         f"The NetCDF file for {surface['site']} "
#                         "does not contain the variable 'runup'."
#                     )
    
#                 animation_html = make_xbeach_animation(
#                     surface=surface,
#                     interval_ms=interval_ms,
#                     view_mode=view_mode,
#                     tracked_point_index=tracked_point_index,
#                 )
    
#                 _xbeach_animation_cache[cache_key] = animation_html
#                 source_message = "New animation generated."
    
#             with xbeach_animation_output:
#                 clear_output(wait=True)
#                 display(HTML(animation_html))
    
#             layer_name = (
#                 "wave runup"
#                 if view_mode == "runup"
#                 else "water depth / inundation extent"
#             )
    
#             xbeach_animation_status.value = (
#                 f"<span style='color:green'><b>Ready.</b></span> "
#                 f"{XBEACH_ANIMATION_NAMES[case_id]} — {layer_name}. "
#                 f"{source_message}"
#             )
    
#         except Exception as error:
#             with xbeach_animation_output:
#                 clear_output(wait=True)
#                 print(f"{type(error).__name__}: {error}")
    
#             xbeach_animation_status.value = (
#                 "<span style='color:#b00020'><b>Error:</b> "
#                 f"{type(error).__name__}: {error}</span>"
#             )
    
#             raise
    
#         finally:
#             xbeach_generate_button.disabled = False
    
    
#     def clear_xbeach_animation_cache(button=None):
#         _xbeach_animation_cache.clear()
    
#         xbeach_animation_status.value = (
#             "<span style='color:#555'>Animation cache cleared.</span>"
#         )
    
    
    
#     xbeach_generate_button.on_click(render_xbeach_animation)
#     xbeach_clear_cache_button.on_click(clear_xbeach_animation_cache)
    
    
#     xbeach_controls = widgets.VBox(
#         [
#             widgets.HTML(
#                 """
#                 <h3 style="margin-bottom:4px;">
#                     Coastal Flooding Impact Maps
#                 </h3>
#                 <p style="margin-top:0;">
#                     Select a study area and a map layer to display the
#                     corresponding XBeach animation.
#                 </p>
#                 """
#             ),
#             widgets.HBox(
#                 [
#                     xbeach_municipality_selector,
#                     xbeach_layer_selector,
#                 ]
#             ),
#             # widgets.HBox(
#             #     [
#             #         xbeach_frame_selector,
#             #         xbeach_interval_selector,
#             #     ]
#             # ),
#             widgets.HBox(
#                 [
#                     # xbeach_point_selector,
#                     xbeach_generate_button,
#                     # xbeach_clear_cache_button,
#                 ]
#             ),
#             xbeach_animation_status,
#         ],
#         layout=widgets.Layout(
#             border="1px solid #cccccc",
#             padding="12px",
#             margin="0 0 12px 0",
#             width="100%",
#         ),
#     )
    
#     flood_map_panel = widgets.VBox(
#         [
#             xbeach_controls,
#             xbeach_animation_output,
#         ],
#         layout=widgets.Layout(width="100%"),
#     )
    
#     display(flood_map_panel)


# except Exception as error:
#     print(
#         f"{type(error).__name__}: {error}"
#     )
#     raise

# %%
try:
    import contextily as ctx
except ImportError:
    ctx = None

MINIMUM_WATER_DEPTH_M = 0.05

MAXIMUM_ANIMATION_FRAMES = 60

XBEACH_CRS = "EPSG:32629"


XBEACH_ANIMATION_FILES = {
    "caparica": HERCULES_FILES["XBeach_Caparica"],
    "oeiras": HERCULES_FILES["XBeach_Oeiras"],
}

XBEACH_ANIMATION_NAMES = {
    "caparica": "Costa da Caparica",
    "oeiras": "Oeiras",
}

def clean_netcdf_values(
    variable,
    values,
    absolute_limit=1e10,
):
    """
    Convert NetCDF values to float and replace invalid or fill
    values with NaN.
    """

    values = np.asarray(values, dtype=float)

    invalid = (
        ~np.isfinite(values)
        | (np.abs(values) > absolute_limit)
    )

    fill_value = getattr(
        variable,
        "_FillValue",
        None,
    )

    if fill_value is not None:
        invalid |= np.isclose(
            values,
            float(fill_value),
            equal_nan=False,
        )

    missing_value = getattr(
        variable,
        "missing_value",
        None,
    )

    if missing_value is not None:
        try:
            missing_value = float(
                np.asarray(missing_value).ravel()[0]
            )

            invalid |= np.isclose(
                values,
                missing_value,
                equal_nan=False,
            )

        except (TypeError, ValueError):
            pass

    return np.where(
        invalid,
        np.nan,
        values,
    )


def sample_indices(
    total_count,
    maximum_count,
):
    """Return regularly spaced integer indices."""

    if total_count <= 0:
        raise ValueError(
            "The selected variable contains no time records."
        )

    number_of_samples = min(
        total_count,
        maximum_count,
    )

    return np.unique(
        np.linspace(
            0,
            total_count - 1,
            number_of_samples,
            dtype=int,
        )
    )


def align_runup_time_indices(
    depth_indices,
    depth_time_count,
    runup_time_count,
):
    """
    Convert depth-output indices into corresponding runup indices.

    This works when runup and hh use different output frequencies.
    """

    if runup_time_count <= 0:
        raise ValueError(
            "The runup variable contains no time records."
        )

    if depth_time_count <= 1:
        return np.zeros(
            len(depth_indices),
            dtype=int,
        )

    relative_position = (
        np.asarray(depth_indices, dtype=float)
        / float(depth_time_count - 1)
    )

    runup_indices = np.rint(
        relative_position
        * float(runup_time_count - 1)
    ).astype(int)

    return np.clip(
        runup_indices,
        0,
        runup_time_count - 1,
    )


def normalise_runup_array(runup_values):
    """
    Convert runup to a 2-D array with dimensions:

        (time, shoreline_point)
    """

    if runup_values is None:
        return None

    runup_values = np.asarray(
        runup_values,
        dtype=float,
    )

    runup_values = np.squeeze(
        runup_values
    )

    if runup_values.ndim == 1:
        return runup_values[:, np.newaxis]

    if runup_values.ndim == 2:
        return runup_values

    # Preserve the first axis as time and flatten the remaining
    # dimensions into a point dimension.
    return runup_values.reshape(
        runup_values.shape[0],
        -1,
    )


# ------------------------------------------------------------
# Data loader
# ------------------------------------------------------------

def load_xbeach_animation_frames(
    case_id,
    max_frames=MAXIMUM_ANIMATION_FRAMES,
    minimum_water_depth_m=MINIMUM_WATER_DEPTH_M,
):
    """
    Read sampled XBeach water-depth frames and the corresponding
    runup time series.

    Water depths below minimum_water_depth_m are excluded.
    """

    if case_id not in XBEACH_ANIMATION_FILES:
        raise KeyError(
            f"Unknown XBeach case: {case_id}"
        )

    path = XBEACH_ANIMATION_FILES[
        case_id
    ]

    with Dataset(path) as dataset:
        dataset.set_auto_mask(False)

        required_variables = {
            "hh",
            "zb",
            "globalx",
            "globaly",
            "globaltime",
            "runup",
        }

        missing = (
            required_variables
            - set(dataset.variables)
        )

        if missing:
            raise ValueError(
                f"XBeach variables missing in {path}: "
                f"{sorted(missing)}"
            )

        depth_var = dataset.variables["hh"]
        bed_var = dataset.variables["zb"]
        time_var = dataset.variables["globaltime"]
        runup_var = dataset.variables["runup"]

        depth_time_count = int(
            depth_var.shape[0]
        )

        depth_indices = sample_indices(
            total_count=depth_time_count,
            maximum_count=max_frames,
        )

        # ----------------------------------------------------
        # Water depth
        # ----------------------------------------------------

        water_depths = clean_netcdf_values(
            depth_var,
            depth_var[depth_indices, ...],
            absolute_limit=1e6,
        ).astype(np.float32)

        water_depths[
            water_depths < minimum_water_depth_m
        ] = np.nan

        # ----------------------------------------------------
        # Runup
        # ----------------------------------------------------

        runup_time_count = int(
            runup_var.shape[0]
        )

        runup_indices = align_runup_time_indices(
            depth_indices=depth_indices,
            depth_time_count=depth_time_count,
            runup_time_count=runup_time_count,
        )

        runup_values = clean_netcdf_values(
            runup_var,
            runup_var[runup_indices, ...],
            absolute_limit=1e6,
        ).astype(np.float32)

        runup_values = normalise_runup_array(
            runup_values
        )

        # ----------------------------------------------------
        # Horizontal grid
        # ----------------------------------------------------

        x = clean_netcdf_values(
            dataset.variables["globalx"],
            dataset.variables["globalx"][:],
        )

        y = clean_netcdf_values(
            dataset.variables["globaly"],
            dataset.variables["globaly"][:],
        )

        # ----------------------------------------------------
        # Bed level
        # ----------------------------------------------------

        if bed_var.ndim >= 3:
            bed = clean_netcdf_values(
                bed_var,
                bed_var[0, ...],
                absolute_limit=1e6,
            ).astype(np.float32)

        else:
            bed = clean_netcdf_values(
                bed_var,
                bed_var[:],
                absolute_limit=1e6,
            ).astype(np.float32)

        times_s = clean_netcdf_values(
            time_var,
            time_var[depth_indices],
            absolute_limit=1e20,
        )

    # --------------------------------------------------------
    # Extract the approximate zero-metre shoreline
    # --------------------------------------------------------

    shoreline_columns = np.zeros(
        bed.shape[0],
        dtype=int,
    )

    shoreline_valid = np.zeros(
        bed.shape[0],
        dtype=bool,
    )

    for row_index, bed_row in enumerate(bed):

        valid = np.isfinite(
            bed_row
        )

        if valid.any():
            valid_columns = np.flatnonzero(
                valid
            )

            nearest_local_index = np.argmin(
                np.abs(
                    bed_row[valid]
                )
            )

            shoreline_columns[row_index] = (
                valid_columns[
                    nearest_local_index
                ]
            )

            shoreline_valid[row_index] = True

    shoreline_rows = np.arange(
        bed.shape[0],
        dtype=int,
    )

    shoreline_x = x[
        shoreline_rows,
        shoreline_columns,
    ]

    shoreline_y = y[
        shoreline_rows,
        shoreline_columns,
    ]

    shoreline_x[
        ~shoreline_valid
    ] = np.nan

    shoreline_y[
        ~shoreline_valid
    ] = np.nan

    # --------------------------------------------------------
    # Match runup points to shoreline points
    # --------------------------------------------------------

    number_of_runup_points = (
        runup_values.shape[1]
    )

    number_of_shoreline_points = (
        shoreline_x.size
    )

    common_point_count = min(
        number_of_runup_points,
        number_of_shoreline_points,
    )

    if common_point_count == 0:
        raise ValueError(
            "No shoreline/runup points are available."
        )

    shoreline_x = shoreline_x[
        :common_point_count
    ]

    shoreline_y = shoreline_y[
        :common_point_count
    ]

    runup_values = runup_values[
        :,
        :common_point_count,
    ]

    # --------------------------------------------------------
    # Approximate cell dimensions and flooded area
    # --------------------------------------------------------

    horizontal_distance = np.hypot(
        np.diff(x, axis=1),
        np.diff(y, axis=1),
    )

    vertical_distance = np.hypot(
        np.diff(x, axis=0),
        np.diff(y, axis=0),
    )

    dx = (
        float(
            np.nanmedian(
                horizontal_distance
            )
        )
        if np.isfinite(
            horizontal_distance
        ).any()
        else 0.0
    )

    dy = (
        float(
            np.nanmedian(
                vertical_distance
            )
        )
        if np.isfinite(
            vertical_distance
        ).any()
        else 0.0
    )

    flooded_cell_count = np.isfinite(
        water_depths
    ).sum(axis=(1, 2))

    flooded_area_km2 = (
        flooded_cell_count
        * dx
        * dy
        / 1e6
    )

    finite_depths = water_depths[
        np.isfinite(water_depths)
    ]

    depth_vmax = (
        float(
            np.nanpercentile(
                finite_depths,
                99.5,
            )
        )
        if finite_depths.size
        else minimum_water_depth_m + 0.20
    )

    return {
        "case_id": case_id,
        "site": XBEACH_ANIMATION_NAMES[
            case_id
        ],

        "x_m": x,
        "y_m": y,
        "bed_level_m": bed,

        "water_depths_m": water_depths,

        "runup_values_m": runup_values,

        "shoreline_x_m": shoreline_x,
        "shoreline_y_m": shoreline_y,

        "frame_indices": depth_indices,
        "runup_indices": runup_indices,

        "times_s": times_s,

        "minimum_water_depth_m": (
            minimum_water_depth_m
        ),

        "vmax_m": max(
            depth_vmax,
            minimum_water_depth_m + 0.05,
        ),

        "water_area_km2": (
            flooded_area_km2
        ),

        "model_frame_count": (
            depth_time_count
        ),

        "number_of_shoreline_points": (
            common_point_count
        ),
    }


# ------------------------------------------------------------
# Animation
# ------------------------------------------------------------

def make_xbeach_animation(
    surface,
    interval_ms=250,
    shoreline_point_index=0,
):
    """
    Create a combined animation containing:

    - animated water-depth map;
    - selected shoreline point;
    - runup time series at that point;
    - vertical cursor indicating the current time.
    """

    runup_values = np.asarray(
        surface["runup_values_m"],
        dtype=float,
    )

    number_of_points = int(
        surface[
            "number_of_shoreline_points"
        ]
    )

    shoreline_point_index = int(
        np.clip(
            shoreline_point_index,
            0,
            number_of_points - 1,
        )
    )

    x = np.asarray(
        surface["x_m"],
        dtype=float,
    )

    y = np.asarray(
        surface["y_m"],
        dtype=float,
    )

    bed = np.asarray(
        surface["bed_level_m"],
        dtype=float,
    )

    times_s = np.asarray(
        surface["times_s"],
        dtype=float,
    )

    shoreline_x = np.asarray(
        surface["shoreline_x_m"],
        dtype=float,
    )

    shoreline_y = np.asarray(
        surface["shoreline_y_m"],
        dtype=float,
    )

    selected_x = float(
        shoreline_x[
            shoreline_point_index
        ]
    )

    selected_y = float(
        shoreline_y[
            shoreline_point_index
        ]
    )

    selected_runup = runup_values[
        :,
        shoreline_point_index,
    ]

    # --------------------------------------------------------
    # Figure with map and time series
    # --------------------------------------------------------

    fig, (
        map_axis,
        series_axis,
    ) = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(13, 6),
        constrained_layout=True,
        gridspec_kw={
            "width_ratios": [
                1.15,
                1.0,
            ]
        },
    )

    # --------------------------------------------------------
    # Animated water-depth map
    # --------------------------------------------------------

    map_axis.set_xlim(
        float(np.nanmin(x)),
        float(np.nanmax(x)),
    )

    map_axis.set_ylim(
        float(np.nanmin(y)),
        float(np.nanmax(y)),
    )

    map_axis.set_facecolor(
        "#e8edf1"
    )

    if ctx is not None:
        try:
            ctx.add_basemap(
                map_axis,
                crs=XBEACH_CRS,
                source=(
                    ctx.providers.Esri
                    .WorldImagery
                ),
                attribution=False,
                reset_extent=False,
            )
        except Exception:
            pass

    levels = np.linspace(
        surface[
            "minimum_water_depth_m"
        ],
        surface["vmax_m"],
        15,
    )

    cmap = plt.get_cmap(
        "RdYlBu"
    ).copy()

    cmap.set_bad(
        alpha=0.0
    )

    norm = BoundaryNorm(
        levels,
        ncolors=cmap.N,
        clip=True,
    )

    initial_depth = np.asarray(
        surface[
            "water_depths_m"
        ][0],
        dtype=float,
    )

    initial_depth = np.ma.masked_where(
        (
            ~np.isfinite(
                initial_depth
            )
        )
        | (
            initial_depth
            < surface[
                "minimum_water_depth_m"
            ]
        ),
        initial_depth,
    )

    depth_image = map_axis.pcolormesh(
        x,
        y,
        initial_depth,
        norm=norm,
        cmap=cmap,
        shading="auto",
        alpha=0.86,
        antialiased=True,
        zorder=2,
        rasterized=True,
    )

    if (
        np.isfinite(bed).any()
        and np.nanmin(bed) <= 0
        and np.nanmax(bed) >= 0
    ):
        map_axis.contour(
            x,
            y,
            bed,
            levels=[0],
            colors="black",
            linewidths=0.9,
            zorder=3,
        )

    # Zero-metre shoreline
    map_axis.plot(
        shoreline_x,
        shoreline_y,
        color="black",
        linewidth=0.8,
        alpha=0.8,
        zorder=4,
    )

    # Selected point along shoreline
    selected_point = map_axis.scatter(
        [selected_x],
        [selected_y],
        s=75,
        marker="o",
        facecolor="red",
        edgecolor="white",
        linewidth=1.2,
        zorder=6,
    )

    map_axis.annotate(
        f"Point {shoreline_point_index}",
        xy=(
            selected_x,
            selected_y,
        ),
        xytext=(7, 7),
        textcoords="offset points",
        fontsize=8,
        bbox={
            "facecolor": "white",
            "edgecolor": "red",
            "alpha": 0.85,
        },
        zorder=7,
    )

    colorbar = fig.colorbar(
        depth_image,
        ax=map_axis,
        boundaries=levels,
        fraction=0.04,
        pad=0.03,
    )

    colorbar.set_label(
        "Water depth (m)"
    )

    map_title = map_axis.set_title(
        "",
        fontsize=12,
        fontweight="bold",
    )

    map_axis.set_xlabel(
        "X UTM (m)"
    )

    map_axis.set_ylabel(
        "Y UTM (m)"
    )

    map_axis.ticklabel_format(
        style="plain",
        useOffset=False,
    )

    map_axis.set_aspect(
        "equal"
    )

    # --------------------------------------------------------
    # Runup time series
    # --------------------------------------------------------

    series_axis.plot(
        times_s,
        selected_runup,
        color="#8e24aa",
        linewidth=1.8,
        label="Runup",
    )

    current_time_line = (
        series_axis.axvline(
            times_s[0],
            color="#d32f2f",
            linewidth=1.5,
            linestyle="--",
            label="Current time",
        )
    )

    current_runup_point = (
        series_axis.scatter(
            [times_s[0]],
            [selected_runup[0]],
            s=45,
            facecolor="#d32f2f",
            edgecolor="white",
            linewidth=0.8,
            zorder=4,
        )
    )

    series_title = (
        series_axis.set_title(
            (
                "Runup at the selected "
                "shoreline point\n"
                f"Point {shoreline_point_index}"
            ),
            fontsize=12,
            fontweight="bold",
        )
    )

    series_axis.set_xlabel(
        "Model time (s)"
    )

    series_axis.set_ylabel(
        "Runup (m)"
    )

    series_axis.grid(
        alpha=0.25
    )

    series_axis.legend(
        loc="best"
    )

    # --------------------------------------------------------
    # Statistics box
    # --------------------------------------------------------

    # stats_text = map_axis.text(
    #     0.02,
    #     0.02,
    #     "",
    #     transform=map_axis.transAxes,
    #     va="bottom",
    #     zorder=8,
    #     bbox={
    #         "facecolor": "white",
    #         "edgecolor": "#666",
    #         "alpha": 0.90,
    #     },
    # )

    def update(frame_number):

        depth_frame = np.asarray(
            surface[
                "water_depths_m"
            ][frame_number],
            dtype=float,
        )

        depth_frame = np.ma.masked_where(
            (
                ~np.isfinite(
                    depth_frame
                )
            )
            | (
                depth_frame
                < surface[
                    "minimum_water_depth_m"
                ]
            ),
            depth_frame,
        )

        depth_image.set_array(
            depth_frame.ravel()
        )

        current_time = float(
            times_s[
                frame_number
            ]
        )

        current_runup = float(
            selected_runup[
                frame_number
            ]
        )

        current_time_line.set_xdata(
            [current_time, current_time]
        )

        if np.isfinite(
            current_runup
        ):
            current_runup_point.set_offsets(
                np.asarray(
                    [[
                        current_time,
                        current_runup,
                    ]]
                )
            )
        else:
            current_runup_point.set_offsets(
                np.empty(
                    (0, 2)
                )
            )

        map_title.set_text(
            f"XBeach — {surface['site']}\n"
            f"Water depth at "
            f"t = {current_time:.0f} s"
        )

        finite_depth = (
            depth_frame.compressed()
        )

        maximum_depth = (
            float(
                np.nanmax(
                    finite_depth
                )
            )
            if finite_depth.size
            else np.nan
        )

        # stats_lines = [
        #     (
        #         f"Area with depth ≥ "
        #         f"{surface['minimum_water_depth_m']:.2f} m: "
        #         f"{surface['water_area_km2'][frame_number]:.3f} km²"
        #     )
        # ]

        # if np.isfinite(
        #     maximum_depth
        # ):
        #     stats_lines.append(
        #         f"Maximum depth: "
        #         f"{maximum_depth:.2f} m"
        #     )

        # if np.isfinite(
        #     current_runup
        # ):
        #     stats_lines.append(
        #         f"Runup at selected point: "
        #         f"{current_runup:.2f} m"
        #     )

        # stats_text.set_text(
        #     "\n".join(
        #         stats_lines
        #     )
        # )

        return (
            depth_image,
            selected_point,
            map_title,
            # stats_text,
            current_time_line,
            current_runup_point,
            series_title,
        )

    update(0)

    player = mpl_animation.FuncAnimation(
        fig,
        update,
        frames=len(
            surface[
                "frame_indices"
            ]
        ),
        interval=interval_ms,
        blit=False,
        repeat=True,
    )

    try:
        with plt.rc_context({
            "animation.embed_limit": 100.0,
        }):
            html = player.to_jshtml(
                fps=1000 / interval_ms,
                embed_frames=True,
                default_mode="loop",
            )

    finally:
        plt.close(fig)

    return html

xbeach_case_selector = widgets.Dropdown(
    options=[
        (
            "Costa da Caparica, Almada",
            "caparica",
        ),
        (
            "Cruz Quebrada, Oeiras",
            "oeiras",
        ),
    ],
    value="caparica",
    description="Study area:",
    style={
        "description_width": "80px",
    },
    layout=widgets.Layout(
        width="310px",
    ),
)


xbeach_shoreline_point_selector = (
    widgets.IntSlider(
        value=0,
        min=0,
        max=0,
        step=1,
        description="Shoreline point:",
        continuous_update=False,
        style={
            "description_width": "100px",
        },
        layout=widgets.Layout(
            width="450px",
        ),
    )
)


xbeach_status = widgets.HTML(
    value=""
)


xbeach_output = widgets.Output(
    layout=widgets.Layout(
        width="100%",
        min_height="300px",
    )
)


_xbeach_surface_cache = {}


def get_selected_surface():
    """Load or retrieve the selected XBeach case."""

    case_id = (
        xbeach_case_selector.value
    )

    if case_id not in _xbeach_surface_cache:

        _xbeach_surface_cache[
            case_id
        ] = load_xbeach_animation_frames(
            case_id=case_id,
            max_frames=MAXIMUM_ANIMATION_FRAMES,
            minimum_water_depth_m=(
                MINIMUM_WATER_DEPTH_M
            ),
        )

    return _xbeach_surface_cache[
        case_id
    ]


def update_point_slider():
    """Update the valid shoreline-point range."""

    surface = get_selected_surface()

    point_count = int(
        surface[
            "number_of_shoreline_points"
        ]
    )

    xbeach_shoreline_point_selector.max = max(
        point_count - 1,
        0,
    )

    xbeach_shoreline_point_selector.value = min(
        xbeach_shoreline_point_selector.value,
        xbeach_shoreline_point_selector.max,
    )


def render_xbeach_panel(change=None):
    """Generate the flooding animation and runup time series."""

    xbeach_case_selector.disabled = True
    xbeach_shoreline_point_selector.disabled = True

    xbeach_status.value = (
        "<span style='color:#555;'>"
        "Loading flooding animation..."
        "</span>"
    )

    try:
        surface = get_selected_surface()

        update_point_slider()

        animation_html = make_xbeach_animation(
            surface=surface,
            interval_ms=250,
            shoreline_point_index=(
                xbeach_shoreline_point_selector.value
            ),
        )

        with xbeach_output:
            clear_output(
                wait=True
            )

            display(
                HTML(
                    animation_html
                )
            )

        selected_point = (
            xbeach_shoreline_point_selector.value
        )

        selected_x = (
            surface[
                "shoreline_x_m"
            ][selected_point]
        )

        selected_y = (
            surface[
                "shoreline_y_m"
            ][selected_point]
        )

        xbeach_status.value = (
            f"<b>Selected point:</b> "
            f"{selected_point} — "
            f"X={selected_x:.1f} m, "
            f"Y={selected_y:.1f} m"
        )

    except Exception as error:

        with xbeach_output:
            clear_output(
                wait=True
            )

            print(
                f"{type(error).__name__}: "
                f"{error}"
            )

        xbeach_status.value = (
            "<span style='color:#b00020;'>"
            f"<b>Error:</b> {error}"
            "</span>"
        )

    finally:
        xbeach_case_selector.disabled = False
        xbeach_shoreline_point_selector.disabled = False


def on_case_change(change):
    if change["name"] == "value":
        update_point_slider()
        render_xbeach_panel()


def on_point_change(change):
    if change["name"] == "value":
        render_xbeach_panel()


xbeach_case_selector.observe(
    on_case_change,
    names="value",
)


xbeach_shoreline_point_selector.observe(
    on_point_change,
    names="value",
)


xbeach_controls = widgets.VBox(
    [
        widgets.HBox(
            [
                xbeach_case_selector,
                xbeach_shoreline_point_selector,
            ],
            layout=widgets.Layout(
                flex_flow="row wrap",
                align_items="center",
                gap="12px",
            ),
        ),

        xbeach_status,
    ],
    layout=widgets.Layout(
        width="100%",
        margin="0 0 8px 0",
    ),
)


flood_map_panel = widgets.VBox(
    [
        xbeach_controls,
        xbeach_output,
    ],
    layout=widgets.Layout(
        width="100%",
    ),
)


display(
    flood_map_panel
)


update_point_slider()
render_xbeach_panel()


# %% [markdown]
# ## Interactive Time Series
#
# The interactive map displays the modelling domain covering the Lisbon Metropolitan Area. Users can click anywhere within the domain to select a location and visualise the corresponding hydrodynamic and wave conditions throughout the available simulation period.
#
# For the selected point, the application simultaneously displays four time series: water level, significant wave height (Hs); peak wave period (Tp); mean wave direction (Dir).
#
# These interactive time series allow users to explore the temporal evolution of the forcing conditions driving coastal flooding and wave overtopping during the analysed event.
#

# %%
def read_hercules_swan_table(path, mohid):
    path = Path(path)

    grid_shape = (
        mohid.sizes["time"],
        mohid.sizes["lat"],
        mohid.sizes["lon"],
    )

    expected_rows = int(np.prod(grid_shape))

    raw = np.loadtxt(
        path,
        usecols=(0, 1, 2),
        dtype=np.float32,
    )

    if raw.ndim == 1:
        raw = raw.reshape(1, -1)

    if raw.shape != (expected_rows, 3):
        raise ValueError(
            f"O ficheiro SWAN tem shape {raw.shape}, "
            f"mas era esperado ({expected_rows}, 3)."
        )

    raw = raw.reshape(*grid_shape, 3)

    return xr.Dataset(
        data_vars={
            "significant_wave_height": (
                ("time", "lat", "lon"),
                np.where(raw[..., 0] <= -8, np.nan, raw[..., 0]),
            ),
            "wave_period": (
                ("time", "lat", "lon"),
                np.where(raw[..., 1] <= -8, np.nan, raw[..., 1]),
            ),
            "mean_wave_direction": (
                ("time", "lat", "lon"),
                np.where(raw[..., 2] <= -8, np.nan, raw[..., 2]),
            ),
        },
        coords={
            "time": mohid.time.values,
            "lat": mohid.lat.values,
            "lon": mohid.lon.values,
        },
    )
    
def build_mohid_swan_explorer(
    mohid,
    swan,
    map_width=700,
    series_width=700,
    figure_height=570,
):
    """
    Build an interactive MOHID/SWAN explorer.

    Parameters
    ----------
    mohid : xarray.Dataset
        Dataset containing:
            ssh(time, lat, lon)

    swan : xarray.Dataset
        Dataset containing:
            significant_wave_height(time, lat, lon)
            wave_period(time, lat, lon)
            mean_wave_direction(time, lat, lon)

    map_width : int
        Plotly map width.

    series_width : int
        Plotly time-series figure width.

    figure_height : int
        Height of both figures.

    Returns
    -------
    ipywidgets.VBox
        Complete interactive application.
    """

    # ============================================================
    # 1. PREPARE DATA
    # ============================================================

    def prepare_data():
        """Extract and validate the MOHID/SWAN arrays."""

        required_mohid = ["ssh"]

        required_swan = [
            "significant_wave_height",
            "wave_period",
            "mean_wave_direction",
        ]

        for variable in required_mohid:
            if variable not in mohid:
                raise KeyError(
                    f"MOHID variable '{variable}' was not found. "
                    f"Available variables: {list(mohid.data_vars)}"
                )

        for variable in required_swan:
            if variable not in swan:
                raise KeyError(
                    f"SWAN variable '{variable}' was not found. "
                    f"Available variables: {list(swan.data_vars)}"
                )

        times = pd.to_datetime(
            mohid.time.values,
            utc=True,
        )

        latitudes = np.asarray(
            mohid.lat.values,
            dtype=float,
        )

        longitudes = np.asarray(
            mohid.lon.values,
            dtype=float,
        )

        if latitudes.ndim != 1 or longitudes.ndim != 1:
            raise ValueError(
                "This implementation expects one-dimensional "
                "latitude and longitude coordinates."
            )

        cubes = {
            "ssh": np.asarray(
                mohid["ssh"]
                .transpose("time", "lat", "lon")
                .values,
                dtype=float,
            ),
            "hs": np.asarray(
                swan["significant_wave_height"]
                .transpose("time", "lat", "lon")
                .values,
                dtype=float,
            ),
            "period": np.asarray(
                swan["wave_period"]
                .transpose("time", "lat", "lon")
                .values,
                dtype=float,
            ),
            "direction": np.asarray(
                swan["mean_wave_direction"]
                .transpose("time", "lat", "lon")
                .values,
                dtype=float,
            ),
        }

        expected_shape = (
            len(times),
            len(latitudes),
            len(longitudes),
        )

        for variable, cube in cubes.items():
            if cube.shape != expected_shape:
                raise ValueError(
                    f"Variable '{variable}' has shape {cube.shape}; "
                    f"expected {expected_shape}."
                )

        common_valid_mask = (
            np.isfinite(cubes["ssh"]).any(axis=0)
            & np.isfinite(cubes["hs"]).any(axis=0)
            & np.isfinite(cubes["period"]).any(axis=0)
            & np.isfinite(cubes["direction"]).any(axis=0)
        )

        if not common_valid_mask.any():
            raise ValueError(
                "No common valid MOHID/SWAN cells were found."
            )

        return (
            times,
            latitudes,
            longitudes,
            cubes,
            common_valid_mask,
        )

    (
        model_times,
        model_lat,
        model_lon,
        data_cubes,
        common_valid_mask,
    ) = prepare_data()

    number_of_times = len(model_times)

    # Configuration for every map variable
    variable_config = {
        "ssh": {
            "label": "Water level",
            "short_label": "SSH",
            "units": "m",
            "colorscale": "Viridis",
            "cube": data_cubes["ssh"],
            "fixed_range": None,
        },
        "hs": {
            "label": "Significant wave height",
            "short_label": "Hs",
            "units": "m",
            "colorscale": "Turbo",
            "cube": data_cubes["hs"],
            "fixed_range": None,
        },
        "period": {
            "label": "Wave period",
            "short_label": "Tp",
            "units": "s",
            "colorscale": "Plasma",
            "cube": data_cubes["period"],
            "fixed_range": None,
        },
        "direction": {
            "label": "Mean wave direction",
            "short_label": "Dir",
            "units": "°",
            "colorscale": "HSV",
            "cube": data_cubes["direction"],
            "fixed_range": (0.0, 360.0),
        },
    }

    # State shared by callbacks
    state = {
        "selected_i": None,
        "selected_j": None,
    }

    # ============================================================
    # 2. AUXILIARY FUNCTIONS
    # ============================================================

    def nearest_valid_cell(target_latitude, target_longitude):
        """Return the common valid cell nearest to the clicked position."""

        latitude_difference = (
            model_lat[:, None] - target_latitude
        )

        longitude_difference = (
            model_lon[None, :] - target_longitude
        ) * np.cos(
            np.deg2rad(target_latitude)
        )

        distance_squared = (
            latitude_difference**2
            + longitude_difference**2
        )

        distance_squared = np.where(
            common_valid_mask,
            distance_squared,
            np.inf,
        )

        if not np.isfinite(distance_squared).any():
            raise ValueError(
                "No valid model cell is available."
            )

        i, j = np.unravel_index(
            np.argmin(distance_squared),
            distance_squared.shape,
        )

        distance_km = (
            np.sqrt(distance_squared[i, j])
            * 111.32
        )

        return int(i), int(j), float(distance_km)

    def find_initial_cell():
        """Select the valid cell nearest to the domain centre."""

        centre_latitude = float(
            (
                np.nanmin(model_lat)
                + np.nanmax(model_lat)
            )
            / 2
        )

        centre_longitude = float(
            (
                np.nanmin(model_lon)
                + np.nanmax(model_lon)
            )
            / 2
        )

        i, j, _ = nearest_valid_cell(
            centre_latitude,
            centre_longitude,
        )

        return i, j

    def get_colour_limits(variable_key):
        """Return robust colour limits for one complete data cube."""

        config = variable_config[variable_key]

        if config["fixed_range"] is not None:
            return config["fixed_range"]

        cube = config["cube"]
        finite_values = cube[np.isfinite(cube)]

        if finite_values.size == 0:
            return 0.0, 1.0

        cmin, cmax = np.nanpercentile(
            finite_values,
            [2, 98],
        )

        if np.isclose(cmin, cmax):
            difference = max(
                abs(float(cmin)) * 0.01,
                0.01,
            )

            cmin -= difference
            cmax += difference

        return float(cmin), float(cmax)

    def get_map_field(variable_key, time_index):
        """Return one spatial field at one model time."""

        field = np.array(
            variable_config[variable_key]["cube"][time_index],
            copy=True,
        )

        field[~common_valid_mask] = np.nan

        return field

    def format_model_time(time_index):
        """Return a readable UTC time label."""

        timestamp = model_times[time_index]

        return timestamp.strftime(
            "%Y-%m-%d %H:%M UTC"
        )

    # ============================================================
    # 3. WIDGETS
    # ============================================================

    parameter_dropdown = widgets.Dropdown(
        options=[
            ("Water level (SSH)", "ssh"),
            ("Significant wave height (Hs)", "hs"),
            ("Wave period (Tp)", "period"),
            ("Mean wave direction", "direction"),
        ],
        value="ssh",
        description="Map parameter:",
        style={
            "description_width": "initial",
        },
        layout=widgets.Layout(
            width="310px",
        ),
    )

    time_slider = widgets.IntSlider(
        value=0,
        min=0,
        max=number_of_times - 1,
        step=1,
        description="Time:",
        continuous_update=True,
        readout=False,
        style={
            "description_width": "45px",
        },
        layout=widgets.Layout(
            width="500px",
        ),
    )

    play_widget = widgets.Play(
        value=0,
        min=0,
        max=number_of_times - 1,
        step=1,
        interval=400,
        description="Play",
        disabled=False,
    )

    widgets.jslink(
        (play_widget, "value"),
        (time_slider, "value"),
    )

    time_label = widgets.HTML()

    selected_point_label = widgets.HTML(
        value=(
            "<div style='"
            "padding:9px 12px;"
            "background:#eef7f7;"
            "border-left:4px solid #00897b;"
            "'>"
            "<b>Selection:</b> click the model map to select a cell."
            "</div>"
        )
    )

    # ============================================================
    # 4. CREATE MAP
    # ============================================================

    def create_map_figure():
        """Create the animated spatial map."""

        variable_key = parameter_dropdown.value
        config = variable_config[variable_key]

        cmin, cmax = get_colour_limits(
            variable_key
        )

        initial_field = get_map_field(
            variable_key,
            time_slider.value,
        )

        figure = go.FigureWidget(
            data=[
                go.Heatmap(
                    x=model_lon,
                    y=model_lat,
                    z=initial_field,
                    colorscale=config["colorscale"],
                    zmin=cmin,
                    zmax=cmax,
                    colorbar={
                        "title": (
                            f"{config['short_label']} "
                            f"({config['units']})"
                        ),
                    },
                    hoverongaps=False,
                    hovertemplate=(
                        "Longitude: %{x:.5f}°<br>"
                        "Latitude: %{y:.5f}°<br>"
                        f"{config['label']}: "
                        f"%{{z:.3f}} {config['units']}"
                        "<extra></extra>"
                    ),
                    name="Model field",
                ),
                go.Scatter(
                    x=[],
                    y=[],
                    mode="markers",
                    name="Selected point",
                    showlegend=False,
                    marker={
                        "size": 15,
                        "color": "#ff1744",
                        "symbol": "x",
                        "line": {
                            "width": 2,
                            "color": "white",
                        },
                    },
                    hovertemplate=(
                        "Selected point<br>"
                        "Longitude: %{x:.5f}°<br>"
                        "Latitude: %{y:.5f}°"
                        "<extra></extra>"
                    ),
                ),
            ]
        )

        mean_latitude = float(
            np.nanmean(model_lat)
        )

        figure.update_layout(
            width=map_width,
            height=figure_height,
            template="plotly_white",
            showlegend=True,
            margin={
                "l": 65,
                "r": 30,
                "t": 85,
                "b": 55,
            },
            uirevision="preserve-map-view",
            xaxis={
                "title": "Longitude (°E)",
                "range": [
                    float(np.nanmin(model_lon)),
                    float(np.nanmax(model_lon)),
                ],
            },
            yaxis={
                "title": "Latitude (°N)",
                "range": [
                    float(np.nanmin(model_lat)),
                    float(np.nanmax(model_lat)),
                ],
                "scaleanchor": "x",
                "scaleratio": (
                    1
                    / np.cos(
                        np.deg2rad(mean_latitude)
                    )
                ),
            },
        )

        return figure

    map_figure = create_map_figure()

    # ============================================================
    # 5. CREATE TIME-SERIES FIGURE
    # ============================================================

    def create_series_figure():
        """Create the four time-series panels."""

        figure = make_subplots(
            rows=4,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.055,
            subplot_titles=[
                "Water level",
                "Significant wave height",
                "Wave period",
                "Mean wave direction",
            ],
        )

        figure.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="lines",
                name="Water level (SSH)",
                line={
                    "color": "#1565c0",
                    "width": 2,
                },
            ),
            row=1,
            col=1,
        )

        figure.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="lines",
                name="Significant wave height (Hs)",
                line={
                    "color": "#00897b",
                    "width": 2,
                },
            ),
            row=2,
            col=1,
        )

        figure.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="lines",
                name="Wave period (Tp)",
                line={
                    "color": "#ef6c00",
                    "width": 2,
                },
            ),
            row=3,
            col=1,
        )

        figure.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="lines",
                name="Mean wave direction",
                line={
                    "color": "#6a1b9a",
                    "width": 2,
                },
            ),
            row=4,
            col=1,
        )

        # Vertical line showing the current animation time
        current_time = model_times[
            time_slider.value
        ]

        figure.add_vline(
            x=current_time,
            line_width=1.5,
            line_dash="dash",
            line_color="#d32f2f",
        )

        figure_widget = go.FigureWidget(
            figure
        )

        figure_widget.update_layout(
            width=series_width,
            height=figure_height,
            template="plotly_white",
            hovermode="x unified",
            showlegend=False,
            margin={
                "l": 75,
                "r": 30,
                "t": 85,
                "b": 55,
            },
        )

        figure_widget.update_yaxes(
            title_text="SSH (m)",
            row=1,
            col=1,
        )

        figure_widget.update_yaxes(
            title_text="Hs (m)",
            row=2,
            col=1,
        )

        figure_widget.update_yaxes(
            title_text="Tp (s)",
            row=3,
            col=1,
        )

        figure_widget.update_yaxes(
            title_text="Dir (°)",
            range=[0, 360],
            dtick=90,
            row=4,
            col=1,
        )

        figure_widget.update_xaxes(
            title_text="Time (UTC)",
            row=4,
            col=1,
        )

        return figure_widget

    series_figure = create_series_figure()

    # ============================================================
    # 6. UPDATE FUNCTIONS
    # ============================================================

    def update_time_label():
        """Update the text displayed beside the animation controls."""

        time_label.value = (
            "<div style='"
            "min-width:180px;"
            "padding:6px 10px;"
            "font-weight:600;"
            "'>"
            f"{format_model_time(time_slider.value)}"
            "</div>"
        )

    def update_map():
        """Update the spatial field, colour scale and map title."""

        variable_key = parameter_dropdown.value
        time_index = time_slider.value

        config = variable_config[
            variable_key
        ]

        field = get_map_field(
            variable_key,
            time_index,
        )

        cmin, cmax = get_colour_limits(
            variable_key
        )

        with map_figure.batch_update():
            heatmap = map_figure.data[0]

            heatmap.z = field
            heatmap.colorscale = config[
                "colorscale"
            ]
            heatmap.zmin = cmin
            heatmap.zmax = cmax

            heatmap.colorbar = {
                "title": (
                    f"{config['short_label']} "
                    f"({config['units']})"
                )
            }

            heatmap.hovertemplate = (
                "Longitude: %{x:.5f}°<br>"
                "Latitude: %{y:.5f}°<br>"
                f"{config['label']}: "
                f"%{{z:.3f}} {config['units']}"
                "<extra></extra>"
            )

            map_figure.layout.title = (
                f"{config['label']} — "
                f"{format_model_time(time_index)}<br>"
                "<sup>Click on the map to select a point "
                "to inspect water level and wave conditions</sup>"
            )

        update_time_label()

    def update_time_indicator():
        """Move the vertical time indicator on all time-series plots."""

        current_time = model_times[
            time_slider.value
        ]

        shapes = []

        for axis_reference in [
            ("x", "y domain"),
            ("x2", "y2 domain"),
            ("x3", "y3 domain"),
            ("x4", "y4 domain"),
        ]:
            x_reference, y_reference = axis_reference

            shapes.append(
                {
                    "type": "line",
                    "x0": current_time,
                    "x1": current_time,
                    "xref": x_reference,
                    "y0": 0,
                    "y1": 1,
                    "yref": y_reference,
                    "line": {
                        "color": "#d32f2f",
                        "width": 1.5,
                        "dash": "dash",
                    },
                }
            )

        series_figure.layout.shapes = tuple(
            shapes
        )

    def update_series(i, j, clicked_lat=None, clicked_lon=None):
        """Update all four series using one selected model cell."""

        i = int(i)
        j = int(j)

        state["selected_i"] = i
        state["selected_j"] = j

        latitude = float(
            model_lat[i]
        )

        longitude = float(
            model_lon[j]
        )

        with series_figure.batch_update():
            series_figure.data[0].x = model_times
            series_figure.data[0].y = (
                data_cubes["ssh"][:, i, j]
            )

            series_figure.data[1].x = model_times
            series_figure.data[1].y = (
                data_cubes["hs"][:, i, j]
            )

            series_figure.data[2].x = model_times
            series_figure.data[2].y = (
                data_cubes["period"][:, i, j]
            )

            series_figure.data[3].x = model_times
            series_figure.data[3].y = (
                data_cubes["direction"][:, i, j]
            )

            series_figure.layout.title = (
                "Time series at the selected point<br>"
                f"<sup>{latitude:.5f}°N, "
                f"{longitude:.5f}°E · "
                f"i={i}, j={j}</sup>"
            )

        with map_figure.batch_update():
            map_figure.data[1].x = [
                longitude
            ]
            map_figure.data[1].y = [
                latitude
            ]

        information = (
            "<div style='"
            "padding:9px 12px;"
            "background:#eef7f7;"
            "border-left:4px solid #00897b;"
            "'>"
            f"<b>Selected point:</b> "
            f"{latitude:.5f}°N, "
            f"{longitude:.5f}°E "
            # f"[i={i}, j={j}]"
        )

        if clicked_lat is not None:
            _, _, distance_km = nearest_valid_cell(
                clicked_lat,
                clicked_lon,
            )

            information += (
                "<br>"
                # f"<b>Distance between map click and selected point:</b> "
                # f"{distance_km:.2f} km"
            )

        information += "</div>"

        selected_point_label.value = information

    # ============================================================
    # 7. CALLBACKS
    # ============================================================

    def map_clicked(trace, points, selector):
        """Handle a click on the spatial heatmap."""

        if not points.xs or not points.ys:
            return

        clicked_longitude = float(
            points.xs[0]
        )

        clicked_latitude = float(
            points.ys[0]
        )

        i, j, _ = nearest_valid_cell(
            clicked_latitude,
            clicked_longitude,
        )

        update_series(
            i,
            j,
            clicked_lat=clicked_latitude,
            clicked_lon=clicked_longitude,
        )

    def parameter_changed(change):
        """Update the map when the dropdown selection changes."""

        if change["name"] == "value":
            update_map()

    def time_changed(change):
        """Update map and time indicator during animation."""

        if change["name"] == "value":
            update_map()
            update_time_indicator()

    map_figure.data[0].on_click(
        map_clicked
    )

    parameter_dropdown.observe(
        parameter_changed,
        names="value",
    )

    time_slider.observe(
        time_changed,
        names="value",
    )

    # ============================================================
    # 8. INITIALISE
    # ============================================================

    initial_i, initial_j = (
        find_initial_cell()
    )

    update_map()
    update_series(
        initial_i,
        initial_j,
    )
    update_time_indicator()

    # ============================================================
    # 9. LAYOUT
    # ============================================================

    # header = widgets.HTML(
    #     value=f"""
    #     <div style="
    #         background:#07545c;
    #         color:white;
    #         padding:16px 20px;
    #         border-radius:10px 10px 0 0;
    #     ">

    #         <div style="
    #             margin-top:5px;
    #             font-size:14px;
    #         ">
    #             Select a model parameter and click on the map to inspect water level and waves conditions.
    #         </div>

    #         <div style="
    #             margin-top:7px;
    #             font-size:12px;
    #             opacity:0.85;
    #         ">
    #             Common valid cells:
    #             {int(common_valid_mask.sum()):,}
    #         </div>
    #     </div>
    #     """
    # )

    top_controls = widgets.HBox(
        [
            parameter_dropdown,
            selected_point_label,
        ],
        layout=widgets.Layout(
            width="100%",
            flex_flow="row wrap",
            align_items="center",
            gap="14px",
            padding="10px 14px",
            border="1px solid #d9e2e6",
        ),
    )

    map_output = widgets.Output(
        layout=widgets.Layout(
            width=f"{map_width + 10}px",
        )
    )

    series_output = widgets.Output(
        layout=widgets.Layout(
            width=f"{series_width + 10}px",
        )
    )

    with map_output:
        display(map_figure)

    with series_output:
        display(series_figure)

    animation_controls = widgets.HBox(
        [
            play_widget,
            time_slider,
            time_label,
        ],
        layout=widgets.Layout(
            width="100%",
            align_items="center",
            justify_content="center",
            flex_flow="row wrap",
            gap="8px",
        ),
    )

    map_panel = widgets.VBox(
        [
            map_output,
            animation_controls,
        ],
        layout=widgets.Layout(
            width=f"{map_width + 20}px",
            align_items="center",
        ),
    )

    series_panel = widgets.VBox(
        [
            series_output,
        ],
        layout=widgets.Layout(
            width=f"{series_width + 20}px",
        ),
    )

    main_panel = widgets.HBox(
        [
            map_panel,
            series_panel,
        ],
        layout=widgets.Layout(
            width="100%",
            flex_flow="row wrap",
            align_items="flex-start",
            justify_content="center",
            gap="8px",
        ),
    )

    application = widgets.VBox(
        [
            top_controls,
            main_panel,
        ],
        layout=widgets.Layout(
            width="100%",
        ),
    )

    return application

real_mohid = xr.open_dataset(
    HERCULES_FILES["MOHID"]
)

real_swan = read_hercules_swan_table(
    Path(HERCULES_FILES["SWAN"]),
    real_mohid,
)

explorer_panel = build_mohid_swan_explorer(
    real_mohid,
    real_swan,
    map_width=680,
    series_width=680,
    figure_height=590,
)

display(explorer_panel)

# %% [markdown]
# <!-- ### Validation -->

# %% [markdown]
# ## HOW
#
# ### Technical Description
#
# The demonstrator implements a multi-scale coastal forecasting workflow designed to improve storm surge, extreme water level, overtopping, and flooding forecasts in the Tagus Estuary and adjacent coastal areas. The workflow integrates hydrodynamic, wave, and coastal impact models to provide both national-scale and local-scale forecasts supporting coastal risk assessment and decision-making.
#
# MOHID Water (Campuzano, 2018) and WaveWatch III (WW3DG, 2019) provide the national forcing. Tier 1 converts site time series into a rapid first layer overtopping forecasting indicator. Tier 2 uses the coastal model XBeach (Roelvink, 2009) to predict coastal overtopping and flooding. XBeach model is feeded by MOHID Water and SWAN (Booij, 1996) models, coupled, for the Lisbon Metropolitan Area, both with a spatial resolution of 280 metres. The main variables considered in the forecasts include total water level, wave height and period.
#
# ### Integration within FOCCUS WP
#
# <div style="background:white;padding:14px;border:1px solid #d9e2e6;border-radius:8px;text-align:center">
#   <img src="Images/WP_Integration.png" alt="Integration flowchart within the FOCCUS work packages" style="width:min(80%,980px);height:auto">
# </div>

# %% [markdown] tags=["how", "pdf"]
# ### Schematic workflow

# %% hide_input=true jupyter={"source_hidden": true} tags=["hide-input", "remove-input", "pdf"]
workflow_pdf_path = Path("Images") / "DF323.pdf"
workflow_pdf_b64 = base64.b64encode(workflow_pdf_path.read_bytes()).decode("ascii")
workflow_pdf_html = HTML(
    f"""<div style='border:1px solid #d9e2e6;border-radius:8px;overflow:hidden;background:white'>
    <object data='data:application/pdf;base64,{workflow_pdf_b64}' type='application/pdf' width='100%' height='680px'>
      <div style='padding:18px'>PDF preview is unavailable in this renderer.
      <a href='{workflow_pdf_path.as_posix()}' target='_blank'>Open DF323.pdf</a>.</div>
    </object></div>"""
)
workflow_pdf_output = widgets.Output()
workflow_pdf_button = widgets.Button(
    description="Reload workflow PDF", icon="file-pdf-o",
    layout=widgets.Layout(width="235px"),
)

def render_workflow_pdf(_=None):
    with workflow_pdf_output:
        clear_output(wait=True)
        display(workflow_pdf_html)

workflow_pdf_button.on_click(render_workflow_pdf)
display(widgets.VBox([workflow_pdf_button, workflow_pdf_output]))
display(workflow_pdf_html)

# %% [markdown]
# ### Conclusions
#
# This demonstrator illustrates how a multi-scale modelling chain
# can support coastal impact forecasting from the regional to the
# local scale.
#
# The workflow integrates hydrodynamic, wave and coastal impact
# models to produce operational products for MSCS operators,
# supporting preparedness and climate adaptation.
#
# ### References
#
# Booij, N., Holthuijsen, L.H. and R.C. Ris, 1996. ‘The SWAN wave model for shallow water’, Proc. 25th Int. Conf. Coastal Engng., Orlando, USA, Vol. 1, pp. 668-676.
#
# Campuzano, F., 2018. ‘Coupling watersheds, estuaries and regional seas through numerical modelling for Western Iberia’, [PhD Thesis]. Universidade de Lisboa.
#
# Roelvink, J.A., Reniers, A.J.H.M., van Dongeren, A.R., van Thiel de Vries, J.S.M., McCall, R.T., Lescinski, J., 2009. ‘Modelling storm impacts on beaches, dunes and barrier islands’, Coastal Engineering, 56(11-12):1133–1152, November 2009. https://doi.org/10.1016/j.coastaleng.2009.08.006
#
# Stockdon, H. F., Long, J. W., Palmsten, M. L., Van der Westhuysen, A., Doran, K. S., & Snell, R. J., 2023. ‘Operational forecasts of wave-driven water levels and coastal hazards for US Gulf and Atlantic coasts’, Communications Earth & Environment, 4(1), 169. https://doi.org/10.1038/s43247-023-00817-2
#
# Turner, I. L., Leaman, C. K., Harley, M. D., Thran, M. C., David, D. R., Splinter, K. D., Matheen, N., Hansen, J. E., Cuttler, M. V. W., Greenslade, D. J. M., Zieger, S., & Lowe, R. J., 2024. ‘A framework for national-scale coastal storm hazards early warning’, Coastal Engineering, 192, 104571. https://doi.org/10.1016/j.coastaleng.2024.104571
#
# WW3DG, T., 2019. ‘User manual and system documentation of Wavewatch III version 6’,07. NOAA NWS NCEP MMAB Tech Note, 333, 465.
