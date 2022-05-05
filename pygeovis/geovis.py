from typing import List, Tuple, Union
from folium import folium, Map, LayerControl
from .raster import Raster
from .vector import Vector


class Geovis(object):
    def __init__(self) -> None:
        self.map = Map(location=[0, 0], zoom_start=16, max_zoom=21, prefer_canvas=True)
        self.center = None

    def addRaster(
        self, raster_path: str, band_list: Union[List[int], Tuple[int], None] = None
    ) -> None:
        layer, self.center = Raster(raster_path, band_list).getLayer()
        layer.add_to(self.map)

    def addVector(self, vecter_path: str) -> None:
        layer, self.center = Vector(vecter_path).getLayer()
        layer.add_to(self.map)

    def show(self) -> folium.Map:
        if self.center is not None:
            self.map.location = self.center
        LayerControl().add_to(self.map)
        return self.map
