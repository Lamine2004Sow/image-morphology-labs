# Element structurant ligne taille 50 (longueur 100)
# objet sombre a preserver >> fermeture

from Commun import strel, morpho, myutils
import cv2, numpy

im = cv2.imread("Images/aeroport1.png", cv2.IMREAD_GRAYSCALE)

#cv2.imshow("Image", im)

imcolor = cv2.imread("Images/aeroport1.png")

accumulateur = numpy.zeros_like(im)+255

for angle in range(0, 180):
    el = strel.build("ligne", 50, angle)
    fe = morpho.myclose(im, el)
    accumulateur = numpy.minimum(accumulateur, fe)
    #print(angle)
    #cv2.imshow("fermeture", fe)
    #cv2.waitKey(0)

cv2.imshow("accu", accumulateur)
cv2.waitKey(0)

myutils.myseuil_interactif(im)
myutils.myseuil_interactif(accumulateur)