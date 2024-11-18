from shapely.geometry import Point
from shapely.ops import nearest_points
from shapely.geometry import MultiPoint
import math



def add_safe_zones(G, points):
    # find closest node to each point
    for point in points:
        nearest = None
        min_dist = float('inf')
        for node in G.nodes:
            dist = point.distance(Point(eval(node)))
            if dist < min_dist:
                min_dist = dist
                nearest = node
        G.nodes[nearest]['safe_zone'] = True

    return G
    

# Read shapefile
import geopandas as gpd
gdf = gpd.read_file("Data\Ashville Road Shp files\evac\\flood_evac.shp")
# read coordinates of points from shapefile
points = gdf['geometry']

import networkx as nx
network_path = "Data\Buncombe_Couny_Centerline_Data.gml"
G = nx.read_gml(network_path)
G = add_safe_zones(G, points)

# Save the graph
nx.write_gml(G, "Data\Buncombe_Couny_Centerline_Data.gml")
