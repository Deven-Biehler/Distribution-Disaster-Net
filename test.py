import os
import geopandas as gpd

# Load the shapefile
shapefile_path = 'Data/Ashville Road Shp files/Buncombe_Couny_Centerline_Data.shp'
gdf = gpd.read_file(shapefile_path)

# Print the first few rows of the GeoDataFrame
print(list(gdf.columns))