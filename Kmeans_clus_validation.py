import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.mask import mask
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# Load clustered image
output_path = "G:/Mijn Drive/Dennensterfte/Labelme/testdata_Thomas/UAV/clustered_output4.tif"
clustered_img = rasterio.open(output_path)
clustered_array = clustered_img.read(1)

# Load reference image
reference_img = rasterio.open("G:/Mijn Drive/Dennensterfte/Labelme/testdata_Thomas/UAV/NDVI_threshold/resultaat vitaliteit drone NDVI/result_vitality_Arendonk.tif")

# Reproject reference image to match the clustered image
reprojected_reference_array = np.empty_like(clustered_array)
reproject(
    source=rasterio.band(reference_img, 1),
    destination=reprojected_reference_array,
    src_transform=reference_img.transform,
    src_crs=reference_img.crs,
    dst_transform=clustered_img.transform,
    dst_crs=clustered_img.crs,
    resampling=Resampling.nearest
)

# Set no-data values to -3
clustered_array[clustered_array == clustered_img.nodata] = -3
reprojected_reference_array[reprojected_reference_array == reference_img.nodata] = -3

# Ensure both images have the same extent (crop clustered image)
min_row = max(0, (clustered_img.height - reprojected_reference_array.shape[0]) // 2)
min_col = max(0, (clustered_img.width - reprojected_reference_array.shape[1]) // 2)

cropped_clustered_array = clustered_array[min_row:min_row + reprojected_reference_array.shape[0],
                                          min_col:min_col + reprojected_reference_array.shape[1]]

# Flatten arrays and remove no-data values before computing confusion matrix
valid_mask = (cropped_clustered_array != -3) & (reprojected_reference_array != -3)
y_true = reprojected_reference_array[valid_mask].flatten()
y_pred = cropped_clustered_array[valid_mask].flatten()


'''
# Count unique values in y_true
unique_values, counts = np.unique(y_pred, return_counts=True)

# Plot the counts of unique values in y_true
plt.figure(figsize=(8, 6))
sns.barplot(x=unique_values, y=counts, palette="viridis")

# Set labels and title
plt.xlabel('Unique Class Labels')
plt.ylabel('Count')
plt.title('Distribution of Unique Labels in True Values (y_true)')
plt.xticks(rotation=45)
plt.show()

# Optionally, print the counts for each unique value
for label, count in zip(unique_values, counts):
    print(f"Label: {label}, Count: {count}")
'''
# ["-1 (no data)", "0 (dead)", "1 (alive)", "2 (soil)", "3 (alive)"]
y_pred_modified = np.where(y_pred == 2, -1, y_pred)
y_pred_modified = np.where(y_pred_modified == 3, 1, y_pred_modified)

# Compute confusion matrix
conf_matrix = confusion_matrix(y_true, y_pred_modified)

# Define class labels (modify according to your classes)
class_labels= ["-1 (soil/no data)", "0 (dead)", "1 (alive)"]  # Adjust this based on your cluster IDs



# Plot confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap="Blues",
            xticklabels=class_labels, yticklabels=class_labels)

plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix")

plt.show()

print("Confusion Matrix:")
print(conf_matrix)

# Print the classification report
print("Classification Report:")
print(classification_report(y_true, y_pred_modified, target_names=class_labels))