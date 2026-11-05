import numpy as np
import cv2


#Seuillage : pixels >= s mis à 255 (blanc), les autres à 0 (noir).
#Impact : transforme une image en niveaux de gris en image binaire, étape qui suit presque tous les traitements (top hat, fermeture...).
def seuil(im, s):
    im_s = np.zeros_like(im)
    im_s[im >= s]=255
    return im_s


#Seuillage interactif : ouvre une fenêtre avec une barre (0 à 256) qui réaffiche le seuillage à chaque changement.
#On appuie sur une touche pour valider et la fonction renvoie le seuil choisi.
#Utilité : trouver à l'oeil la bonne valeur de seuil, à reporter ensuite en dur dans le script.
def myseuil_interactif(im):
    global seuil1

    def myseuil_interactif_callback(val):
        global seuil1
        seuil1=val
        cv2.imshow('Interactive Threshold', seuil(im, seuil1))

    cv2.namedWindow('Interactive Threshold')
    cv2.createTrackbar('Threshold', 'Interactive Threshold', 100, 256, myseuil_interactif_callback)
    myseuil_interactif_callback(100)

    cv2.waitKey(0)
    cv2.destroyWindow('Interactive Threshold')
    return seuil1