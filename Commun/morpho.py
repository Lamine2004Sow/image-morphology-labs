import cv2
import numpy

#Érosion : chaque pixel prend la valeur MIN des pixels couverts par l'élément structurant (el).
#Impact : les objets clairs rétrécissent et les petits détails clairs (plus petits que el) disparaissent.
#Utilité : brique de base de toutes les autres opérations (ouverture, gradient, mesure d'épaisseur...).
def myerode(im, el):
    return cv2.erode(im, el)

#Dilatation : chaque pixel prend la valeur MAX des pixels couverts par l'élément structurant (dual de l'érosion).
#Impact : les objets clairs grossissent et les petits trous sombres se bouchent.
def mydilate(im, el):
    return cv2.dilate(im, el)

#Gradient morphologique : dilatation - érosion.
#Impact : ne reste que les zones où l'image varie, c'est-à-dire les contours des objets (épaisseur liée à la taille de el).
def mygradient(im, el):
    return cv2.subtract(mydilate(im, el), myerode(im, el))

#Ouverture : érosion puis dilatation.
#Impact : supprime les objets clairs plus petits que el, les autres gardent à peu près leur taille (coins arrondis).
#Utilité : nettoyer du bruit, et sert au top hat (image - ouverture) pour retirer le fond clair.
def myopen(im, el):
    return mydilate(myerode(im, el), el)

#Fermeture : dilatation puis érosion (dual de l'ouverture).
#Impact : bouche les trous et les détails sombres plus petits que el, sans grossir les objets.
#Utilité : préserver les objets sombres (pistes d'aéroport, texte) et bottom hat (fermeture - image).
def myclose(im, el):
    return myerode(mydilate(im, el), el)

#Dilatation conditionnelle : on dilate le marqueur (mask), puis on le limite par l'image de référence (minimum).
#Impact : le marqueur grossit mais ne peut jamais dépasser ref. C'est un seul pas de la reconstruction.
def myconddilat(ref, mask, el):
    return numpy.minimum(ref, mydilate(mask, el))

#Érosion conditionnelle : dual de la dilatation conditionnelle. On érode le marqueur, puis on le garde au-dessus de ref (maximum).
def myconderod(ref, mask, el):
    return numpy.maximum(ref, myerode(mask, el))

#Reconstruction inférieure : on répète la dilatation conditionnelle jusqu'à ce que l'image ne change plus (stabilité).
#Impact : restitue en entier, avec leur forme exacte, les objets de ref que touche le marqueur mask.
#Utilité : extraire un grain/une composante connexe (el = g4 ou g8 donne la connexité), supprimer les objets collés au bord.
#(previous = ref au départ sert juste à ce que la boucle démarre : previous est différent de mask)
def myreconinf(ref, mask, el):
    previous = ref
    while not numpy.array_equal(previous, mask):
        previous = mask
        mask = myconddilat(ref, mask, el)

    return mask

#Reconstruction supérieure : même principe avec l'érosion conditionnelle, jusqu'à stabilité (dual de myreconinf).
def myreconsup(ref, mask, el):
    previous = ref
    while not numpy.array_equal(previous, mask):
        previous = mask
        mask = myconderod(ref, mask, el)

    return mask

#Ouverture par reconstruction : on ouvre avec F_op (le marqueur), puis on reconstruit avec la connexité E_recon.
#Impact : comme l'ouverture, elle supprime les petits objets, mais les objets conservés retrouvent leur forme exacte (pas de coins arrondis).
def myopenrecon(ref, F_op, E_recon):
    op = myopen(ref, F_op)
    return myreconinf(ref, op, E_recon)

#Fermeture par reconstruction : dual de l'ouverture par reconstruction. Bouche les petits trous sombres en gardant la forme exacte du reste.
def mycloserecon(ref, F_cl, E_recon):
    cl = myclose(ref, F_cl)
    return myreconsup(ref, cl, E_recon)