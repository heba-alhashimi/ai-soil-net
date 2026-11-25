# AI-Soil Net (v1.1.0)

[![PyPI version](https://img.shields.io/pypi/v/ai-soil-net.svg)](https://pypi.org/project/ai-soil-net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24525683.svg)](https://doi.org/10.5281/zenodo.24525683)

**AI-Soil Net** is a cloud-native, open-source Python library built on the **Google Earth Engine (GEE)** Python API for automated **Digital Soil Mapping (DSM)** using multi-sensor Optical–SAR fusion (Landsat 8 + Sentinel-1), automated NDVI/NDWI Dual-Masking, Spatial Transfer Learning, and publication-grade (600 DPI) cartography.

## Key Features
- **5 Modular Components:** `SoilDataFetcher`, `SoilIndicesCalculator`, `EcoHydroFusion`, `SoilPredictor`, and `SoilVisualizer`.
- **Multi-Sensor Fusion:** Harmonizes Landsat 8 C2 L2 (30 m), Sentinel-1 C-band SAR GRD (10 m), JRC Global Surface Water (30 m), TerraClimate (~4.6 km), and ISRIC SoilGrids 2.0 (250 m).
- **Automated Dual-Masking:** Filters dense active canopies (NDVI) and open surface water (NDWI) prior to modeling.
- **Flexible Modeling:** Supports standalone covariate extraction, local field-calibrated Random Forest DSM, and zero-shot cross-regional Spatial Transfer Learning.
- **GIS-Ready Cloud Exports:** Exports 30 m GeoTIFF stacks and predicted soil quality maps directly to Google Drive for ArcGIS/QGIS workflows.
- **Publication-Grade Cartography (600 DPI):** Built-in automated map rendering (`PNG` & vector `PDF`) with geographic coordinates, north arrows, auto-scaled scale bars, JRC surface water masking, area-percentage legends, and global/regional context insets.

## Installation

### Standard Installation (PyPI)
```bash
pip install ai-soil-net==1.1.0
```

### Full Installation (Including 600-DPI Cartography Tools)
To include `rasterio` and `cartopy` for automated 600-DPI journal-ready mapping (`plot_single_index`, `plot_multi_sensor_panels`, and `plot_soil_quality_map`):
```bash
pip install "ai-soil-net[cartography]==1.1.0"
```

## Publication-Grade Cartography (600 DPI)
`SoilVisualizer` enables researchers to generate journal-ready figures directly from exported GeoTIFF outputs for any region of interest worldwide:

```python
from ai_soil_net.soil_visualizer import SoilVisualizer

# 1. Standalone Single-Index Map (e.g., RVI, NDVI, NDWI, Clay)
SoilVisualizer.plot_single_index(
    tif_path="Fayoum_All_Indices_Master_2026.tif",
    band_idx=7,
    index_name="RVI",
    unit="RVI (Dimensionless)",
    region_name="Al-Fayoum Oasis, Egypt",
    year="2026"
)

# 2. Multi-Sensor Panel Map (defaults to 6 key predictors, or pass a custom 'panels' list)
SoilVisualizer.plot_multi_sensor_panels(
    tif_path="Fayoum_All_Indices_Master_2026.tif",
    region_name="Al-Fayoum Oasis, Egypt",
    year="2026"
)

# 3. Predicted Soil Quality Map with Automatic Global & Regional Context Insets
SoilVisualizer.plot_soil_quality_map(
    quality_tif_path="Fayoum_Predicted_Quality_Map_2026.tif",
    region_name="Al-Fayoum Oasis",
    country_name="Egypt",
    year="2026",
    water_tif_path="Fayoum_All_Indices_Master_2026.tif"
)
```

## Reproducibility Sample Dataset
To support full workflow reproducibility, this repository includes **`Imperial_EcoHydro_Master.csv`** (`n = 134` georeferenced samples with GEE-compatible `.geo` geometry). Researchers can upload this file directly as a Google Earth Engine Table Asset to replicate the Spatial Transfer Learning workflow.

## Documentation & User Guides
Complete step-by-step manuals with reproducible code snippets and the system architecture diagram are available inside the [`docs/`](docs/) folder.

## Citation
If you use **AI-Soil Net** in your research, please cite:
> Al-Hashimi, H. (2026). *AI-Soil Net (v1.1.0): A Cloud-Native Open-Source Python Framework for Automated Digital Soil Mapping Using Multi-Sensor Optical–SAR Fusion, Dual-Masking, and Spatial Transfer Learning*. Zenodo: https://doi.org/10.5281/zenodo.24525683 | PyPI: https://pypi.org/project/ai-soil-net/ | GitHub: https://github.com/heba-alhashimi/ai-soil-net
