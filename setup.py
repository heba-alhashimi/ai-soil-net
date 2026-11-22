from setuptools import setup, find_packages

setup(
    name="ai-soil-net",
    version="1.0.0",
    author="Dr. Heba Al-Hashimi",
    description="The First Comprehensive Global Eco-Hydrological AI Framework for Soil Quality Assessment.",
    packages=find_packages(),
    install_requires=[
        "earthengine-api",
        "geemap",
        "pandas",
        "matplotlib",
        "seaborn"
    ],
)
