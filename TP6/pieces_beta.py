from Commun import morpho, strel, myutil
import numpy, cv2, bisect

im =  cv2.imread("Images/coins.jpg", cv2.IMREAD_GRAYSCALE)

resultat_asf = im
g8 = strel.build("carre", 1)

for rayon in range(2, 16):
    el = strel.build("disque", rayon)
    resultat_asf = morpho.myopenrecon(resultat_asf, el, g8)
    resultat_asf = morpho.mycloserecon(resultat_asf, el, g8)

fe = morpho.myclose(resultat_asf, strel.build("disque", 3))

#v = myutil.myseuil_interactif(fe)
s = myutil.seuil(fe, 156)
r=s

distance = numpy.zeros_like(im)
er1 = s
rayon=2
while numpy.sum(er1)>0:
    er2 = er1 #equivalent a er2 = morpho.myerode(s, strel.build("disque", rayon-1))
    er1 = morpho.myerode(s, strel.build("disque", rayon))
    #er1 = morpho.myerode(s, strel.build("disque", rayon))
    #er2 = morpho.myerode(s, strel.build("disque", rayon-1))
    pixels_interessants = er2 - er1
    distance[pixels_interessants>0] = rayon
    rayon+=1



#H-maxima
#Etape 1 : Soustraction de h
h= 10
distance2 = numpy.copy(distance)
distance2[distance2<h] = h
distance2 = distance2 - h

#Etape 2 : reconstruction inférieure
distance3 = morpho.myreconinf(distance, distance2, g8)

#Etape 3 : qui a disparu de distance par rapport à distance 3 ?
distance4 = distance - distance3
#myutil.myseuil_interactif(distance4)
marqueurs = myutil.seuil(distance4, h-3)


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

m[0,:]=1
m[:,0]=1
m[-1,:]=1
m[:,-1]=1

#Ligne de partage des eaux sur l'image sans details
g = morpho.mygradient(resultat_asf, strel.build("carre", 1))
el = strel.build_as_list("carre", 1)

L = []
lignes,colonnes = numpy.nonzero(m)
for l,c in zip(lignes, colonnes):
    L.append((l,c,g[l,c]))
L.sort(key = lambda elem:elem[2])

cpt_pixel = 0
while len(L)>0:
    ligne,colonne,valeur = L.pop(0)
    cpt_pixel+=1
    for el_ligne, el_colonne in el:
        ligne_voisin = ligne+el_ligne
        colonne_voisin = colonne+el_colonne
        if 0<=ligne_voisin<g.shape[0] and 0<=colonne_voisin<g.shape[1] and m[ligne_voisin, colonne_voisin]==0:
            m[ligne_voisin,colonne_voisin]=m[ligne, colonne]
            bisect.insort(L, (ligne_voisin, colonne_voisin, g[ligne_voisin, colonne_voisin]), key = lambda elem:elem[2])

    if cpt_pixel%1000 == 0:
        print(cpt_pixel/(im.shape[0]*im.shape[1])*100)

m = numpy.uint8(numpy.uint64(m)*255/numpy.max(m))
cv2.imshow("Resultat", m)

g2 = morpho.mygradient(m, strel.build("carre", 1))
imcouleur = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
imcouleur[g2>0]=[0, 0, 255]

cv2.imshow("Resultat", imcouleur)
cv2.waitKey(0)

#el = strel.build("disque", 2)
#s2 = morpho.myerode(s, el)

#resultat_openclose = morpho.myopenrecon(im, el, g8)
#resultat_openclose = morpho.mycloserecon(resultat_openclose, el, g8)

#cv2.imshow("Resultat asf", resultat_asf)
#cv2.imshow("Fermeture", fe)
#cv2.imshow("Seuil", s)
#cv2.imshow("Carte distance", distance)
#cv2.imshow("Distance 3", distance3)
#cv2.imshow("Distance 4", distance4)
#cv2.imshow("Seuil grignoter", s2)
#cv2.imshow("Resultat simple open close", resultat_openclose)
#cv2.waitKey(0)