# Changelog

All notable changes to **AI-Soil Net** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Main Branch

### Added
- **Automated 600-DPI Publication-Grade Cartography** in `ai_soil_net.soil_visualizer.SoilVisualizer` (exports both `600-DPI PNG` and vector `PDF` figures):
  - `plot_single_index()`: Standalone mapping for any individual spectral, radar, or soil band with physically intuitive scientific colormaps, 2%–98% percentile stretching, JRC surface water masking, north arrow, and auto-scaled scale bar.
  - `plot_multi_sensor_panels()`: Customizable multi-panel predictor layouts (defaults to 6 core eco-hydrological predictors or accepts any user-defined band list with automatic grid sizing).
  - `plot_soil_quality_map()`: Complete 3-part soil quality assessment layout featuring automatic Global (Robinson) and Regional (Cartopy) context inset maps, JRC water overlay, and class area percentages in the legend.
- **Reproducibility Sample Dataset:** Included `Imperial_EcoHydro_Master.csv` (`n = 134` georeferenced samples with GEE-compatible `.geo` geometry) in the repository for direct Google Earth Engine Table Asset upload and Spatial Transfer Learning replication.

### Updated
- **README.md:** Documented the new 600-DPI cartography tools, GitHub `main`-branch installation instructions, optional `rasterio`/`cartopy` dependencies, sample dataset, and official Zenodo DOI citation.
- **Official User Guide (`docs/AI_Soil_Net_User_Guide.pdf`):** Expanded to include Operational Mode 5 (Automated 600-DPI Cartography), updated module architecture, and additional Colab/GeoTIFF troubleshooting safeguards.
- **System Architecture Diagram:** Refined terminology (`Random Forest Regressor`) and updated Step 5 (`SoilVisualizer`) to reflect the new 600-DPI cartographic outputs.

---

## [1.0.0] - 2026-11

### Released
- Initial public release of **AI-Soil Net** on [PyPI](https://pypi.org/project/ai-soil-net/), [GitHub](https://github.com/heba-alhashimi/ai-soil-net), and [Zenodo](https://doi.org/10.5281/zenodo.24439875).
- Core 5-module cloud-native DSM architecture on Google Earth Engine:
  - `SoilDataFetcher` (Landsat 8 C2 L2 SR, Sentinel-1 IW GRD, JRC Surface Water, TerraClimate, ISRIC SoilGrids 2.0).
  - `SoilIndicesCalculator` (>15 optical and microwave pedological indices).
  - `EcoHydroFusion` (automated NDVI/NDWI Dual-Masking and multi-sensor stacking).
  - `SoilPredictor` (distributed GEE Smile Random Forest regression, Spatial Transfer Learning, and Google Drive GeoTIFF export).
  - `SoilVisualizer` (feature importance and soil quality class distribution plots).
