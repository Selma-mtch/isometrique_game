import libgame
import pygame
from typing import List

TILE = 32
GAME_MAP = [
    "XXXXXXXXXXXXXXXX",
    "X..............X",
    "X..T...........X",
    "X..............X",
    "X.....XX.......X",
    "X.....XX.......X",
    "X.....T........X",
    "X.T..WWW.......X",
    "X....WWWW......X",
    "X.....WW.......X",
    "X..............X",
    "X.....XX..T....X",
    "X..T...XX......X",
    "X..............X",
    "X....T....T....X",
    "X..............X",
    "X..P...........X",
    "X..............X",
    "X..............X",
    "XXXXXXXXXXXXXXXX",
]
MAP_COLS = len(GAME_MAP[0])
MAP_ROWS = len(GAME_MAP)

player = None


class Player(libgame.Walker2D):

    def do_event(self, event):
        return True

    def do_accelerate(self, etime):
        self.oldx = self.x
        self.oldy = self.y
        keys = pygame.key.get_pressed()
        speed = 80
        self.vx = 0
        self.vy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy += speed
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.707
            self.vy *= 0.707
        self.dontadjust = True


def game_init(scene: libgame.Scene) -> List[libgame.Element]:
    global player
    objects: List[libgame.Element] = []

    grass = libgame.Ground((80, 150, 60), 0, 0, MAP_COLS * TILE, MAP_ROWS * TILE)
    grass.depth = 1
    objects.append(grass)

    player = None

    for row_i, row in enumerate(GAME_MAP):
        for col_i, ch in enumerate(row):
            wx = col_i * TILE
            wy = row_i * TILE
            if ch == "X":
                objects.append(libgame.Ground((80, 70, 65), wx, wy, TILE, TILE))
            elif ch == "W":
                objects.append(libgame.Ground((40, 100, 190), wx, wy, TILE, TILE))
            elif ch == "T":
                objects.append(libgame.Ground((30, 110, 40), wx, wy, TILE, TILE))
            elif ch == "P":
                player = Player(wx + TILE // 2, wy + TILE // 2)

    objects.append(player)
    return objects


def game_controller(objects: List[libgame.Element], event: pygame.event.Event) -> bool:
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return False
    return True


def game_prepaint(scene: libgame.Scene) -> bool:
    width, height = scene.window_size
    dx = player.rect.centerx - width // 2
    dy = player.rect.centery - height // 2
    if abs(dx) > 1 or abs(dy) > 1:
        for obj in scene.objects:
            obj.x -= dx
            obj.y -= dy
            obj.adjust_position_from_center()
    return True


if __name__ == "__main__":
    game = libgame.Scene(
        init=game_init,
        controller=game_controller,
        prepaint=game_prepaint,
    )
    RUN = True
    while RUN:
        RUN = game.mainloop()
    print(f"Fin apres {libgame.loops} frames")

