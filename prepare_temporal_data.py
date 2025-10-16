#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_temporal_data.py  (dataset-aware defaults)
--------------------------------------------------
Usa directamente tus archivos subidos para crear los insumos temporales:
- /mnt/data/prices_with_metrics.csv
- /mnt/data/trends_enriched.csv

Genera en /mnt/data/outputs:
- processed_prices.csv
- processed_interest_global.csv
- interest_by_country.csv
- spatiotemporal_merged.csv

Notas:
- Si ya existen columnas returns/volatilidad en precios, se conservan.
- global_interest = media diaria del interés por país.
"""
import argparse
import os
import pandas as pd
import numpy as np

DEFAULT_PRICES = "/mnt/data/prices_with_metrics.csv"
DEFAULT_TRENDS = "/mnt/data/trends_enriched.csv"
DEFAULT_OUT_DIR = "/mnt/data/outputs"
DEFAULT_VOL_WINDOW = 7

def main():
    ap = argparse.ArgumentParser(description="Prepara datos temporales (precios, interés global, merge) usando tus CSV.")
    ap.add_argument("--prices", default=DEFAULT_PRICES, help="Precios con métricas (default: prices_with_metrics.csv).")
    ap.add_argument("--trends", default=DEFAULT_TRENDS, help="Trends enriquecido (default: trends_enriched.csv).")
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Directorio de salida (default: /mnt/data/outputs).")
    ap.add_argument("--vol-window", type=int, default=DEFAULT_VOL_WINDOW, help="Ventana de volatilidad si hay que recalcular.")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # ---- precios
    prices = pd.read_csv(args.prices)
    # detectar columnas típicas
    dcol = "Date" if "Date" in prices.columns else "date"
    cclose = "Close" if "Close" in prices.columns else "close"
    # si faltan retornos/vol, crearlos
    if "returns" not in prices.columns:
        prices = prices.sort_values(dcol)
        prices["returns"] = prices[cclose].pct_change()
    if not any(c.startswith("volatility_") for c in prices.columns):
        prices[f"volatility_{args.vol_window}d"] = prices["returns"].rolling(args.vol_window).std()

    prices.to_csv(os.path.join(args.out_dir, "processed_prices.csv"), index=False)

    # ---- interés
    trends = pd.read_csv(args.trends)
    if "date" not in trends.columns or "interest" not in trends.columns:
        raise ValueError("Se requieren columnas 'date' e 'interest' en trends_enriched.csv")

    # interés global (media diaria)
    gi = trends.groupby("date")["interest"].mean().reset_index(name="global_interest")
    gi.to_csv(os.path.join(args.out_dir, "processed_interest_global.csv"), index=False)

    # interés por país (pivot)
    if "country" in trends.columns:
        pivot = trends.pivot_table(index="date", columns="country", values="interest", aggfunc="mean").reset_index()
        pivot.to_csv(os.path.join(args.out_dir, "interest_by_country.csv"), index=False)

    # merge vol vs interés
    # usar la primera columna de fecha en prices (dcol) y alinear por fecha
    merged = prices[[dcol] + [c for c in prices.columns if c.startswith("volatility_")]].merge(
        gi.rename(columns={"date": dcol}), on=dcol, how="inner"
    ).rename(columns={dcol: "date"})
    merged.to_csv(os.path.join(args.out_dir, "spatiotemporal_merged.csv"), index=False)

    print("✅ Guardado: processed_prices.csv, processed_interest_global.csv, interest_by_country.csv, spatiotemporal_merged.csv")

if __name__ == "__main__":
    main()
