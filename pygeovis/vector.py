from typing import List
import codecs
import os.path as osp
import geojson
from folium import GeoJson


class Vector(object):
    def __init__(self, path: str) -> None:
        super(Vector, self).__init__()
        if not osp.exists(path):
            raise FileNotFoundError("{} not found.".format(path))
        geo_reader = codecs.open(path, "r", encoding="utf-8")
        self.json_data = geojson.loads(geo_reader.read())
        self.center = self.getCenter()

    def getLayer(self) -> GeoJson:
        layer = GeoJson(self.json_data)
        return layer, self.center

    def getCenter(self) -> List:
        clat = 0
        clon = 0
        feats = self.json_data["features"]
        lens = len(feats)
        for feat in feats:
            geo = feat["geometry"]
            if geo["type"] == "Polygon":
                geo_points = geo["coordinates"][0]
            elif geo["type"] == "MultiPolygon":
                geo_points = geo["coordinates"][0][0]
            else:
                raise TypeError(
                    "Geometry type must be `Polygon` or `MultiPolygon`, not {}.".format(
                        geo["type"]
                    )
                )
            plat = 0
            plon = 0
            plens = len(geo_points)
            for point in geo_points:
                plat += point[1]
                plon += point[0]
            plat /= plens
            plon /= plens
            clat += plat
            clon += plon
        return [clat / lens, clon / lens]
