# Isometric Survival Game

Jeu de survie en vue isométrique développé en Python avec Pygame.
Dirigez votre personnage, évitez les zombies et tenez le plus longtemps possible.

## Fonctionnalités

- Déplacement d'un personnage en projection isométrique
- IA de zombies qui poursuivent le joueur
- Ralentissement dans les zones d'eau
- Obstacles, reliefs et simulation de hauteur (saut, gravité)
- Difficulté progressive (spawn dynamique des zombies)
- Score basé sur le temps de survie

## Contrôles

| Touche           | Action        |
| ---------------- | ------------- |
| `Z Q S D` / Flèches | Déplacement   |
| `Espace`         | Saut          |
| `Échap`          | Quitter       |

## Installation

### Prérequis

- Python 3.10+
- Pygame

### Étapes

```bash
git clone https://github.com/<user>/isometrique_game.git
cd isometrique_game
pip install pygame
python game_zombie.py
```

## Structure du projet

```
.
├── game_zombie.py    # Point d'entrée du jeu (boucle principale, logique)
├── libgame.py        # Moteur maison (Element, rendu, helpers)
├── assets/           # Sprites, textures, sons
└── README.md
```

## Concept technique : rendu isométrique

Un jeu isométrique simule la 3D à l'aide d'une **projection 2D inclinée**.
Les coordonnées monde `(x, y)` sont converties en coordonnées écran `(iso_x, iso_y)` :

```python
def to_iso(wx, wy, sw, sh):
    iso_x = (wx - wy) + sh / 2
    iso_y = (wx + wy) / 2 + (sh - sw) / 4
    return iso_x, iso_y
```

Effets obtenus :
- Se déplacer à droite → mouvement diagonal à l'écran
- Se déplacer vers le bas → rapprochement visuel
- Se déplacer vers le haut → éloignement visuel

### Tuiles en losange

Chaque case de la grille est dessinée comme un losange (un carré vu en perspective).
Les 4 coins sont calculés puis tracés avec `pygame.draw.polygon`.

### Tri par profondeur

Le rendu 2D étant « à plat », les objets sont triés avant affichage : les plus « bas »
à l'écran sont dessinés en dernier pour simuler la profondeur.

### Axe Z (hauteur)

La coordonnée `self.z` permet de simuler la verticalité (2.5D) :

```python
screen.blit(img, (x, y - self.z))
```

Utilisée pour le saut, le décalage des sprites et les ombres au sol.

### Caméra centrée joueur

Le joueur reste au centre de l'écran ; c'est le monde qui défile :

```python
dx = player.rect.centerx - width // 2
obj.x -= dx
obj.y -= dy
```

## Carte du jeu

Le monde est une grille de tuiles de `TILE = 32` pixels :

```python
GAME_MAP = [
    "XXXXXXXXXXXXXXXX",
    "X..............X",
    "X..T.........Z.X",
    ...
]
```

| Symbole | Description       |
| ------- | ----------------- |
| `X`     | Mur               |
| `.`     | Sol               |
| `W`     | Eau               |
| `T`     | Arbre / obstacle  |
| `P`     | Joueur            |
| `Z`     | Spawn zombie      |

## Mécaniques de jeu

### Joueur

- Mouvement vectoriel adapté à la projection isométrique
- Saut avec simulation de gravité
- Vitesse variable selon la nature du sol (ralentissement dans l'eau)

### Zombies

- Poursuite du joueur (mouvement vectoriel)
- Vitesse variable
- Apparition dynamique : plus le score augmente, plus les spawns sont rapides

```python
spawn_timer = max(0.3, 1.5 - game_score * 0.05)
```

### Condition de défaite

La partie s'arrête dès qu'un zombie atteint le joueur au sol :

```python
if dist2 < 100 and player.z < 5:
    game_alive = False
```
