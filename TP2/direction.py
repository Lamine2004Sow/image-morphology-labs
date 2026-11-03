import sys

from Commun import strel,morpho
import numpy as np
import cv2

im = cv2.imread(sys.argv[1])

#bleu = im[:,:,0]
#vert = im[:,:,1]
rouge = im[:,:,2]

s_min = None
angle_min = None

for angle in range(-90,91,1):
    el = strel.build("ligne",40, angle)
    g = morpho.mygradient(rouge, el)
    s = np.sum(g)
    if s_min is None or s < s_min:
        s_min = s
        angle_min = angle

print(angle_min)