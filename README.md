# isometrique_game
# 🧟‍♂️ Isometric Survival Game

> Jeu de survie en **vue isométrique** développé avec **Pygame**.
> Évite les zombies,pour survive le plus longtemps possible !

---

* 🧍 Contrôler les déplacements d'un personnage 
* 🧟‍♂️ Éviter des zombies qui poursuivent le personnage
* 🌊 Ralentissement des déplacement dans l’eau
* ⛰️ Obstacles et reliefs
* ⏱️ Difficulté progressive (spawn dynamique des zombies)
* 🏆 Score basé sur le temps de survie

---
🎮 Contrôles
Touche	Action
ZQSD / Flèches	Déplacement
Espace	Saut
Échap	Quitter

---

## 🧠 Concept : Jeu Isométrique

Un jeu isométrique est une représentation **2D simulant la 3D** grâce à une projection inclinée.

### 🔑 Principes techniques
### 1. Projection isométrique (le cœur du système)
   
   Certains jeux utilisent des coordonnées classiques (x, y) (vue du dessus).
   Pour afficher ces coordonnées à l’écran, on applique une transformation :
   def to_iso(wx, wy, sw, sh): 
       iso_x = (wx - wy) 
       iso_y = (wx + wy) / 2 
       return iso_x, iso_y
   
   * Projection des coordonnées `(x, y)` → `(iso_x, iso_y)`
   Effet obtenu : 
       * aller à droite → mouvement diagonal
       * aller en bas → rapprochement visuel
       * aller en haut → éloignement visuel

### 2. Représentation en losange (tiles isométriques)
   Chaque case de la grille est dessinée comme un losange  car un carré en vue perspective devient un losange en projection isométrique:
       * 4 points calculés (haut, droite, bas, gauche)
       * dessin avec pygame.draw.polygon

### 3. Tri des objets pour simuler la profondeur
   En 2D, tout est dessiné à plat → pas de vraie profondeur. Alors, on trie les objets: les plus "bas" sont dessinés au-dessus des autres.

### 5. Simulation de hauteur (axe Z)

   self.z
   
   👉 Utilisation :
   
   saut du joueur
   affichage décalé verticalement
   ombre au sol
   screen.blit(img, (x, y - self.z))
   
   💡 Résultat :
   ➡️ illusion de verticalité (2.5D)

### 6. Caméra dynamique (centrée joueur)
   dx = player.rect.centerx - width // 2
   
   Puis déplacement de tous les objets :
   
   obj.x -= dx
   obj.y -= dy
   
   Ainsi, le joueur reste au centre et le monde bouge autour

---

## 🗺️ Structure du jeu

### Carte

```python
GAME_MAP = [
    "XXXXXXXXXXXXXXXX",
    ...
]
```

| Symbole | Description      |
| ------- | ---------------- |
| X       | Mur              |
| .       | Sol              |
| W       | Eau              |
| T       | Arbre / obstacle |
| P       | Joueur           |
| Z       | Spawn zombie     |

---
### 🧍 Joueur

* Mouvement vectoriel adapté à l’isométrie
* Saut avec simulation de gravité
* Suivi du joueur (vectoriel)
* Vitesse variable (en fonction des zones de la map)

---

### 🧟 IA des zombies
* Vitesse variable
* Apparition dynamique:
  spawn_timer = max(0.3, 1.5 - game_score * 0.05)
  Plus le joueur survis plus c'est difficile.
---

### 💀 Conditions de défaite
* Lorsque le joueur rencontre un zombie
```python
if dist2 < 100 and player.z < 5:
    game_alive = False


## ⚙️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/ton-username/isometric-game.git
cd isometric-game
```

---

### 2. Installer les dépendances

```bash
pip install pygame
```

---

### 3. Lancer le jeu

```bash
python main.py
```
---

## 🧩 Architecture du projet

```
.
├── main.py
├── libgame/
├── assets/
│   ├── sprites.png
│   └── textures/
├── screenshots/
└── README.md
```

---

## 🔍 Détails techniques

### 🧱 Grille

```python
TILE = 32
```

→ Le monde est basé sur une grille de tuiles.

---
