import os.path as osp
from typing import List

try:
    from osgeo import gdal, osr
except:
    import gdal
    import osr


class Converter(object):
    def __init__(self, proj: str, geotf: tuple) -> None:
        # source data
        self.source = osr.SpatialReference()
        self.source.ImportFromWkt(proj)
        self.geotf = geotf
        # target data
        self.target = osr.SpatialReference()
        self.target.ImportFromEPSG(4326)

    @classmethod
    def openAsWGS84(self, path: str) -> gdal.Dataset:
        if not osp.exists(path):
            raise FileNotFoundError("{} not found.".format(path))
        result = gdal.Warp("", path, dstSRS="EPSG:4326", format="VRT")
        return result

    def xy2Latlon(self, row: int, col: int) -> List:
        px = self.geotf[0] + col * self.geotf[1] + row * self.geotf[2]
        py = self.geotf[3] + col * self.geotf[4] + row * self.geotf[5]
        ct = osr.CoordinateTransformation(self.source, self.target)
        coords = ct.TransformPoint(px, py)
        return coords[:2]
