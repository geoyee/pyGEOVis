from typing import List, Tuple, Union
import numpy as np
from skimage import exposure
from folium import folium, Map, raster_layers, LayerControl
from .converter import Converter

try:
    from osgeo import gdal
except:
    import gdal


class Raster(object):
    def __init__(
        self, path: str, band_list: Union[List[int], Tuple[int], None] = None
    ) -> None:
        super(Raster, self).__init__()
        self.path = path
        self.__src_data = gdal.Open(path)
        self.__getInfo()
        self.setBands(band_list)

    def setBands(self, band_list: Union[List[int], Tuple[int], None]) -> None:
        self.bands = self.__src_data.RasterCount
        if band_list is None:
            if self.bands == 3:
                band_list = [1, 2, 3]
            else:
                band_list = [1]
        if len(band_list) > self.bands:
            raise ValueError(
                "The lenght of band_list must be less than {0}.".format(str(self.bands))
            )
        if max(band_list) > self.bands or min(band_list) < 1:
            raise ValueError(
                "The range of band_list must within [1, {0}].".format(str(self.bands))
            )
        self.band_list = band_list

    def getArray(self) -> np.ndarray:
        return self.__getArray(self.__src_data, self.band_list)

    def display(
        self, display_band: Union[List[int], Tuple[int], None] = None
    ) -> folium.Map:
        if display_band is None:
            display_band = self.band_list
        band_num = len(display_band)
        if band_num != 1 and band_num != 3:
            raise ValueError("display_band must be 1 or 3, ont {}.".format(band_num))
        wgs_data = Converter.openAsWGS84(self.path)
        wgs_image = self.__getArray(wgs_data, display_band, True)
        wgs_range = self.__getWGS84Range(
            wgs_data.GetProjection(),
            wgs_data.GetGeoTransform(),
            wgs_data.RasterYSize,
            wgs_data.RasterXSize,
        )
        wgs_center = self.__getWGS84Center(wgs_range)
        map = Map(location=wgs_center, zoom_start=15)
        img = raster_layers.ImageOverlay(wgs_image, wgs_range)
        img.add_to(map)
        LayerControl().add_to(map)
        return map

    @classmethod
    def toUint8(self, im: np.ndarray) -> np.ndarray:
        # simple image standardization
        def __sample_norm(image):
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
            im = __sample_norm(im)
        return im

    def __getInfo(self) -> None:
        self.width = self.__src_data.RasterXSize
        self.height = self.__src_data.RasterYSize
        self.geotf = self.__src_data.GetGeoTransform()
        self.proj = self.__src_data.GetProjection()

    def __getWGS84Range(self, proj: str, geotf: Tuple, height: int, width: int) -> List:
        converter = Converter(proj, geotf)
        lat1, lon1 = converter.xy2Latlon(height - 1, 0)
        lat2, lon2 = converter.xy2Latlon(0, width - 1)
        return [[lon1, lat1], [lon2, lat2]]

    def __getWGS84Center(self, range) -> List:
        clat = (range[0][0] + range[1][0]) / 2
        clon = (range[0][1] + range[1][1]) / 2
        return [clat, clon]

    def __getArray(
        self, src_data: gdal.Dataset, band_list: List, to_uint8: bool = False
    ) -> np.ndarray:
        band_array = []
        for b in band_list:
            band_i = src_data.GetRasterBand(b).ReadAsArray()
            band_array.append(band_i)
        ima = np.stack(band_array, axis=0)
        if self.bands == 1:
            # the type is complex means this is a SAR data
            if isinstance(type(ima[0, 0]), complex):
                ima = abs(ima)
            ima = ima.squeeze()
        else:
            ima = ima.transpose((1, 2, 0))
        if to_uint8:
            ima = Raster.toUint8(ima)
        return ima
