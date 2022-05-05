from typing import List, Tuple, Union
import numpy as np
from skimage import exposure
from folium.raster_layers import ImageOverlay
from .converter import Converter


class Raster(object):
    def __init__(
        self, path: str, band_list: Union[List[int], Tuple[int], None] = None
    ) -> None:
        super(Raster, self).__init__()
        self.src_data = Converter.openAsWGS84(path)
        self.setBands(band_list)
        self.getInfo()

    def getLayer(self) -> ImageOverlay:
        layer = ImageOverlay(self.getArray(), self.wgs_range)
        return layer, self.wgs_center

    @classmethod
    def toUint8(self, im: np.ndarray) -> np.ndarray:
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

    def setBands(self, band_list: Union[List[int], Tuple[int], None]) -> None:
        self.bands = self.src_data.RasterCount
        if band_list is None:
            if self.bands == 3:
                band_list = [1, 2, 3]
            else:
                band_list = [1]
        band_list_lens = len(band_list)
        if band_list_lens != 1 and band_list_lens != 3:
            raise ValueError(
                "The lenght of band_list must be 1 or 3, not {}.".format(
                    str(band_list_lens)
                )
            )
        if max(band_list) > self.bands or min(band_list) < 1:
            raise ValueError(
                "The range of band_list must within [1, {}].".format(str(self.bands))
            )
        self.band_list = band_list

    def getInfo(self) -> None:
        self.width = self.src_data.RasterXSize
        self.height = self.src_data.RasterYSize
        self.geotf = self.src_data.GetGeoTransform()
        self.proj = self.src_data.GetProjection()  # WGS84
        self.wgs_range = self.getWGS84Range()
        self.wgs_center = self.getWGS84Center()

    def getWGS84Range(self) -> List:
        converter = Converter(self.proj, self.geotf)
        lat1, lon1 = converter.xy2Latlon(self.height - 1, 0)
        lat2, lon2 = converter.xy2Latlon(0, self.width - 1)
        return [[lon1, lat1], [lon2, lat2]]

    def getWGS84Center(self) -> List:
        clat = (self.wgs_range[0][0] + self.wgs_range[1][0]) / 2
        clon = (self.wgs_range[0][1] + self.wgs_range[1][1]) / 2
        return [clat, clon]

    def getArray(self) -> np.ndarray:
        band_array = []
        for b in self.band_list:
            band_i = self.src_data.GetRasterBand(b).ReadAsArray()
            band_array.append(band_i)
        ima = np.stack(band_array, axis=0)
        if self.bands == 1:
            # the type is complex means this is a SAR data
            if isinstance(type(ima[0, 0]), complex):
                ima = abs(ima)
            ima = ima.squeeze()
        else:
            ima = ima.transpose((1, 2, 0))
        ima = Raster.toUint8(ima)
        return ima
