# Time–Series + Spatial + Spatiotemporal Pipeline

Este proyecto implementa un pipeline reproducible para:
- **Parte 1 – Series de tiempo:** retornos, volatilidad, ACF, CCF.
- **Parte 2 – Espacial:** mapa coroplético (estático y animado) por país.
- **Parte 3 – Espaciotemporal:** correlación e interpretación **lead/lag** (CCF) entre el interés geográfico y la volatilidad.

---

## Estructura esperada
```
.
├── analyst/
│   ├── country_aggregated.csv
│   ├── country_mapping.csv
│   ├── geo_countries.csv
│   ├── geo_countries.geojson
│   ├── prices_with_metrics.csv
│   ├── trends_enriched.csv
│   └── outputs/            # (se genera)
├── clean_geographic_data.py
├── prepare_temporal_data.py
├── generate_maps.py        # autodetecta llave del GeoJSON (ADM0_A3, ISO_A3, etc.)
├── generate_temporal_viz.py
└── (opcional) .venv/
```

> Si tus archivos están en otra carpeta/nombre, ajusta las **rutas** con los flags mostrados abajo.

---

## Requisitos
- Python 3.10+
- Recomendado: entorno virtual (venv)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pandas numpy matplotlib plotly statsmodels pycountry kaleido
```

> En Ubuntu con PEP 668 (entorno “externally-managed”), **usa venv** para instalar paquetes.

---

## Ejecución rápida

1) **Geográfico (ISO-3 + cortes full/latest):**
```bash
python3 clean_geographic_data.py   --trends ./analyst/trends_enriched.csv   --mapping ./analyst/country_mapping.csv   --out-full ./analyst/outputs/trends_geo_full.csv   --out-latest ./analyst/outputs/trends_geo_latest.csv
```

2) **Temporal (retornos, volatilidad, interés global, merge):**
```bash
python3 prepare_temporal_data.py   --prices ./analyst/prices_with_metrics.csv   --trends ./analyst/trends_enriched.csv   --out-dir ./analyst/outputs
```

3) **Mapas (Plotly):**
```bash
python3 generate_maps.py   --full ./analyst/outputs/trends_geo_full.csv   --latest ./analyst/outputs/trends_geo_latest.csv   --geojson ./analyst/geo_countries.geojson   --out-map ./analyst/outputs/map_latest.html   --out-anim ./analyst/outputs/map_animated.html
```
*El script autodetecta la llave correcta del GeoJSON (p. ej. `ADM0_A3`, `ISO_A3`). Si no hay buen match, hace **fallback** a `locationmode="ISO-3"`.*

4) **Visualizaciones temporales (líneas, ACF, CCF):**
```bash
python3 generate_temporal_viz.py   --in-dir ./analyst/outputs   --out-dir ./analyst/outputs   --acf-lags 40
```

---

## Outputs principales
- **Mapas:** `map_latest.html`, `map_animated.html`
- **Series:** `price_level.png`, `returns.png`, `returns_squared.png`, `volatility.png`
- **ACF:** `acf_prices.png`, `acf_returns.png`, `acf_returns_squared.png`
- **CCF:** `ccf_interest_vs_volatility.png`
- **Tablas:** `processed_prices.csv`, `processed_interest_global.csv`, `interest_by_country.csv`,  
  `spatiotemporal_merged.csv`, `trends_geo_full.csv`, `trends_geo_latest.csv`

Para abrir el mapa: `xdg-open analyst/outputs/map_latest.html`

---

## Tips / Notas
- Si no quieres pasar flags cada vez, puedes editar los *defaults* dentro de cada script para que apunten a `analyst/`.
- Exportar mapas a PNG (para informes/PDF):
  ```python
  import plotly.express as px, plotly.io as pio, pandas as pd
  df = pd.read_csv("analyst/outputs/trends_geo_latest.csv")
  fig = px.choropleth(df, locations="iso3", color="interest", locationmode="ISO-3", color_continuous_scale="Plasma")
  pio.write_image(fig, "analyst/outputs/map_latest.png", scale=2, width=1400, height=700)
  ```
- Si trabajas con archivos grandes, considera **Git LFS**.

---

## Reproducibilidad (opcional)
Genera un archivo con dependencias y un runner 1-click:

```bash
# Dependencias
source .venv/bin/activate
pip freeze > requirements.txt

# Runner
cat > run_all.sh <<'SH'
#!/usr/bin/env bash
set -e
python3 clean_geographic_data.py   --trends ./analyst/trends_enriched.csv   --mapping ./analyst/country_mapping.csv   --out-full ./analyst/outputs/trends_geo_full.csv   --out-latest ./analyst/outputs/trends_geo_latest.csv

python3 prepare_temporal_data.py   --prices ./analyst/prices_with_metrics.csv   --trends ./analyst/trends_enriched.csv   --out-dir ./analyst/outputs

python3 generate_maps.py   --full ./analyst/outputs/trends_geo_full.csv   --latest ./analyst/outputs/trends_geo_latest.csv   --out-map ./analyst/outputs/map_latest.html   --out-anim ./analyst/outputs/map_animated.html

python3 generate_temporal_viz.py   --in-dir ./analyst/outputs   --out-dir ./analyst/outputs   --acf-lags 40
SH
chmod +x run_all.sh
```

---

## Flujo con Git (rama nueva)
```bash
git checkout -b feat/analysis-pipeline
git add README.md .gitignore         clean_geographic_data.py prepare_temporal_data.py generate_maps.py generate_temporal_viz.py         analyst/*.csv analyst/*.geojson
git commit -m "feat: add time-series + spatial pipeline with docs"
git push -u origin feat/analysis-pipeline
```
> Si **no** quieres subir los datos, no los incluyas en `git add` y agrega los patrones de datos a `.gitignore`.

---

## Licencia
Este proyecto se distribuye con fines educativos. Ajusta o agrega tu licencia preferida (MIT, Apache-2.0, etc.).
