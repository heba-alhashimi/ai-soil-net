import logging
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


class SoilVisualizer:
    """
    Generates publication-grade academic charts, statistical summaries,
    and 600-DPI geospatial maps from extracted soil and multi-sensor data.
    """

    DEFAULT_CMAPS = {
        "NDVI": "RdYlGn",
        "SAVI": "YlGn",
        "NDWI": "BrBG",
        "NDSI": "YlOrRd",
        "SI": "OrRd",
        "BSI": "YlOrBr",
        "VV": "cividis",
        "VH": "viridis",
        "VV_VH_RATIO": "plasma",
        "RVI": "PuBuGn",
        "CLAY": "YlOrBr",
        "SG_CLAY": "YlOrBr",
    }

    DEFAULT_PANELS = [
        {"band": 1, "title": "(a) NDVI (Vegetation Index)",         "cmap": "RdYlGn",  "unit": "Index (−1 to +1)"},
        {"band": 2, "title": "(b) NDWI (Water / Moisture Index)",   "cmap": "BrBG",    "unit": "Index (−1 to +1)"},
        {"band": 3, "title": "(c) Sentinel-1 VV Backscatter",       "cmap": "cividis", "unit": "Backscatter (dB)"},
        {"band": 4, "title": "(d) Sentinel-1 VH Backscatter",       "cmap": "viridis", "unit": "Backscatter (dB)"},
        {"band": 7, "title": "(e) RVI (Radar Vegetation Index)",    "cmap": "PuBuGn",  "unit": "RVI (Dimensionless)"},
        {"band": 9, "title": "(f) SoilGrids Clay Content (0–5 cm)", "cmap": "YlOrBr",  "unit": "Clay (g/kg)"},
    ]

    @staticmethod
    def _compute_scale_bar(bounds, is_geo):
        """Automatically computes a clean scale bar length (km) and map-unit width."""
        import numpy as np

        mid_lat = (bounds.bottom + bounds.top) / 2.0
        km_per_deg = 111.32 * np.cos(np.radians(mid_lat)) if is_geo else 0.001
        width_km = (bounds.right - bounds.left) * km_per_deg
        nice_scales = [1, 2, 5, 10, 20, 50, 100, 200]
        scale_km = min(nice_scales, key=lambda x: abs(x - width_km * 0.25))
        bar_len = (scale_km / km_per_deg) if is_geo else (scale_km * 1000.0)
        return scale_km, bar_len

    @staticmethod
    def _add_north_arrow(ax, x=0.92, y=0.88, fontsize=10):
        """Adds a clean north arrow to a map axis."""
        ax.annotate(
            "N",
            xy=(x, y + 0.08),
            xytext=(x, y - 0.04),
            xycoords="axes fraction",
            ha="center",
            va="center",
            fontsize=fontsize,
            fontweight="bold",
            color="#0F172A",
            arrowprops=dict(
                facecolor="#0F172A",
                edgecolor="#0F172A",
                width=2.2,
                headwidth=8,
                headlength=9,
            ),
            zorder=10,
        )

    @staticmethod
    def _add_scale_bar(ax, bounds, scale_km, bar_len, align="left", fontsize=8.0):
        """Adds a segmented black-and-white scale bar to a map axis."""
        import matplotlib.patches as mpatches

        x_span = bounds.right - bounds.left
        y_span = bounds.top - bounds.bottom
        if align == "right":
            x0 = bounds.right - bar_len - 0.05 * x_span
        else:
            x0 = bounds.left + 0.05 * x_span
        y0 = bounds.bottom + 0.055 * y_span
        bh = 0.017 * y_span

        ax.add_patch(
            mpatches.Rectangle((x0, y0), bar_len / 2, bh, facecolor="#0F172A", edgecolor="#0F172A", lw=0.8, zorder=10)
        )
        ax.add_patch(
            mpatches.Rectangle((x0 + bar_len / 2, y0), bar_len / 2, bh, facecolor="white", edgecolor="#0F172A", lw=0.8, zorder=10)
        )
        ax.text(x0, y0 + bh * 1.4, "0", ha="center", va="bottom", fontsize=fontsize, fontweight="bold", color="#0F172A", zorder=11)
        ax.text(x0 + bar_len / 2, y0 + bh * 1.4, f"{scale_km / 2:g}", ha="center", va="bottom", fontsize=fontsize, fontweight="bold", color="#0F172A", zorder=11)
        ax.text(x0 + bar_len, y0 + bh * 1.4, f"{scale_km} km", ha="center", va="bottom", fontsize=fontsize, fontweight="bold", color="#0F172A", zorder=11)

    @staticmethod
    def plot_feature_importance(importance_dict, title="AI-Soil Net: Feature Importance"):
        """Plots a professional bar chart for Random Forest Feature Importance."""
        df = pd.DataFrame(list(importance_dict.items()), columns=["Feature", "Importance Score"])
        df = df.sort_values(by="Importance Score", ascending=False)

        plt.figure(figsize=(12, 6))
        sns.barplot(x="Importance Score", y="Feature", data=df, palette="viridis")
        plt.title(title, fontsize=16, fontweight="bold")
        plt.xlabel("Gini Decrease (Importance)", fontsize=12)
        plt.ylabel("Spectral/Structural Features", fontsize=12)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_soil_quality_distribution(quality_data, title="Soil Quality Class Distribution"):
        """Plots a professional pie chart for soil quality classes."""
        plt.figure(figsize=(8, 8))
        colors = ["#d7191c", "#fdae61", "#ffffbf", "#a6d96a", "#1a9641"]
        labels = ["Very Low", "Low", "Moderate", "High", "Very High"]

        plt.pie(quality_data, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140, shadow=True)
        plt.title(title, fontsize=16, fontweight="bold")
        plt.show()

    @staticmethod
    def plot_single_index(
        tif_path,
        band_idx=1,
        index_name="NDVI",
        unit="Index Value",
        cmap=None,
        region_name="Study Area",
        year="2026",
        water_band_idx=8,
        output_prefix=None,
        dpi=600,
    ):
        """
        Generates a standalone publication-grade (600 DPI) map for any single
        spectral, radar, or soil band chosen by the researcher.
        """
        try:
            import numpy as np
            import rasterio
            import matplotlib.patches as mpatches
            from matplotlib.colors import ListedColormap
            from matplotlib.ticker import FormatStrFormatter
        except ImportError as e:
            raise ImportError(
                "Please install rasterio and matplotlib: pip install rasterio matplotlib"
            ) from e

        chosen_cmap = cmap if cmap else SoilVisualizer.DEFAULT_CMAPS.get(index_name.upper(), "viridis")
        out_name = output_prefix if output_prefix else f"{index_name}_{region_name.replace(' ', '_')}_Q1"

        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            crs = src.crs
            extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
            nodata = src.nodata

            arr = src.read(band_idx).astype("float32")
            if nodata is not None:
                arr[arr == nodata] = np.nan
            arr[~np.isfinite(arr)] = np.nan

            water_mask = None
            if water_band_idx and water_band_idx <= src.count and water_band_idx != band_idx:
                w_band = src.read(water_band_idx).astype("float32")
                if nodata is not None:
                    w_band[w_band == nodata] = np.nan
                valid_roi = np.isfinite(arr) | np.isfinite(w_band)
                water_mask = np.where((w_band >= 15) & valid_roi, 1.0, np.nan)

        WATER_BLUE = "#0B5ED7"
        is_geo = crs.is_geographic if crs is not None else True
        scale_km, bar_len = SoilVisualizer._compute_scale_bar(bounds, is_geo)

        plt.rcParams["font.family"] = "DejaVu Sans"
        fig, ax = plt.subplots(figsize=(9.5, 8.8), dpi=300)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("#F1F5F9")

        valid_vals = arr[np.isfinite(arr)]
        vmin, vmax = np.percentile(valid_vals, [2, 98])

        im = ax.imshow(arr, extent=extent, cmap=chosen_cmap, vmin=vmin, vmax=vmax, interpolation="nearest", zorder=2)
        if water_mask is not None:
            ax.imshow(water_mask, extent=extent, cmap=ListedColormap([WATER_BLUE]), vmin=0, vmax=1, interpolation="nearest", zorder=3)

        ax.grid(True, linestyle="--", linewidth=0.55, color="#94A3B8", alpha=0.6, zorder=1)
        for spine in ax.spines.values():
            spine.set_edgecolor("#1E293B")
            spine.set_linewidth(1.1)

        if is_geo:
            ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f°"))
            ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f°"))
        ax.locator_params(axis="x", nbins=5)
        ax.locator_params(axis="y", nbins=5)
        ax.tick_params(axis="both", labelsize=9.0, colors="#334155")

        SoilVisualizer._add_north_arrow(ax, x=0.93, y=0.88, fontsize=11)
        SoilVisualizer._add_scale_bar(ax, bounds, scale_km, bar_len, align="left", fontsize=8.5)

        cbar = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.045, pad=0.09, aspect=30)
        cbar.set_label(unit, fontsize=9.5, fontweight="bold", color="#1E293B", labelpad=4)
        cbar.ax.tick_params(labelsize=8.5, colors="#334155")

        if water_mask is not None:
            legend_handles = [
                mpatches.Patch(facecolor=WATER_BLUE, edgecolor="#0F172A", lw=0.6, label="Surface Water (JRC Mask)"),
                mpatches.Patch(facecolor="#F1F5F9", edgecolor="#94A3B8", lw=0.6, label="Outside ROI / Masked"),
            ]
            ax.legend(handles=legend_handles, loc="lower right", fontsize=8.5, frameon=True, facecolor="white", edgecolor="#CBD5E1")

        ax.set_title(f"{index_name} Spatial Distribution — {region_name} ({year})", fontsize=13, fontweight="bold", color="#0F172A", pad=10)

        plt.savefig(f"{out_name}.png", dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.savefig(f"{out_name}.pdf", bbox_inches="tight", facecolor="white")
        plt.show()
        logger.info("Saved: %s.png (%d DPI) & %s.pdf", out_name, dpi, out_name)

    @staticmethod
    def plot_multi_sensor_panels(
        tif_path,
        panels=None,
        region_name="Study Area",
        year="2026",
        water_band_idx=8,
        output_prefix="Multi_Sensor_Panels_Q1",
        dpi=600,
    ):
        """
        Generates a publication-grade (600 DPI) multi-panel map for any custom
        selection of bands/indices (defaults to 6 key eco-hydrological predictors).

        Parameters
        ----------
        tif_path : str
            Path to the multi-band GeoTIFF exported by AI-Soil Net.
        panels : list of dict, optional
            Custom list of panels, e.g.:
            [{"band": 1, "title": "(a) NDVI", "cmap": "RdYlGn", "unit": "Index"}]
        """
        try:
            import numpy as np
            import rasterio
            import matplotlib.patches as mpatches
            from matplotlib.colors import ListedColormap
            from matplotlib.ticker import FormatStrFormatter
        except ImportError as e:
            raise ImportError(
                "Please install rasterio and matplotlib: pip install rasterio matplotlib"
            ) from e

        selected_panels = panels if panels is not None else SoilVisualizer.DEFAULT_PANELS
        n_panels = len(selected_panels)
        if n_panels == 0:
            raise ValueError("The 'panels' list cannot be empty.")

        ncols = 3 if n_panels >= 3 else n_panels
        nrows = math.ceil(n_panels / ncols)

        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            crs = src.crs
            extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
            nodata = src.nodata

            band_data = {}
            for p in selected_panels:
                arr = src.read(p["band"]).astype("float32")
                if nodata is not None:
                    arr[arr == nodata] = np.nan
                arr[~np.isfinite(arr)] = np.nan
                band_data[p["band"]] = arr

            water_mask = None
            if water_band_idx and water_band_idx <= src.count:
                w_band = src.read(water_band_idx).astype("float32")
                if nodata is not None:
                    w_band[w_band == nodata] = np.nan
                ref_band = band_data[selected_panels[0]["band"]]
                valid_roi = np.isfinite(ref_band) | np.isfinite(w_band)
                water_mask = np.where((w_band >= 15) & valid_roi, 1.0, np.nan)

        WATER_BLUE = "#0B5ED7"
        water_cmap = ListedColormap([WATER_BLUE])
        is_geo = crs.is_geographic if crs is not None else True
        scale_km, bar_len = SoilVisualizer._compute_scale_bar(bounds, is_geo)

        plt.rcParams["font.family"] = "DejaVu Sans"
        fig, axes = plt.subplots(nrows, ncols, figsize=(5.5 * ncols, 5.6 * nrows), dpi=300)
        fig.patch.set_facecolor("white")

        axes_flat = np.atleast_1d(axes).ravel()
        bottom_left_idx = (nrows - 1) * ncols

        for idx, ax in enumerate(axes_flat):
            if idx >= n_panels:
                ax.axis("off")
                continue

            p = selected_panels[idx]
            data = band_data[p["band"]]
            ax.set_facecolor("#F1F5F9")
            valid_vals = data[np.isfinite(data)]
            vmin, vmax = np.percentile(valid_vals, [2, 98])

            im = ax.imshow(data, extent=extent, cmap=p.get("cmap", "viridis"), vmin=vmin, vmax=vmax, interpolation="nearest", zorder=2)
            if water_mask is not None:
                ax.imshow(water_mask, extent=extent, cmap=water_cmap, vmin=0, vmax=1, interpolation="nearest", zorder=3)

            ax.set_title(p["title"], fontsize=11.5, fontweight="bold", color="#0F172A", pad=8, loc="left")
            ax.grid(True, linestyle="--", linewidth=0.5, color="#94A3B8", alpha=0.6, zorder=1)
            for spine in ax.spines.values():
                spine.set_edgecolor("#334155")
                spine.set_linewidth(1.0)

            if is_geo:
                ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f°"))
                ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f°"))
            ax.locator_params(axis="x", nbins=4)
            ax.locator_params(axis="y", nbins=4)
            ax.tick_params(axis="both", labelsize=8.2, colors="#334155")
            if idx % ncols > 0:
                ax.tick_params(axis="y", labelleft=False)

            if idx == 0:
                SoilVisualizer._add_north_arrow(ax, x=0.92, y=0.88, fontsize=10)
            if idx == bottom_left_idx or (n_panels == 1 and idx == 0):
                SoilVisualizer._add_scale_bar(ax, bounds, scale_km, bar_len, align="left", fontsize=7.5)

            cbar = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.046, pad=0.11, aspect=26)
            cbar.set_label(p.get("unit", "Value"), fontsize=8.8, fontweight="bold", color="#1E293B", labelpad=3)
            cbar.ax.tick_params(labelsize=8.0, colors="#334155")

        fig.suptitle(
            f"Multi-Sensor Eco-Hydrological & Soil Predictors — {region_name} ({year})",
            fontsize=15, fontweight="bold", color="#0F172A", y=0.975,
        )

        legend_elements = [
            mpatches.Patch(facecolor=WATER_BLUE, edgecolor="#0F172A", lw=0.7, label="Surface Water (JRC Mask)"),
            mpatches.Patch(facecolor="#F1F5F9", edgecolor="#94A3B8", lw=0.7, label="Outside ROI / Dual-Masked Pixels (NDVI/NDWI)"),
        ]
        fig.legend(
            handles=legend_elements, loc="lower center", ncol=2, frameon=True,
            facecolor="white", edgecolor="#CBD5E1", fontsize=9.5, bbox_to_anchor=(0.5, 0.01),
        )

        plt.subplots_adjust(left=0.055, right=0.985, top=0.915, bottom=0.085, wspace=0.10, hspace=0.28)
        plt.savefig(f"{output_prefix}.png", dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.savefig(f"{output_prefix}.pdf", bbox_inches="tight", facecolor="white")
        plt.show()
        logger.info("Saved: %s.png (%d DPI) & %s.pdf", output_prefix, dpi, output_prefix)

    @staticmethod
    def plot_soil_quality_map(
        quality_tif_path,
        region_name="Study Area",
        country_name="Region",
        year="2026",
        water_tif_path=None,
        water_band_idx=8,
        output_prefix="Predicted_Soil_Quality_Q1",
        dpi=600,
    ):
        """
        Generates a publication-grade (600 DPI) Soil Quality Map with automatic
        Global and Regional inset maps, area percentages, north arrow, and scale bar.
        """
        try:
            import numpy as np
            import rasterio
            import matplotlib.patches as mpatches
            import matplotlib.gridspec as gridspec
            from matplotlib.colors import ListedColormap, BoundaryNorm
            from matplotlib.ticker import FormatStrFormatter
            import cartopy.crs as ccrs
            import cartopy.feature as cfeature
        except ImportError as e:
            raise ImportError(
                "Please install rasterio and cartopy: pip install rasterio cartopy matplotlib"
            ) from e

        with rasterio.open(quality_tif_path) as src:
            q_arr = src.read(1).astype("float32")
            q_bounds = src.bounds
            q_crs = src.crs
            q_extent = [q_bounds.left, q_bounds.right, q_bounds.bottom, q_bounds.top]
            if src.nodata is not None:
                q_arr[q_arr == src.nodata] = np.nan
            q_arr[~np.isfinite(q_arr)] = np.nan

        water_mask, w_extent = None, None
        if water_tif_path:
            with rasterio.open(water_tif_path) as wsrc:
                w_arr = wsrc.read(water_band_idx).astype("float32")
                wb = wsrc.bounds
                w_extent = [wb.left, wb.right, wb.bottom, wb.top]
                if wsrc.nodata is not None:
                    w_arr[w_arr == wsrc.nodata] = np.nan
                water_mask = np.where(w_arr >= 15, 1.0, np.nan)

        valid_q = q_arr[np.isfinite(q_arr)]
        p2, p98 = np.percentile(valid_q, [2, 98])
        bins = np.linspace(p2, p98, 6)
        bins[0], bins[-1] = np.nanmin(valid_q) - 1e-5, np.nanmax(valid_q) + 1e-5

        class_names = ["Very Low Quality", "Low Quality", "Moderate Quality", "High Quality", "Very High Quality"]
        class_colors = ["#d73027", "#fc8d59", "#fee08b", "#91cf60", "#1a9850"]
        WATER_BLUE = "#0B5ED7"

        total_px = len(valid_q)
        class_pcts = [
            100.0 * np.sum((valid_q >= bins[i]) & (valid_q < bins[i + 1] if i < 4 else valid_q <= bins[i + 1])) / total_px
            for i in range(5)
        ]

        cmap_q = ListedColormap(class_colors)
        norm_q = BoundaryNorm(bins, cmap_q.N)

        center_lon = (q_bounds.left + q_bounds.right) / 2.0
        center_lat = (q_bounds.bottom + q_bounds.top) / 2.0
        is_geo = q_crs.is_geographic if q_crs is not None else True
        scale_km, bar_len = SoilVisualizer._compute_scale_bar(q_bounds, is_geo)

        plt.rcParams["font.family"] = "DejaVu Sans"
        fig = plt.figure(figsize=(15.5, 9.2), dpi=300)
        fig.patch.set_facecolor("white")
        gs = gridspec.GridSpec(
            2, 2, width_ratios=[1.0, 1.85], height_ratios=[1.0, 1.35],
            wspace=0.14, hspace=0.22, left=0.04, right=0.97, top=0.90, bottom=0.06,
        )

        # (a) Global Location Inset
        ax_world = fig.add_subplot(gs[0, 0], projection=ccrs.Robinson())
        ax_world.set_global()
        ax_world.add_feature(cfeature.OCEAN, facecolor="#E0F2FE", zorder=0)
        ax_world.add_feature(cfeature.LAND, facecolor="#E2E8F0", edgecolor="#94A3B8", lw=0.4, zorder=1)
        ax_world.add_feature(cfeature.BORDERS, edgecolor="#CBD5E1", lw=0.3, zorder=2)
        if is_geo:
            ax_world.plot(
                center_lon, center_lat, marker="o", color="#DC2626", markersize=7.5,
                markeredgecolor="white", markeredgewidth=1.0, transform=ccrs.PlateCarree(), zorder=5,
            )
        ax_world.set_title("(a) Global Location", fontsize=11, fontweight="bold", color="#0F172A", loc="left", pad=6)

        # (b) Regional Context Inset
        ax_reg = fig.add_subplot(gs[1, 0], projection=ccrs.PlateCarree())
        if is_geo:
            ax_reg.set_extent([center_lon - 6.5, center_lon + 6.5, center_lat - 5.5, center_lat + 5.5], crs=ccrs.PlateCarree())
            ax_reg.plot(
                center_lon, center_lat, marker="*", color="#DC2626", markersize=13,
                markeredgecolor="white", markeredgewidth=0.8, transform=ccrs.PlateCarree(), zorder=6,
            )
            ax_reg.text(
                center_lon, center_lat + 1.2, region_name, fontsize=8.5, fontweight="bold", color="#991B1B",
                ha="center", bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#DC2626", lw=0.8, alpha=0.9),
                transform=ccrs.PlateCarree(), zorder=7,
            )
        ax_reg.add_feature(cfeature.OCEAN, facecolor="#DBEAFE", zorder=0)
        ax_reg.add_feature(cfeature.LAND, facecolor="#F8FAFC", zorder=1)
        ax_reg.add_feature(cfeature.COASTLINE, edgecolor="#475569", lw=0.8, zorder=2)
        ax_reg.add_feature(cfeature.BORDERS, edgecolor="#334155", lw=1.0, zorder=2)
        ax_reg.add_feature(cfeature.RIVERS, edgecolor="#3B82F6", lw=1.0, zorder=3)
        gl = ax_reg.gridlines(draw_labels=True, linewidth=0.4, color="#94A3B8", alpha=0.6, linestyle="--")
        gl.top_labels = gl.right_labels = False
        gl.xlabel_style = gl.ylabel_style = {"size": 7.8, "color": "#334155"}
        ax_reg.set_title(f"(b) Regional Context ({country_name})", fontsize=11, fontweight="bold", color="#0F172A", loc="left", pad=6)

        # (c) Main Predicted Soil Quality Map
        ax_main = fig.add_subplot(gs[:, 1])
        ax_main.set_facecolor("#F1F5F9")
        ax_main.imshow(q_arr, extent=q_extent, cmap=cmap_q, norm=norm_q, interpolation="nearest", zorder=2)
        if water_mask is not None:
            ax_main.imshow(water_mask, extent=w_extent, cmap=ListedColormap([WATER_BLUE]), vmin=0, vmax=1, interpolation="nearest", zorder=3)

        ax_main.grid(True, linestyle="--", linewidth=0.55, color="#94A3B8", alpha=0.6, zorder=1)
        for spine in ax_main.spines.values():
            spine.set_edgecolor("#1E293B")
            spine.set_linewidth(1.1)
        if is_geo:
            ax_main.xaxis.set_major_formatter(FormatStrFormatter("%.2f°"))
            ax_main.yaxis.set_major_formatter(FormatStrFormatter("%.2f°"))
        ax_main.locator_params(axis="x", nbins=5)
        ax_main.locator_params(axis="y", nbins=5)
        ax_main.tick_params(axis="both", labelsize=9.0, colors="#334155")

        SoilVisualizer._add_north_arrow(ax_main, x=0.93, y=0.88, fontsize=11)
        SoilVisualizer._add_scale_bar(ax_main, q_bounds, scale_km, bar_len, align="right", fontsize=8.5)

        ax_main.set_title(
            f"(c) Predicted Soil Quality Map — {region_name} ({year})",
            fontsize=11.5, fontweight="bold", color="#0F172A", loc="left", pad=8,
        )

        legend_handles = [
            mpatches.Patch(
                facecolor=class_colors[i], edgecolor="#334155", lw=0.6,
                label=f"{class_names[i]} ({class_pcts[i]:.1f}%)",
            )
            for i in range(5)
        ]
        if water_mask is not None:
            legend_handles.append(mpatches.Patch(facecolor=WATER_BLUE, edgecolor="#0F172A", lw=0.6, label="Surface Water"))
        legend_handles.append(mpatches.Patch(facecolor="#F1F5F9", edgecolor="#94A3B8", lw=0.6, label="Outside ROI / Masked"))

        ax_main.legend(
            handles=legend_handles, title="Predicted_MASQI Classes", title_fontsize=9.2,
            fontsize=8.5, loc="lower left", frameon=True, facecolor="white",
            edgecolor="#CBD5E1", framealpha=0.95,
        )

        fig.suptitle(
            f"Spatial Transfer Learning Soil Quality Assessment — {region_name} ({year})",
            fontsize=14.5, fontweight="bold", color="#0F172A", y=0.965,
        )

        plt.savefig(f"{output_prefix}.png", dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.savefig(f"{output_prefix}.pdf", bbox_inches="tight", facecolor="white")
        plt.show()
        logger.info("Saved: %s.png (%d DPI) & %s.pdf", output_prefix, dpi, output_prefix)
