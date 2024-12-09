from shapely.geometry import Point
from shapely.ops import nearest_points
from shapely.geometry import MultiPoint
import math



def add_safe_zones(G, points):
    # find closest node to each point
    for point in points:
        nearest = None
        min_dist = float('inf')
        for node in G.nodes:
            dist = point.distance(Point(eval(node)))
            if dist < min_dist:
                min_dist = dist
                nearest = node
        G.nodes[nearest]['safe_zone'] = True

    return G
    


