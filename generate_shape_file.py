import shapefile
import networkx as nx
import geopandas as gpd
import pandas as pd
import json


'''
Takes a list of graph and generates a shape file.
The graphs nodes are assumed to be in the form of a list of tuples (x, y) for coordinates.
'''


def generate_shape_file_from_gml(graphs, output_file):
    # Create a new shapefile
    w = shapefile.Writer(output_file, shapeType=shapefile.POLYLINE)
    w.field('ID', 'N')
    # for field in graphs[0].graph:
    #     w.field(field, 'C')
        


    for graph in graphs:
        for edge in graph.edges(data=True):
            # Create a line
            x1 = float(edge[0].split(',')[0][1:])
            y1 = float(edge[0].split(',')[1][:-1])
            x2 = float(edge[1].split(',')[0][1:])
            y2 = float(edge[1].split(',')[1][:-1])
            line = [(x1, y1), (x2, y2)]
            w.line([line])
            w.record(1)


    w.close()

def generate_shape_file_from_json(json_file, output_file):
    # read the json file
    with open(json_file) as f:
        data = json.load(f)
    # Create a new shapefile
    crs = {'init': 'epsg:4326'}
    w = shapefile.Writer(output_file, shapeType=shapefile.POLYLINE, crs=crs)
    w.field('ID', 'N')
    # for field in data[0].graph:
    #     w.field(field, 'C')

    for i in range(len(data)-1):
        edge = (data[i], data[i+1])
        
        # Create a line
        x1 = float(edge[0].split(',')[0][1:])
        y1 = float(edge[0].split(',')[1][:-1])
        x2 = float(edge[1].split(',')[0][1:])
        y2 = float(edge[1].split(',')[1][:-1])
        line = [(x1, y1), (x2, y2)]
        w.line([line])
        w.record(1)
        


def main():
    graph_path = "Data\Buncombe_Couny_Centerline_Data.gml"
    graph = nx.read_gml(graph_path)
    generate_shape_file_from_gml([graph], "Data\Buncombe_County_Centerline_Data.shp")
    generate_shape_file_from_json("Data\quickest_route.json", "Data\quickest_route.shp")
    

if __name__ == "__main__":
    main()
