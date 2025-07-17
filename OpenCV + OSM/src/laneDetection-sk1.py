import numpy as np
import matplotlib.pyplot as plt
from skimage import io, color, filters, morphology, exposure
import cv2

# Load the orthophoto
image = io.imread('../data/reprojected-tiles/2019/tile_5_11_2019.tif')

# Convert to grayscale
gray = color.rgb2gray(image)

# Contrast stretching for better edge visibility
p2, p98 = np.percentile(gray, (2, 98))
gray_eq = exposure.rescale_intensity(gray, in_range=(p2, p98))

# Sobel edge detection
edges = filters.sobel(gray_eq)

# Threshold to binary
binary = edges > 0.05

# Morphological operations to clean up
binary = morphology.closing(binary, morphology.square(3))
binary = morphology.remove_small_objects(binary, min_size=150)

# Save the result
binary_img = (binary * 255).astype(np.uint8)
cv2.imwrite("../data/output/lane_mask_ski_noguidance.png", binary_img)

# Display
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(image)
ax[0].set_title("Original Orthophoto")
ax[1].imshow(binary, cmap='gray')
ax[1].set_title("Detected Lanes (No OSM)")
plt.show()
