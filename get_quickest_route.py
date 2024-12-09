import networkx as nx
import json


def quickest_route(G, start_node, end_nodes):
    '''
    Find the quickest route from a start node to a list of end nodes.
    If the quickest route is not found, use Bellman-Ford as a fallback.

    Parameters:
    G: networkx.Graph
    start_node: str
    end_nodes: list of str

    Returns:
    quickest_route: list of str
    '''
    quickest_route = None
    route_length = None
    for end_node in end_nodes:

        # Using Bellman-Ford as a fallback
        paths = nx.single_source_bellman_ford_path(G, source=start_node, weight='weight')
        lengths = nx.single_source_bellman_ford_path_length(G, source=start_node, weight='weight')

        # Get the path and length to the specific end_node
        new_quickest_route = paths.get(end_node)
        new_route_length = lengths.get(end_node)
        
        if new_route_length is None:
            print("No path found from start_node to end_node using Bellman-Ford.")
            continue
        
        if quickest_route is None:
            quickest_route = new_quickest_route
            route_length = new_route_length
        if new_route_length > route_length:
            quickest_route = new_quickest_route
            route_length = new_route_length
        else:
            continue
    


    if quickest_route is not None and route_length is not None:
        # print("Fallback shortest route:", quickest_route)
        print("Fallback route length:", route_length)
    else:
        print("No path found from start_node to end_node using Bellman-Ford.")
        
    if not nx.has_path(G, start_node, end_node):
        print("No path between start_node and end_node.")
    else:
        print("Path exists between start_node and end_node.")

    

    return quickest_route

def subselect_network(G):
    # Create a subgraph with only the edges with risk attribute < 1
    subgraph = G.copy()
    for edge in G.edges:
        if G[edge[0]][edge[1]]['risk'] >= 1:
            subgraph.remove_edge(edge[0], edge[1])
    return subgraph


# # read the graph
# G = nx.read_gml("Data\Buncombe_Couny_Centerline_Data_w_safezone_filtered.gml")

# # Pick a random start node
# import random
# random.seed(0)


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
# nx.write_gml(G, "Data\quickest_routes_labeled.gml")
