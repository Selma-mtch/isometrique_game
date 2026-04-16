# isometrique_game
# 🧟‍♂️ Isometric Survival Game

> Jeu de survie en **vue isométrique** développé avec **Pygame**.
> Évite les zombies,pour survive le plus longtemps possible !

---

## 🎮 Gameplay

* 🧍 Contrôler les déplacements d'un personnage 
* 🧟‍♂️ Éviter des zombies qui poursuivent le personnage
* 🌊 Ralentissement des déplacement dans l’eau
* ⛰️ Obstacles et reliefs
* ⏱️ Difficulté progressive (spawn dynamique des zombies)
* 🏆 Score basé sur le temps de survie

---

## 🧠 Concept : Jeu Isométrique

Un jeu isométrique est une représentation **2D simulant la 3D** grâce à une projection inclinée.

### 🔑 Principes techniques

* Projection des coordonnées `(x, y)` → `(iso_x, iso_y)`
* Tuiles en forme de losange
* Tri des objets pour simuler la profondeur

Les objets les plus "bas" sont dessinés au-dessus des autres.

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

## 🎮 Contrôles

| Touche          | Action      |
| --------------- | ----------- |
| ⬆️⬇️⬅️➡️ / ZQSD | Déplacement |
| Espace          | Saut        |
| Échap           | Quitter     |

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

### 🧍 Joueur

* Mouvement vectoriel adapté à l’isométrie
* Saut avec simulation de gravité
* Suivi du joueur (vectoriel)
* Vitesse variable (en fonction des zones de la map)

---

### 🧟 IA des zombies
* Vitesse variable
* Apparition dynamique 
---

### 💀 Conditions de défaite
* Lorsque le joueur rencontre un zombie
```python
if dist2 < 100 and player.z < 5:
    game_alive = False
