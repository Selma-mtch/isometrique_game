import libgame
import pygame
import math
import random
from typing import List, Dict

TILE = 32
GAME_MAP = [
    "XXXXXXXXXXXXXXXX",
    "X..............X",
    "X..T.........Z.X",
    "X..............X",
    "X.....XX.......X",
    "X.....XX.......X",
    "X.....T........X",
    "X.T..WWW.......X",
    "X....WWWW......X",
    "X.....WW......ZX",
    "X..............X",
    "X.....XX..T....X",
    "X..T...XX......X",
    "XZ.............X",
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
zombie_spawns = []
game_alive = True
game_score = 0.0
spawn_timer = 3.0
want_restart = False
last_time = 0.0


class Player(libgame.Walker2D):

    def do_event(self, event):
        return True

    def do_accelerate(self, etime):
        self.oldx = self.x
        self.oldy = self.y
        if not game_alive:
            self.vx = 0
            self.vy = 0
            self.dontadjust = True
            return
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


class Zombie2D(libgame.Element):

    def __init__(self, x: float, y: float, target: libgame.Element):
        base = libgame.Element.load_image("man")
        rect = pygame.Rect(0, 0, 16, 16)
        w, h = rect.size
        super().__init__(rect)
        self.target = target
        self._sprites: Dict[str, pygame.Surface] = {}
        for i, direction in enumerate(["N", "E", "S", "W"]):
            for pos in range(4):
                xpos = pos if pos < 3 else 1
                frame = pygame.Surface.subsurface(base, xpos * w, i * h, w, h).copy()
                tint = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                tint.fill((0, 60, 0))
                frame.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                self._sprites[f"z{direction}{pos}"] = frame
        self.image = self._sprites["zS0"]
        self.gravity = 0
        self.speed = 35 + random.uniform(-5, 10)
        self.rect.center = int(x), int(y)
        self.x, self.y = x, y
        self.type = "zombie"
        self.solids = ["ground"]
        self.mass = 50
        self.elasticity = 0
        self.finalize()

    def do_paint(self, screen):
        state = int(self.distance / 4) % 4
        if abs(self.vy) > abs(self.vx):
            d = "N" if self.vy < 0 else "S"
        else:
            d = "W" if self.vx < 0 else "E"
        screen.blit(self._sprites[f"z{d}{state}"], self.rect)

    def do_accelerate(self, etime):
        self.oldx = self.x
        self.oldy = self.y
        if not game_alive:
            self.vx = 0
            self.vy = 0
            self.dontadjust = True
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 1:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        self.dontadjust = True


class GameHUD(libgame.Element):

    def __init__(self, w: int, h: int):
        super().__init__(pygame.Rect(0, 0, 0, 0))
        self.gravity = 0
        self.type = "hud"
        self.depth = 100
        self.sw, self.sh = w, h
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 40, bold=True)

    def do_paint(self, screen):
        txt = f"Survie: {int(game_score)}s"
        screen.blit(self.font.render(txt, True, (0, 0, 0)), (11, 11))
        screen.blit(self.font.render(txt, True, (255, 255, 255)), (10, 10))
        if not game_alive:
            overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            go = self.big_font.render("GAME OVER", True, (220, 40, 40))
            screen.blit(go, go.get_rect(center=(self.sw // 2, self.sh // 2 - 20)))
            info = self.font.render(
                f"Survie: {int(game_score)}s  -  ESPACE: recommencer",
                True, (255, 255, 255),
            )
            screen.blit(info, info.get_rect(center=(self.sw // 2, self.sh // 2 + 25)))

    def do_accelerate(self, etime):
        pass

    def do_move(self, etime):
        pass

    def do_adjustspeed(self, etime):
        pass


def game_init(scene: libgame.Scene) -> List[libgame.Element]:
    global player, zombie_spawns, game_alive, game_score, spawn_timer, last_time
    game_alive = True
    game_score = 0.0
    spawn_timer = 3.0
    last_time = 0.0

    width, height = scene.window_size
    objects: List[libgame.Element] = []
    zombie_spawns = []

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
            elif ch == "Z":
                zombie_spawns.append((wx + TILE // 2, wy + TILE // 2))

    objects.append(player)

    for zx, zy in zombie_spawns:
        objects.append(Zombie2D(zx, zy, player))

    objects.append(GameHUD(width, height))
    return objects


def game_controller(objects: List[libgame.Element], event: pygame.event.Event) -> bool:
    global want_restart
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            want_restart = False
            return False
        if event.key == pygame.K_SPACE and not game_alive:
            want_restart = True
            return False
    return True


def game_prepaint(scene: libgame.Scene) -> bool:
    global game_alive, game_score, spawn_timer, last_time

    if last_time == 0.0:
        last_time = scene.time_game
    dt = scene.time_game - last_time
    last_time = scene.time_game

    if game_alive:
        game_score += dt

        spawn_timer -= dt
        if spawn_timer <= 0 and zombie_spawns:
            zx, zy = random.choice(zombie_spawns)
            new_z = Zombie2D(zx, zy, player)
            scene.objects.append(new_z)
            scene.objects_by_depth.append(new_z)
            spawn_timer = max(1.0, 3.0 - game_score * 0.03)

        for obj in scene.objects:
            if obj.type == "zombie":
                dx = obj.x - player.x
                dy = obj.y - player.y
                if math.sqrt(dx * dx + dy * dy) < 10:
                    game_alive = False

    # Camera centree sur le joueur
    width, height = scene.window_size
    dx = player.rect.centerx - width // 2
    dy = player.rect.centery - height // 2
    if abs(dx) > 1 or abs(dy) > 1:
        for obj in scene.objects:
            if obj.type != "hud":
                obj.x -= dx
                obj.y -= dy
                obj.adjust_position_from_center()

    return True


if __name__ == "__main__":
    want_restart = True
    while want_restart:
        want_restart = False
        game = libgame.Scene(
            init=game_init,
            controller=game_controller,
            prepaint=game_prepaint,
        )
        RUN = True
        while RUN:
            RUN = game.mainloop()
    print(f"Fin apres {libgame.loops} frames")
