import sys

from Commun import strel,morpho
import numpy as np
import cv2

#But : retrouver l'angle d'inclinaison des lignes d'une feuille (le fichier image est donné en argument).
#Principe : un gradient avec une ligne dans la direction des traits de la feuille donne très peu de contours,
#donc la somme du gradient est MINIMALE pour le bon angle.
im = cv2.imread(sys.argv[1])

#OpenCV charge en BGR : indice 2 = canal rouge. On garde le rouge car c'est lui qui donne le meilleur contraste ici.
#bleu = im[:,:,0]
#vert = im[:,:,1]
rouge = im[:,:,2]

s_min = None
angle_min = None

#On teste tous les angles de -90 à 90 degrés, de 1 en 1, avec une ligne de taille 40
for angle in range(-90,91,1):
    el = strel.build("ligne",40, angle)
    g = morpho.mygradient(rouge, el)
    #Somme de tous les pixels du gradient : mesure de la quantité de contours
    s = np.sum(g)
    #On retient l'angle pour lequel la somme est la plus petite
    if s_min is None or s < s_min:
        s_min = s
        angle_min = angle

#Affiche l'angle trouvé (le résultat du script)
print(angle_min)