import geopandas as gpd
from shapely.ops import nearest_points
from shapely.strtree import STRtree
import time

def add_population_density():
    # Set the maximum allowable distance (adjust based on your CRS and data)
    MAX_DISTANCE = 0.03

    # Load shapefiles
    polygons_gdf = gpd.read_file("Data/Ashville_Population/blocks.shp")
    lines_gdf = gpd.read_file("Data\Ashville_Roads\Buncombe_Couny_Centerline_Data.shp")

    # Ensure both GeoDataFrames have the same CRS
    if polygons_gdf.crs != lines_gdf.crs:
        lines_gdf = lines_gdf.to_crs(polygons_gdf.crs)

    # Compute centroids of polygons
    polygons_gdf['centroid'] = polygons_gdf.geometry.centroid

    # Use centroids for distance calculations
    centroids = polygons_gdf[['centroid', 'POP20']]
    centroids = gpd.GeoDataFrame(centroids, geometry='centroid')

    # Build spatial index for lines
    line_geometries = lines_gdf.geometry.tolist()
    line_index = STRtree(line_geometries)

    start_time = time.time()

    # Function to find the nearest line using spatial index with distance threshold
    def find_nearest_line_with_threshold(centroid):
        # Query the spatial index for the nearest line
        nearest_line_idx = line_index.nearest(centroid)  # Returns the index of the closest geometry
        nearest_line = line_geometries[nearest_line_idx]  # Retrieve the geometry using the index
        
        # Check the distance; return None if it's greater than the threshold
        if centroid.distance(nearest_line) > MAX_DISTANCE:
            return None
        return nearest_line

    # Find nearest line and assign it to centroids, considering the threshold
    centroids['closest_line'] = centroids.geometry.apply(find_nearest_line_with_threshold)

    print(f"Processing time: {time.time() - start_time} seconds")

    # Filter out polygons with no valid closest line
    centroids = centroids[centroids['closest_line'].notnull()]

    # Group by closest line and sum the population values
    grouped_gdf = centroids.groupby("closest_line").agg({
        "POP20": "sum"  # Sum the population values
    }).reset_index()

    # Ensure all original lines and attributes are included, even if they don't have a label
    grouped_gdf = grouped_gdf.merge(
        lines_gdf,
        left_on="closest_line",
        right_on="geometry",
        how="right"
    )

    # Replace NaN with 0 for lines without associated blocks
    grouped_gdf['POP20'] = grouped_gdf['POP20'].fillna(0)

    # Drop the additional geometry column ('closest_line')
    grouped_gdf.drop(columns=['closest_line'], inplace=True)

    # Convert back to GeoDataFrame and set the geometry
    grouped_gdf = gpd.GeoDataFrame(
        grouped_gdf,
        geometry="geometry",
        crs=lines_gdf.crs
    )

    # Save the GeoDataFrame to a file
    grouped_gdf.to_file("Data/temp/population_mapping.shp")

    return grouped_gdf


if __name__ == "__main__":
    add_population_density()
