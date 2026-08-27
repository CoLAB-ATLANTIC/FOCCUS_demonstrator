from pathlib import Path

import folium
import numpy as np
import pandas as pd
import xarray as xr
from folium import FeatureGroup
from folium.plugins import Fullscreen, MeasureControl, MousePosition

def load_tier1_event_summary(path: Path):
    with xr.open_dataset(path) as dataset:
        regime = np.asarray(dataset["Regime"].values, dtype=int)
        peak_step = np.argmax(regime, axis=0)
        max_regime = np.max(regime, axis=0)
        take_peak = lambda name: np.take_along_axis(
            np.asarray(dataset[name].values), peak_step[None, :], axis=0
        )[0]
        summary = pd.DataFrame({
            "id": dataset["id"].values.astype(str),
            "name": dataset["Name"].values.astype(str),
            "lat": np.asarray(dataset["Latitude"].values, dtype=float),
            "lon": np.asarray(dataset["Longitude"].values, dtype=float),
            "hazard_index": max_regime,
            "peak_time": pd.to_datetime(dataset["time"].values[peak_step], utc=True),
            "wave_height_m": take_peak("significant_wave_height"),
            "water_level_m": take_peak("water_level"),
            "total_water_level_m": take_peak("TWL"),
        })
    return summary


def make_study_area_map(regional_domain, site_config, tier1_path, hazard_classes):
    tier1 = load_tier1_event_summary(tier1_path)
    fmap = folium.Map(location=[39.45, -8.75], zoom_start=7, tiles=None, control_scale=True)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap", show=True).add_to(fmap)
    folium.TileLayer(
        tiles=("https://server.arcgisonline.com/ArcGIS/rest/services/"
               "World_Imagery/MapServer/tile/{z}/{y}/{x}"),
        attr="Esri World Imagery", name="Satellite imagery", show=False,
    ).add_to(fmap)

    tier1_layer = FeatureGroup(name="Tier 1: Flooding Hazard Index", show=True)
    for point in tier1.itertuples(index=False):
        hazard = hazard_classes.get(int(point.hazard_index), hazard_classes[0])
        point_name = point.name if point.name and point.name != "nan" else point.id
        popup = (
            f"<div style='font-family:Arial;min-width:250px'><b>{point_name}</b> ({point.id})<br>"
            f"Hazard index: <b style='color:{hazard['color']}'>{point.hazard_index} — {hazard['name']}</b><br>"
            f"{hazard['meaning']}<br><hr style='margin:6px 0'>"
            f"Critical time: {point.peak_time:%Y-%m-%d %H:%M UTC}<br>"
            f"Wave height: {point.wave_height_m:.2f} m<br>"
            f"Water level: {point.water_level_m:.2f} m<br>"
            f"Total water level: {point.total_water_level_m:.2f} m</div>"
        )
        folium.CircleMarker(
            location=[point.lat, point.lon], radius=4.5,
            color="white", weight=0.8, fill=True, fill_color=hazard["color"], fill_opacity=0.92,
            tooltip=f"{point.id}: {point.hazard_index} — {hazard['name']}",
            popup=folium.Popup(popup, max_width=360),
        ).add_to(tier1_layer)
    tier1_layer.add_to(fmap)

    regional_layer = FeatureGroup(name="Lisbon Metropolitan Area domain", show=True)
    folium.Rectangle(
        bounds=regional_domain["bounds"], tooltip=regional_domain["name"],
        color="#37474f", weight=3, fill=True, fill_opacity=0.05,
    ).add_to(regional_layer)
    regional_layer.add_to(fmap)

    for site_id, cfg in site_config.items():
        layer = FeatureGroup(name=f"Tier 2: {cfg['name']} domain", show=True)
        popup = (f"<b>{cfg['name']}</b><br>Municipality: {cfg['municipality']}<br>"
                 f"{cfg['setting']}<br><i>Approximate demonstrator coordinates</i>")
        folium.Rectangle(
            bounds=cfg["bounds"], tooltip=f"Local domain: {cfg['name']}",
            color=cfg["color"], weight=3, fill=True, fill_color=cfg["color"],
            fill_opacity=0.15, popup=folium.Popup(popup, max_width=360),
        ).add_to(layer)
        folium.CircleMarker(
            location=[cfg["lat"], cfg["lon"]], radius=7, color=cfg["color"],
            fill=True, fill_opacity=1, tooltip=f"Tier 2 — {cfg['name']}",
            popup=folium.Popup(popup, max_width=360),
        ).add_to(layer)
        layer.add_to(fmap)

    legend_items = "".join(
        f"<div><span style='display:inline-block;width:11px;height:11px;border-radius:50%;"
        f"background:{hazard_classes[value]['color']};margin-right:6px'></span>"
        f"<b>{value} — {hazard_classes[value]['name']}</b>: "
        # f"{hazard_classes[value]['meaning']}</div>" for value in [1, 2, 3, 4]
        f"{hazard_classes[value]['meaning']}</div>" for value in [1, 2, 3]

    )
    legend = (
        "<div style='position:fixed;bottom:28px;left:28px;z-index:9999;background:white;"
        "padding:11px 14px;border:1px solid #777;border-radius:6px;font-size:12px;max-width:370px'>"
        #"<b>Flooding Hazard Index</b>"
        "<b>Flooding Hazard Index</b><br><span style='color:#555'>Maximum over 3 February 2026 (24 h)</span>"
        + legend_items + "</div>"\
    )
    fmap.get_root().html.add_child(folium.Element(legend))
    Fullscreen(position="topright").add_to(fmap)
    MeasureControl(position="topleft", primary_length_unit="kilometers").add_to(fmap)
    MousePosition(position="bottomright", prefix="Coordinates:", num_digits=5).add_to(fmap)
    folium.LayerControl(collapsed=False).add_to(fmap)
    fmap.fit_bounds([[float(tier1.lat.min()), float(tier1.lon.min())],
                     [float(tier1.lat.max()), float(tier1.lon.max())]])
    return fmap
