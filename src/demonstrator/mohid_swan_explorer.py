from pathlib import Path

import ipywidgets as widgets
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import xarray as xr
from IPython.display import display
from plotly.subplots import make_subplots


def read_mohid_files(path):
    path = Path(path)

    paths = sorted(path.parent.glob(path.name))

    if not paths:
        raise FileNotFoundError(f"Nenhum ficheiro MOHID *.nc encontrado em {path}.")

    datasets = [xr.open_dataset(p) for p in paths]

    mohid = xr.concat(datasets, dim="time")

    mohid = mohid.sortby("time")

    _, unique_idx = np.unique(mohid["time"], return_index=True)
    mohid = mohid.isel(time=unique_idx[:-1])

    return mohid

def read_swan_table_files(path, ssh_ds=None):
    path = Path(path)

    paths = sorted(path.parent.glob(path.name))

    if not paths:
        raise FileNotFoundError(f"Nenhum ficheiro SWAN *.tbl encontrado em {path}.")


    grid_shape = (ssh_ds.sizes["time"], ssh_ds.sizes["lat"], ssh_ds.sizes["lon"]) # in case ssh matches swan grid
    #grid_shape = (int(24*7), 285, 355)  # assuming 7 days of hourly data, 285 lat points, and matching lon points

    expected_rows = int(np.prod(grid_shape))

    raw = np.concatenate(
        [np.loadtxt(p, usecols=(0, 1, 2), dtype=np.float32).reshape(-1, 3)[:-int( ssh_ds.sizes["lat"] * ssh_ds.sizes["lon"]),:] for p in paths],
        axis=0,
    )

    # raw = np.concatenate(
    #     [np.loadtxt(p, usecols=(0, 1, 2), dtype=np.float32).reshape(-1, 3) for p in paths],
    #     axis=0,
    # )

    if raw.shape != (expected_rows, 3):
        raise ValueError(
            f"O ficheiro SWAN tem shape {raw.shape}, "
            f"mas era esperado ({expected_rows}, 3)."
        )

    raw = raw.reshape(*grid_shape, 3)

    time = np.datetime64("2014-01-01T00:00:00") + np.arange(grid_shape[0]) * np.timedelta64(1, "h")

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
            "time": time,
            "lat": ssh_ds.lat.values,
            "lon": ssh_ds.lon.values,
        },
    )


def read_ibi_files(path):
    path = Path(path)

    paths = sorted(path.parent.glob(path.name))

    if not paths:
        raise FileNotFoundError(f"Nenhum ficheiro IBI *.nc encontrado em {path}.")

    datasets = [xr.open_dataset(p) for p in paths]
    

    ibi = xr.concat(datasets, dim="time")

    ibi = ibi.sortby("time")

    return ibi


