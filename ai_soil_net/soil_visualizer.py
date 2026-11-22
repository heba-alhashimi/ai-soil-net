import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

class SoilVisualizer:
    """
    Generates professional academic charts and statistical tables 
    from extracted soil data.
    """
    @staticmethod
    def plot_feature_importance(importance_dict, title="AI-Soil Net: Feature Importance"):
        """Plots a professional bar chart for Random Forest Feature Importance."""
        df = pd.DataFrame(list(importance_dict.items()), columns=['Feature', 'Importance Score'])
        df = df.sort_values(by='Importance Score', ascending=False)

        plt.figure(figsize=(12, 6))
        sns.barplot(x='Importance Score', y='Feature', data=df, palette='viridis')
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Gini Decrease (Importance)', fontsize=12)
        plt.ylabel('Spectral/Structural Features', fontsize=12)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_soil_quality_distribution(quality_data, title="Soil Quality Class Distribution"):
        """Plots a professional pie chart for soil quality classes."""
        plt.figure(figsize=(8, 8))
        colors = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641'] # Red to Green
        labels = ['Very Low', 'Low', 'Moderate', 'High', 'Very High']

        plt.pie(quality_data, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140, shadow=True)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.show()
