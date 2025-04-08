# Data collection and preprocessing steps for modelling vitality of Pine trees based on UAV data and aerial (airplane) orthomosaics. 

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


#### Data downloading and preparation in QGIS 
1. Take the forest plot boundaries of the thesis of Thomas D'Hulster "testdata_Thomas/locaties bosbestanden/plots.geojson". 
Add an extra column to the attribute table with the name of each municipality where the plot is located. With this information, 
you can download the relevant ortho images (see later step 2). You can find the plot boundaries of the municipalities of Belgium at 
https://download.vlaanderen.be/Catalogus/?thema=grenzen&sort=4&q=voorlopig.
2. Download the 2023 ortho winter images for these municipalities via: https://download.vlaanderen.be/product/10426-orthofotomoza%C3%AFek-middenschalig-winteropnamen-kleur-2023-vlaanderen
These files are saved at > "./OrthoB_MS_winter_2023" --> the subfolders starting with "OMWRGB23VL_{unique code}". A copy of the .j2w and .jp2 are saved in the folder "jpeg_files". 
3. Through the metadata of the ortho images you can also indicate to the plots.geojson at which data campaign (shooting date) the images were taken. You can find this per download in the OMWRGB23VL_vdc.shp file.
OMWRGB23VL_vdc stands for:
- Nederlands: ortofotomozaïeken, middenschalig, rgb, 2023, Vlaanderen, vliegdagcontour.
- English: ortophoto mosaics, mid-scale, rgb, 2023, Flanders, flight day contour.

### Data preprocessing in python and data annotation orthomosaics (winter images, RGB, 2023)
4. clip_ortho_images.py: Clips the ortho images based on the plots.geojson file. The results are saved "./OrthoB_MS_winter_2023/clips".
5. drawRasterortho.py: makes raster of tiles for the model, select buffer to be large enough to cover full orthomosaic.
6. correctRasterortho.py: remove empty boxes (with no pixels).
7. extractTilesortho.py: crop the orthomosaic to the extent of every box. The results are saved here: "./OrthoB_MS_winter_2023/crop_clips".
5. Label the images using labelme with the pre-defined labels and flags. Type following command in the terminal:
~~~shell
labelme --labels labels_ortho.txt --flags flags_ortho.txt --nodata --validatelabel exact --config '{shift_auto_shape_color: -2}' 
~~~ 
Try to annotated 2-5 objects per label (where possible). Use the reference data of Thomas ("./testdata_Thomas/UAV/orthomozaiek" & "./testdata_Thomas/UAV/NDVI_threshold") for the photo interpretation. 