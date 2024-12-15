import networkx as nx
from networkx.algorithms.approximation import traveling_salesman_problem
import json


import networkx as nx

def calculate_weighted_graph(G, risk_tolerance):
    # Take the weight property of each edge and multiply it by the risk property
    for edge in G.edges:
        risk = G[edge[0]][edge[1]]['risk'] # 1 risk is guaranteed to be uncrossable, 0 is guaranteed to be crossable, 0.5 is a 50% chance of being crossable, ect.
        if risk > risk_tolerance:
            risk = 1
        time = G[edge[0]][edge[1]]['weight'] # time to traverse the edge, length(m) * speed limit(mi/h)
        if risk == 1:
            G[edge[0]][edge[1]]['weight'] = float('inf')
        else:
            G[edge[0]][edge[1]]['weight'] = time / (1 - risk)
    return G


def networkx_tsp_with_nodes(G, start_node, nodes_to_visit, threshold=0.1):
    '''
    Solve the Traveling Salesperson Problem (TSP) for a given graph and specific nodes using NetworkX.

    Parameters:
    G: networkx.Graph
    start_node: str - the node where the salesperson starts and ends.
    nodes_to_visit: list of str - the nodes that must be visited.

    Returns:
    tsp_route: list of str - the TSP route visiting all specified nodes.
    route_length: float - the total length of the route.
    '''

    G = G.copy()
    if threshold != 1:
        G = calculate_weighted_graph(G, threshold)

    # Subgraph containing only the nodes to visit
    nodes_to_visit = [start_node] + nodes_to_visit
    
    # Solve the TSP on the subgraph using the greedy approach
    tsp_route = traveling_salesman_problem(
        G=G,
        nodes=nodes_to_visit,
        cycle=True,  # Ensure it returns to the start node
        weight='weight'
    )
    
    # Compute the total route length
    # route_length = sum(G[tsp_route[i]][tsp_route[i + 1]]['weight'] for i in range(len(tsp_route) - 1))
    
    return tsp_route

def quickest_route(G, start_node, end_nodes, threshold=0.1):
    '''
    Find the k globally shortest routes from a start node to a list of end nodes.

    Parameters:
    G: networkx.Graph
    start_node: str
    end_nodes: list of str
    k: int, optional (default=5)
       Number of globally shortest routes to return.

    Returns:
    quickest_routes: list of dict containing end_node, path, and length for the k shortest routes.
    '''
    G = G.copy()
    if threshold != 1:
        G = calculate_weighted_graph(G, threshold)
    
    fastest_routes = []
    # Evaluate paths to all end nodes
    for end_node in end_nodes:
        try:
            # Attempt Dijkstra's algorithm for the path
            path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
            length = nx.shortest_path_length(G, source=start_node, target=end_node, weight='weight')
            fastest_routes.append({'end_node': end_node, 'path': path, 'length': length})
        except (nx.NetworkXNoPath, nx.NetworkXError):
            # Fallback to Bellman-Ford if Dijkstra fails
            try:
                paths = nx.single_source_bellman_ford_path(G, source=start_node, weight='weight')
                lengths = nx.single_source_bellman_ford_path_length(G, source=start_node, weight='weight')
                if end_node in paths and end_node in lengths:
                    fastest_routes.append({'end_node': end_node, 'path': paths[end_node], 'length': lengths[end_node]})
            except (nx.NetworkXNoPath, nx.NetworkXUnbounded):
                # Skip this end_node if no path exists even with Bellman-Ford
                continue
    if len(fastest_routes) == 0:
        return None
    fastest_route = min(fastest_routes, key=lambda x: x['length'])
    return fastest_route




def subselect_network(G):
    # Create a subgraph with only the edges with risk attribute < 1
    subgraph = G.copy()
    for edge in G.edges:
        if G[edge[0]][edge[1]]['risk'] >= 1:
            subgraph.remove_edge(edge[0], edge[1])
    return subgraph

import random

def main():
    random.seed(0)
    print("Finding route")
    G = nx.read_gml("Graph_data\Buncombe_Couny_Centerline_Data_w_safezone.gml")
    start_node = random.choice(list(G.nodes))
    end_nodes = [node for node in G.nodes if G.nodes[node].get('safe_zone')]

    route = quickest_route(G, start_node, end_nodes, threshold=0.1)
    print(route)


if __name__ == "__main__":
    main()


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
