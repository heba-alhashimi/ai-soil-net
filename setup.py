from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="ai-soil-net",
    version="1.1.0",
    author="Dr. Heba Abdel Hakim Al-Hashimi",
    author_email="pgs.heba.abdulhakeem@uobasrah.edu.iq",
    description=(
        "Cloud-native Python library for automated Digital Soil Mapping on "
        "Google Earth Engine using Optical-SAR fusion, Spatial Transfer Learning, "
        "and 600-DPI publication-grade cartography."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/heba-alhashimi/ai-soil-net",
    project_urls={
        "Homepage": "https://github.com/heba-alhashimi/ai-soil-net",
        "Documentation": "https://github.com/heba-alhashimi/ai-soil-net/tree/main/docs",
        "Bug Tracker": "https://github.com/heba-alhashimi/ai-soil-net/issues",
        "Zenodo DOI": "https://doi.org/10.5281/zenodo.24525683",
    },
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "earthengine-api",
        "geemap",
        "pandas",
        "matplotlib",
        "seaborn",
    ],
    extras_require={
        "cartography": ["rasterio", "cartopy", "numpy"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "digital-soil-mapping",
        "google-earth-engine",
        "remote-sensing",
        "optical-sar-fusion",
        "transfer-learning",
        "cartography",
    ],
)
