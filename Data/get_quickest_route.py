import networkx as nx
def quickest_route(G, start_node, end_nodes):
    quickest_route = None
    route_length = None
    for end_node in end_nodes:
        try:
            # Using Dijkstra's algorithm
            quickest_route = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
            route_length = nx.dijkstra_path_length(G, source=start_node, target=end_node, weight='weight')
            print("Quickest route:", quickest_route)
            print("Route length:", route_length)
        except ValueError as e:
            print("Error encountered:", e)
            print("Trying Bellman-Ford as a fallback...")

            # Using Bellman-Ford as a fallback
            paths = nx.single_source_bellman_ford_path(G, source=start_node, weight='weight')
            lengths = nx.single_source_bellman_ford_path_length(G, source=start_node, weight='weight')

            # Get the path and length to the specific end_node
            new_quickest_route = paths.get(end_node)
            new_route_length = lengths.get(end_node)
        
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

    # Label the edges in the quickest route
    for edge in zip(quickest_route[:-1], quickest_route[1:]):
        if edge in G.edges:
            G[edge[0]][edge[1]]['quickest'] = 1

    return G

def subselect_network(G):
    # Create a subgraph with only the edges with risk attribute < 1
    subgraph = G.copy()
    for edge in G.edges:
        if G[edge[0]][edge[1]]['risk'] >= 1:
            subgraph.remove_edge(edge[0], edge[1])
    return subgraph


# read the graph
G = nx.read_gml("Data\Buncombe_Couny_Centerline_Data.gml")

# Pick a random start node
import random
random.seed(0)
start_node = random.choice(list(G.nodes))

# Find a node with safe_zone attribute
safe_nodes = [node for node in G.nodes if G.nodes[node].get('safe_zone')]

G = quickest_route(G, start_node, safe_nodes)

# Save the graph
nx.write_gml(G, "Data\quickest_routes_labeled.gml")
