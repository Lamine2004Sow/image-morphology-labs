import sys

from Commun import strel, morpho, myutil
import cv2, numpy

#But : extraire les pistes d'un aéroport et les entourer en rouge sur l'image.
#Utilisation : python3 aeroport.py image.png l s r sortie.png
#(l = taille de la ligne, s = seuil, r = taille du carré de nettoyage, sortie = fichier résultat)
nom = sys.argv[1]
l = int(sys.argv[2])
s = int(sys.argv[3])
r = int(sys.argv[4])
sortie = sys.argv[5]


#Passage en HSV puis on garde le maximum entre la saturation (S) et la valeur (V) : permet de traiter aussi une image
#où les pistes ne se détachent pas en niveaux de gris simples (cas de aeroport3)
hsv = cv2.cvtColor(cv2.imread(nom), cv2.COLOR_BGR2HSV)
im = numpy.maximum(hsv[:, :, 1], hsv[:, :, 2])

#Image de départ toute blanche, qui garde le minimum des fermetures
accumulateur = numpy.zeros_like(im)+255

#Fermeture par une ligne dans chaque direction : les pistes (bandes longues et sombres) survivent dans leur direction,
#les petits objets sombres sont effacés. Le minimum sur tous les angles garde les pistes.
for angle in range(0, 180):
    el = strel.build("ligne", l, angle)
    fe = morpho.myclose(im, el)
    accumulateur = numpy.minimum(accumulateur, fe)

#Seuillage de l'accumulateur : image binaire des pistes
pistes = myutil.seuil(accumulateur, s)

#Nettoyage : l'ouverture enlève les petits points parasites, puis la fermeture bouche les petits trous dans les pistes
el = strel.build("carre", r)
pistes = morpho.myclose(morpho.myopen(pistes, el), el)

#Contour des pistes : gradient morphologique de l'image binaire (bord de 1 pixel)
g = morpho.mygradient(pistes, strel.build("carre", 1))
#Image d'origine en couleur (3 canaux) pour pouvoir dessiner en rouge dessus
imcolor = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
#Les pixels du contour sont coloriés en rouge (BGR : [0, 0, 255])
imcolor[g>0] = [0, 0, 255]

cv2.imwrite(sortie, imcolor)
