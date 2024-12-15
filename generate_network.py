import networkx as nx

import geopandas as gpd
import pandas as pd
import math
import numpy as np
import random



def create_edge(node1, node2, properties):
    edge = {
        "node1": node1,
        "node2": node2,
        "properties": properties
    }
    return edge

def get_risk_coords(risk):
    risk_coords = set()
    for i, row in risk.iterrows():
        geom = row['geometry']
        if geom.geom_type != 'LineString':
            print(f"Skipping geometry of type {geom.geom_type}")
            continue
        for coords in geom.coords:
            risk_coords.add(coords)
    return risk_coords

def add_risk(G, risk):
    risk_coords = get_risk_coords(risk)
    # round the coordinates to 5 decimal places
    # risk_coords = set([(round(x, 5), round(y, 5)) for (x, y) in risk_coords])
    edges = list(G.edges)
    # edges = [(round(x, 5), round(y, 5)) for edge in edges for x, y in edge]
    for edge in edges:
        if edge[0] in risk_coords or edge[1] in risk_coords:
            G[edge[0]][edge[1]]['risk'] = random.random() / 3
        else:
            G[edge[0]][edge[1]]['risk'] = 0
    return G

def create_graph(gdf, risk):
    # Create a bounding box for the entire dataset
    # minx, miny, maxx, maxy = gdf.total_bounds
    # rangex = maxx - minx
    # rangey = maxy - miny

    # marginx = rangex * 0
    # marginy = rangey * 0

    # new_minx = minx + marginx
    # new_miny = miny + marginy
    # new_maxx = maxx - marginx
    # new_maxy = maxy - marginy

    PROPERTIES = list(gdf.columns)


    G = nx.Graph()
    
    for i, row in gdf.iterrows():
        error = False
        for property in PROPERTIES:
            if property not in row:
                print(f"Error: {property} not found in row")
                error = True
                break
        if error:
            continue


        geom = row['geometry']

        # Filter out centerlines that are not roads
        if row["STREET_TYP"] == 'RIV' or row["STREET_TYP"] == 'TRL':
            continue


        if geom.geom_type != 'LineString':
            # print(f"Skipping geometry of type {geom.geom_type}")
            continue
        
        edge_attributes = {
            'weight': geom.length
        }

        for property in PROPERTIES:
            # Check if the property is a number
            if isinstance(row[property], (int, float)):
                edge_attributes[property] = row[property]
        
        G.add_edge(geom.coords[0], 
                    geom.coords[-1],
                    **edge_attributes)
        
    G = add_risk(G, risk)
        

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

def accumulate_proerties(properties1, properties2):
    properties = {}
    for key in properties1.keys():
        # check for the risk property
        if key == 'risk':
            properties[key] = max(properties1[key], properties2[key])
            continue
        # Check if the property is a number
        if isinstance(properties1[key], (int, float)) and isinstance(properties2[key], (int, float)):
            properties[key] = properties1[key] + properties2[key]
        
        # accumulate all of the object ids for late use
        if property == 'geometry':
            properties[key] = []
            if isinstance(properties1[key], list):
                properties[key].extend(properties1[key])
            else:
                properties[key].append(properties1[key])
            if isinstance(properties2[key], list):
                properties[key].extend(properties2[key])
            else:
                properties[key].append(properties2[key])
    return properties




def combine_edges(edge1, edge2):
    # Check if the edges share a node
    new_properties = accumulate_proerties(edge1, edge2)
    if edge1[0] == edge2[0]:
        return (edge1[1], edge2[1], new_properties)
    if edge1[0] == edge2[1]:
        return (edge1[1], edge2[0], new_properties)
    if edge1[1] == edge2[0]:
        return (edge1[0], edge2[1], new_properties)
    if edge1[1] == edge2[1]:
        return (edge1[0], edge2[0], new_properties)
    return None


# Simplifies the network by removing connector nodes and accumulating their properties
def remove_connector_nodes(G):
    nodes_to_remove = set()
    edges_to_add = []
    nodes_processed = set()
    
    for i, node in enumerate(G.nodes):
        # If the node has only two neighbors, it is a connector node and should be removed
        neighbors = list(G.neighbors(node))
        if len(neighbors) == 2 and node not in nodes_to_remove and node not in nodes_processed:
            new_properties = accumulate_proerties(G[node][neighbors[0]], G[node][neighbors[1]])

            # Find two intersection nodes
            current_string = set([node])
            left_node = neighbors[0]
            # Traverse left nodes until a node with more than 2 neighbors is found or 
            while G.degree[left_node] == 2:
                # Find the neighbor that is not the current string
                next_node = get_next_node(G, left_node, current_string)
                # Update Properties
                new_properties = accumulate_proerties(new_properties, G[left_node][next_node])

                current_string.add(left_node)
                left_node = next_node


            right_node = neighbors[1]
            # Traverse right nodes until a node with more than 2 neighbors is found or
            while G.degree[right_node] == 2:
                # Find the neighbor that is not the current string
                next_node = get_next_node(G, right_node, current_string)
                # Update Properties
                new_properties = accumulate_proerties(new_properties, G[right_node][next_node])

                current_string.add(right_node)
                right_node = next_node

            # Sanity check
            degrees = [G.degree(x) for x in current_string] 
            if 3 in degrees or 1 in degrees:
                print("error")
            
            nodes_to_remove.update(current_string)
            current_string.update([left_node, right_node])
            nodes_processed.update(current_string)
            edges_to_add.append((left_node, right_node, new_properties))


    print(f"Processed {len(nodes_processed)} nodes")
    print(f"Removing {len(nodes_to_remove)} nodes")
    # Remove the nodes and add new edges
    for node in nodes_to_remove:
        G.remove_node(node)

    for (edge1, edge2, properties) in edges_to_add: # TODO for some reason, the edges add back all the nodes meant to be removed
        if edge1 in nodes_to_remove or edge2 in nodes_to_remove:
            print("skipping edge")
            continue

        G.add_edge(edge1, edge2, **properties)

    return G


if __name__ == "__main__":
    # Read the data
    gdf = gpd.read_file("Data\Ashville_Roads\Bun_DBO_CENTERLINE.shp")
    risk = gpd.read_file("Data\Ashville_Floods\Risk_zone.shp")

    # make sure the points are in the same crs as the graph
    risk = risk.to_crs(gdf.crs)

    # Create the graph
    G = create_graph(gdf, risk)

    # Remove connector nodes
    G = remove_connector_nodes(G)

    # Save the graph
    nx.write_gml(G, "Graph_data\Buncombe_Couny_Centerline_Data.gml")
    # Check to make sure risk is added with the correct values
    for edge in G.edges:
        if G[edge[0]][edge[1]]['risk'] > 0:
            G[edge[0]][edge[1]]['risk'] *= 100  # Example: scale values up for better visibility

    print("Done")