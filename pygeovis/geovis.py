from typing import List, Tuple, Union
from folium import folium
from .raster import Raster


class Geovis(object):
    @classmethod
    def showRaster(
        self, raster_path: str, band_list: Union[List[int], Tuple[int], None] = None
    ) -> folium.Map:
        raster = Raster(raster_path, band_list)
        map = raster.display()
        return map
