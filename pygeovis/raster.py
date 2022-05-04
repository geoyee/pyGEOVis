from typing import List, Tuple, Union
import numpy as np
from skimage import exposure
try:
    from osgeo import gdal
except:
    import gdal
import folium
from .converter import Converter


class Raster(object):
    def __init__(self,
                 path: str,
                 band_list: Union[List[int], Tuple[int]]=[1, 2, 3]) -> None:
        super(Raster, self).__init__()
        self.path = path
        self._src_data = gdal.Open(path)
        self._getInfo()
        self.setBands(band_list)

    def setBands(self, band_list: Union[List[int], Tuple[int], None]) -> None:
        if len(band_list) > self.bands:
            raise ValueError(
                "The lenght of band_list must be less than {0}.".format(
                    str(self.bands)))
        if max(band_list) > self.bands or min(band_list) < 1:
            raise ValueError("The range of band_list must within [1, {0}].".
                                format(str(self.bands)))
        self.band_list = band_list

    def _getInfo(self) -> None:
        self.bands = self._src_data.RasterCount
        self.width = self._src_data.RasterXSize
        self.height = self._src_data.RasterYSize
        self.geotf = self._src_data.GetGeoTransform()
        self.proj = self._src_data.GetProjection()
        converter = Converter(self.proj, self.geotf)
        self.range = converter.get_geo_range(self.width, self.height)
        self.center = [
            (self.range[0][0] + self.range[1][0]) / 2,
            (self.range[0][1] + self.range[1][1]) / 2
        ]

    def getArray(self) -> np.ndarray:
        ima = self._src_data.ReadAsArray()
        band_array = []
        for b in self.band_list:
            band_i = self._src_data.GetRasterBand(b).ReadAsArray()
            band_array.append(band_i)
        ima = np.stack(band_array, axis=0)
        if self.bands == 1:
            # the type is complex means this is a SAR data
            if isinstance(type(ima[0, 0]), complex):
                ima = abs(ima)
        else:
            ima = ima.transpose((1, 2, 0))
        if self.to_uint8 is True:
            ima = Raster.to_uint8(ima)
        return ima

    @classmethod
    def to_uint8(im: np.ndarray) -> np.ndarray:
        # simple image standardization
        def _sample_norm(image):
            stretches = []
            if len(image.shape) == 3:
                for b in range(image.shape[-1]):
                    stretched = exposure.equalize_hist(image[:, :, b])
                    stretched /= float(np.max(stretched))
                    stretches.append(stretched)
                stretched_img = np.stack(stretches, axis=2)
            else:
                stretched_img = exposure.equalize_hist(image)
            return np.uint8(stretched_img * 255)
        dtype = im.dtype.name
        if dtype != "uint8":
            im = _sample_norm(im)
        return im

    def display(self) -> folium.folium.Map:
        map = folium.Map(location=self.center, zoom_start=15)
        img = folium.raster_layers.ImageOverlay(
            self.getArray(),
            bounds=self.range
        )
        img.add_to(map)
        folium.LayerControl().add_to(map)
        return map