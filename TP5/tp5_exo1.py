import cv2, numpy
from Commun import strel, morpho, myutils

ref = cv2.imread("../TP1/Images/dog.png", cv2.IMREAD_GRAYSCALE)
mask = cv2.imread("Images/mask_inf.png", cv2.IMREAD_GRAYSCALE)

el =  strel.build("disque", 5)

resultat = morpho.myreconinf(ref, mask, el)

solution = cv2.imread("Images/result_reconinf.png", cv2.IMREAD_GRAYSCALE)

print(numpy.array_equal(solution, resultat))