import numpy as np
import cv2

im = cv2.imread("Images/dog.png", cv2.IMREAD_GRAYSCALE)

#Première érosion écrite à la main, avec un voisinage 3x3 fixe : chaque pixel prend le minimum de ses 8 voisins + lui-même.
#Les bords de l'image (1 pixel) restent à 0 car on ne parcourt que de 1 à shape-1.
#Utilité : comprendre le principe avant d'utiliser cv2.erode et strel (voir Commun/morpho.py). Très lente car boucles Python.
def first_erode(im):
    im_out = np.zeros_like(im)
    for i in range(1, im.shape[0] - 1):
        for j in range(1, im.shape[1] - 1):
            im_out[i, j] = np.min(im[i-1:i+2, j-1:j+2])
    return im_out

#Même principe que first_erode, mais avec le MAXIMUM du voisinage 3x3 : les objets clairs grossissent.
def first_dilate(im):
    im_out = np.zeros_like(im)
    for i in range(1, im.shape[0] - 1):
        for j in range(1, im.shape[1] - 1):
            im_out[i,j] = np.max(im[i-1:i+2, j-1:j+2])
    return im_out

#Gradient prévu : dilatation - érosion, pour obtenir les contours.
#Attention : la ligne actuelle fait first_erode(im) - first_erode(im), ce qui vaut toujours 0 (probablement first_dilate(im) - first_erode(im) voulu).
def my_gradient(im):
    return first_erode(im) - first_erode(im)


#On recharge une autre image (kingdom.png) et on l'affiche. waitKey(0) attend l'appui sur une touche avant de fermer la fenêtre.
im = cv2.imread("Images/kingdom.png", cv2.IMREAD_GRAYSCALE)
cv2.imshow("im", im)
cv2.waitKey(0)


