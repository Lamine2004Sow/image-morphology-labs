from Commun import morpho, strel
import cv2, numpy, bisect

im = cv2.imread("Images/route.png", cv2.IMREAD_GRAYSCALE)
#On calcule le gradient : il est fort sur les bords des objets. La ligne de partage des eaux voit ce gradient comme un relief,
#les bords sont les crêtes entre les bassins, et c'est sur ces crêtes que les deux objets vont se rencontrer
g = morpho.mygradient(im, strel.build("carre", 1))
m = numpy.zeros_like(im)
#Voisinage Γ8 sous forme de liste de coordonnées, pour parcourir les voisins d'un pixel un par un
el = strel.build_as_list("carre", 1)

#Une seule image de marqueurs : chaque objet a son propre niveau de gris (100 la forêt, 200 le bitume), 0 = pas encore inondé
for image, valeur in [("Images/route_foret.png", 100), ("Images/route_bitume.png", 200)]:
    m1 = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    m[m1>0]=valeur

#On met dans la liste L tous les pixels marqués, avec la valeur du gradient en ce pixel (son altitude)
L = []
lignes,colonnes = numpy.nonzero(m)

for l,c in zip(lignes, colonnes):
    L.append((l,c,g[l,c]))

#On trie par altitude : on inonde toujours en premier le pixel le plus bas
L.sort(key = lambda elem:elem[2])

#Inondation : on sort le pixel le plus bas, et chaque voisin pas encore inondé prend le niveau de gris (l'objet) de ce pixel.
#Le voisin est inséré dans L à sa place selon son altitude (bisect.insort garde la liste triée).
#Un pixel n'est inondé qu'une seule fois (test m==0) : là où deux objets se rencontrent, le premier arrivé gagne.
#Le test sur les bornes évite de sortir de l'image (un indice -1 en numpy reviendrait de l'autre côté sans erreur)
while len(L)>0:
    ligne,colonne,valeur = L.pop(0)
    for el_ligne, el_colonne in el:
        ligne_voisin = ligne+el_ligne
        colonne_voisin = colonne+el_colonne
        if 0<=ligne_voisin<g.shape[0] and 0<=colonne_voisin<g.shape[1] and m[ligne_voisin, colonne_voisin]==0:
            m[ligne_voisin, colonne_voisin] = m[ligne, colonne]
            bisect.insort(L, (ligne_voisin, colonne_voisin, g[ligne_voisin, colonne_voisin]), key = lambda elem:elem[2])



#Chaque pixel de m vaut maintenant le niveau de son objet : le gradient de m n'est non nul que sur la frontière entre les objets.
#On la colorie en rouge sur l'image de départ, passée en couleur (GRAY2BGR) pour avoir 3 canaux
g2 = morpho.mygradient(m, strel.build("carre", 1))
imcouleur = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
imcouleur[g2>0]=[0, 0, 255]

cv2.imshow("Resultat", imcouleur)
cv2.waitKey(0)