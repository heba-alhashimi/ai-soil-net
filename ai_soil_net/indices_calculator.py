import logging
import ee

logger = logging.getLogger(__name__)


class SoilIndicesCalculator:
    """
    Computes standardized optical and microwave (SAR) pedological,
    salinity, vegetation, and moisture indices on Google Earth Engine.
    """

    @staticmethod
    def calculate_optical_indices(image):
        """Calculates 11 optical soil, salinity, vegetation, and moisture indices."""
        logger.info("Calculating Global Optical Soil Indices...")
        b2 = image.select("SR_B2")
        b3 = image.select("SR_B3")
        b4 = image.select("SR_B4")
        b5 = image.select("SR_B5")
        b6 = image.select("SR_B6")
        b7 = image.select("SR_B7")

        ndvi = image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
        ndwi = image.normalizedDifference(["SR_B3", "SR_B5"]).rename("NDWI")
        savi = image.expression("((B5 - B4) / (B5 + B4 + 0.5)) * (1.5)", {"B5": b5, "B4": b4}).rename("SAVI")
        si = image.expression("sqrt(B2 * B4)", {"B2": b2, "B4": b4}).rename("SI")
        ndsi = image.normalizedDifference(["SR_B4", "SR_B5"]).rename("NDSI")
        gi = image.normalizedDifference(["SR_B6", "SR_B7"]).rename("GI")
        ci = image.expression("B4 / B3", {"B4": b4, "B3": b3}).rename("CI")
        cri = image.expression("1 - (B4 / B2)", {"B4": b4, "B2": b2}).rename("CRI")
        color = image.normalizedDifference(["SR_B4", "SR_B3"]).rename("Color")
        bi = image.expression("sqrt((B4**2) + (B3**2))", {"B4": b4, "B3": b3}).rename("BI")
        bsi = image.expression(
            "((B6 + B4) - (B5 + B2)) / ((B6 + B4) + (B5 + B2))",
            {"B2": b2, "B4": b4, "B5": b5, "B6": b6},
        ).rename("BSI")

        return ee.Image([ndvi, ndwi, savi, si, ndsi, gi, ci, cri, color, bi, bsi])

    @staticmethod
    def calculate_radar_indices(sar_image):
        """Calculates dual-polarization Radar Vegetation Index (RVI) in linear power."""
        logger.info("Calculating Structural Radar Indices (Linear Power Conversion)...")
        vv_lin = ee.Image(10).pow(sar_image.select("VV").divide(10))
        vh_lin = ee.Image(10).pow(sar_image.select("VH").divide(10))
        rvi = vh_lin.multiply(4).divide(vv_lin.add(vh_lin)).rename("RVI")
        return sar_image.addBands(rvi)
