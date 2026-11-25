# Changelog

All notable changes to **AI-Soil Net** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [1.1.0] - 2026-11-25

### Added
- **Automated 600-DPI Publication-Grade Cartography** in `ai_soil_net.soil_visualizer.SoilVisualizer` (exports both `600-DPI PNG` and vector `PDF` figures):
  - `plot_single_index()`: Standalone mapping for any individual spectral, radar, or soil band with physically intuitive scientific colormaps, 2%–98% percentile stretching, JRC surface water masking, north arrow, and auto-scaled scale bar.
  - `plot_multi_sensor_panels()`: Customizable multi-panel predictor layouts (defaults to 6 core eco-hydrological predictors or accepts any user-defined band list with automatic grid sizing).
  - `plot_soil_quality_map()`: Complete 3-part soil quality assessment layout featuring automatic Global (Robinson) and Regional (Cartopy) context inset maps, JRC water overlay, and class area percentages in the legend.
- **Reproducibility Sample Dataset:** Included `Imperial_EcoHydro_Master.csv` (`n = 134` georeferenced samples with GEE-compatible `.geo` geometry) in the repository for direct Google Earth Engine Table Asset upload and Spatial Transfer Learning replication.
- **Modern Packaging Support:** Added `pyproject.toml`, `MANIFEST.in`, `.gitignore`, and optional `cartography` extras (`pip install "ai-soil-net[cartography]"`).

### Fixed & Improved
- `EcoHydroFusion.get_fused_master_dataset()` now passes `include_climate` and `include_soilgrids` directly to `SoilDataFetcher.fetch_all_integrated()` to avoid unnecessary TerraClimate queries in ongoing real-time years.
- `SoilPredictor.__init__()` now accepts both original parameter names (`training_feature_collection`, `fused_master_image`, `target_properties`) and concise aliases (`training_data`, `fused_image`, `target_props`).
- `SoilPredictor.export_map_to_drive()` now automatically accepts either raw `ee.Geometry` or `ee.Feature` objects and casts outputs via `.toFloat()` to prevent GEE Error Code 3.
- Cleaned `usage_example.py` by removing hardcoded project credentials and adding 600-DPI cartography examples.

---

## [1.0.0] - 2026-11

### Released
- Initial public release of **AI-Soil Net** on [PyPI](https://pypi.org/project/ai-soil-net/), [GitHub](https://github.com/heba-alhashimi/ai-soil-net), and [Zenodo](https://doi.org/10.5281/zenodo.24439875).
- Core 5-module cloud-native DSM architecture on Google Earth Engine.
