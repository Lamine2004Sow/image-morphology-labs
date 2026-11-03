import numpy as np
import cv2
from Commun import strel,morpho

im =cv2.imread("Images/papier_60.png")

bleu = im[:,:,0]
vert = im[:,:,1]
rouge = im[:,:,2]

"""
for im,title in[(bleu, "bleu"), (vert, "vert"), (rouge, "rouge")]:
    cv2.imshow(title,im)
cv2.waitKey(0)
"""

for angle in range(-90,90,5):
#angle=-90
#while True:
    el = strel.build("ligne", 40, angle)
    g = morpho.mygradient(rouge, el)
    s = np.sum(g)
    print(f"{angle}, {s}")

    #cv2.imshow("Resultat gradient",g)
    #print(f"Angle : {angle}")
    #cv2.waitKey(0)
    #angle+=5

