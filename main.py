from add_safe_zones import add_safe_zones
from generate_network import create_graph, remove_connector_nodes
from generate_shape_file import generate_shape_file_from_gml, generate_shape_file_from_json
from filter_graph import filter_danger_zone
from get_quickest_route import quickest_route, networkx_tsp_with_nodes
from add_population import add_population_density
import networkx as nx
import geopandas as gpd
import json
import os

CRS = "EPSG:4326"


def get_TSP_route(G):
    # Pick a random start node
    import random
    import time
    # Find a node with safe_zone attribute
    safe_nodes = [node for node in G.nodes if G.nodes[node].get('safe_zone')]
    print("Finding routes...")
    num_routes = 5
    
    routes = []
    while True: # check if all routes are the same
        if None not in routes:
            if len(set([tuple(route) for route in routes])) > 1:
                break
        starting_threshold = 0.01
        ending_threshold = 0.99
        threshold = starting_threshold
        timer = time.time()
        routes = []
        start_node = random.choice(list(G.nodes))
        while len(routes) < num_routes:
            # Intialize variables for each attempt
            # if time.time() - timer > 60: # if it takes too long, reset the variables

            print(f"finding route with threshold: {threshold}")
            routes.append(networkx_tsp_with_nodes(G, start_node, safe_nodes, threshold))
            threshold += (ending_threshold - starting_threshold) / (num_routes - 1) # change the threshold for each route
        break

    # save quickest route as a json file
    
    for i, route in enumerate(routes):
        with open(f"Data/Ashville_Routes/quickest_route{i}.json", "w") as f:
            json.dump(route, f)
        # Label the edges in the quickest route
        for edge in zip(route[:-1], route[1:]):
            if edge in G.edges:
                G[edge[0]][edge[1]]['quickest'] = i
        # Save as a shape file
        generate_shape_file_from_json(f"Data/Ashville_Routes/quickest_route{i}.json", f"Data/Ashville_Routes/quickest_route{i}.shp")
    # Save the graph
    nx.write_gml(G, "Data\Buncombe_Couny_Centerline_Data_w_safezone_filtered.gml")

def get_route(G):
    # Pick a random start node
    import random
    import time
    # Find a node with safe_zone attribute
    safe_nodes = [node for node in G.nodes if G.nodes[node].get('safe_zone')]
    print("Finding routes...")
    num_routes = 5
    
    routes = []
    while True: # check if all routes are the same
        if None not in routes:
            if len(set([tuple(route['path']) for route in routes])) > 1:
                break
        starting_threshold = 0.01
        ending_threshold = 0.99
        threshold = starting_threshold
        timer = time.time()
        routes = []
        start_node = random.choice(list(G.nodes))
        while len(routes) < num_routes:
            # Intialize variables for each attempt
            if time.time() - timer > 60: # if it takes too long, reset the variables
                routes = []
                threshold = starting_threshold
                timer = time.time()
                start_node = random.choice(list(G.nodes))
                print("resetting variables")



            print(f"finding route with threshold: {threshold}")
            routes.append(quickest_route(G, start_node, safe_nodes, threshold))
            threshold += (ending_threshold - starting_threshold) / (num_routes - 1) # change the threshold for each route

    # save quickest route as a json file
    
    for i, route in enumerate(routes):
        with open(f"Data/Ashville_Routes/quickest_route{i}.json", "w") as f:
            json.dump(route['path'], f)
        # Label the edges in the quickest route
        for edge in zip(route['path'][:-1], route['path'][1:]):
            if edge in G.edges:
                G[edge[0]][edge[1]]['quickest'] = i
        # Save as a shape file
        generate_shape_file_from_json(f"Data/Ashville_Routes/quickest_route{i}.json", f"Data/Ashville_Routes/quickest_route{i}.shp")
    # Save the graph
    nx.write_gml(G, "Data\Buncombe_Couny_Centerline_Data_w_safezone_filtered.gml")

def pipeline():
    # Add population density
    add_population_density("Data\Ashville_Roads\Bun_DBO_CENTERLINE.shp")

    # Load the shapefile
    shapefile_path = 'Data/temp/population_mapping.shp'


    gdf = gpd.read_file(shapefile_path)

    risk_path = 'Data\Ashville_Floods\Risk_zone.shp'
    risk = gpd.read_file(risk_path)
    risk = risk.to_crs(gdf.crs)

    # print size of both
    print("Shapefile size: ", gdf.shape)
    print("Risk size: ", risk.shape)

    # Example usage
    G = create_graph(gdf, risk)
    print("nodes", len(G.nodes))
    G = remove_connector_nodes(G)

    # save the graph to a gml file
    nx.write_gml(G, 'Graph_data/Buncombe_Couny_Centerline_Data.gml')



    # Add safe zones
    # Read shapefile
    gdf = gpd.read_file("Data/Ashville_Safe/flood_evac.shp")
    # make sure the points are in the same crs as the graph
    gdf = gdf.to_crs(CRS)

    # read coordinates of points from shapefile
    points = gdf['geometry']

    network_path = "Graph_data/Buncombe_Couny_Centerline_Data.gml"
    G = nx.read_gml(network_path)
    G = add_safe_zones(G, points)

    # Save the graph
    nx.write_gml(G, "Graph_data/Buncombe_Couny_Centerline_Data_w_safezone.gml")




    # Filter out danger zones
    # read the graph
    G = nx.read_gml("Graph_data/Buncombe_Couny_Centerline_Data_w_safezone.gml")
    G = filter_danger_zone(G, 1)
    # save the graph
    nx.write_gml(G, "Graph_data/Buncombe_Couny_Centerline_Data_w_safezone_filtered.gml")


    # Get the quickest routes while avoiding danger zones
    # delete files in the directory
    for file in os.listdir("Data/Ashville_Routes"):
        os.remove(f"Data/Ashville_Routes/{file}")
    # get_route(G)


    # get_TSP_route(G)





    # Generate shape file
    graph_path = "Graph_data/Buncombe_Couny_Centerline_Data_w_safezone_filtered.gml"
    graph = nx.read_gml(graph_path)
    generate_shape_file_from_gml([graph], "Data/Ashville_Roads/Buncombe_County_Centerline_Data.shp")
    

























if __name__ == "__main__":
    pipeline()