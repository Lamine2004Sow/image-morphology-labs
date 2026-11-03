import cv2
from Commun import strel, morpho


# 1. CAMERA EN DIRECT
def camera():
    cap = cv2.VideoCapture(0)
    el = strel.build('carre', 1)

    if not cap.isOpened():
        print("Impossible d'ouvrir la caméra")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = frame[:, ::-1]

        im_grad = morpho.mygradient(frame, el)

        cv2.imshow("Gradient Camera", 255-im_grad)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# 2. VIDEO DEJA ENREGISTREE
def video(chemin):
    cap = cv2.VideoCapture(chemin)
    el = strel.build('carre', 1)

    if not cap.isOpened():
        print("Impossible d'ouvrir la vidéo")
        return

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

