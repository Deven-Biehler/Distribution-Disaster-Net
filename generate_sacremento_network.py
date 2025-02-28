import networkx as nx

import geopandas as gpd
import pandas as pd
import math
import numpy as np

# Step 1: Load the shapefile
shapefile_path = 'Data/Sacremento Shp Files/roads/tl_2021_06067_roads.shp'
gdf = gpd.read_file(shapefile_path)

risk_path = "Data/Sacremento Shp Files/flood_data/USA_Flood_Hazard_Reduced_Set.shp"
risk = gpd.read_file(risk_path)

# print size of both
print("Shapefile size: ", gdf.shape)
print("Risk size: ", risk.shape)


# Step 2: Inspect the first few rows of the shapefile (including vector data)
# print(gdf.head())

# Step 3: Extract the geometry column (which holds the vector data)
geometry = gdf['geometry']
centerline = gdf['CENTERLINE']

# Create a bounding box for the entire dataset
minx, miny, maxx, maxy = gdf.total_bounds
rangex = maxx - minx
rangey = maxy - miny

marginx = rangex * 0
marginy = rangey * 0

new_minx = minx + marginx
new_miny = miny + marginy
new_maxx = maxx - marginx
new_maxy = maxy - marginy

PROPERTIES = ['SPEED_LIMI', 'STREET_TYP', 'FULL_STREE', 'OneWay', 'ROAD_CLASS']
types = [float, str, str, float, int]

def create_graph(gdf, risk):
    G = nx.Graph()
    risk_coords = set()
    for i, row in risk.iterrows():
        geom = row['geometry']
        if geom.geom_type != 'LineString':
            print(f"Skipping geometry of type {geom.geom_type}")
            continue
        for coords in geom.coords:
            risk_coords.add(coords)
    
    for i, row in gdf.iterrows():
        error = False
        for property in PROPERTIES:
            if property not in row:
                print(f"Error: {property} not found in row")
                error = True
                break
            if row[property] is None:
                # print(f"Error: {property} is None")
                error = True
                break
            if type(row[property]) != types[PROPERTIES.index(property)]:
                print(f"Error: {property} has type {type(row[property])} instead of {types[PROPERTIES.index(property)]}")
                error = True
                break
        if error:
            continue


        geom = row['geometry']
        weight = geom.length

        if row["STREET_TYP"] == 'RIV' or row["STREET_TYP"] == 'TRL':
            continue
        # filter out centerlines that are outside the bounding box
        if geom.bounds[0] < new_minx or geom.bounds[1] < new_miny or geom.bounds[2] > new_maxx or geom.bounds[3] > new_maxy:
            continue
        if geom.geom_type != 'LineString':
            print(f"Skipping geometry of type {geom.geom_type}")
            continue
            # weight = math.sqrt((geom.coords[i][0] - geom.coords[i + 1][0])**2 + (geom.coords[i][1] - geom.coords[i + 1][1])**2)
        risk = 0
        for geom_coords in geom.coords:
            if geom_coords in risk_coords:
                risk = 1
        speed_limit = row['SPEED_LIMI']
        weight = weight * speed_limit
        G.add_edge(geom.coords[0], 
                    geom.coords[-1], 
                    weight=weight,
                    risk=risk)
        

    print("total nodes: ", len(G.nodes))
    print("total edges: ", len(G.edges))
    return G

def get_edge_weight(G, edge):
    weight = G[edge[0]][edge[1]]['weight']
    return weight

def get_next_node(G, left_node, current_string):
    next_left = list(G.neighbors(left_node))[0]
    next_right = list(G.neighbors(left_node))[1]
    if next_left not in current_string or G.degree[next_left] != 2:
        next_node = next_left
    else:
        next_node = next_right
    if next_node in current_string and G.degree(next_node) == 2:
        print("error")
    return next_node

def combine_edges(G, edge1, edge2):
    # Check if the edges share a node
    weight = get_edge_weight(G, edge1) + get_edge_weight(G, edge2)
    risk = G[edge1[0]][edge1[1]]['risk'] or G[edge2[0]][edge2[1]]['risk']
    if edge1[0] == edge2[0]:
        return (edge1[1], edge2[1], weight, risk)
    if edge1[0] == edge2[1]:
        return (edge1[1], edge2[0], weight, risk)
    if edge1[1] == edge2[0]:
        return (edge1[0], edge2[1], weight, risk)
    if edge1[1] == edge2[1]:
        return (edge1[0], edge2[0], weight, risk)
    return None

def remove_connector_nodes(G):
    nodes_to_remove = set()
    edges_to_add = set()
    nodes_processed = set()
    
    for i, node in enumerate(G.nodes):
        # If the node has only two neighbors, it is a connector node and should be removed
        neighbors = list(G.neighbors(node))
        if len(neighbors) == 2 and node not in nodes_to_remove and node not in nodes_processed:
            weight = G[node][neighbors[0]]['weight'] + G[node][neighbors[1]]['weight']
            risk = G[node][neighbors[0]]['risk'] or G[node][neighbors[1]]['risk']
            new_edge = (neighbors[0], neighbors[1], weight, risk)

            # Find two intersection nodes
            current_string = set([node])
            left_node = neighbors[0]
            # Traverse left nodes until a node with more than 2 neighbors is found or 
            while G.degree[left_node] == 2:
                # Find the neighbor that is not the current string
                next_node = get_next_node(G, left_node, current_string)
                # Update the weight
                weight += G[left_node][next_node]['weight']
                # Update the risk
                risk = risk or G[left_node][next_node]['risk']
                current_string.add(left_node)
                left_node = next_node


            right_node = neighbors[1]
            # Traverse right nodes until a node with more than 2 neighbors is found or
            while G.degree[right_node] == 2:
                # Find the neighbor that is not the current string
                next_node = get_next_node(G, right_node, current_string)
                # Update the weight
                weight += G[right_node][next_node]['weight']
                # Update the risk
                risk = risk or G[right_node][next_node]['risk']
                current_string.add(right_node)
                right_node = next_node

            # Sanity check
            degrees = [G.degree(x) for x in current_string] 
            if 3 in degrees or 1 in degrees:
                print("error")

            new_edge = (left_node, right_node, weight, risk)
            nodes_to_remove.update(current_string)
            current_string.update([left_node, right_node])
            nodes_processed.update(current_string)
            edges_to_add.add(new_edge)


    print(f"Processed {len(nodes_processed)} nodes")
    print(f"Removing {len(nodes_to_remove)} nodes")
    # Remove the nodes and add new edges
    for node in nodes_to_remove:
        G.remove_node(node)

    for edge in edges_to_add: # TODO for some reason, the edges add back all the nodes meant to be removed
        if edge[0] in nodes_to_remove or edge[1] in nodes_to_remove:
            print("skipping edge")
            continue

        G.add_edge(edge[0], edge[1], weight=edge[2], risk=edge[3])

    return G

# Example usage
G = create_graph(gdf, risk)
G = remove_connector_nodes(G)


# display number of components
# print("Number of connected components: ", nx.number_connected_components(G))
# only save the largest connected component
# largest_component = max(nx.connected_components(G), key=len)
# G = G.subgraph(largest_component).copy()

# G = remove_connector_nodes(G)



# save the graph to a gml file
nx.write_gml(G, 'Data\sacremento.gml')