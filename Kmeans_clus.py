import matplotlib.pyplot as plt
import sklearn
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix, classification_report
import rasterio
import rasterio.features
import rasterio.warp
from rasterio.plot import show
import pandas as pd
import numpy as np
import seaborn as sns



img=rasterio.open("G:/Mijn Drive/Dennensterfte/Labelme/testdata_Thomas/UAV/Geclipt_Arendonk_repr.tif")
#img=rasterio.open("https://drive.google.com/drive/u/0/my-drive/Geclipt_Arendonk_repr.tif")
#show(img,0)

#read image
array=img.read()

# Store original shape
original_shape = array.shape[1:]


# Convert to DataFrame
dataframe = pd.DataFrame(array.reshape([5,-1]).T, columns=['B', 'G', 'R', 'RE', 'NIR'])
mask = dataframe.B != -32767.0
valid_data = dataframe[mask]

inertias = []

'''
Hyperparameter tuning --> determine the number of clusters

for i in range(1,11):
    kmeans = KMeans(n_clusters=i)
    kmeans.fit(valid_data)
    inertias.append(kmeans.inertia_)

plt.plot(range(1,11), inertias, marker='o')
plt.title('Elbow method')
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')
plt.show()

'''
# Apply KMeans clustering
kmeans = KMeans(n_clusters=4, init='k-means++', max_iter=500, random_state=42)

Y_KMeans = kmeans.fit(valid_data)

# Assign cluster labels to a full-size array
clustered_labels = np.full(mask.shape, -1)  # Initialize with -1 (no data)
clustered_labels[mask] = kmeans.labels_

# Assign label
X_group = dataframe.copy()
X_group['cluster_id'] = clustered_labels
print(X_group.head())

# Checking how many data points are there in each cluster
print(X_group['cluster_id'].value_counts())

# Scatter plot
#sns.scatterplot(x='R', y = 'NIR', hue = 'cluster_id', s=1, data = X_group, palette="deep")
#plt.show()

# Reshape clustered labels back into image shape
clustered_image = clustered_labels.reshape(original_shape)

# Export clustered result as a new TIFF file
output_path = "G:/Mijn Drive/Dennensterfte/Labelme/testdata_Thomas/UAV/clustered_output4b.tif"
with rasterio.open(
    output_path, "w",
    driver="GTiff",
    height=clustered_image.shape[0],
    width=clustered_image.shape[1],
    count=1,
    dtype=rasterio.int32,
    crs=img.crs,
    transform=img.transform
) as dst:
    dst.write(clustered_image.astype(rasterio.int32), 1)

print(f"Clustered image saved to {output_path}")

