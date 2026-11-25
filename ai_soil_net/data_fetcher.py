import logging
import ee

logger = logging.getLogger(__name__)


class SoilDataFetcher:
    """
    Fetches multi-sensor Satellite (Optical/SAR), Hydrological, Climatic,
    and Global Soil (ISRIC SoilGrids 2.0) datasets from Google Earth Engine.
    """

    def __init__(self, roi, start_date="2023-01-01", end_date="2023-12-31"):
        self.roi = roi
        self.start_date = start_date
        self.end_date = end_date

    def _apply_l8_scale_factors(self, image):
        optical_bands = image.select("SR_B.").multiply(0.0000275).add(-0.2).clamp(0, 1)
        thermal_bands = image.select("ST_B.*").multiply(0.00341802).add(149.0)
        return image.addBands(optical_bands, None, True).addBands(thermal_bands, None, True)

    def _mask_l8_clouds(self, image):
        qa = image.select("QA_PIXEL")
        mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
        return image.updateMask(mask)

    def fetch_optical_data(self, cloud_threshold=10):
        """Fetches cloud-masked Landsat 8 Collection 2 Level-2 surface reflectance."""
        logger.info("Fetching Landsat 8 Optical Data...")
        l8 = (
            ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
            .filterBounds(self.roi)
            .filterDate(self.start_date, self.end_date)
            .filter(ee.Filter.lt("CLOUD_COVER", cloud_threshold))
            .map(self._mask_l8_clouds)
            .map(self._apply_l8_scale_factors)
        )
        return l8.median().clip(self.roi)

    def fetch_sar_data(self):
        """Fetches Sentinel-1 C-band IW GRD dual-polarization (VV, VH) backscatter."""
        logger.info("Fetching Sentinel-1 SAR Data...")
        s1 = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(self.roi)
            .filterDate(self.start_date, self.end_date)
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
            .filter(ee.Filter.eq("instrumentMode", "IW"))
        )
        med = s1.select(["VV", "VH"]).median().clip(self.roi)
        # In dB scale, polarization ratio (VV/VH) is computed via subtraction (VV - VH)
        return med.addBands(med.select("VV").subtract(med.select("VH")).rename("VV_VH_ratio"))

    def fetch_hydrological_context(self):
        """Fetches JRC Global Surface Water occurrence (%) layer."""
        logger.info("Fetching JRC Hydrological Context...")
        return (
            ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
            .select("occurrence")
            .unmask(0)
            .clip(self.roi)
            .rename("Surface_Water_Occurrence")
        )

    def fetch_climate_data(self):
        """Fetches Global Climate Data (Precipitation and Max Temperature) using TerraClimate."""
        logger.info("Fetching Global Climate Data (TerraClimate)...")
        climate = (
            ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE")
            .filterBounds(self.roi)
            .filterDate(self.start_date, self.end_date)
            .median()
            .clip(self.roi)
        )
        precip = climate.select("pr").rename("Precipitation")
        temp = climate.select("tmmx").multiply(0.1).rename("Max_Temperature")
        return ee.Image([precip, temp])

    def fetch_soilgrids_baseline(self):
        """Fetches Global ISRIC SoilGrids 2.0 (250 m) baseline soil layers for 0-5 cm depth."""
        logger.info("Fetching Global SoilGrids Database (ISRIC)...")
        clay = ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean").clip(self.roi).rename("SG_Clay")
        soc = ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean").clip(self.roi).rename("SG_SOC")
        ph = ee.Image("projects/soilgrids-isric/phh2o_mean").select("phh2o_0-5cm_mean").clip(self.roi).rename("SG_pH")
        cec = ee.Image("projects/soilgrids-isric/cec_mean").select("cec_0-5cm_mean").clip(self.roi).rename("SG_CEC")
        nitrogen = (
            ee.Image("projects/soilgrids-isric/nitrogen_mean")
            .select("nitrogen_0-5cm_mean")
            .clip(self.roi)
            .rename("SG_Nitrogen")
        )
        return ee.Image([clay, soc, ph, cec, nitrogen])

    def fetch_all_integrated(self, include_climate=True, include_soilgrids=True):
        """Fetches all requested multi-sensor layers as a dictionary of ee.Image objects."""
        data = {
            "optical": self.fetch_optical_data(),
            "sar": self.fetch_sar_data(),
            "hydro": self.fetch_hydrological_context(),
        }
        if include_climate:
            data["climate"] = self.fetch_climate_data()
        if include_soilgrids:
            data["soilgrids"] = self.fetch_soilgrids_baseline()
        return data
