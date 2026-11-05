# Couteau suisse — Morphologie mathématique (TP1 → TP5)

Pour chaque outil : **l'idée en une phrase**, **un schéma**, **pourquoi ça marche**, **le code**, **les pièges**.
Les fonctions viennent du package `Commun/` (`strel.py`, `morpho.py`, `myutil.py`).
Source des définitions : le cours *Morphological Image Analysis* (J. Chaussard) et les sujets de TP.

---

## 0. Quel outil pour quel problème ? (à lire en premier)

| Je veux... | Outil | Section | Lien direct |
|---|---|---|---|
| Voir les **contours** | gradient `dilatation − érosion` | 4 | [→ Gradient](#s4) |
| Supprimer les **petits objets clairs** (bruit, grains parasites) | ouverture | 6 | [→ Ouverture](#s6) |
| Supprimer les **petits objets sombres** / boucher des trous | fermeture | 7 | [→ Fermeture](#s7) |
| Extraire des objets **clairs** sur un fond **mal éclairé** | top hat (`I − ouverture`) | 8 | [→ Top hat](#s8) |
| Extraire des objets **sombres** sur un fond mal éclairé (texte) | bottom hat (`fermeture − I`) | 8 | [→ Bottom hat](#s8) |
| Passer en noir et blanc | seuil | 9 | [→ Seuil](#s9) |
| Trouver l'**orientation** de bords rectilignes | gradient par une ligne, on cherche le minimum | 11 | [→ Gradient directionnel](#s11) |
| Garder les objets **sombres et allongés** (pistes) | fermeture par une ligne, minimum sur tous les angles | 12 | [→ Aéroport](#s12) |
| Mesurer l'**épaisseur** d'un objet | érosions successives par un disque | 13 | [→ Épaisseur](#s13) |
| Extraire **un** objet précis / **compter** les objets | reconstruction inférieure depuis un pixel | 15 | [→ Extraire et compter](#s15) |
| Nettoyer **sans déformer** les objets restants | ouverture par reconstruction | 16 | [→ Ouverture par reconstruction](#s16) |
| Supprimer les objets qui **touchent le bord** | reconstruction depuis le cadre | 17 | [→ Grains du bord](#s17) |
| Mesurer la **longueur** et l'**orientation** d'un objet | érosions par une ligne, tous les angles | 18 | [→ Longueur et orientation](#s18) |
| Afficher une mesure **en couleur** (bleu = petit, rouge = grand) | normalisation + `COLORMAP_JET` | 19 | [→ Cartes en couleur](#s19) |
| Repérer les grains **non conformes** (cassés, collés, déformés) | ellipsoïdalité : aire observée contre aire d'une ellipse | 20 | [→ Ellipsoïdalité](#s20) |

---

## 1. Les images en morphologie

### Image = tableau de nombres
- Une image en gris est une matrice 2D de valeurs entre 0 (noir) et 255 (blanc).
- Une image **binaire** n'a que deux valeurs : 0 (fond) et 255 (objet).
- Une image **couleur** = 3 matrices superposées (OpenCV : ordre **B, G, R**).

### L'image vue comme un relief (très utile pour comprendre la suite)
Zones claires = **montagnes**, zones sombres = **vallées**.

```
valeur
 255 |        ___                  Les opérations morpho "coupent" les sommets
     |       /   \      __        (ouverture), "comblent" les vallées (fermeture),
 128 |   ___/     \____/  \___     ou "gonflent / dégonflent" le relief
     |  /                      \
   0 +---------------------------> position (une ligne de l'image)
```

<a id="lire-afficher"></a>
### Lire, afficher, écrire (OpenCV)
```python
import cv2, numpy
im  = cv2.imread("Images/rice.png", cv2.IMREAD_GRAYSCALE)   # gris : une matrice 2D
imc = cv2.imread("Images/rice.png")                         # couleur : 3 canaux, ordre BGR !
cv2.imshow("titre", im)
cv2.waitKey(0)            # attend une touche — À ENLEVER dans le rendu JARVIS
cv2.imwrite("sortie.png", im)
```

### Canaux couleur (TP2)
`im[:, :, 0]` = bleu, `im[:, :, 1]` = vert, `im[:, :, 2]` = rouge. On garde le canal où l'objet ressort le mieux du fond.

<a id="piege-uint8"></a>
### Piège n°1 : les `uint8` rebouclent
`3 - 5` donne `254` sur un `uint8`, pas `-2`. Pour soustraire deux images :
- si on sait que `A >= B` (top hat, bottom hat), le `-` est sûr ;
- sinon utiliser `cv2.subtract(A, B)` (sature à 0).

---

<a id="s2"></a>
## 2. Éléments structurants (`strel`)

**Idée :** c'est la « forme sonde » qu'on promène sur l'image. Le résultat dépend entièrement de cette forme.

```
Γ4 (diamant, 4 voisins)     Γ8 (carré, 8 voisins)      Disque B(r)           Ligne (rayon n, angle α)
      0 1 0                      1 1 1                  0 1 1 1 0               . . . . . X
      1 1 1                      1 1 1                  1 1 1 1 1               . . . . X .
      0 1 0                      1 1 1                  1 1 1 1 1               . . . X . .
                                                        1 1 1 1 1               . . X . . .
 on touche par un côté       on touche par côté ou      0 1 1 1 0               . X . . . .
                             par un coin                                        (ici ~45°)
```

| Élément | Code | Quand l'utiliser |
|---|---|---|
| Γ8 (carré 3×3) | `strel.build("carre", 1)` | opérations de base, gradient, connexité 8 |
| Γ4 (diamant) | `strel.build("diamant", 1)` | petit nettoyage, connexité 4 |
| rΓ8 (grand carré) | `strel.build("carre", r)` | nettoyage plus fort |
| Disque | `strel.build("disque", r)` | **isotrope** : taille mesurée indépendamment de l'orientation |
| Ligne | `strel.build("ligne", l, angle)` | sélectionner selon une **direction** |

**Remarque :** pour `"ligne"`, le premier paramètre est le *rayon* : la ligne va de `-l` à `+l`, donc sa longueur totale vaut environ `2*l`.

### Connexité : Γ4 ou Γ8 ?
Deux pixels qui se touchent par un coin forment-ils le même objet ?
```
 . X X .        Γ8 : 1 seul objet (le coin compte)
 . X . X        Γ4 : 2 objets (il faut se toucher par un côté)
```
Pour compter / extraire des grains, on prend l'un ou l'autre (dans le TP5 on utilise Γ4 pour séparer les grains qui se touchent par un coin).

---

## 3. Érosion et dilatation (TP1)

### Érosion = minimum local
**Idée :** chaque pixel prend la **plus petite** valeur sous l'élément structurant.

```
Image (1 ligne)  :  1  2  8  8  8  2  9  2  1       élément structurant : 3 pixels [-1, 0, +1]
Érosion (min)    :  1  1  2  8  2  2  2  1  1
                          ^ le pic de 8 8 8 est devenu 8 : un seul pixel a survécu
                            (le "9" isolé disparaît : 2)
```
- **Sur une image binaire :** un pixel blanc survit seulement si l'élément structurant **rentre entièrement** dans l'objet. Les objets rétrécissent, les objets trop petits disparaissent.
- **Sur un relief :** on « rabote » les montagnes.

```
Objet blanc (binaire)            Érosion par Γ8
 . . . . . . .                    . . . . . . .
 . X X X X X .                    . . . . . . .
 . X X X X X .       ──────▶      . . X X X . .
 . X X X X X .                    . . . . . . .
 . . . . . . .                    . . . . . . .
```

### Dilatation = maximum local
**Idée :** chaque pixel prend la **plus grande** valeur sous l'élément structurant.
```
Image (1 ligne)  :  1  2  8  8  8  2  9  2  1
Dilatation (max) :  2  8  8  8  8  9  9  9  2
```
Les objets clairs grossissent, les petits trous sombres se bouchent.

### Les deux sont duales, mais pas inverses
Éroder puis dilater ne redonne **pas** l'image de départ : ce qui a disparu par l'érosion ne revient pas. C'est exactement ce qui est exploité par l'ouverture (section 6).

### Code
```python
# version "à la main" (voisinage 3x3 = Γ8) : TP1/tp1_firsterode.py
def first_erode(im):
    im_out = numpy.zeros_like(im)
    for i in range(1, im.shape[0] - 1):
        for j in range(1, im.shape[1] - 1):
            im_out[i, j] = numpy.min(im[i-1:i+2, j-1:j+2])
    return im_out

# version Commun/morpho.py (n'importe quel élément structurant, rapide)
def myerode(im, el):  return cv2.erode(im, el)
def mydilate(im, el): return cv2.dilate(im, el)
```

### Pièges
- **Le bord de l'image :** pour l'érosion, ce qui est hors de l'image compte comme **blanc** (255, « +∞ » dans le cours). Un objet coupé par le bord n'est donc pas érodé de ce côté : voir la section 13 (ajout d'un cadre noir).
- La version « à la main » laisse les bords à 0 et est très lente (boucles Python).

---

<a id="s4"></a>
## 4. Gradient morphologique (TP1)

**Idée :** dilatation − érosion = les endroits où l'image **change vite** = les **contours**.

```
Image            :  0  0  0  9  9  9  0  0  0
Dilatation (max) :  0  0  9  9  9  9  9  0  0
Érosion (min)    :  0  0  0  0  9  0  0  0  0
Gradient         :  0  0  9  9  0  9  9  0  0     ← uniquement les bords de l'objet
                              ^ à l'intérieur du plateau il vaut 0
```

```python
def mygradient(im, el):
    return cv2.subtract(mydilate(im, el), myerode(im, el))

g8 = strel.build("carre", 1)
contours = morpho.mygradient(im, g8)       # contour de 1 ou 2 pixels d'épaisseur
```
- **Plus l'élément structurant est gros, plus le contour est épais.**
- On utilise `cv2.subtract` (sature à 0) car sur des `uint8` le `-` reboucle.

### Webcam / vidéo en gradient (TP1 — `TP1/webcam.py`)
Même traitement, image par image :
```python
cap = cv2.VideoCapture(0)                 # 0 = webcam, ou chemin d'une vidéo
el = strel.build("carre", 1)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = frame[:, ::-1]                # effet miroir
    cv2.imshow("Gradient", 255 - morpho.mygradient(frame, el))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
```

---

## 5. Pourquoi tout se compose : propriétés utiles

| Propriété | Sens | Utilité |
|---|---|---|
| **Anti-extensive / extensive** | ouverture ≤ image ≤ fermeture | le top hat et le bottom hat ne donnent jamais de valeur négative |
| **Monotonie** | plus l'élément structurant est gros, plus l'ouverture coupe | on règle la taille de ce qu'on veut supprimer |
| **Dualité** | ouvrir les objets clairs = fermer le fond sombre | tout ce qui marche pour le clair marche pour le sombre en inversant |
| **Idempotence** | ouvrir 2 fois = ouvrir 1 fois | inutile de répéter une ouverture |

---

<a id="s6"></a>
## 6. Ouverture (TP3)

**Idée :** érosion **puis** dilatation. Supprime les objets clairs **plus petits que l'élément structurant**, sans rétrécir les autres.

```
Image             :  1  2  8  8  8  2  9  2  1
Érosion (min 3)   :  1  1  2  8  2  2  2  1  1      ← le "9" étroit est déjà tombé à 2
Puis dilatation   :  1  2  8  8  8  2  2  2  1      ← le groupe large 8 8 8 est restauré
                                    ^ le pic étroit "9" a disparu, le plateau large reste
```

**L'analogie du pinceau :** l'élément structurant est un pinceau. Le résultat de l'ouverture est l'ensemble des pixels qu'on peut peindre **sans toucher** les zones noires. Si le pinceau est trop gros pour passer dans une zone, elle n'est pas peinte.

```
Objet binaire                      Ouverture par un disque
 . X X X X X . . .                  . . . . . . . . .
 . X X X X X . . X                  . X X X X X . . .      le petit point isolé disparaît,
 . X X X X X X X .      ──────▶     . X X X X X . . .      le "pont" fin disparaît,
 . X X X X X . . .                  . X X X X X . . .      les coins du carré s'arrondissent
```

```python
def myopen(im, el):
    return mydilate(myerode(im, el), el)
```

**Utilité :** nettoyer du bruit, estimer le fond (section 8).
**Pièges :**
- Le résultat est plus petit ou égal à l'image (`ouverture ≤ image`).
- Les coins des objets conservés sont **arrondis** : si on veut garder la forme exacte, voir l'ouverture par reconstruction (section 16).
- Dans le cours (§3.5), OpenCV dilate sans retourner l'élément structurant : le résultat est exact seulement si l'élément est symétrique (disque, carré, diamant, ligne centrée).

---

<a id="s7"></a>
## 7. Fermeture (TP3)

**Idée :** dilatation **puis** érosion (l'ouverture du « négatif »). Supprime les objets **sombres** plus petits que l'élément structurant, bouche les trous et les coupures.

```
Image            :  8  8  1  8  8  1  1  1  8       un petit trou (1 pixel) et un grand trou (3 pixels)
Dilatation (max) :  8  8  8  8  8  8  1  8  8       le petit trou est comblé, le grand rétrécit
Puis érosion     :  8  8  8  8  8  1  1  1  8       le grand trou retrouve sa taille, le petit a disparu
```
Résultat ≥ image. Un trou plus petit que l'élément structurant est entièrement rempli, les autres retrouvent leur taille.

```python
def myclose(im, el):
    return myerode(mydilate(im, el), el)
```

**Utilité :** préserver / mettre en valeur les objets sombres (pistes d'aéroport, texte) ou combler les coupures d'un objet.

---

<a id="s8"></a>
## 8. Top hat et bottom hat (TP3)

### Le problème : un seuil global ne marche pas si l'éclairage varie
Les grains du bas de l'image ont les mêmes niveaux de gris que le fond du haut. Un seul seuil ne peut pas séparer les deux.

### La solution : soustraire le fond
1. Une **ouverture** par un gros élément (plus gros que les grains) **efface les grains** et ne garde que le fond.
2. `image − fond` = les grains seuls, sur un fond plat → un seul seuil suffit partout.

```
Profil d'une ligne (rampe d'éclairage + 2 grains) :

I           10  12  14  40  16  18  45  22  24
ouverture   10  12  14  16  16  18  22  22  22     ← fond reconstitué, les 2 pics ont disparu
I - ouv.     0   0   0  24   0   0  23   0   2     ← les 2 grains ressortent, la rampe a disparu
seuil à 10   0   0   0 255   0   0 255   0   0     ← résultat : 2 grains
```

```
 hauteur                              hauteur
   |      grain                         |
   |   ___/\___   grain                 |    /\       /\        ← grains seuls
   |  /        \_/\__                   |   /  \     /  \         (fond remis à plat)
   | /                \___              |__/    \___/    \____
   +------------------------            +------------------------
   image avec fond incliné              image − ouverture
```

### Top hat (objets clairs) et bottom hat (objets sombres)
```python
# TP3 riz : grains CLAIRS sur fond sombre → top hat
op = morpho.myopen(im, strel.build("disque", 20))
th = im - op                          # op <= im, donc pas de dépassement uint8

# TP3 texte : lettres SOMBRES sur fond clair → bottom hat
cl = morpho.myclose(im, strel.build("disque", 30))
bh = cl - im                          # cl >= im
```

**Règle de choix de la taille :** l'élément structurant doit être **plus gros que les objets à effacer** (sinon ils restent dans le « fond » et disparaissent de la différence) mais **plus petit que les variations d'éclairage**.

---

<a id="s9"></a>
## 9. Seuil (`myutil.py`)

**Idée :** passer d'une image en gris à une image binaire.
```
niveau de gris :   0 ........ s-1 | s ........ 255
résultat       :   0 (noir)       | 255 (blanc)
```
```python
def seuil(im, s):
    im_s = numpy.zeros_like(im)
    im_s[im >= s] = 255
    return im_s
```

### Seuil interactif
Pour trouver la bonne valeur à l'œil (une barre de réglage) puis la recopier en dur :
```python
s = myutil.myseuil_interactif(th)    # touche pour valider ; renvoie le seuil choisi
```

---

## 10. Nettoyer une image binaire (TP3)

**Idée :** après un seuil il reste des points isolés (bruit). Une **petite ouverture** les efface, une **petite fermeture** bouche les petits trous.

```
Après seuil                    Ouverture par Γ4                Puis fermeture par Γ4
 . X . . . . . .                . . . . . . . .                 . . . . . . . .
 . . . X X X . .                . . . X X X . .                 . . . X X X . .
 . . . X X X . .      ──▶       . . . X X X . .      ──▶        . . . X X X . .
 . . . X . X . .                . . . X X X . .                 . . . X X X . .
 . . . . . . X .                . . . . . . . .                 . . . . . . . .
 (point isolé + trou)           (points isolés disparus)        (trou bouché)
```
```python
g4 = strel.build("diamant", 1)
riz = morpho.myopen(riz, g4)
```
Si on nettoie à la fin d'un traitement (TP4) : `fermeture(ouverture(x))` avec un petit carré.

---

<a id="s11"></a>
## 11. Gradient directionnel → trouver l'orientation (TP2)

**Idée :** un gradient par une **ligne** ne voit que les variations **le long de la ligne**.

```
Feuille à lignes inclinées                Ligne d'angle différent        Ligne parallèle aux traits
 / / / / / /                               ──────────                     / / / /
/ / / / / /       gradient par       ligne coupe plein de bords       ligne reste DANS un bord
/ / / / / /                          → somme du gradient GRANDE       → somme du gradient PETITE
```
- Si la ligne est **parallèle** aux bords, elle ne traverse presque aucun bord → la somme du gradient est **minimale**.
- L'angle qui minimise `sum(gradient)` est l'orientation de la feuille.

```
somme du gradient
   |  *                                *
   |     *                          *
   |        *                    *
   |           *    *   *     *           ← creux net = bon angle
   +----------------------------------→ angle (-90 ... 90)
                    ^angle_min
```
```python
import sys
im = cv2.imread(sys.argv[1])
rouge = im[:, :, 2]                          # canal avec le meilleur contraste

s_min = None
angle_min = None
for angle in range(-90, 91, 1):
    el = strel.build("ligne", 40, angle)
    s = numpy.sum(morpho.mygradient(rouge, el))
    if s_min is None or s < s_min:
        s_min = s
        angle_min = angle
print(angle_min)
```

---

<a id="s12"></a>
## 12. Garder les objets sombres et allongés : aéroport (TP4)

**Problème :** extraire les pistes (bandes sombres longues) mais **pas** les autres objets sombres (voitures, bâtiments, petites marques).

**Idée :** fermeture par une **ligne**, pour tous les angles, puis on garde le **minimum**.

### Pourquoi une fermeture par une ligne fait le tri
Une fermeture **efface les objets sombres plus petits que l'élément structurant**, mais ici l'élément est une ligne : « plus petit » dépend de la direction.

```
Image : une piste (bande sombre ####) et une voiture (objet sombre @)

   ##########################             ligne ⟂ à la piste         ligne ∥ à la piste
   ##########################             (traverse la piste)        (reste dans la piste)
              @
                                          la piste est plus étroite   la ligne rentre dans
                                          que la ligne :              la piste : la fermeture
                                          → COMBLÉE (devient claire)  ne la comble PAS
                                                                      → piste reste SOMBRE
```
- **Voiture :** plus petite que la ligne dans **toutes** les directions → comblée **pour tous les angles** → disparaît.
- **Piste :** comblée sauf quand la ligne est dans sa direction → reste sombre **pour un angle**.

### Pourquoi le minimum sur tous les angles
Le minimum garde un pixel sombre dès qu'**un seul** angle l'a conservé sombre :
```
angle   0°    45°   90°  (pour un pixel de la piste horizontale)
fermeture 200   200    40
minimum   = 40   ← la piste reste sombre dans l'accumulateur
```
Pour un pixel de la voiture, la fermeture est claire pour **tous** les angles → le minimum reste clair.

```python
accumulateur = numpy.zeros_like(im) + 255          # image blanche de départ

for angle in range(0, 180):
    el = strel.build("ligne", l, angle)            # l = taille de la ligne (argument)
    fe = morpho.myclose(im, el)
    accumulateur = numpy.minimum(accumulateur, fe)

pistes = myutil.seuil(accumulateur, s)             # s = seuil (argument)
```
- **Choix de `l` :** plus grand que la largeur de la piste, mais pas plus long que la piste elle-même.
- **Seuil :** les pistes sont **sombres** dans l'accumulateur, le reste clair.

### Cas de `aeroport3.png` : image couleur → HSV
L'image est en couleur et la piste ne ressort pas en gris simple. On passe dans l'espace **HSV** (Teinte, Saturation, Valeur) et on prend `max(S, V)` :
```python
hsv = cv2.cvtColor(cv2.imread(nom), cv2.COLOR_BGR2HSV)
im = numpy.maximum(hsv[:, :, 1], hsv[:, :, 2])
```

### Nettoyer et surligner en rouge
```python
el = strel.build("carre", r)
pistes = morpho.myclose(morpho.myopen(pistes, el), el)     # petite ouverture puis fermeture

g = morpho.mygradient(pistes, strel.build("carre", 1))     # contour des pistes (Γ8)
imcolor = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
imcolor[g > 0] = [0, 0, 255]                               # BGR : rouge
cv2.imwrite(sortie, imcolor)
```
(Le gradient d'une image binaire donne exactement le contour des objets.)

---

<a id="s13"></a>
## 13. Mesurer l'épaisseur par érosions successives (TP3 — riz)

**Idée :** l'épaisseur d'un objet est le diamètre du **plus grand disque qui rentre dedans**.

```
Grain (vue de dessus)                 Érosion par disques de plus en plus gros

 . . X X X X X X . .                  rayon 1       rayon 3       rayon 5
 . X X X X X X X X .                  . . . . . .   . . . . . .   . . . . . .
 . X X X X X X X X .       ──▶        . X X X X .   . . . . . .   . . . . . .
 . . X X X X X X . .                  . X X X X .   . . X X . .   . . . . . .
                                      (reste un       (très petit  VIDE !
                                       grain)          reste)      → on s'arrête
```
- **On augmente le rayon** jusqu'à ce que l'image soit vide.
- Le **dernier rayon non vide** est le rayon du plus grand disque inscrit → épaisseur = `2 × rayon`.

### Pourquoi un disque ?
Un disque est **isotrope** : sa taille ne dépend pas de la direction. Un grain penché ou horizontal donne la même épaisseur.

### Pourquoi l'érosion et pas l'ouverture ?
L'ouverture s'annule exactement au même rayon (dilater du vide donne du vide), mais coûte une dilatation en plus à chaque tour pour rien.

### Pourquoi un bord noir ?
Pour l'érosion, ce qui est hors de l'image compte comme **blanc**. Sans bord noir, un grain coupé par le bord n'est pas érodé de ce côté et paraît plus épais (13 au lieu de 9 sur `rice.png`).

```
Sans bord :   |████████        Le bord de l'image est "vu" comme blanc
Avec bord :   0|████████       On ajoute un pixel noir, l'érosion érode bien de ce côté
```

```python
riz = cv2.copyMakeBorder(riz, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)

ero = riz
rayon = 2.0
while numpy.sum(ero) > 0:
    rayon = rayon + 0.1
    ero = morpho.myerode(riz, strel.build("disque", rayon))

print(round(2*(rayon-0.1), 1))
```
- `rayon - 0.1` : quand la boucle s'arrête, le rayon courant donne **déjà** une image vide ; on revient au dernier rayon non vide.
- `round(..., 1)` : `0.1` n'est pas exact en binaire, sans arrondi on afficherait `8.999999999999996`.

---

## 14. Reconstruction morphologique : les briques (TP5)

### Dilatation conditionnelle
**Idée :** on dilate un **marqueur** M, mais il n'a pas le droit de dépasser l'image de **référence** R.
```
M ⊕_R E = (M ⊕ E) ∧ R          (∧ = minimum pixel à pixel)
```
```python
def myconddilat(ref, mask, el):
    return numpy.minimum(ref, mydilate(mask, el))
```

### Reconstruction inférieure = on répète jusqu'à stabilité
```python
def myreconinf(ref, mask, el):
    previous = ref                      # juste pour que la boucle démarre
    while not numpy.array_equal(previous, mask):
        previous = mask
        mask = myconddilat(ref, mask, el)
    return mask
```

```
R (référence)  :  1 1 1 1 1 0 1 1        deux objets : [0..4] et [6..7]
M (marqueur)   :  0 0 1 0 0 0 0 0        un seul pixel, dans le premier objet

étape 1 : dilater M      0 1 1 1 0 0 0 0   puis ∧ R  →  0 1 1 1 0 0 0 0
étape 2 : dilater        1 1 1 1 1 0 0 0   puis ∧ R  →  1 1 1 1 1 0 0 0
étape 3 : dilater        1 1 1 1 1 1 0 0   puis ∧ R  →  1 1 1 1 1 0 0 0   (le 0 de R bloque)
          stable → fini

Résultat : 1 1 1 1 1 0 0 0   ← tout le premier objet, rien du second
```

### Ce que ça veut dire
**La reconstruction inférieure de R depuis M donne toutes les composantes connexes de R qui contiennent au moins un pixel de M** (propriété 4.2 du cours).
- L'élément structurant décide de la connexité : `g4` ou `g8`.
- La forme **exacte** de l'objet est restituée (R sert de « moule »).

### Reconstruction supérieure
Le même principe, mais avec l'érosion conditionnelle (`numpy.maximum`) : elle agit sur les zones **sombres**.
```python
def myconderod(ref, mask, el):  return numpy.maximum(ref, myerode(mask, el))
def myreconsup(ref, mask, el):   # même boucle que myreconinf avec myconderod
    ...
```

---

<a id="s15"></a>
## 15. Extraire un grain et compter les grains (TP5)

**Idée :** on pose **un pixel** dans un grain, on reconstruit : on obtient **tout le grain**. On le retire de l'image, on recommence : le nombre de tours = le nombre de grains.

```
Image I (3 grains)          Marqueur M (1 pixel)       Reconstruction             I - grain
 X X . . X X . . .           . . . . . . . . .          X X . . . . . . .          . . . . X X . . .
 X X . . X X . X X           . . . . . . . . .          X X . . . . . . .          . . . . X X . X X
 . . . . . . . X X           . . . . . . . . .          . . . . . . . . .          . . . . . . . X X
 (grain A, B, C)             (pixel dans A)             (grain A entier)           (A retiré)
```
```python
m = numpy.zeros_like(r3)               # le marqueur, toujours vide au départ
im = r3.copy()
cpt = 0
for x in range(im.shape[0]):
    for y in range(im.shape[1]):
        if im[x, y] > 0:               # premier pixel d'un grain pas encore traité
            m[x, y] = 255              # on le met dans le marqueur
            grain = morpho.myreconinf(im, m, g4)   # tout le grain (connexité 4)
            im = im - grain            # on le retire pour ne pas le recompter
            cpt += 1
            # ... ici on peut mesurer ce grain (épaisseur, longueur, orientation)
```
- `g4` (connexité 4) évite de coller deux grains qui se touchent juste par un coin.
- Limite : deux grains **qui se touchent** par un côté forment une seule composante (un « grain » à 56 de long au lieu de 28).

---

<a id="s16"></a>
## 16. Ouverture par reconstruction (TP5)

**Idée :** l'ouverture simple nettoie le bruit mais **déforme** les objets restants (coins arrondis). On ouvre pour **trouver quels objets garder**, puis on les **reconstruit en entier**.

```
Image I                   Ouverture simple          Ouverture par reconstruction
 X X X X X X . .           . X X X X . . .           X X X X X X . .
 X X X X X X . X           . X X X X . . .           X X X X X X . .       ← forme intacte
 X X X X X X . .           . X X X X . . .           X X X X X X . .
 (rectangle + point)       (coins arrondis,          (point supprimé,
                            point supprimé)           rectangle identique à l'original)
```
```python
def myopenrecon(ref, F_op, E_recon):
    op = myopen(ref, F_op)               # étape 1 : le marqueur = ce qui survit à l'ouverture
    return myreconinf(ref, op, E_recon)  # étape 2 : on reconstruit les objets entiers
```
- `F_op` : la taille de ce qu'on veut supprimer (le marqueur).
- `E_recon` : la connexité (Γ8 ou Γ4).
- **Pourquoi ça marche** (cours §4.2.3) : le résultat a l'**aspect** de l'image de départ et seulement les **montagnes** du marqueur. Le cours conseille de toujours préférer l'ouverture par reconstruction, sauf si on ne se soucie pas de la forme.

La **fermeture par reconstruction** est le dual : `myreconsup(ref, myclose(ref, F), E)`.

---

<a id="s17"></a>
## 17. Supprimer les grains qui touchent le bord (TP5)

**Idée :** on construit un marqueur avec les pixels des grains qui sont **sur le cadre de l'image**, on reconstruit : on obtient exactement les grains qui touchent le bord, qu'on soustrait.

```
Image binaire r3                 Cadre ∧ r3 (marqueur)       Reconstruction               r3 - t
 X . . X X . . .                 X . . X X . . .             X . . X X . . .             . . . . . . . .
 . . X X . . . .                 . . . . . . . .             . . . . . . . .             . . X X . . . .
 . . X X . . X X     ──▶         . . . . . . . X    ──▶      . . . . . . X X    ──▶     . . X X . . . .
 . . . . . . X X                 . . . . . . . X             . . . . . . X X             . . . . . . . .
 (4 grains, 2 sur le bord)       (pixels du cadre dans un    (les 2 grains du bord       (il reste le grain
                                  grain)                      en entier)                  du milieu)
```
```python
cadre = numpy.zeros_like(r3)
cadre[:, 0]  = 255
cadre[:, -1] = 255
cadre[0, :]  = 255
cadre[-1, :] = 255
cadre[r3 == 0] = 0                       # on ne garde du cadre que ce qui est dans un grain

t = morpho.myreconinf(r3, cadre, g8)     # tous les grains qui touchent le bord
r3 = r3 - t                              # on les enlève
```
**Utilité :** un grain coupé par le bord fausserait les mesures de longueur et d'épaisseur.

---

<a id="s18"></a>
## 18. Mesurer longueur et orientation par érosion avec une ligne (TP5)

**Idée :** comme pour l'épaisseur, mais avec une **ligne** qu'on fait **tourner**. La longueur d'un grain est la longueur de la plus longue ligne qui rentre dedans, dans la meilleure direction.

```
Grain penché                         Ligne à 0°       Ligne à 45°       Ligne à 120° (≈ axe du grain)
    ____                              ─────           ╱                  ╲ ____
   /    \____                         ne rentre       rentre un peu      la ligne longue rentre !
  /          \                         pas loin        loin               → le grain survit longtemps
  \____       \
       \______/

Pour chaque angle, on agrandit la ligne jusqu'à ce que le grain disparaisse.
longueur = le plus grand rayon obtenu sur tous les angles    orientation = l'angle correspondant
```

```python
def mesurer_longueur(grain):
    x2, y2 = numpy.nonzero(grain)
    grain = grain[max(x2.min()-1, 0): min(x2.max()+2, grain.shape[0]),
                  max(y2.min()-1, 0): min(y2.max()+2, grain.shape[1])]   # recadrage (marge de 1)

    rayonmax = 0.0
    anglemax = 0
    rayon = 1.0
    for angle in range(0, 180):             # un demi-tour suffit (une ligne est symétrique)
        op1 = grain
        while numpy.sum(op1) > 0:
            rayon = rayon + 1.0
            el = strel.build("ligne", rayon, angle)
            op1 = morpho.myerode(grain, el)
        rayon = rayon - 1.0                 # dernier rayon pour lequel le grain survivait
        if rayon > rayonmax:
            rayonmax = rayon
            anglemax = angle
    return (2*rayonmax, anglemax)           # (longueur en pixels, orientation en degrés)
```

### Les astuces du code
- **Recadrage** : on découpe autour du grain (marge de 1 pixel) pour que les érosions soient rapides.
  La borne de fin d'un slice est **exclue** : on met `grain.shape[0]` et non `shape[0]-1`, sinon on coupe la dernière ligne.
- **`rayon` n'est pas remis à 1 à chaque angle** : on repart du meilleur rayon déjà atteint. Un angle qui ne peut pas battre `rayonmax` ne coûte qu'**une seule érosion** (le test à `rayon+1` est déjà vide). Résultat identique, beaucoup plus rapide.
- **`rayon - 1.0`** : on retire le pas où l'érosion était déjà vide.
- **Longueur** = `2 × rayon` car la ligne va de `-rayon` à `+rayon`.

### Disque ou ligne ?
| | Disque | Ligne |
|---|---|---|
| Mesure | **épaisseur** (la plus petite dimension) | **longueur** (la plus grande dimension) |
| Dépend de l'angle ? | non | oui : on teste tous les angles |

---

<a id="s19"></a>
## 19. Cartes en couleur : épaisseur, longueur, orientation (TP5)

**Idée :** une image où chaque pixel d'un grain contient la **mesure de ce grain**, convertie en couleur (bleu = petit, rouge = grand).

```
Étape 1 : image flottante (float64)        Étape 2 : normalisation          Étape 3 : colormap JET
 0   0   0   0   0                          (v - mini) / (maxi - mini) * 255   0 ................ 255
 0  26  26   0  28                                                             bleu  cyan  vert  jaune  rouge
 0  26  26   0  28
 0   0   0   0  28                          mini = plus petite valeur d'un GRAIN (pas le fond !)
 (chaque grain = sa mesure)                 maxi = plus grande valeur
```

```python
carte = numpy.zeros(im.shape, numpy.float64)         # pas d'affichage direct possible (float)
# dans la boucle de comptage :  carte[grain > 0] = valeur_du_grain

maxi = numpy.max(carte)
mini = numpy.min(carte[carte > 0])                    # surtout pas la valeur min de l'image (c'est le fond = 0)
carte = numpy.uint8((carte - mini) / (maxi - mini) * 255)   # entiers entre 0 et 255
carte = cv2.applyColorMap(carte, cv2.COLORMAP_JET)    # image couleur
carte[r3 == 0] = imcolor[r3 == 0]                     # fond : on remet l'image d'origine (ou 0 pour du noir)
```

### Cas de l'orientation : min et max fixés
On connaît déjà les valeurs possibles (angles testés de 0 à 179), donc pas besoin de les chercher :
```python
mini_o = 0
maxi_o = 179
carte_orientation = numpy.uint8((carte_orientation - mini_o) / (maxi_o - mini_o) * 255)
```
**Attention :** 0° et 179° sont presque la même direction, mais avec `COLORMAP_JET` elles auraient des couleurs opposées (bleu et rouge). Dans `tp5_riz.py`, on utilise donc la colormap cyclique `cv2.COLORMAP_HSV` pour l'orientation : la couleur de 179° rejoint celle de 0°.

### Pièges
- Si **toutes** les cartes sont à 0 (mesure non faite), `numpy.min(carte[carte>0])` plante : « zero-size array ».
- Les images flottantes ne s'affichent pas avec `imshow` : on convertit d'abord en `uint8`.

---

<a id="s20"></a>
## 20. Repérer les grains non conformes : l'ellipsoïdalité (TP5)

**Idée :** un bon grain de riz ressemble à une **ellipse**. On compare l'**aire réelle** du grain à l'**aire qu'aurait une ellipse** de même longueur et de même épaisseur. Si les deux s'accordent, le grain est conforme ; sinon, il est cassé, collé à un autre ou déformé.

```
Les deux mesures que l'on a déjà             Ellipse de même longueur L et même épaisseur W

        longueur L = 2a                              ___________
   ┌──────────────────────┐                       ,-'           '-.      W = 2b  (épaisseur)
   │   grain de riz       │ épaisseur W = 2b     (                 )
   └──────────────────────┘                       '-.___________.-'
                                                     aire = π · a · b = π · (L/2) · (W/2)

Cas typiques :                          aire observée                aire d'une ellipse L×W
  grain normal                          ≈ celle de l'ellipse         → rapport proche de la valeur typique
  grain CASSÉ (court, petit)            trop petite                  → rapport faible
  DEUX GRAINS collés (long, gros)       trop grande (≈ le double)    → rapport élevé
```

### Pourquoi nos deux mesures correspondent aux axes de l'ellipse
| Ellipse | Notre mesure |
|---|---|
| grand axe `2a` | **longueur** : la plus longue ligne qui rentre dans le grain (section 18) |
| petit axe `2b` | **épaisseur** : le plus grand disque qui rentre dans le grain (section 13) |

Pour une vraie ellipse, la plus longue ligne qui rentre est bien le grand axe, et le plus grand disque inscrit a bien pour diamètre le petit axe.

### Le calcul
```
aire_theorique = π × (ep/2) × (long/2)          ep et long sont des DIAMÈTRES (2×rayon) → on divise par 2
aire_observee  = nombre de pixels du grain       (somme des pixels / 255, car un pixel de grain vaut 255)
coefficient    = aire_observee / aire_theorique
ellipsoidalite = log(coefficient)²
```
- **Pourquoi le logarithme ?** Il rend les écarts symétriques : un grain deux fois trop grand (rapport 2) et un grain deux fois trop petit (rapport 1/2) sont aussi « anormaux » l'un que l'autre, et ont `log(2)` et `log(1/2) = −log(2)`.
- **Pourquoi le carré ?** Il supprime le signe : seul compte **l'écart**, qu'il soit trop grand ou trop petit. Résultat toujours ≥ 0, plus il est grand, plus le grain s'éloigne d'une ellipse.

```python
import math

aire_theorique = ep/2 * long/2 * math.pi
aire_observee = numpy.sum(grain)/255
ellipsoidalite = math.log(aire_observee/aire_theorique)**2

carte_ellipsoidalite[grain>0] = ellipsoidalite        # puis normalisation + COLORMAP_JET (section 19)
```
Dans la carte, les grains **bleus** sont proches d'une ellipse (valeur proche de 0) et les **rouges** s'en éloignent le plus.

### Ce qu'on observe sur `rice.png` (70 grains)
- Un grain normal n'a **pas** un rapport de 1 : la médiane du rapport `aire_observee / aire_theorique` est d'environ **1,26**. Les extrémités d'un grain sont plus carrées que celles d'une ellipse, donc l'aire réelle dépasse celle de l'ellipse (cause non vérifiée en détail).
- L'amas de **deux grains collés** ressort à environ **1,57** (longueur 42, aire 404) : c'est la tache rouge foncé de la carte.
- Conséquence : pour décider qu'un grain est anormal, on se compare à la **valeur typique** (médiane), pas à 1. Un seuil vers 1,45 à 1,5 isole l'amas sans toucher aux autres.

### Lien avec le critère R du sujet
Le sujet demande `R = (1 − l_mesurée / l_estimée)²`, où `l_estimée` est la longueur déduite de l'aire en supposant une ellipse. En inversant `aire = π·L·W/4` on obtient `l_estimée = 4·aire / (π·W)`, donc :
```
l_mesurée / l_estimée = π·L·W / (4·aire) = 1 / coefficient       →   R = (1 − 1/coefficient)²
```
C'est le même principe que `log(coefficient)²` : un écart au carré autour d'une valeur de référence. (Cette formule de `l_estimée` est déduite de la géométrie de l'ellipse, pas lue dans le sujet : à vérifier avec le cours.)

### Pièges
- `math.log` plante si `aire_observee` vaut 0 (grain vide) : ne peut pas arriver pour un grain reconstruit, il contient au moins un pixel.
- Ne pas comparer à 1 : la valeur « normale » est celle de la majorité des grains (≈ 1,26 ici).
- Un grain **cassé** reste elliptique : il peut passer inaperçu avec ce critère seul. Le compléter avec la longueur ou l'aire.
- L'orientation de l'ellipse ne dit rien sur la conformité : elle ne sert pas ici.

---

<a id="s21"></a>
## 21. Rendu JARVIS / Moodle

### Règles générales (valables pour tous les TP)
- **Arguments en ligne de commande** (JARVIS lance `python3 prog.py ...`) :
```python
import sys
nom = sys.argv[1]
r = int(sys.argv[2])
s = int(sys.argv[3])
```
- **Pas de `imshow` / `waitKey`** dans le rendu : le programme attendrait une touche indéfiniment.
- **Afficher uniquement ce qui est demandé** (pas de texte en plus).
- Zip `Nom_Prenom_NumeroEtudiant.zip` (pas d'accents ni de ponctuation), avec à la racine le fichier principal + le dossier `Commun/` (`__init__.py`, `morpho.py`, `strel.py`, `myutil.py`). Ni images, ni `venv`, ni `__pycache__`.
- Adresse JARVIS : `chaussard.laga+image_tpN@gmail.com` (N = numéro du TP).

> ⚠️ Les sujets (TP4) parlent de **`myutils.py`** alors que notre fichier s'appelle `myutil.py`. Les imports `from Commun import myutil` doivent correspondre au nom **réel** du fichier dans le zip. À vérifier avant l'envoi.

### Appels demandés par les sujets
| TP | Fichier | Appel |
|---|---|---|
| TP3 | `riz.py` | `python3 riz.py image.png r s` → affiche l'épaisseur |
| TP4 | `aeroport.py` | `python3 aeroport.py input.png l s r output.png` |
| TP5 | `riz.py` | `python3 riz.py entree.png sortie1.png sortie2.png sortie3.png r s` |

### Sorties demandées au TP5 : niveaux de gris imposés
| Image | Contenu | Valeur min → niveau de gris | Valeur max → niveau de gris |
|---|---|---|---|
| `sortie1.png` | épaisseur des grains | grain le plus étroit → **50** | grain le plus épais → **255** |
| `sortie2.png` | longueur des grains | grain le plus court → **20** | grain le plus long → **255** |
| `sortie3.png` | critère R | R = 0 → **30** | R ≥ 0.15 → **200** |

Le fond reste à **0** partout. C'est une normalisation **affine** vers `[bas, haut]` (et non vers 0-255) :
```python
gris = bas + (valeur - mini) / (maxi - mini) * (haut - bas)
```
Le critère `R = (1 − l_mesurée / l_estimée)²` compare la longueur mesurée par la ligne (section 18) à celle de l'approximation par une ellipse : un grain dont la forme s'éloigne d'une ellipse a un `R` grand. Détail du calcul en section 20.

---

## 22. Pièges à retenir (liste de contrôle)

Chaque ligne renvoie vers la solution (clique sur le lien).

- [ ] `uint8` : `-` reboucle, `cv2.subtract` sature à 0. → [solution : `cv2.subtract` et cas où on peut soustraire directement](#piege-uint8)
- [ ] Bord de l'image : ajouter un cadre noir avant de mesurer par érosion. → [solution : `copyMakeBorder`](#s13)
- [ ] Les images flottantes ne s'affichent pas : convertir en `uint8`. → [solution : normalisation de la carte](#s19)
- [ ] OpenCV charge en **BGR**, pas RGB. → [solution : ordre des canaux](#lire-afficher)
- [ ] `cv2.waitKey(0)` et `imshow` : à enlever pour JARVIS. → [solution : règles du rendu](#s21)
- [ ] Lire les arguments avec `sys.argv`, afficher uniquement ce qui est demandé. → [solution : arguments et affichage](#s21)
- [ ] Taille de l'élément structurant : plus grand que les objets à supprimer / mesurer. → [solution : règle de choix de la taille](#s8) et [choix de l'élément](#s2)
- [ ] Deux grains qui se touchent sont comptés comme un seul (ils ressortent avec une ellipsoïdalité élevée). → [solution : repérer ces grains](#s20) et [limite du comptage](#s15)
- [ ] Ellipsoïdalité : comparer à la valeur typique des grains, pas à 1 ; `ep` et `long` sont des diamètres, diviser par 2. → [solution : le calcul pas à pas](#s20)
- [ ] Nom du zip et fichier principal exactement comme demandé. → [solution : nom du zip et appels demandés](#s21)
