import os
import rasterio
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import shape, box
from rasterio.warp import calculate_default_transform, reproject, Resampling


def reproject_raster(src, dst_crs):
    """Reprojects a raster to a specified CRS."""
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds)

    kwargs = src.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height
    })

    with rasterio.MemoryFile() as memfile:
        with memfile.open(**kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest
                )
        return memfile.open()


def clip_raster(raster_path, plots, target_folder):
    """Clips a raster using all overlapping plots from a GeoDataFrame."""
    with rasterio.open(raster_path) as src:
        if src.crs.to_epsg() != 31370:
            src = reproject_raster(src, 'EPSG:31370')

        raster_bounds = box(*src.bounds)
        overlapping_plots = plots[plots.intersects(raster_bounds)]

        for _, plot in overlapping_plots.iterrows():
            geom = [plot.geometry]
            try:
                out_image, out_transform = mask(src, geom, crop=True)
            except Exception as e:
                print(f"Skipping plot {plot['naam']} due to error: {e}")
                continue

            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })

            output_path = os.path.join(target_folder,
                                       f"{os.path.basename(raster_path).split('.')[0]}_{plot['naam']}_clipped.tif")
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(out_image)


def main(input_folder, geojson_path, output_folder):
    """Main function to process all JP2 files and clip them with overlapping plots."""
    os.makedirs(output_folder, exist_ok=True)
    plots = gpd.read_file(geojson_path)

    if plots.crs.to_epsg() != 31370:
        plots = plots.to_crs(epsg=31370)

    for file in os.listdir(input_folder):
        if file.endswith(".jp2"):
            clip_raster(os.path.join(input_folder, file), plots, output_folder)


if __name__ == "__main__":
    main("./OrthoB_MS_winter_2023/jpeg_files", "./testdata_Thomas/locaties bosbestanden/plots.geojson", "./OrthoB_MS_winter_2023/clips")