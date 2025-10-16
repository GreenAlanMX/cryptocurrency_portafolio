#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_geographic_data.py  (dataset-aware defaults)
--------------------------------------------------
Usa directamente tus archivos subidos para preparar datos geográficos:
- /mnt/data/trends_enriched.csv
- /mnt/data/country_mapping.csv   (opcional, para completar ISO-3)
- /mnt/data/geo_countries.csv     (opcional, validación)

Genera:
- /mnt/data/outputs/trends_geo_full.csv        (date, iso3, interest)
- /mnt/data/outputs/trends_geo_latest.csv      (último corte por iso3)

CLI opcional para rutas personalizadas.
"""
import argparse
import os
import pandas as pd

DEFAULT_TRENDS = "analyst/trends_enriched.csv"
DEFAULT_MAP = "analyst/country_mapping.csv"
DEFAULT_OUT_FULL = "analyst/outputs/trends_geo_full.csv"
DEFAULT_OUT_LATEST = "analyst/outputs/trends_geo_latest.csv"


def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def normalize_iso3(trends: pd.DataFrame, mapping_path: str|None) -> pd.DataFrame:
    df = trends.copy()
    # Si ya hay iso3, la respetamos; si falta, intentamos mapear por country_code o name
    if "iso3" not in df.columns or df["iso3"].isna().any():
        if mapping_path and os.path.exists(mapping_path):
            mapdf = pd.read_csv(mapping_path)
            # intentamos por country_code
            if "country_code" in df.columns and "country_code" in mapdf.columns:
                df = df.merge(mapdf[["country_code","iso3"]].drop_duplicates(), on="country_code", how="left", suffixes=("","_m"))
                df["iso3"] = df["iso3"].fillna(df.pop("iso3_m"))
            # intentamos por name
            if ("name" in df.columns) and ("name" in mapdf.columns):
                df = df.merge(mapdf[["name","iso3"]].drop_duplicates(), on="name", how="left", suffixes=("","_m2"))
                df["iso3"] = df["iso3"].fillna(df.pop("iso3_m2"))
        # drop si aún faltan
        df = df[~df["iso3"].isna()].copy()
    return df

def main():
    ap = argparse.ArgumentParser(description="Limpia/normaliza datos geográficos (ISO-3) y genera cortes full/latest.")
    ap.add_argument("--trends", default=DEFAULT_TRENDS, help="CSV de interés por país y fecha (default: trends_enriched.csv).")
    ap.add_argument("--mapping", default=DEFAULT_MAP, help="CSV con mapping country_code/name a iso3 (opcional).")
    ap.add_argument("--out-full", default=DEFAULT_OUT_FULL, help="Salida full (para mapa animado).")
    ap.add_argument("--out-latest", default=DEFAULT_OUT_LATEST, help="Salida último corte (para mapa estático).")
    args = ap.parse_args()

    trends = load_csv(args.trends)
    # columnas mínimas
    for c in ["date","interest"]:
        if c not in trends.columns:
            raise ValueError(f"Columna requerida '{c}' no encontrada en {args.trends}.")

    df = normalize_iso3(trends, args.mapping)
    keep = [c for c in ["date","iso3","country","interest"] if c in df.columns]
    df = df[keep].copy()
    # full
    os.makedirs(os.path.dirname(args.out_full), exist_ok=True)
    df.to_csv(args.out_full, index=False, encoding="utf-8")
    # latest
    d = pd.to_datetime(df["date"], errors="coerce")
    latest_date = d.max()
    latest = df[d == latest_date].copy()
    latest.to_csv(args.out_latest, index=False, encoding="utf-8")

    print(f"✅ Full: {args.out_full} ({len(df)} filas)")
    print(f"✅ Latest ({latest_date.date()}): {args.out_latest} ({len(latest)} filas)")

if __name__ == "__main__":
    main()