def build_mohid_swan_explorer(mohid,swan, map_width=700,series_width=700,figure_height=570):
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

        times = pd.to_datetime(mohid.time.values,utc=True)
        latitudes = np.asarray(mohid.lat.values,dtype=float)
        longitudes = np.asarray(mohid.lon.values,dtype=float)

        if latitudes.ndim != 1 or longitudes.ndim != 1:
            raise ValueError(
                "This implementation expects one-dimensional "
                "latitude and longitude coordinates."
            )

        cubes = {
            "ssh": np.asarray(
                mohid["ssh"].transpose("time", "lat", "lon").values,
                dtype=float,
            ),
            "hs": np.asarray(
                swan["significant_wave_height"].transpose("time", "lat", "lon").values,
                dtype=float,
            ),
            "period": np.asarray(
                swan["wave_period"].transpose("time", "lat", "lon").values,
                dtype=float,
            ),
            "direction": np.asarray(
                swan["mean_wave_direction"].transpose("time", "lat", "lon").values,
                dtype=float,
            ),
        }

        expected_shape = (len(times),len(latitudes),len(longitudes))

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

        return times,latitudes,longitudes,cubes,common_valid_mask

    model_times,model_lat,model_lon,data_cubes,common_valid_mask = prepare_data()
    number_of_times = len(model_times)

    # Configuration for every map variable
    variable_config = {
        "ssh": {
            "label": "Water level",
            "short_label": "SSH",
            "units": "m",
            "colorscale": "Viridis_r",
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

        latitude_difference = (model_lat[:, None] - target_latitude)

        longitude_difference = (model_lon[None, :] - target_longitude) * \
                                np.cos(np.deg2rad(target_latitude))

        distance_squared = (latitude_difference**2 + longitude_difference**2)

        distance_squared = np.where(common_valid_mask,distance_squared,np.inf,)

        if not np.isfinite(distance_squared).any():
            raise ValueError("No valid model cell is available.")

        i, j = np.unravel_index(np.argmin(distance_squared),distance_squared.shape)

        distance_km = (np.sqrt(distance_squared[i, j]) * 111.32)

        return int(i), int(j), float(distance_km)

    def find_initial_cell():
        """Select the valid cell nearest to the domain centre."""

        centre_latitude = float((np.nanmin(model_lat) + np.nanmax(model_lat))/ 2)
        centre_longitude = float((np.nanmin(model_lon) + np.nanmax(model_lon))/ 2)
        i, j, _ = nearest_valid_cell(centre_latitude,centre_longitude)

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

        cmin, cmax = np.nanpercentile(finite_values,[2, 98],)

        if np.isclose(cmin, cmax):
            difference = max(abs(float(cmin)) * 0.01,0.01)
            cmin -= difference
            cmax += difference

        return float(cmin), float(cmax)

    def get_map_field(variable_key, time_index):
        """Return one spatial field at one model time."""

        field = np.array(
            variable_config[variable_key]["cube"][time_index],
            copy=True,
        )

        field[~common_valid_mask] = None

        return field

    def format_model_time(time_index):
        """Return a readable UTC time label."""

        timestamp = model_times[time_index]

        return timestamp.strftime("%Y-%m-%d %H:%M UTC")

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
        style={"description_width": "45px"},
        layout=widgets.Layout(width="500px"))

    play_widget = widgets.Play(
        value=0,
        min=0,
        max=number_of_times - 1,
        step=1,
        interval=400,
        description="Play",
        disabled=False)

    widgets.jslink((play_widget, "value"),(time_slider, "value"))

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
                            f"[{config['units']}]"
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
                        "color": "#850720",
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
            font={
                "family": "Helvetica",
                },
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
                "title": "Longitude [°E]",
                "range": [
                    float(np.nanmin(model_lon)),
                    float(np.nanmax(model_lon)),
                ],
            },
            yaxis={
                "title": "Latitude [°N]",
                "range": [
                    float(np.nanmin(model_lat)),
                    float(np.nanmax(model_lat)),
                ],
                "scaleanchor": "x",
                "scaleratio": (1/np.cos(np.deg2rad(mean_latitude)))
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
            vertical_spacing=0.06,
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
                name="SSH [m]",
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
                name="Hs [m]",
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
                name="Tp [s]",
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
                mode="markers",
                name="Dir [°]",
                marker={
                    "symbol": "arrow",
                    "size": 8,
                    "angle": [],
                    "angleref": "up",
                    "color": "#790FBB",
                    "line": {
                        "color": "#790FBB",
                        "width": 1,
                    },
                },
            ),
            row=4,
            col=1,
        )

        # Vertical line showing the current animation time
        current_time = model_times[time_slider.value]

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
            font={
                "family": "Helvetica",
                },
            template="plotly_white",
            hovermode="x unified",
            hoverlabel={
                "font": {
                    "family": "Helvetica",
                    "size": 13,        # bump this up — larger font = larger box
                },
                "namelength": -1,       # -1 = don't truncate trace names at all
                "bgcolor": "white",
                "bordercolor": "#1a181a",
                "align": "left",
            },
            showlegend=False,
            margin={
                "l": 75,
                "r": 30,
                "t": 85,
                "b": 55,
            },
        )

        figure_widget.update_yaxes(
            title_text="SSH [m]",
            row=1,
            col=1,
        )

        figure_widget.update_yaxes(
            title_text="Hs [m]",
            row=2,
            col=1,
        )

        figure_widget.update_yaxes(
            title_text="Tp [s]",
            row=3,
            col=1,
        )

        figure_widget.update_yaxes(
            title_text="Dir [°]",
            range=[0, 360],
            dtick=90,
            row=4,
            col=1,
        )

        figure_widget.update_xaxes(
            title_text="Time [UTC]",
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
                    f"[{config['units']}]"
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

        #update_time_label()

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

            direction_values = data_cubes["direction"][:, i, j]

            series_figure.data[3].x = model_times
            series_figure.data[3].y = direction_values
            series_figure.data[3].marker.angle = (direction_values + 180) % 360

            series_figure.layout.title = (
                "Time series at the selected point<br>"
                f"<sup>{latitude:.5f}°N, "
                f"{longitude:.5f}°E "
                #f"i={i}, j={j}</sup>"
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
