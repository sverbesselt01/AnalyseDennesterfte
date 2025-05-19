# AI for orthomosaics

### Requirements
- Pycharm (community edition) or Visual studio
- Python 3.12 (or 3.13, but then the requirements file must be updated).
- QGIS (e.g. 3.40.4)

### Install python modules
1. Open terminal
2. Type following command in the terminal
~~~shell
pip install -r requirements.txt
~~~

:rocket: Ready to start :rocket:

### General processing steps
0. Modify the hyperparameters in the .env file. 
1. drawRaster.py: makes raster of tiles for DL model, select buffer to be large enough to cover full orthomosaic.
2. correctRaster.py: remove empty boxes (with no pixels).
3. In QGIS: Make a copy of your tile file and select the tiles that have a dead tree within the tile (data of Thomas).
4. extractTiles.py: crop the orthomosaic to the extent of every box.
5. Label the images using labelme. Type following command in the terminal:
~~~shell
labelme 
~~~
or reference directly to your folder and add your pre-defined labels:
~~~shell
labelme ./Images/FC --labels labels.txt --nodata --validatelabel exact --config '{shift_auto_shape_color: -2}'
~~~
or reference directly to your folder and add your pre-defined flags (for annotation or classification):
~~~shell
labelme ./Images/FC --flags flags.txt --nodata
~~~

6. Convert_json_to_polygons.py: make shape file with labels.

### Analysis options (first toy data --> UAV images)
7. Merge the alive trees and dead trees, dissolve boundaries. Make sure the dead trees are on top of the alive trees (shape_labels_merging.model3 script in QGIS). 
8. Scatterplot_and_correlation.py: Calculate the amount (in %) of dead trees, alive trees, soil for every tile do correlation between segemented trees (labelme) and result Thomas (NDVI thresholds + CHM threshold).
9. Kmeans_clus.py: Pixel-wise clustering of UAV imagery. Find optimal amount of clusters and predict.
10. Kmeans_clus_validation.py: Validation of the clustering result with the reference imagery (Thomas: result_vitality_{name_location}.tif).

