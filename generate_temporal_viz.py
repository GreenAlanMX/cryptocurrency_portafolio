#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_temporal_viz.py (dataset-aware defaults)
------------------------------------------------
Usa directamente los archivos de /mnt/data/outputs creados por prepare_temporal_data.py
y genera figuras PNG: precio, retornos, retornos², volatilidad, ACFs y CCF interés vs volatilidad.
"""
import argparse
import os
import pandas as pd
import numpy as np

DEFAULT_IN = "/mnt/data/outputs"
DEFAULT_OUT = "/mnt/data/outputs"
DEFAULT_LAGS = 40

def fig_path(out_dir, name):
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, name)

def plot_line(df, x, y, title, path):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(11,5))
    plt.plot(df[x], df[y])
    plt.title(title); plt.xlabel(x); plt.ylabel(y)
    plt.grid(True, alpha=0.3); plt.tight_layout(); plt.savefig(path, dpi=160); plt.close()

def plot_acf(series, lags, title, path):
    import matplotlib.pyplot as plt
    try:
        from statsmodels.tsa.stattools import acf as sm_acf
        vals = sm_acf(series.dropna(), nlags=lags, fft=True)
    except Exception:
        x = (series - series.mean()).dropna()
        vals = [1.0]
        for k in range(1, lags+1):
            num = np.dot(x[k:], x[:-k]); den = np.dot(x, x)
            vals.append(num/den if den != 0 else 0.0)
    n = series.dropna().shape[0]; conf = 2/np.sqrt(n) if n>0 else 0.0
    import matplotlib.pyplot as plt
    xx = np.arange(0, len(vals))
    plt.figure(figsize=(10,5))
    markerline, stemlines, baseline = plt.stem(xx, vals)
    plt.hlines([+conf, -conf], 0, lags, colors='r', linestyles='dashed')
    plt.title(title); plt.xlabel("Lag"); plt.ylabel("ACF"); plt.grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig(path, dpi=160); plt.close()

def plot_ccf(df, x_col, y_col, max_lag, title, path):
    import matplotlib.pyplot as plt
    x = df[x_col].astype(float); y = df[y_col].astype(float)
    x = (x - x.mean())/x.std(ddof=0); y = (y - y.mean())/y.std(ddof=0)
    lags = np.arange(-max_lag, max_lag+1); vals = []
    for L in lags:
        vals.append(x.corr(y.shift(+abs(L))) if L<0 else x.shift(L).corr(y))
    n = df[[x_col,y_col]].dropna().shape[0]; conf = 2/np.sqrt(n) if n>0 else 0.0
    plt.figure(figsize=(12,5))
    markerline, stemlines, baseline = plt.stem(lags, vals)
    plt.hlines([+conf, -conf], lags.min(), lags.max(), colors='r', linestyles='dashed')
    plt.title(title + "\\nInterpretación: lag<0 (interés→vol); lag>0 (vol→interés); lag≈0 simultáneo")
    plt.xlabel("Lag (días)"); plt.ylabel("CCF"); plt.grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig(path, dpi=160); plt.close()

def main():
    ap = argparse.ArgumentParser(description="Genera visualizaciones temporales desde /mnt/data/outputs.")
    ap.add_argument("--in-dir", default=DEFAULT_IN)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--acf-lags", type=int, default=DEFAULT_LAGS)
    args = ap.parse_args()

    prices = pd.read_csv(os.path.join(args.in_dir, "processed_prices.csv"))
    p_date = "Date" if "Date" in prices.columns else "date"
    p_close = "Close" if "Close" in prices.columns else "close"
    vol_cols = [c for c in prices.columns if c.startswith("volatility_") and c.endswith("d")]
    vol_col = vol_cols[0] if vol_cols else None

    # Líneas
    if p_close in prices.columns: plot_line(prices, p_date, p_close, "Precio (nivel)", fig_path(args.out_dir, "price_level.png"))
    if "returns" in prices.columns: plot_line(prices, p_date, "returns", "Retornos", fig_path(args.out_dir, "returns.png"))
    if "returns_squared" in prices.columns: plot_line(prices, p_date, "returns_squared", "Retornos²", fig_path(args.out_dir, "returns_squared.png"))
    if vol_col: plot_line(prices, p_date, vol_col, f"Volatilidad ({vol_col})", fig_path(args.out_dir, "volatility.png"))

    # ACFs
    if p_close in prices.columns: plot_acf(prices[p_close], args.acf_lags, "ACF de Precios", fig_path(args.out_dir, "acf_prices.png"))
    if "returns" in prices.columns: plot_acf(prices["returns"], args.acf_lags, "ACF de Retornos", fig_path(args.out_dir, "acf_returns.png"))
    if "returns_squared" in prices.columns: plot_acf(prices["returns_squared"], args.acf_lags, "ACF de Retornos²", fig_path(args.out_dir, "acf_returns_squared.png"))

    # Serie por región (Top-N) si existe interest_by_country.csv
    path_countries = os.path.join(args.in_dir, "interest_by_country.csv")
    if os.path.exists(path_countries):
        df = pd.read_csv(path_countries)
        date_col = "date" if "date" in df.columns else df.columns[0]
        long = df.melt(id_vars=[date_col], var_name="country", value_name="interest")
        top = long.groupby("country")["interest"].mean().sort_values(ascending=False).head(6).index
        long_top = long[long["country"].isin(top)].copy()
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12,6))
        for c in top:
            sub = long_top[long_top["country"] == c]
            plt.plot(sub[date_col], sub["interest"], label=c)
        plt.legend(ncol=2); plt.title("Interés por región (Top 6)"); plt.xlabel("Fecha"); plt.ylabel("Interés")
        plt.grid(True, alpha=0.3); plt.tight_layout(); plt.savefig(fig_path(args.out_dir, "interest_by_region.png"), dpi=160); plt.close()

    # CCF: interés vs volatilidad
    merged_path = os.path.join(args.in_dir, "spatiotemporal_merged.csv")
    if os.path.exists(merged_path):
        merged = pd.read_csv(merged_path)
        dcol = "date" if "date" in merged.columns else merged.columns[0]
        gcol = "global_interest"
        vcols = [c for c in merged.columns if c.startswith("volatility_") and c.endswith("d")]
        if gcol in merged.columns and vcols:
            plot_ccf(merged[[dcol, gcol, vcols[0]]].dropna(), gcol, vcols[0], args.acf_lags,
                     "CCF: Interés global vs Volatilidad", fig_path(args.out_dir, "ccf_interest_vs_volatility.png"))

    print("✅ Figuras generadas en", args.out_dir)

if __name__ == "__main__":
    main()
