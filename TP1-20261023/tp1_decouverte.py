import numpy as np
import cv2
im = cv2.imread("Images/parrot.jpg", cv2.IMREAD_GRAYSCALE)

#print(im.shape)
#im[82::3,222:227] = (255,100,100)

im[im<100] = 0
im[im>=100] = 255

cv2.imshow("perroquet",im)
cv2.waitKey(0)
#cv2.imwrite("Images/parrot2.jpg",im)
