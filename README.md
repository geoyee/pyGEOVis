# pyGEOVis

Visualize geo-tiff/json based on [folium](https://github.com/python-visualization/folium). It can be used to visualize geo-data (geotiff/geojson) after ML/DL about RS.

## USE

The class named `Geovis` just have three functions.Useing `addRaster` to add a image with geo-info (like geotiff) to the map and useing `addVector` to add a vector (just support geojson with polygon or multipolygon) to the map. In the end, useing `show` to show this interactive map.

```python
from pygeovis import Geovis

viser = Geovis()
viser.addRaster("data/val.tif", band_list=[1, 2, 3])
viser.addVector("data/val.geojson")
viser.show()
```

![R71JZHV@RIG33GLP0FK9SN3](https://user-images.githubusercontent.com/71769312/166901498-a5aee485-8a96-487d-8ef8-a279ba42a6b9.png)
