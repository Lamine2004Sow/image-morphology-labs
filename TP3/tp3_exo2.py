import cv2, numpy
from Commun import morpho, strel, myutils

im = cv2.imread("Images/text4.png", cv2.IMREAD_GRAYSCALE)

#Procédure de Top hat : Image - Ouverture(Image)
el = strel.build("disque", 30)
cl = morpho.myclose(im, el) # cl > im
bh = cl - im

#s = myutils.myseuil_interactif(th)
result = myutils.seuil(bh, 15)

cv2.imshow("Texte", im)
cv2.imshow("Fermeture", cl)
cv2.imshow("Bottom Hat", bh)
cv2.imshow("Seuil", result)
cv2.waitKey(0)
