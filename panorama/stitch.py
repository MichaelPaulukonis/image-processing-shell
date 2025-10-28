import cv2
import numpy as np

image1 = './samples/nancy.FB_sluggo_museum.jpg'
image2 = './samples/nancy.FB_IMG_1681563314624.jpg'
image3 = './samples/nancy.FB_so.hairbrush.jpg'

# Load images
images = [cv2.imread(image2), cv2.imread(image3)]

# Create stitcher object
stitcher = cv2.Stitcher_create()
stitcher.setPanoConfidenceThresh(0.0)

# Stitch images
status, panorama = stitcher.stitch(images)

# Check for errors
if status == cv2.Stitcher_OK:
    print("Panorama created successfully!")
    cv2.imshow('Panorama', panorama)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Error during stitching!")
    print(status)
