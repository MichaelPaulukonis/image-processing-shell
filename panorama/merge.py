import cv2
import numpy as np

def merge_panorama(images):
    """
    Merge a list of images into a panorama using a homography matrix.
    
    Args:
        images (list): List of image paths or numpy arrays.
        
    Returns:
        numpy.ndarray: Merged panorama image.
    """
    # Convert images to grayscale and numpy arrays
    imgs_gray = [cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY) if isinstance(img, str) else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) for img in images]
    
    # Find the homography matrices
    homographies = []
    for i in range(len(imgs_gray) - 1):
        img1 = imgs_gray[i]
        img2 = imgs_gray[i + 1]
        
        # Find keypoints and descriptors
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)
        
        # Match keypoints
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        # good_matches = matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.9 * n.distance:
                good_matches.append(m)
        
        # Find the homography matrix
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        homographies.append(H)
    
    # Warp and merge images
    result = imgs_gray[0]
    for i in range(len(homographies)):
        h, w = result.shape
        img = imgs_gray[i + 1]
        H = homographies[i]
        result[0:h, 0:w] = imgs_gray[i]
        result[0:img.shape[0], w:w + img.shape[1]] = img
    
    return result

# image1 = './samples/nancy.FB_so.hairbrush.jpg'
# # image2 = './samples/nancy.FB_museum.crop.01.jpg'
# image3 = './samples/nancy.FB_sluggo_museum.jpg'

image1 = './samples/nancy.FB_sluggo_museum.crop.00.jpg'
image2 = './samples/nancy.FB_sluggo_museum.crop.01.jpg'
image3 = './samples/nancy.FB_sluggo_museum.crop.02.jpg'


panorama = merge_panorama([image1, image2, image3])
cv2.imwrite('panorama.jpg', panorama)