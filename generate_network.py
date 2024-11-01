import networkx as nx

import geopandas as gpd
import pandas as pd
import math
import numpy as np

# Step 1: Load the shapefile
shapefile_path = 'Data\Ashville Road Shp files\Buncombe_Couny_Centerline_Data.shp'
gdf = gpd.read_file(shapefile_path)

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

def create_graph(gdf):
    G = nx.Graph()
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
        G.add_edge(geom.coords[0], 
                    geom.coords[-1], 
                    weight=weight,
                    SPEED_LIM=row['SPEED_LIMI'],
                    street_type=row['STREET_TYP'],
                    full_street=row['FULL_STREE'],
                    one_way=row['OneWay'],
                    road_class=row['ROAD_CLASS'])
        

    print("total nodes: ", len(G.nodes))
    print("total edges: ", len(G.edges))
    return G

def get_edge_weight(G, edge, speed_limit = False):
    weight = G[edge[0]][edge[1]]['weight']
    if speed_limit:
        speed_limit = G[edge[0]][edge[1]]['speed_limit']
        weight = weight * speed_limit
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


def remove_connector_nodes(G):
    nodes_to_remove = set()
    edges_to_add = set()
    nodes_processed = set()
    
    for i, node in enumerate(G.nodes):
        # If the node has only two neighbors, it is a connector node and should be removed
        if G.degree[node] == 2 and node not in nodes_to_remove and node not in nodes_processed:
            neighbors = list(G.neighbors(node))
            new_edge = combine_edges(G, (node, neighbors[0]), (node, neighbors[1]))

            # Find two intersection nodes
            current_string = set([node])
            left_node = neighbors[0]
            # Traverse left nodes until a node with more than 2 neighbors is found or 
            while G.degree[left_node] == 2:
                # Find the neighbor that is not the current string
                next_node = get_next_node(G, left_node, current_string)
                # Update the weight
                new_edge = combine_edges(G, (new_edge[0], new_edge[1]), (left_node, next_node))
                current_string.add(left_node)
                left_node = next_node


            right_node = neighbors[1]
            # Traverse right nodes until a node with more than 2 neighbors is found or
            while G.degree[right_node] == 2:
                # Find the neighbor that is not the current string
                next_node = get_next_node(G, right_node, current_string)
                # Update the weight
                new_edge = combine_edges(G, (new_edge[0], new_edge[1]), (right_node, next_node))
                current_string.add(right_node)
                right_node = next_node

            # Sanity check
            degrees = [G.degree(x) for x in current_string] 
            if 3 in degrees or 1 in degrees:
                print("error")

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

        G.add_edge(edge[0], edge[1], weight=edge[2])


    
    return G

# Example usage
G = create_graph(gdf)

# display number of components
# print("Number of connected components: ", nx.number_connected_components(G))
# only save the largest connected component
# largest_component = max(nx.connected_components(G), key=len)
# G = G.subgraph(largest_component).copy()

# G = remove_connector_nodes(G)



# save the graph to a gml file
nx.write_gml(G, 'Data\Buncombe_Couny_Centerline_Data.gml')