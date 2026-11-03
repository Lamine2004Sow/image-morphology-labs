import sys

from Commun import strel, morpho, myutils
import cv2, numpy

nom = sys.argv[1]
l = int(sys.argv[2])
s = int(sys.argv[3])
r = int(sys.argv[4])
sortie = sys.argv[5]


hsv = cv2.cvtColor(cv2.imread(nom), cv2.COLOR_BGR2HSV)
im = numpy.maximum(hsv[:, :, 1], hsv[:, :, 2])

accumulateur = numpy.zeros_like(im)+255

for angle in range(0, 180):
    el = strel.build("ligne", l, angle)
    fe = morpho.myclose(im, el)
    accumulateur = numpy.minimum(accumulateur, fe)

pistes = myutils.seuil(accumulateur, s)

el = strel.build("carre", r)
pistes = morpho.myclose(morpho.myopen(pistes, el), el)

g = morpho.mygradient(pistes, strel.build("carre", 1))
imcolor = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
imcolor[g>0] = [0, 0, 255]

cv2.imwrite(sortie, imcolor)
