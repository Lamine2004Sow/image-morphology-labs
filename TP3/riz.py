import sys

import cv2, numpy
from Commun import morpho, strel, myutils

nom = sys.argv[1]
r = int(sys.argv[2])
s = int(sys.argv[3])

im = cv2.imread(nom, cv2.IMREAD_GRAYSCALE)

op = morpho.myopen(im, strel.build("disque", r))
th = im - op

#s = myutils.myseuil_interactif(th)
riz = myutils.seuil(th, s)

#Une ouverture supplémentaire sur l'image binaire pour retirer les petits pixels
g4 = strel.build("diamant", 1)
riz = morpho.myopen(riz, g4)

riz = cv2.copyMakeBorder(riz, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)

ero = riz
rayon = 2.0
while numpy.sum(ero)>0:
    rayon = rayon + 0.1
    ero = morpho.myerode(riz, strel.build("disque", rayon))

print(round(2*(rayon-0.1), 1))
