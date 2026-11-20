from Commun import morpho, strel, myutil
import numpy, cv2

def equilibre_histo(im):
    N = im.shape[0] * im.shape[1]

    Hp = cv2.calcHist([im], [0], None, [256], [0, 255])

    SomHp = [Hp[0]]
    sum = Hp[0]
    imsortie = numpy.zeros_like(im)

    for i in range(1, 256):
        sum += Hp[i]
        SomHp.append(sum)

    for l in range(0, im.shape[0]):
        for c in range(0, im.shape[1]):
            imsortie[l, c] = 255 / N * SomHp[im[l, c]]

    return imsortie
#im = cv2.imread("Images/chat.jpg")
im = cv2.imread("Images/chat.jpg")
cv2.imshow("Image", im)
sortie = numpy.zeros_like(im)
im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

#sortie[:, :, 0] = equilibre_histo(im[:, :, 0])
#sortie[:, :, 1] = equilibre_histo(im[:, :, 1])
sortie[:, :, 0] = im[:, :, 0]
sortie[:, :, 1] = im[:, :, 1]
sortie[:, :, 2] = equilibre_histo(im[:, :, 2])

sortie = cv2.cvtColor(sortie, cv2.COLOR_HSV2BGR)

#sortie = equilibre_histo(im)
#cv2.imshow("Image", im)
cv2.imshow("Sortie", sortie)
#cv2.imwrite("Images/sortie_chat.jpg", sortie)
cv2.waitKey(0)