import numpy as np
import cv2

im = cv2.imread("Images/dog.png", cv2.IMREAD_GRAYSCALE)

def first_erode(im):
    im_out = np.zeros_like(im)
    for i in range(1, im.shape[0] - 1):
        for j in range(1, im.shape[1] - 1):
            im_out[i, j] = np.min(im[i-1:i+2, j-1:j+2])
    return im_out

def first_dilate(im):
    im_out = np.zeros_like(im)
    for i in range(1, im.shape[0] - 1):
        for j in range(1, im.shape[1] - 1):
            im_out[i,j] = np.max(im[i-1:i+2, j-1:j+2])
    return im_out

