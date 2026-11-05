import cv2, numpy
from Commun import morpho, strel, myutil
from Commun import myutil
import sys


def mesurer_epaisseur(grain):
    x, y = numpy.nonzero(grain)
    #On recadre autour du grain avec une marge de 1 pixel. La borne de fin d'un slice est exclue : on utilise donc
    #grain.shape[0] et non grain.shape[0]-1, sinon la dernière ligne (ou colonne) de l'image serait coupée
    grain = grain[max(x.min()-1,0) : min(x.max()+2, grain.shape[0]), max(y.min()-1,0) : min(y.max()+2, grain.shape[1])]

    rayon = 1.0
    op1=grain
    while numpy.sum(op1) > 0:
        rayon = rayon + 0.1
        el = strel.build("disque", rayon)
        op1 = morpho.myerode(grain, el)
    return 2*rayon


def mesurer_longueur(grain):
    x2, y2 = numpy.nonzero(grain)
    #Même recadrage que pour l'épaisseur : on garde grain.shape[0] (et non shape[0]-1) car la borne de fin d'un slice
    #est exclue, sinon la dernière ligne (ou colonne) de l'image serait coupée
    grain = grain[max(x2.min() - 1, 0): min(x2.max() + 2, grain.shape[0]), max(y2.min() - 1, 0):min(y2.max() + 2, grain.shape[1])]

    rayonmax = 0.0
    anglemax = 0
    rayon = 1.0
    for angle in range(0,180):
        op1 = grain
        while numpy.sum(op1) > 0:
            rayon = rayon + 1.0
            el = strel.build("ligne", rayon, angle)
            op1 = morpho.myerode(grain, el)
        rayon = rayon - 1.0
        if rayon > rayonmax:
            rayonmax = rayon
            anglemax = angle
    return (2*rayonmax, anglemax)

im = cv2.imread("../TP3/Images/rice.png", cv2.IMREAD_GRAYSCALE)
imcolor = cv2.imread("../TP3/Images/rice.png")

op = morpho.myopen(im, strel.build("disque", 20))
th = im - op

#s = myutil.myseuil_interactif(th)
r = myutil.seuil(th, 50)

#Une ouverture supplémentaire sur l'image binaire pour retirer les petits pixels parasites
g4_4 = strel.build("diamant", 2)
g8 = strel.build("carre", 1)
g4 = strel.build("diamant", 1)

r3 = morpho.myopenrecon(r, g4_4, g8)

cadre = numpy.zeros_like(r3)
cadre[:,0]=255
cadre[:,-1]=255
cadre[0,:]=255
cadre[-1,:]=255
cadre[r3==0]=0

t = morpho.myreconinf(r3, cadre, g8)

r3 = r3 - t


#Dénombrement des composantes connexes
m = numpy.zeros_like(r3)
im = r3.copy()
carte_epaisseur = numpy.zeros(im.shape, numpy.float64)
carte_longueur = numpy.zeros(im.shape, numpy.float64)
carte_orientation = numpy.zeros(im.shape, numpy.float64)
cpt=0
for x in range(0, im.shape[0]):
    for y in range(0, im.shape[1]):
        if im[x,y] > 0:
            m[x,y] = 255
            grain = morpho.myreconinf(im, m, g4)
            im = im - grain
            cpt+=1
            ep = mesurer_epaisseur(grain)
            long,orient = mesurer_longueur(grain)
            carte_epaisseur[grain>0] = ep
            carte_longueur[grain>0] = long
            carte_orientation[grain>0] = orient
            print(long, orient)
            #cv2.imshow("grain", grain)
            #cv2.waitKey(0)



#Phase de normalisation de carte epaisseur : on cherche la valeur max des épaisseurs (= valeur max de l'image)
#ainsi que la valeur min des épaisseur (n'est pas la valeur min de l'image car la valeur min de l'image, c'est le fond)
maxi_e = numpy.max(carte_epaisseur)
mini_e = numpy.min(carte_epaisseur[carte_epaisseur>0])
#On réalise la normalisation pour avoir des valeur entières entre 0 et 255
carte_epaisseur = numpy.uint8((carte_epaisseur - mini_e)/(maxi_e-mini_e)*255)
#On applique la colormap pour avoir une image en couleur : les valeurs les plus faibles seront bleues et les plus élevées
#seront rouges
carte_epaisseur = cv2.applyColorMap(carte_epaisseur, cv2.COLORMAP_JET)
#On colorie manuellement les pixels du fond (qui n'ont pas d'épaisseur) en noir ou, comme ici, avec leur niveau de gris
#dans l'image d'origine
carte_epaisseur[r3==0]=imcolor[r3==0]

#Phase de normalisation de carte longueur : on cherche la valeur max des longueurs (= valeur max de l'image)
#ainsi que la valeur min des longueurs (n'est pas la valeur min de l'image car la valeur min de l'image, c'est le fond)
maxi_l = numpy.max(carte_longueur)
mini_l = numpy.min(carte_longueur[carte_longueur>0])
#On réalise la normalisation pour avoir des valeur entières entre 0 et 255
carte_longueur = numpy.uint8((carte_longueur - mini_l)/(maxi_l-mini_l)*255)
#On applique la colormap pour avoir une image en couleur : les grains les plus courts seront bleus et les plus longs
#seront rouges
carte_longueur = cv2.applyColorMap(carte_longueur, cv2.COLORMAP_JET)
#On colorie manuellement les pixels du fond (qui n'ont pas de longueur) en noir ou, comme ici, avec leur niveau de gris
#dans l'image d'origine
carte_longueur[r3==0]=imcolor[r3==0]

#Phase de normalisation de carte orientation : ici pas besoin de chercher le min et le max dans l'image, on les connaît :
#les angles testés vont de 0 à 179 degrés, on fixe donc mini_o = 0 et maxi_o = 179
mini_o = 0
maxi_o = 179
#On réalise la normalisation pour avoir des valeur entières entre 0 et 255
carte_orientation = numpy.uint8((carte_orientation - mini_o)/(maxi_o-mini_o)*255)
#On applique la colormap pour avoir une image en couleur : les angles les plus faibles seront bleus et les plus élevés
#seront rouges (attention : 0 et 179 degrés sont presque la même direction, mais auront des couleurs opposées)
carte_orientation = cv2.applyColorMap(carte_orientation, cv2.COLORMAP_HSV)
#On colorie manuellement les pixels du fond (qui n'ont pas d'orientation) en noir ou, comme ici, avec leur niveau de gris
#dans l'image d'origine
carte_orientation[r3==0]=imcolor[r3==0]

#cv2.imshow("Carte Epaisseur", carte_epaisseur)
cv2.imshow("Carte Longueur", carte_longueur)
cv2.imshow("Carte Orientation", carte_orientation)
cv2.imwrite("cartepaisseur.png", carte_epaisseur)
cv2.imwrite("cartelongueur.png", carte_longueur)
cv2.imwrite("carteorientation.png", carte_orientation)
cv2.waitKey(0)
