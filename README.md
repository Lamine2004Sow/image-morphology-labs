# image-morphology-labs

TP de morphologie mathématique (INFO3) en Python avec OpenCV et numpy.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Les scripts importent le package `Commun`, il faut donc que la racine du dépôt soit dans le `PYTHONPATH` :

```bash
cd TP3
PYTHONPATH=.. python3 riz.py Images/rice.png r s
```

## Structure

| Dossier | Contenu |
|---------|---------|
| `Commun/` | Package partagé : `strel` (éléments structurants), `morpho` (érosion, dilatation, gradient, ouverture, fermeture, dilatation conditionnelle, reconstruction), `myutil.py` (seuillage) |
| `TP1/` | Découverte d'OpenCV, première érosion/dilatation codée à la main, gradient morphologique sur webcam ou vidéo |
| `TP2/` | Recherche de la direction des fibres du papier par gradient avec un élément structurant ligne orienté |
| `TP3/` | Top-hat : taille des grains de riz, extraction du texte sur fond non uniforme |
| `TP4/` | Extraction des pistes d'aéroport par fermetures directionnelles, puis nettoyage ouverture/fermeture |
| `TP5/` | Reconstruction morphologique, ouverture et fermeture conditionnelles, comptage et caractérisation des grains de riz (épaisseur, longueur, orientation, ellipsoïdalité) |
| `TP6/` | Ligne de partage des eaux : séparation forêt / bitume sur une route à partir de marqueurs, puis délimitation de pièces qui se touchent (ASF, carte de distance, h-maxima, étiquetage des marqueurs) |
| `TP7/` | Histogrammes : égalisation d'histogramme d'une image en niveaux de gris, puis d'une image couleur (canaux séparés contre HSV, en n'égalisant que V) |

## Documentation

`couteau_suisse_tp.md` est un aide-mémoire de TP1 à TP7 : pour chaque outil (érosion, ouverture, top-hat, reconstruction, mesures sur les grains, ligne de partage des eaux, h-maxima, égalisation d'histogramme...), l'idée, un schéma, le pourquoi, le code et les pièges, avec un tableau « je veux... » qui renvoie à la bonne section.

## Scripts en ligne de commande

```bash
# TP2 : angle des fibres du papier
python3 direction.py Images/papier_60.png

# TP3 : diamètre du plus gros grain de riz (r = rayon du top-hat, s = seuil)
python3 riz.py Images/rice.png r s

# TP4 : pistes d'aéroport (l = longueur ligne, s = seuil, r = rayon nettoyage)
python3 aeroport.py Images/aeroport1.png l s r sortie.png

# TP5 : cartes en couleur des grains de riz (épaisseur, longueur, orientation, ellipsoïdalité)
# Pas d'argument : lit ../TP3/Images/rice.png, ouvre des fenêtres (touche pour quitter)
# et écrit les cartes en .png dans le dossier courant
cd TP5
PYTHONPATH=.. python3 tp5_riz.py

# TP6 : ligne de partage des eaux (pas d'argument, ouvre des fenêtres)
cd TP6
PYTHONPATH=.. python3 route.py    # frontière forêt / bitume en rouge sur Images/route.png
PYTHONPATH=.. python3 pieces.py   # bords des pièces de Images/coins.jpg en rouge, puis une couleur par pièce

# TP7 : égalisation d'histogramme d'une image couleur en HSV (seul le canal V est égalisé)
# Pas d'argument : lit une image de Images/, ouvre l'image d'origine et le résultat
cd TP7
PYTHONPATH=.. python3 equilibre_histo.py
```
