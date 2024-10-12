import networkx as nx
import matplotlib.pyplot as plt
import random


# G = nx.gnm_random_graph(10, 20)
# for u, v in G.edges():
#     G[u][v]['pop_dist'] = random.randint(1, 10)
#     G[u][v]['risk'] = random.randint(1, 10)
#     G[u][v]['fresh_water'] = random.randint(1, 10)

# # Accessing the multiple weights of an edge
# edge_data = G.get_edge_data(0, 1)
# print(edge_data)

# # visualize the graph with edge weights as cool-warm colors
# edge_weights = [G[u][v]['pop_dist'] for u, v in G.edges()]
# nx.draw(G, edge_color=edge_weights, edge_cmap=plt.cm.coolwarm, with_labels=True)
# plt.show()

import geopandas as gpd

# Step 1: Load the shapefile
shapefile_path = 'Data\Ashville Road Shp files\Buncombe_Couny_Centerline_Data.shp'
gdf = gpd.read_file(shapefile_path)

# Step 2: Inspect the first few rows of the shapefile (including vector data)
# print(gdf.head())

# Step 3: Extract the geometry column (which holds the vector data)
geometry = gdf['geometry']
centerline = gdf['CENTERLINE']

# Step 4: Loop through the geometries and print the type and coordinates
# for i, geom in enumerate(geometry):
#     # print(centerline[i])
#     if centerline[i] == 9648605129:
#         print(geom.coords)

# Create network using geometry coordinates, where edges connect geometries that share a coordinate
G = nx.Graph()
for i, geom in enumerate(geometry):
    if geom.geom_type != 'LineString':
        print(f"Skipping geometry of type {geom.geom_type}")
        continue
    coords = geom.coords
    for i in range(len(coords) - 1):
        from_node = f"{coords[i]}"
        to_node = f"{coords[i+1]}"
        G.add_edge(from_node, to_node)

# Save the network to visualize in Gephi
nx.write_gexf(G, "Data\Buncombe_Couny_Centerline_Data.gexf")

# Read edge data from a file
# import pandas as pd
# file_path = "Data\Ashville Road CSV\Buncombe_Couny_Centerline_Data.csv"
# df = pd.read_csv(file_path)

# # Initialize an empty Graph
# G = nx.Graph()

# # Add edges using CENTERLINE_ID, and using dummy intersections for now
# for _, row in df.iterrows():
#     # Create unique nodes for each road segment based on CENTERLINE_ID and elevations
#     from_node = f"{row['CENTERLINE_ID']}_start_{row['FromElevation']}"
#     to_node = f"{row['CENTERLINE_ID']}_end_{row['ToElevation']}"
    
#     # Add edge with the street name as a label
#     G.add_edge(from_node, to_node, street=row['FULL_STREET_NAME'], length=row['Shape__Length'])


# # Step 4: save to visualize in Gephi
# nx.write_gexf(G, "Data\Buncombe_Couny_Centerline_Data.gexf")