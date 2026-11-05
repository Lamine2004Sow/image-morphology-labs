import sys

import cv2, numpy
from Commun import morpho, strel, myutil

#But : mesurer l'épaisseur d'un grain de riz. Utilisation : python3 riz.py image.png r s
#(r = rayon du disque du top hat, s = seuil). Le résultat est affiché dans le terminal.
nom = sys.argv[1]
r = int(sys.argv[2])
s = int(sys.argv[3])

im = cv2.imread(nom, cv2.IMREAD_GRAYSCALE)

#Top hat : image - ouverture. L'ouverture par un disque plus gros qu'un grain enlève les grains et laisse le fond,
#donc la différence ne garde que les grains et supprime le gradient d'éclairage de l'image.
#Le disque doit être plus large que l'épaisseur d'un grain, sinon les grains restent dans l'ouverture et disparaissent.
op = morpho.myopen(im, strel.build("disque", r))
th = im - op

#s = myutils.myseuil_interactif(th)
#Seuillage du top hat : image binaire où les grains sont blancs
riz = myutil.seuil(th, s)

#Une ouverture supplémentaire sur l'image binaire pour retirer les petits pixels
g4 = strel.build("diamant", 1)
riz = morpho.myopen(riz, g4)

#On ajoute 1 pixel noir autour de l'image : sans lui, un grain coupé par le bord serait vu comme infini par l'érosion
#(l'érosion ne voit rien de noir au-delà du bord) et fausserait la mesure.
riz = cv2.copyMakeBorder(riz, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)

#Mesure de l'épaisseur : on érode avec un disque de plus en plus grand jusqu'à ce que tout l'image soit noire.
#Le dernier rayon pour lequel il restait quelque chose est le plus grand disque qui rentre dans un grain,
#donc le diamètre (2 x rayon) est l'épaisseur. Le pas de 0.1 donne une mesure précise au dixième de pixel.
ero = riz
rayon = 2.0
while numpy.sum(ero)>0:
    rayon = rayon + 0.1
    ero = morpho.myerode(riz, strel.build("disque", rayon))

#rayon - 0.1 : on revient au dernier rayon pour lequel l'érosion n'était pas vide (le while est sorti un pas trop loin)
print(round(2*(rayon-0.1), 1))
