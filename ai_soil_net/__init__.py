"""
AI-Soil Net: A Cloud-Native Open-Source Python Library for Automated
Digital Soil Mapping & Publication-Grade Cartography on Google Earth Engine.
"""

__version__ = "1.1.0"
__author__ = "Dr. Heba Abdel Hakim Al-Hashimi"

from .data_fetcher import SoilDataFetcher
from .indices_calculator import SoilIndicesCalculator
from .eco_hydro_fusion import EcoHydroFusion
from .cnn_predictor import SoilPredictor
from .soil_visualizer import SoilVisualizer

__all__ = [
    "__version__",
    "__author__",
    "SoilDataFetcher",
    "SoilIndicesCalculator",
    "EcoHydroFusion",
    "SoilPredictor",
    "SoilVisualizer",
]
