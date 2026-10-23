# Webcam virtuelle OpenCV vers Teams sous Linux

Oct 23, 2026 · @Ls

Ce guide envoie l'image traitée par OpenCV (ici le gradient morphologique du TP1) dans Teams, comme une vraie webcam. Testé sur Ubuntu 24.04 avec v4l2loopback 0.12.7 et pyvirtualcam 0.15.0.

## Prérequis

- Ubuntu ou Debian (les commandes `apt` changent sur les autres distributions).
- Un venv Python avec `opencv-python` et `numpy` déjà installés.
- Le fichier `strel.py` du TP, accessible depuis le script (ici dans un dossier `Python/`).
- Teams ouvert dans un navigateur (Chrome, Chromium ou Firefox).

## Étape 1 : créer la webcam virtuelle

Installer le module noyau (une seule fois) :

```bash
sudo apt install v4l2loopback-dkms v4l2loopback-utils
```

Charger le module (à refaire après chaque redémarrage, dans un vrai terminal pour pouvoir taper le mot de passe) :

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="Virtual Cam" exclusive_caps=1
```

- `video_nr=10` crée `/dev/video10`, loin des vraies caméras (`/dev/video0` à `video3`).
- `card_label` est le nom affiché dans Teams.
- `exclusive_caps=1` est indispensable pour que Chrome et Teams voient la caméra.

Vérifier que la caméra existe et accepte des images (la ligne `Video Output` doit apparaître) :

```bash
v4l2-ctl -d /dev/video10 --info
```

## Étape 2 : installer pyvirtualcam

Dans le terminal de PyCharm, avec le venv activé :

```bash
pip install pyvirtualcam
```

## Étape 3 : le script

Le script lit la webcam, calcule le gradient morphologique, l'affiche et l'envoie vers `/dev/video10`. Si la caméra virtuelle est bloquée, il recharge le module tout seul (une fenêtre demande le mot de passe).

```python
import numpy
import cv2
import pyvirtualcam
import subprocess
from Python import strel

def myerode(im, el):
    return cv2.erode(im, el)

def mydilate(im, el):
    return cv2.dilate(im, el)

def mygradient(im, el):
    return mydilate(im, el) - myerode(im, el)

# v4l2loopback 0.12.7 bloque /dev/video10 après chaque utilisation : on recharge le module
def open_virtualcam(width, height):
    try:
        return pyvirtualcam.Camera(width=width, height=height, fps=30, device="/dev/video10")
    except RuntimeError:
        subprocess.run(["pkexec", "sh", "-c",
                        "modprobe -r v4l2loopback; modprobe v4l2loopback devices=1 video_nr=10 "
                        "card_label='Virtual Cam' exclusive_caps=1"], check=True)
        return pyvirtualcam.Camera(width=width, height=height, fps=30, device="/dev/video10")

cap = cv2.VideoCapture(0)
el = strel.build('carre', 1)

_, frame = cap.read()

with open_virtualcam(frame.shape[1], frame.shape[0]) as cam:
    while True:
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = frame[:, ::-1]

        im_grad = mygradient(frame, el)
        cv2.imshow("Gradient", numpy.uint8(im_grad))

        cam.send(cv2.cvtColor(im_grad, cv2.COLOR_GRAY2RGB))
        cam.sleep_until_next_frame()

        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
```

- La taille de la caméra virtuelle est lue sur la première image : pas besoin de connaître la résolution de sa webcam.
- `cam.send` attend une image couleur, d'où la conversion `GRAY2RGB`.
- `frame[:, ::-1]` retourne l'image comme un miroir ; à enlever si on n'en veut pas.
- Pour quitter : cliquer sur la fenêtre « Gradient » puis appuyer sur `q`.

## Étape 4 : choisir la caméra dans Teams

1. Lancer le script **avant** d'ouvrir le menu caméra de Teams.
2. Dans Teams : **Paramètres → Périphériques → Caméra**, choisir **« Virtual Cam »**.
3. Laisser le script tourner pendant toute la démo.
4. Avant d'arrêter le script, repasser sur la vraie webcam dans Teams.

Si « Virtual Cam » n'apparaît pas, recharger la page Teams.

## Dépannage

| Problème | Cause | Solution |
| --- | --- | --- |
| `Device /dev/video10 is not a video output device` | v4l2loopback 0.12.7 reste bloqué après chaque utilisation | Recharger le module (le script le fait tout seul, sinon : `sudo modprobe -r v4l2loopback` puis la commande de l'étape 1) |
| `modprobe: Module v4l2loopback is in use` | Teams ou un autre script utilise encore la caméra | Fermer l'onglet Teams ou le script, puis réessayer |
| `sudo: a terminal is required to read the password` | Commande lancée sans terminal interactif | Utiliser un vrai terminal, ou `pkexec` à la place de `sudo` |
| `mismatch between camera frame shape` | Taille envoyée différente de celle déclarée (ex. 1280×720 alors que la webcam fait 640×480) | Déclarer la taille lue sur la première image, comme dans le script |
| `ModuleNotFoundError: No module named 'pyvirtualcam'` | pyvirtualcam installé hors du venv | `pip install pyvirtualcam` dans le terminal de PyCharm |
| La fenêtre OpenCV se ferme tout de suite avec `waitKey(0)` | Touche F4 coincée dans GNOME/Wayland (code 193 reçu sans appui) | Appuyer une fois sur F4 (ou Fn+F4) |
| La touche `q` ne fait rien | La fenêtre « Gradient » n'a pas le focus | Cliquer sur l'image avant d'appuyer sur `q` |
