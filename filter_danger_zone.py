import networkx as nx
import json
import random
import geopandas as gpd


def filter_danger_zone(G, risk_tolerance):
    '''
    Takes a graph and filters out all zones with high risk
    '''
    
    # Create a subgraph with only the edges with risk attribute < 1
    subgraph = G.copy()
    for edge in G.edges:
        if G[edge[0]][edge[1]]['risk'] >= risk_tolerance:
            subgraph.remove_edge(edge[0], edge[1])
    return subgraph



