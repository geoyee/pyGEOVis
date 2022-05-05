import os.path as osp
from typing import List
from subprocess import call
try:
    from osgeo import osr
except:
    import osr


def convert_WGS84(infile: str, outfile: str="output.tif") -> bool:
    if not osp.exists(infile):
        raise FileNotFoundError("{} not found.".format(infile))
    retcode = call(["gdalwarp", infile, outfile, "-t_srs", '"+proj=longlat', '+ellps=WGS84"'])
    return (retcode == 0)


class Converter(object):
    def __init__(self, proj: str, geotf: tuple) -> None:
        # source data
        self.source = osr.SpatialReference()
        self.source.ImportFromWkt(proj)
        self.geotf = geotf
        # target data
        self.target = osr.SpatialReference()
        self.target.ImportFromEPSG(4326)

    def get_geo_range(self, width: int, height: int) -> List:
        lat1, lon1 = self.xy2latlon(height - 1, 0)
        lat2, lon2 = self.xy2latlon(0, width - 1)
        return [[lon1, lat1], [lon2, lat2]]

    def xy2latlon(self, row: int, col: int) -> List:
        px = self.geotf[0] + col * self.geotf[1] + row * self.geotf[2]
        py = self.geotf[3] + col * self.geotf[4] + row * self.geotf[5]
        ct = osr.CoordinateTransformation(self.source, self.target)
        coords = ct.TransformPoint(px, py)
        return coords[:2]