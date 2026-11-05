import cv2, numpy
from Commun import morpho, strel, myutil

im = cv2.imread("Images/text4.png", cv2.IMREAD_GRAYSCALE)

#But : extraire le texte noir d'une page dont l'éclairage n'est pas uniforme.
#Procédure de Bottom hat : Fermeture(Image) - Image (le texte est sombre, donc on utilise la fermeture et non l'ouverture)
#La fermeture par un disque plus gros que l'épaisseur des lettres efface le texte et garde le fond.
el = strel.build("disque", 30)
cl = morpho.myclose(im, el) # cl > im
#Comme cl >= im, la différence est positive : il ne reste que le texte (clair), le fond est à 0
bh = cl - im

#s = myutils.myseuil_interactif(th)
#Seuillage final : le texte devient blanc, le reste noir. 15 trouvé avec le seuillage interactif
result = myutil.seuil(bh, 15)

#On affiche chaque étape pour vérifier que le traitement se passe bien

cv2.imshow("Texte", im)
cv2.imshow("Fermeture", cl)
cv2.imshow("Bottom Hat", bh)
cv2.imshow("Seuil", result)
cv2.waitKey(0)
