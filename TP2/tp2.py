import numpy as np
import cv2
from Commun import strel,morpho

#Version de test de direction.py : même méthode, mais sur une image fixe (papier_60.png) et en affichant la somme
#du gradient pour chaque angle (pas de 5). Permet de voir à quoi ressemble la courbe avant de ne garder que le minimum.
im =cv2.imread("Images/papier_60.png")

#Séparation des trois canaux (OpenCV charge en BGR)
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
    #Gradient avec une ligne de taille 40 orientée selon l'angle, puis somme des contours.
    #Le bon angle est celui où la somme est la plus faible.
    el = strel.build("ligne", 40, angle)
    g = morpho.mygradient(rouge, el)
    s = np.sum(g)
    print(f"{angle}, {s}")

    #cv2.imshow("Resultat gradient",g)
    #print(f"Angle : {angle}")
    #cv2.waitKey(0)
    #angle+=5

