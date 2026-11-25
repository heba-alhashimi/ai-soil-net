import logging
import ee

logger = logging.getLogger(__name__)


class SoilPredictor:
    """
    Cloud-native Random Forest regression engine for local Digital Soil Mapping
    and zero-shot cross-regional Spatial Transfer Learning on Google Earth Engine.
    """

    def __init__(
        self,
        training_feature_collection=None,
        fused_master_image=None,
        target_properties=None,
        input_bands=None,
        *,
        training_data=None,
        fused_image=None,
        target_props=None,
    ):
        train_src = training_feature_collection if training_feature_collection is not None else training_data
        img_src = fused_master_image if fused_master_image is not None else fused_image
        props_src = target_properties if target_properties is not None else target_props

        if train_src is None or img_src is None or props_src is None:
            raise ValueError(
                "Please provide training_feature_collection (or training_data), "
                "fused_master_image (or fused_image), and target_properties (or target_props)."
            )

        self.training_data = ee.FeatureCollection(train_src) if isinstance(train_src, str) else train_src
        self.fused_image = img_src
        self.target_properties = list(props_src)
        self.input_bands = input_bands if input_bands else self.fused_image.bandNames()
        self.models = {}
        self.prediction_maps = None

    def train_random_forest_models(self, n_trees=100):
        """Trains cloud-native Smile Random Forest regression models for each target property."""
        logger.info("Training Global AI models with bands: %s", self.input_bands)
        for prop in self.target_properties:
            rf_model = (
                ee.Classifier.smileRandomForest(n_trees)
                .setOutputMode("REGRESSION")
                .train(
                    features=self.training_data,
                    classProperty=prop,
                    inputProperties=self.input_bands,
                )
            )
            self.models[prop] = rf_model

    def generate_prediction_maps(self):
        """Applies trained Random Forest models across the fused multi-sensor image."""
        if not self.models:
            raise ValueError("Models are not trained yet. Call train_random_forest_models() first.")
        predicted_images = []
        for prop, model in self.models.items():
            predicted_images.append(self.fused_image.classify(model).rename(f"Predicted_{prop}"))
        self.prediction_maps = ee.Image(predicted_images)
        return self.prediction_maps

    def export_map_to_drive(self, roi, description="AI_Soil_Net_Map", scale=30, folder="AI_Soil_Net_Outputs"):
        """Exports predicted soil quality maps as 30 m Float32 GeoTIFFs to Google Drive."""
        if not self.prediction_maps:
            raise ValueError("Prediction maps not generated. Call generate_prediction_maps() first.")
        region = roi if isinstance(roi, ee.Geometry) else roi.geometry()
        logger.info("Exporting map '%s' to Google Drive folder '%s'...", description, folder)
        task = ee.batch.Export.image.toDrive(
            image=self.prediction_maps.toFloat(),
            description=description,
            folder=folder,
            region=region,
            scale=scale,
            maxPixels=1e13,
        )
        task.start()
        logger.info("Export task started. Monitor progress in Google Earth Engine Tasks or Google Drive.")
        return task
