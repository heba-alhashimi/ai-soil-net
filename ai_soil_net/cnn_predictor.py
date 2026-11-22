import ee
import logging

logger = logging.getLogger(__name__)

class SoilPredictor:
    def __init__(self, training_feature_collection, fused_master_image, target_properties, input_bands=None):
        self.training_data = ee.FeatureCollection(training_feature_collection) if isinstance(training_feature_collection, str) else training_feature_collection
        self.fused_image = fused_master_image
        self.target_properties = target_properties
        self.input_bands = input_bands if input_bands else self.fused_image.bandNames()
        self.models = {}
        self.prediction_maps = None

    def train_random_forest_models(self, n_trees=100):
        logger.info(f"Training Global AI models with bands: {self.input_bands}")
        for prop in self.target_properties:
            rf_model = ee.Classifier.smileRandomForest(n_trees).setOutputMode('REGRESSION').train(
                features=self.training_data, classProperty=prop, inputProperties=self.input_bands)
            self.models[prop] = rf_model

    def generate_prediction_maps(self):
        if not self.models:
            raise ValueError("Models are not trained yet.")
        predicted_images = []
        for prop, model in self.models.items():
            predicted_images.append(self.fused_image.classify(model).rename(f'Predicted_{prop}'))
        self.prediction_maps = ee.Image(predicted_images)
        return self.prediction_maps

    def export_map_to_drive(self, roi, description='AI_Soil_Net_Map', scale=30, folder='AI_Soil_Net_Outputs'):
        """Automatically exports the final prediction maps to Google Drive."""
        if not self.prediction_maps:
            raise ValueError("Prediction maps not generated.")
        logger.info(f"Exporting map '{description}' to Google Drive...")
        task = ee.batch.Export.image.toDrive(
            image=self.prediction_maps,
            description=description,
            folder=folder,
            region=roi.geometry(),
            scale=scale,
            maxPixels=1e13
        )
        task.start()
        logger.info(f"Export task started! Check your Google Earth Engine Tasks tab or Google Drive.")
        return task
