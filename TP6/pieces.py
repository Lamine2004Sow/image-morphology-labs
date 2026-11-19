from Commun import morpho, strel, myutil
import cv2, numpy, bisect, random

g8 = strel.build("carre", 1)

im = cv2.imread("Images/coins.jpg", cv2.IMREAD_GRAYSCALE)
g = morpho.mygradient(im, g8)

#ASF par reconstruction en 15 étapes pour éliminer les petits détails sans effacer les pieces
resultat_asf = im
for rayon in range(2, 16):
    el = strel.build("disque", rayon)
    resultat_asf = morpho.myopenrecon(resultat_asf, el, g8)
    resultat_asf = morpho.mycloserecon(resultat_asf, el, g8)

#Ligne de test pour tenter le gradient de la ligne de partage des eaux sur l'image asf
#g = morpho.mygradient(resultat_asf, g8)

#Fermeture pour retirer les ombres portées
#(l'ombre est un creux sombre fin entre deux pièces superposées : la fermeture le bouche, sinon le seuil couperait les pièces)
fe = morpho.myclose(resultat_asf, strel.build("disque", 3))

#v = myutil.myseuil_interactif(fe)
#Seuil : les pièces en blanc, le fond en noir
s = myutil.seuil(fe, 156)
r=s

#Construction de la carte de distance
#On érode par des disques de plus en plus grands : un pixel qui disparaît au rayon r est à une distance d'environ r du fond.
#er2 est l'érosion du tour précédent (rayon-1) : er2 - er1 donne les pixels qui viennent de disparaître,
#ils prennent la valeur rayon.
#On s'arrête quand l'érosion a tout effacé. Le centre des pièces a la plus grande distance.
distance = numpy.zeros_like(im)
er1 = s
rayon=2
while numpy.sum(er1)>0:
    er2 = er1 #equivalent a er2 = morpho.myerode(s, strel.build("disque", rayon-1))
    er1 = morpho.myerode(s, strel.build("disque", rayon))
    pixels_interessants = er2 - er1
    distance[pixels_interessants>0] = rayon
    rayon+=1


#H-maxima : on garde le haut (sur une hauteur h) de chaque montagne de la carte de distance, une montagne par pièce.
#Deux pièces collées ont deux sommets séparés par un col : si chaque sommet dépasse le col d'au moins h,
#on obtient deux marqueurs séparés. Plus h est grand, moins on garde de petits sommets parasites
#Etape 1 : Soustraction de h (on met d'abord à h ce qui est sous h, pour que l'uint8 ne reboucle pas en négatif)
h= 10
distance2 = numpy.copy(distance)
distance2[distance2<h] = h
distance2 = distance2 - h

#Etape 2 : reconstruction inférieure de la carte de distance à partir de la carte abaissée de h.
#La reconstruction remonte la carte abaissée sans jamais dépasser distance : les sommets restent h plus bas,
#les montagnes de moins de h de haut sont rasées
distance3 = morpho.myreconinf(distance, distance2, g8)

#Etape 3 : qui a disparu de distance par rapport à distance 3 ?
#distance4 n'est non nul qu'en haut des montagnes et vaut h au sommet : on seuille un peu sous h (h-3)
#pour ne garder que le sommet, ce sont les marqueurs des pièces
distance4 = distance - distance3
marqueurs = myutil.seuil(distance4, h-3)

#Ligne de partage des eaux
#Etape 1 : chaque composante connexe du marqueurs doit avoir un niveau de gris spécifique
#entre 2 et valeur max
#On extrait chaque composante par reconstruction depuis un pixel, on lui donne le niveau cpt, puis on la retire de marqueurs
#(même principe que le comptage des grains de riz). tmp n'est pas remis à zéro, mais la reconstruction le limite à marqueurs
#donc les anciens pixels disparaissent tout seuls
m = numpy.zeros_like(im)
tmp = numpy.zeros_like(im)
cpt=2
for x in range(0, marqueurs.shape[0]):
    for y in range(0, marqueurs.shape[1]):
        if marqueurs[x,y] > 0:
            tmp[x,y] = 255
            comp_connexe = morpho.myreconinf(marqueurs, tmp, g8)
            marqueurs = marqueurs - comp_connexe
            m[comp_connexe>0] = cpt
            cpt+=1

#Puis, le fond doit avoir un marqueur à 1
#Les pièces ne touchent pas le bord de l'image : le cadre est donc sûr d'être dans le fond.
#Sans ce marqueur, les pièces envahiraient tout le fond pendant l'inondation
m[0,:]=1
m[:,0]=1
m[-1,:]=1
m[:,-1]=1

#Etape 2
#Remplissage de la liste L avec les pixels non nuls de l'image m de marqueurs
print("Debut Watershed")
#Ligne de partage des eaux
cpt_pixel=0
el = strel.build_as_list("carre", 1)
L = []
lignes,colonnes = numpy.nonzero(m)
for l,c in zip(lignes,colonnes):
    L.append((l,c,g[l,c]))

L.sort(key = lambda elem:elem[2])

#Etape 3 : début de la ligne de partage des eaux (même algorithme que route.py)
#On sort le pixel le plus bas, ses voisins pas encore inondés prennent son étiquette et sont insérés dans L selon leur altitude
while len(L)>0:
    ligne,colonne,valeur=L.pop(0)
    cpt_pixel+=1 #cpt_pixel permet de mettre en place un petit compteur d'avancement
    for el_ligne, el_colonne in el:
        ligne_voisin = ligne+el_ligne
        colonne_voisin = colonne+el_colonne
        if 0<=ligne_voisin<g.shape[0] and 0<=colonne_voisin<g.shape[1] and m[ligne_voisin, colonne_voisin]==0:
            m[ligne_voisin,colonne_voisin]=m[ligne, colonne]
            bisect.insort(L, (ligne_voisin, colonne_voisin, g[ligne_voisin, colonne_voisin]), key=lambda elem:elem[2])

    #Affichage du compteur (en % des pixels de l'image), la boucle est lente car L.pop(0) décale toute la liste
    if cpt_pixel%1000 == 0:
        print(cpt_pixel/(im.shape[0]*im.shape[1])*100)


#Affichage des résultats : chaque pixel de l'image m possède une valeur selon l'objet
#auquel il appartient
#on calcule le gradient pour obtenir la frontière entre les objets
#et la faire apparaître en rouge sur l'image de départ
g2 = morpho.mygradient(m, strel.build("carre", 1))
imcouleur = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
imcouleur[g2>0]=[0, 0, 255]
cv2.imshow("Resultat", imcouleur)
cv2.waitKey(0)

#Affichage des résultats : on affiche chaque objet avec une couleur aléatoire
for i in range(2, int(numpy.max(m))+1):
    imcouleur[m==i] = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
imcouleur[m==1] = (0,0,0)

cv2.imshow("Resultat", imcouleur)
cv2.waitKey(0)

