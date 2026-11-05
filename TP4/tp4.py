# Element structurant ligne taille 50 (longueur 100)
# objet sombre a preserver >> fermeture

from Commun import strel, morpho, myutil
import cv2, numpy

im = cv2.imread("Images/aeroport1.png", cv2.IMREAD_GRAYSCALE)

#cv2.imshow("Image", im)

imcolor = cv2.imread("Images/aeroport1.png")

#Accumulateur : image de départ toute blanche (255), qui servira à garder le minimum de toutes les fermetures
accumulateur = numpy.zeros_like(im)+255

#On ferme l'image avec une ligne dans chaque direction (0 à 179 degrés).
#Une piste est une bande sombre longue : elle survit à la fermeture par une ligne dans sa direction (la ligne reste dans
#la bande), alors que les petits objets sombres (voitures, marques) sont effacés par la fermeture.
#Le minimum sur tous les angles garde un pixel sombre dès qu'un angle l'a conservé : les pistes ressortent.
for angle in range(0, 180):
    el = strel.build("ligne", 50, angle)
    fe = morpho.myclose(im, el)
    accumulateur = numpy.minimum(accumulateur, fe)
    #print(angle)
    #cv2.imshow("fermeture", fe)
    #cv2.waitKey(0)

#On affiche le résultat de l'accumulation, puis on cherche à la main un seuil pour l'image d'origine et pour l'accumulateur
#(les valeurs trouvées sont ensuite données en arguments à aeroport.py)
cv2.imshow("accu", accumulateur)
cv2.waitKey(0)

myutil.myseuil_interactif(im)
myutil.myseuil_interactif(accumulateur)