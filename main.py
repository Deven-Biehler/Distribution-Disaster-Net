from add_safe_zones import add_safe_zones
from generate_network import create_graph, remove_connector_nodes
from generate_shape_file import generate_shape_file_from_gml, generate_shape_file_from_json
from filter_danger_zone import filter_danger_zone
from get_quickest_route import quickest_route
from add_population import add_population_density
import networkx as nx
import geopandas as gpd
import json


def pipeline():
    # Add population density
    add_population_density()

    # Load the shapefile
    shapefile_path = 'Data/population_mapping.shp'


    gdf = gpd.read_file(shapefile_path)

    risk_path = 'Data/Ashville Road Shp files/risk_zone/risk_zone.shp'
    risk = gpd.read_file(risk_path)

    # print size of both
    print("Shapefile size: ", gdf.shape)
    print("Risk size: ", risk.shape)

    # Example usage
    G = create_graph(gdf, risk)
    print("nodes", len(G.nodes))
    G = remove_connector_nodes(G)

    # save the graph to a gml file
    nx.write_gml(G, 'Data\Buncombe_Couny_Centerline_Data.gml')



    # Add safe zones
    # Read shapefile
    gdf = gpd.read_file("Data\Ashville Road Shp files\evac\\flood_evac.shp")
    # read coordinates of points from shapefile
    points = gdf['geometry']

    network_path = "Data\Buncombe_Couny_Centerline_Data.gml"
    G = nx.read_gml(network_path)
    G = add_safe_zones(G, points)

    # Save the graph
    nx.write_gml(G, "Data\Buncombe_Couny_Centerline_Data_w_safezone.gml")




    # Filter out danger zones
    # read the graph
    G = nx.read_gml("Data\Buncombe_Couny_Centerline_Data_w_safezone.gml")
    G = filter_danger_zone(G, 1)
    # save the graph
    nx.write_gml(G, "Data\Buncombe_Couny_Centerline_Data_w_safezone_filtered.gml")


    

    # # Pick a random start node
    # import random
    # # Find a node with safe_zone attribute
    # safe_nodes = [node for node in G.nodes if G.nodes[node].get('safe_zone')]
    # route = None
    # while route is None:
    #     start_node = random.choice(list(G.nodes))
    #     route = quickest_route(G, start_node, safe_nodes)
    # # save quickest route as a json file
    # with open("Data\quickest_route.json", "w") as f:
    #     json.dump(route, f)
    # # Label the edges in the quickest route
    # for edge in zip(route[:-1], route[1:]):
    #     if edge in G.edges:
    #         G[edge[0]][edge[1]]['quickest'] = 1
    # # Save the graph
    # nx.write_gml(G, "Data\Buncombe_Couny_Centerline_Data_w_safezone_filtered.gml")





    # Generate shape file
    graph_path = "Data\Buncombe_Couny_Centerline_Data_w_safezone_filtered.gml"
    graph = nx.read_gml(graph_path)
    generate_shape_file_from_gml([graph], "Data\Buncombe_County_Centerline_Data.shp")
    generate_shape_file_from_json("Data\quickest_route.json", "Data\quickest_route.shp")

























if __name__ == "__main__":
    pipeline()