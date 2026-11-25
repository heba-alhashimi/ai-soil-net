"""
AI-Soil Net — Complete End-to-End Usage Example
Replace 'YOUR_PROJECT_ID' with your own Google Earth Engine Cloud Project ID.
"""

import ee
import geemap
from ai_soil_net.eco_hydro_fusion import EcoHydroFusion
from ai_soil_net.cnn_predictor import SoilPredictor
from ai_soil_net.soil_visualizer import SoilVisualizer

# 1. Initialize Google Earth Engine
PROJECT_ID = "YOUR_PROJECT_ID"
try:
    ee.Initialize(project=PROJECT_ID)
except Exception:
    ee.Authenticate()
    ee.Initialize(project=PROJECT_ID)

print("Logged in successfully. Running AI-Soil Net...")

# 2. Define any global Region of Interest (Example: Imperial County, CA, USA)
roi = ee.FeatureCollection("TIGER/2018/Counties").filter(ee.Filter.eq("NAME", "Imperial"))

# 3. Execute Multi-Sensor Optical-SAR Fusion & Automated Dual-Masking
# Note: Set include_climate=False when mapping ongoing real-time years (e.g., 2026)
fusion_engine = EcoHydroFusion(roi=roi, start_date="2024-01-01", end_date="2024-12-31")
master_image = fusion_engine.get_fused_master_dataset(
    include_climate=True,
    include_soilgrids=True,
)

# 4. Train Cloud-Native Random Forest Models (Upload Imperial_EcoHydro_Master.csv as a GEE Asset)
eco_hydro_bands = ["VV", "VH", "VV_VH_ratio", "NDWI", "Surface_Water_Occurrence"]

predictor = SoilPredictor(
    training_feature_collection=f"projects/{PROJECT_ID}/assets/Imperial_EcoHydro_Master",
    fused_master_image=master_image,
    target_properties=["pH", "CEC", "Clay", "Nitrogen", "SOC", "Predicted_MASQI"],
    input_bands=eco_hydro_bands,
)

print("Training cloud-native Random Forest regression models...")
predictor.train_random_forest_models(n_trees=100)
final_maps = predictor.generate_prediction_maps()
print("Prediction maps generated successfully.")

# 5. Automated Export to Google Drive (30 m Float32 GeoTIFF)
print("Initiating GeoTIFF export to Google Drive...")
predictor.export_map_to_drive(roi=roi, description="Imperial_Global_AI_Soil_Map")

# 6. Academic Diagnostic Charts
importance_dict = predictor.models["Predicted_MASQI"].explain().get("importance").getInfo()
SoilVisualizer.plot_feature_importance(importance_dict, title="Feature Importance for MASQI Prediction")
SoilVisualizer.plot_soil_quality_distribution(
    [15, 25, 30, 20, 10],
    title="Predicted Soil Quality Classes (Imperial Valley)",
)

# 7. Interactive Web Map Visualization via geemap
Map = geemap.Map(center=[33.0, -115.5], zoom=9, basemap="SATELLITE")
vis_params = {"min": 0.46, "max": 0.52, "palette": ["d7191c", "fdae61", "ffffbf", "a6d96a", "1a9641"]}
Map.addLayer(final_maps.select("Predicted_Predicted_MASQI"), vis_params, "AI-Soil Net: MASQI Map")
# In Jupyter/Colab, call: display(Map)

# 8. Optional: Publication-Grade 600-DPI Cartography (after downloading GeoTIFFs from Drive)
# SoilVisualizer.plot_single_index(
#     tif_path="All_Indices_Master.tif",
#     band_idx=7,
#     index_name="RVI",
#     unit="RVI (Dimensionless)",
#     region_name="Imperial Valley, USA",
#     year="2024",
# )
# SoilVisualizer.plot_multi_sensor_panels(
#     tif_path="All_Indices_Master.tif",
#     region_name="Imperial Valley, USA",
#     year="2024",
# )
# SoilVisualizer.plot_soil_quality_map(
#     quality_tif_path="Imperial_Global_AI_Soil_Map.tif",
#     region_name="Imperial Valley",
#     country_name="USA",
#     year="2024",
#     water_tif_path="All_Indices_Master.tif",
# )
