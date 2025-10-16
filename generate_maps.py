#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_maps.py  (dataset-aware defaults + GeoJSON key auto-detect)
--------------------------------------------------------------------
Genera mapas con tus archivos:
- /mnt/data/outputs/trends_geo_full.csv
- /mnt/data/outputs/trends_geo_latest.csv
- /mnt/data/geo_countries.geojson (opcional; autodetecta llave)

Salidas en /mnt/data/outputs:
- map_latest.html
- map_animated.html
"""
import argparse
import os
import json
import pandas as pd

DEFAULT_FULL = "/mnt/data/outputs/trends_geo_full.csv"
DEFAULT_LATEST = "/mnt/data/outputs/trends_geo_latest.csv"
DEFAULT_GEOJSON = "/mnt/data/geo_countries.geojson"
DEFAULT_OUT_MAP = "/mnt/data/outputs/map_latest.html"
DEFAULT_OUT_ANIM = "/mnt/data/outputs/map_animated.html"

CANDIDATE_KEYS = ["ADM0_A3", "ISO_A3", "WB_A3", "ADM0_A3_US", "ADM0_A3_UN", "SOV_A3"]

def _detect_feature_key(geojson_obj, iso3_codes):
    """Devuelve (best_key, overlap_count). iso3_codes debe venir en mayúsculas."""
    best_key, best_overlap = None, -1
    for k in CANDIDATE_KEYS:
        try:
            gj_codes = set()
            for feat in geojson_obj.get("features", []):
                v = feat.get("properties", {}).get(k)
                if v is None:
                    continue
                code = str(v).upper()
                if code in {"-99", ""}:
                    continue
                gj_codes.add(code)
            overlap = len(iso3_codes & gj_codes)
            if overlap > best_overlap:
                best_key, best_overlap = k, overlap
        except Exception:
            continue
    return best_key, best_overlap

def _value_column(df, prefer="interest"):
    if prefer in df.columns:
        return prefer
    # toma la última que no sea típica de id/fecha/geo
    candidates = [c for c in df.columns if c.lower() not in {"iso3", "country", "date", "date_str"}]
    if not candidates:
        raise ValueError("No se pudo detectar columna de valor para colorear el mapa.")
    return candidates[-1]

def main():
    ap = argparse.ArgumentParser(description="Genera mapas coropléticos (estático y animado) desde archivos limpios.")
    ap.add_argument("--full", default=DEFAULT_FULL, help="CSV full con columnas [date, iso3, interest].")
    ap.add_argument("--latest", default=DEFAULT_LATEST, help="CSV último corte [iso3, interest].")
    ap.add_argument("--geojson", default=DEFAULT_GEOJSON, help="GeoJSON opcional (propiedad ISO de país variable).")
    ap.add_argument("--out-map", default=DEFAULT_OUT_MAP, help="Salida HTML del mapa estático.")
    ap.add_argument("--out-anim", default=DEFAULT_OUT_ANIM, help="Salida HTML del mapa animado.")
    ap.add_argument("--color-scale", default="Plasma")
    args = ap.parse_args()

    import plotly.express as px

    # ----- Mapa estático (último corte)
    latest = pd.read_csv(args.latest)
    if "iso3" not in latest.columns:
        raise ValueError("Se espera columna 'iso3' en latest.")
    latest["iso3"] = latest["iso3"].astype(str).str.upper()
    valcol = _value_column(latest, "interest")

    fig = None
    used_key = None
    if os.path.exists(args.geojson):
        with open(args.geojson, "r", encoding="utf-8") as f:
            gj = json.load(f)
        best_key, overlap = _detect_feature_key(gj, set(latest["iso3"].unique()))
        if best_key and overlap > 0:
            used_key = best_key
            fig = px.choropleth(
                latest,
                geojson=gj,
                locations="iso3",
                featureidkey=f"properties.{best_key}",
                color=valcol,
                color_continuous_scale=args.color_scale,
                title=f"Mapa (último corte) usando GeoJSON [{best_key}]"
            )
            fig.update_geos(fitbounds="locations", visible=False)

    if fig is None:
        # Fallback sin GeoJSON
        fig = px.choropleth(
            latest,
            locations="iso3",
            color=valcol,
            locationmode="ISO-3",
            color_continuous_scale=args.color_scale,
            title="Mapa (último corte)"
        )
        fig.update_geos(showcountries=True, showcoastlines=True, projection_type="natural earth")

    os.makedirs(os.path.dirname(args.out_map), exist_ok=True)
    fig.write_html(args.out_map, include_plotlyjs="cdn")

    # ----- Mapa animado (si hay fecha en full)
    full = pd.read_csv(args.full)
    if "date" not in full.columns:
        print("⚠️ No hay 'date' en full; no se generará mapa animado.")
        print(f"✅ Mapa estático guardado en: {args.out_map}")
        return

    full["iso3"] = full["iso3"].astype(str).str.upper()
    full["date"] = pd.to_datetime(full["date"], errors="coerce")
    full["date_str"] = full["date"].dt.strftime("%Y-%m-%d")
    valcol2 = _value_column(full, "interest")

    fig2 = None
    if os.path.exists(args.geojson) and used_key:
        # Si funcionó la llave en el estático, reutilízala
        with open(args.geojson, "r", encoding="utf-8") as f:
            gj = json.load(f)
        fig2 = px.choropleth(
            full,
            geojson=gj,
            locations="iso3",
            featureidkey=f"properties.{used_key}",
            color=valcol2,
            animation_frame="date_str",
            color_continuous_scale=args.color_scale,
            title=f"Mapa animado (GeoJSON) [{used_key}]"
        )
        fig2.update_geos(fitbounds="locations", visible=False)
    else:
        # Fallback animado sin GeoJSON
        fig2 = px.choropleth(
            full,
            locations="iso3",
            color=valcol2,
            animation_frame="date_str",
            locationmode="ISO-3",
            color_continuous_scale=args.color_scale,
            title="Mapa animado"
        )
        fig2.update_geos(showcountries=True, showcoastlines=True, projection_type="natural earth")

    fig2.write_html(args.out_anim, include_plotlyjs="cdn")
    print(f"✅ Mapas guardados en: {args.out_map}, {args.out_anim}")

if __name__ == "__main__":
    main()
