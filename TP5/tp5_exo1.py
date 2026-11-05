import cv2, numpy
from Commun import strel, morpho, myutil

#Test de la reconstruction morphologique (myreconinf et myopenrecon de Commun/morpho.py)
#ref = image de référence (le chien), mask = marqueur fourni par le prof
ref = cv2.imread("../TP1/Images/dog.png", cv2.IMREAD_GRAYSCALE)
mask = cv2.imread("Images/mask_inf.png", cv2.IMREAD_GRAYSCALE)

el =  strel.build("disque", 5)

#Reconstruction du marqueur dans ref
resultat = morpho.myreconinf(ref, mask, el)

#Vérification : on compare avec le résultat du prof, doit afficher True si notre fonction est correcte
solution = cv2.imread("Images/result_reconinf.png", cv2.IMREAD_GRAYSCALE)

print(numpy.array_equal(solution, resultat))


#Ouverture par reconstruction : on ouvre avec un carré (marqueur), puis on reconstruit avec la connexité 8 (g8).
#Comparée à l'ouverture simple, les objets conservés gardent leur forme exacte au lieu d'être arrondis.
el = strel.build("carre", 2)
g8 = strel.build("carre", 1)
result = morpho.myopenrecon(ref, el, g8)
cv2.imshow("Chien", ref)
cv2.imshow("Ouverture", morpho.myopen(ref, el))
cv2.imshow("Ouverture Reconstruction", result)
cv2.waitKey(0)
