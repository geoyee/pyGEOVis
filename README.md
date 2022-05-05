# pyGEOVis

Visualize geo-tiff/json based on [folium](https://github.com/python-visualization/folium).

## USE

```python
from pygeovis import Geovis

Geovis.showRaster(
    raster_path="data/pred.tif",
    band_list=[1]
)
```

![U8257G4V`W(B(HK5M9 ~UK](https://user-images.githubusercontent.com/71769312/166859742-fa826dbb-076e-487d-b66b-56c348562f18.png)

## TODO

- [x] Fix issue about CRS (just support WGS84).
- [ ] Add `geojson`.
- [ ] Adaptive zoom.

## TEST

- [ ] Fix issue about CRS (just support WGS84).
