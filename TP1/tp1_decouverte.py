"""
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
"""
#Le bloc ci-dessus (entre guillemets) est le premier essai de découverte d'OpenCV : seuillage manuel du perroquet
#avec des masques numpy, laissé en commentaire car plus utilisé.

import cv2
from Commun import strel, morpho

#g8 : élément structurant carré de rayon 1 (3x3), il représente la connexité 8 (les 8 voisins comptent).
g8 = strel.build("carre", 1)

#g4 : élément structurant en diamant de rayon 1 (croix), il représente la connexité 4 (haut, bas, gauche, droite).
#Ces deux éléments sont réutilisés dans tous les TP suivants (reconstruction, comptage de grains...).
g4 = strel.build("diamant", 1)


