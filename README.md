# AI-Soil Net (v1.0.0)

[![PyPI version](https://img.shields.io/pypi/v/ai-soil-net.svg)](https://pypi.org/project/ai-soil-net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**AI-Soil Net** is a cloud-native, open-source Python library built on the **Google Earth Engine (GEE)** Python API for automated **Digital Soil Mapping (DSM)** using multi-sensor Optical-SAR fusion (Landsat 8 + Sentinel-1), automated NDVI/NDWI Dual-Masking, and Spatial Transfer Learning.

## Key Features
- **5 Modular Components:** `SoilDataFetcher`, `SoilIndicesCalculator`, `EcoHydroFusion`, `SoilPredictor`, and `SoilVisualizer`.
- **Multi-Sensor Fusion:** Harmonizes Landsat 8 C2 L2 (30 m), Sentinel-1 C-band SAR GRD (10 m), JRC Surface Water, TerraClimate, and ISRIC SoilGrids 2.0 (250 m).
- **Automated Dual-Masking:** Filters dense active canopies (NDVI) and open surface water (NDWI) prior to modeling.
- **Flexible Modeling:** Supports standalone covariate extraction, local field-calibrated Random Forest DSM, and zero-shot cross-regional Spatial Transfer Learning.
- **GIS-Ready Exports:** Exports 30 m GeoTIFF stacks and predicted soil quality maps directly to Google Drive for ArcGIS/QGIS.

## Installation
```bash
pip install ai-soil-net==1.0.0
```

## Documentation & User Guides
Complete step-by-step manual with reproducible code snippets are available inside the [`docs/`](docs/) folder.

## Citation
If you use **AI-Soil Net** in your research, please cite:
> Al-Hashimi, H. (2026). *AI-Soil Net (v1.0.0): A Cloud-Native Open-Source Python Framework for Automated Digital Soil Mapping Using Multi-Sensor Optical-SAR Fusion, Dual-Masking, and Spatial Transfer Learning*. PyPI: [https://pypi.org/project/ai-soil-net/](https://pypi.org/project/ai-soil-net/) | GitHub: [https://github.com/heba-alhashimi/ai-soil-net](https://github.com/heba-alhashimi/ai-soil-net)
