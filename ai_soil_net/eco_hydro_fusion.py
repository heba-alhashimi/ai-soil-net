import logging
import ee
from .data_fetcher import SoilDataFetcher
from .indices_calculator import SoilIndicesCalculator

logger = logging.getLogger(__name__)


class EcoHydroFusion:
    """
    Executes automated NDVI/NDWI Dual-Masking and harmonizes Optical,
    SAR, JRC Surface Water, TerraClimate, and SoilGrids 2.0 layers.
    """

    def __init__(self, roi, start_date="2024-01-01", end_date="2024-12-31", veg_mask_threshold=0.45):
        self.roi = roi
        self.fetcher = SoilDataFetcher(roi, start_date, end_date)
        self.calculator = SoilIndicesCalculator()
        self.veg_mask_threshold = veg_mask_threshold

    def get_fused_master_dataset(self, include_climate=True, include_soilgrids=True):
        """Builds and returns the Dual-Masked multi-sensor ee.Image stack."""
        logger.info("Initiating Global Eco-Hydrological Fusion pipeline...")
        raw = self.fetcher.fetch_all_integrated(
            include_climate=include_climate,
            include_soilgrids=include_soilgrids,
        )

        opt = self.calculator.calculate_optical_indices(raw["optical"])
        sar = self.calculator.calculate_radar_indices(raw["sar"])
        hydro = raw["hydro"]

        # Deterministic Dual-Masking (open water + dense active canopy)
        mask = opt.select("NDWI").lt(0).And(opt.select("NDVI").lt(self.veg_mask_threshold))

        bands_to_fuse = [opt.updateMask(mask), sar.updateMask(mask), hydro.updateMask(mask)]

        if include_climate and "climate" in raw:
            bands_to_fuse.append(raw["climate"].updateMask(mask))
        if include_soilgrids and "soilgrids" in raw:
            bands_to_fuse.append(raw["soilgrids"].updateMask(mask))

        fused_master = ee.Image(bands_to_fuse)
        logger.info("Global Fusion complete. Ready for modeling.")
        return fused_master
