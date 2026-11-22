import ee
import geemap
from ai_soil_net.eco_hydro_fusion import EcoHydroFusion
from ai_soil_net.cnn_predictor import SoilPredictor
from ai_soil_net.soil_visualizer import SoilVisualizer

# 1. Initialize
try:
    ee.Initialize(project='heba-505120')
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='heba-505120')

print("🌍 Logged in successfully. Running AI-Soil Net GLOBAL (V1.0.0)...")

# 2. Define ROI (Works for ANY region globally)
roi = ee.FeatureCollection("TIGER/2018/Counties").filter(ee.Filter.eq('NAME', 'Imperial'))

# 3. Global Fusion Engine (Now includes Climate + SoilGrids ISRIC)
fusion_engine = EcoHydroFusion(roi=roi, start_date='2024-01-01', end_date='2024-12-31')

# We can include climate (TerraClimate) and SoilGrids data automatically
master_image = fusion_engine.get_fused_master_dataset(include_climate=True, include_soilgrids=True)

# 4. Predictor 
eco_hydro_bands = ['VV', 'VH', 'VV_VH_ratio', 'NDWI', 'Surface_Water_Occurrence']

predictor = SoilPredictor(
    training_feature_collection='projects/heba-505120/assets/Imperial_EcoHydro_Master',
    fused_master_image=master_image,
    target_properties=['pH', 'CEC', 'Clay', 'Nitrogen', 'SOC', 'Predicted_MASQI'],
    input_bands=eco_hydro_bands
)

print("⏳ Training AI models...")
predictor.train_random_forest_models(n_trees=100)
final_maps = predictor.generate_prediction_maps()
print("✅ Maps generated successfully!")

# 5. NEW: Automated Export to Google Drive
print("📥 Initiating Map Export to Google Drive...")
predictor.export_map_to_drive(roi=roi, description='Imperial_Global_AI_Soil_Map')

# 6. NEW: Professional Visualizations
print("📊 Generating Professional Academic Charts...")
# Extracting the importance dict from the trained MASQI model
importance_dict = predictor.models['Predicted_MASQI'].explain().get('importance').getInfo()

# Plotting the Feature Importance using the new SoilVisualizer module
SoilVisualizer.plot_feature_importance(importance_dict, title="Feature Importance for MASQI Prediction")

# Simulating soil quality distribution for the pie chart based on your typical data
SoilVisualizer.plot_soil_quality_distribution([15, 25, 30, 20, 10], title="Predicted Soil Quality Classes (Imperial Valley)")

# 7. Map Visualization
Map = geemap.Map(center=[33.0, -115.5], zoom=9, basemap='SATELLITE')
vis_params = {'min': 0.46, 'max': 0.52, 'palette': ['d7191c', 'fdae61', 'ffffbf', 'a6d96a', '1a9641']}
Map.addLayer(final_maps.select('Predicted_Predicted_MASQI'), vis_params, 'AI-Soil Net: Global MASQI Map')
display(Map)
