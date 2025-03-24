import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import rasterio
import rasterio.warp
import rasterio.features
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

if __name__ == '__main__':
    # Load the first shapefile (polygons with 'Dead' and 'Alive' labels)
    polygons = gpd.read_file("C:/Users/sebastiaan_verbessel/PycharmProjects/Labelme/Labeler2_merged.gpkg")

    # Load the second shapefile (tiles with TileID)
    tiles = gpd.read_file("C:/Users/sebastiaan_verbessel/PycharmProjects/Labelme/Tiles_sel.shp")

    # Load the raster file
    raster_path = "C:/Users/sebastiaan_verbessel/PycharmProjects/Labelme/testdata_Thomas/UAV/NDVI_threshold/resultaat vitaliteit drone NDVI/result_vitality_Arendonk.tif"
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs  # Get raster CRS
        if raster_crs != tiles.crs:
            transform, width, height = rasterio.warp.calculate_default_transform(
                src.crs, tiles.crs, src.width, src.height, *src.bounds
            )
            kwargs = src.meta.copy()
            kwargs.update({
                "crs": tiles.crs,
                "transform": transform,
                "width": width,
                "height": height
            })
            with rasterio.open("reprojected_raster.tif", "w", **kwargs) as dst:
                for i in range(1, src.count + 1):
                    rasterio.warp.reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=tiles.crs,
                        resampling=rasterio.enums.Resampling.nearest
                    )
        raster_path = "reprojected_raster.tif"

    # Reload reprojected raster
    with rasterio.open(raster_path) as src:
        raster_data = src.read(1)
        raster_transform = src.transform

    # Ensure both shapefiles have the same CRS
    if polygons.crs != tiles.crs:
        polygons = polygons.to_crs(tiles.crs)

    # Initialize results lists
    vector_results = []
    raster_results = []

    # Iterate over each tile
    for _, tile in tiles.iterrows():
        tile_id = tile["TileID"]
        tile_geom = tile.geometry

        # Clip the polygons to the current tile area
        clipped = gpd.overlay(polygons, gpd.GeoDataFrame(geometry=[tile_geom], crs=tiles.crs), how='intersection')

        # Calculate total tile area
        total_area = tile_geom.area

        # Calculate area per class from vector data
        area_dead = clipped.loc[clipped["Label"] == "Dead", "geometry"].area.sum()
        area_alive = clipped.loc[clipped["Label"] == "Alive", "geometry"].area.sum()

        # Calculate percentages from vector data
        dead_percentage = (area_dead / total_area) * 100
        alive_percentage = (area_alive / total_area) * 100
        soil_percentage = 100 - (dead_percentage + alive_percentage)

        vector_results.append({
            "TileID": tile_id,
            "Dead_Percentage_Vector": round(dead_percentage, 2),
            "Alive_Percentage_Vector": round(alive_percentage, 2),
            "Soil_Percentage_Vector": round(soil_percentage, 2)
        })

        # Raster processing: Extract values within tile
        mask = rasterio.features.geometry_mask([tile_geom], transform=raster_transform, invert=True,
                                               out_shape=raster_data.shape)
        tile_pixels = raster_data[mask]

        # Compute raster percentages
        total_pixels = tile_pixels.size
        dead_pixels = np.sum(tile_pixels == 0)
        alive_pixels = np.sum(tile_pixels == 1)

        dead_percentage_raster = (dead_pixels / total_pixels) * 100
        alive_percentage_raster = (alive_pixels / total_pixels) * 100
        soil_percentage_raster = 100 - (dead_percentage_raster + alive_percentage_raster)

        raster_results.append({
            "TileID": tile_id,
            "Dead_Percentage_Raster": round(dead_percentage_raster, 2),
            "Alive_Percentage_Raster": round(alive_percentage_raster, 2),
            "Soil_Percentage_Raster": round(soil_percentage_raster, 2)
        })

    # Convert results to DataFrames
    vector_df = pd.DataFrame(vector_results)
    raster_df = pd.DataFrame(raster_results)

    # Merge vector and raster results
    merged_df = vector_df.merge(raster_df, on="TileID")
    merged_df.to_csv("tile_analysis_combined.csv", index=False)

    # Scatterplot comparison
    plt.figure(figsize=(12, 6))
    classes = ["Dead", "Alive", "Soil"]
    for cls in classes:
        plt.scatter(merged_df[f"{cls}_Percentage_Vector"], merged_df[f"{cls}_Percentage_Raster"], label=cls, alpha=0.7)

    # Add one-to-one line
    plt.plot([0, 100], [0, 100], linestyle='--', color='black', linewidth=1, label='1:1 Line')
    plt.xlabel("Vector Data Percentage")
    plt.ylabel("Raster Data Percentage")
    plt.title("Comparison of Vector and Raster-Based Percentage Calculations")
    plt.legend()
    plt.grid()
    plt.show()

    # Pearson correlation test
    for cls in classes:
        corr, p_value = pearsonr(merged_df[f"{cls}_Percentage_Vector"], merged_df[f"{cls}_Percentage_Raster"])

        MAD = np.mean(np.abs(merged_df[f"{cls}_Percentage_Vector"] - merged_df[f"{cls}_Percentage_Raster"]))
        print(f"Pearson correlation for {cls}: r = {corr:.2f}, p = {p_value:.4f}")
        print(f"Mean Absolute Difference for {cls}: MAD = {MAD:.2f}")

    print("Analysis complete. Results saved to tile_analysis_combined.csv")