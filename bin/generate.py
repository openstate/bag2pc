#!/usr/bin/env python
import sys
import io
from contextlib import closing
import csv
import json
import shapely.geometry
import shapely.ops

from shapely_geojson import dumps, Feature, FeatureCollection

from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt

from geovoronoi import voronoi_regions_from_coords
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area

import geopandas as gpd


_promotion_dispatch = {"Point": shapely.geometry.MultiPoint,
                       "Polygon": shapely.geometry.MultiPolygon,
                       "LineString": shapely.geometry.MultiLineString}

def _maybe_promote_geometry(geom):
    """ Either promote the geometry to a Multi-geometry, or return input"""
    promoter = _promotion_dispatch.get(geom.type, lambda x: x[0])
    return promoter([geom])

def main(argv):
    pc2points_nogeo = {}
    with closing(io.open('bagadres-full.csv')) as io_file:
        rows_read = 0
        old_nr = 0
        last_point = None
        for row in csv.reader(io_file, delimiter=';'):
            rows_read += 1
            if rows_read == 1:
                continue
            # if rows_read % 100 == 0:
            #     print(rows_read)
            if rows_read % 10000 == 0:
                break
            if row[1] == old_nr:
                continue
            old_nr = row[1]
            p = shapely.geometry.Point(float(row[-2]), float(row[-1]))
            if p == last_point:
                continue
            last_point = p
            pc = row[4]
            try:
                pc2points_nogeo[pc].append(p)
            except Exception as e:
                pc2points_nogeo[pc] = [p]
                #    p.coords[:] + p.coords[:] + p.coords[:])

    pc2points = {p: shapely.geometry.MultiPoint(q) for p, q in pc2points_nogeo.items()}
    output = []
    v_input = []
    for p, poly in pc2points.items():
         for p in poly.geoms:
            v_input += p.coords

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    area = world[world.name == 'Netherlands']

    area = area.to_crs(epsg=3395)    # convert to World Mercator CRS
    area_shape = area.iloc[0].geometry   # get the Polygon
    # Recoger todas las lineas y armarlas en poligonos.
    vor = Voronoi(v_input)
    lines = [shapely.geometry.LineString(vor.vertices[line]) for line in vor.ridge_vertices]
    last_pc = ""
    last_polys = []
    polys_found = 0
    polys = 0
    result_polys = []
    pc_polys = {}
    for poly in shapely.ops.polygonize(lines):
        polys += 1
        pc = ""
        old_polys_found = polys_found
        for p2, poly2 in pc2points.items():
            for p in poly2.geoms:
                if poly.contains(p):
                    pc = p2
                    polys_found += 1
                    try:
                        pc_polys[pc].append(poly)
                    except LookupError as e:
                        pc_polys[pc] = [poly]
                    break
        if old_polys_found == polys_found:
            result_polys.append(Feature(poly, {'postcode': None}))

    for pc, polys in pc_polys.items():
        result_polys.append(
            Feature(shapely.ops.unary_union(polys), {'postcode': pc}))

    print(dumps(FeatureCollection(result_polys), indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
