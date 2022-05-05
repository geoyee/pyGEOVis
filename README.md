# pyGEOVis

Visualize geo-tiff/json based on [folium](https://github.com/python-visualization/folium).

## USE

```python
from pygeovis import Raster

raster = Raster("data/pred.tif")
raster.display()
```

## TODO

- [ ] 【TEST】Fix issue about CRS (just support WGS84).
- [ ] Add `geojson`.
