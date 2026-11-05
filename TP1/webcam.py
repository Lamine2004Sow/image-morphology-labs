import cv2
from Commun import strel, morpho


# 1. CAMERA EN DIRECT
#Affiche en temps réel le gradient morphologique (contours) de l'image de la webcam. On quitte avec la touche q.
def camera():
    #0 = première caméra de la machine
    cap = cv2.VideoCapture(0)
    #Élément structurant carré 3x3 : contours fins (1 pixel)
    el = strel.build('carre', 1)

    if not cap.isOpened():
        print("Impossible d'ouvrir la caméra")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        #Le gradient se calcule sur une image en niveaux de gris
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #Effet miroir (on inverse les colonnes) pour que l'image réagisse comme un miroir
        frame = frame[:, ::-1]

        im_grad = morpho.mygradient(frame, el)

        #255-im_grad inverse l'image : contours sombres sur fond blanc, plus lisible
        cv2.imshow("Gradient Camera", 255-im_grad)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# 2. VIDEO DEJA ENREGISTREE
#Même traitement (gradient) mais sur un fichier vidéo, lu à sa vitesse d'origine. On quitte avec la touche q.
def video(chemin):
    cap = cv2.VideoCapture(chemin)
    el = strel.build('carre', 1)

    if not cap.isOpened():
        print("Impossible d'ouvrir la vidéo")
        return

    #Délai entre deux images en millisecondes (1000 / images par seconde) pour lire à la bonne vitesse.
    #Si la vidéo ne donne pas ses fps, on prend 33 ms (environ 30 images par seconde).
    fps = cap.get(cv2.CAP_PROP_FPS)
    delai = int(1000 / fps) if fps > 0 else 33

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        im_grad = morpho.mygradient(frame, el)


        cv2.imshow("Gradient Video", im_grad)

        if cv2.waitKey(delai) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# CHOISIR LA SOURCE

# Pour utiliser la webcam :
# camera()

# Pour utiliser une vidéo :
#video("Images/kingdom.png")

