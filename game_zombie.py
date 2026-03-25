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
    "X.....WW.....Z.X",
    "X..............X",
    "X.....XX..T....X",
    "X..T...XX......X",
    "X.Z............X",
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
zombie_spawns_grid = []
camera_offset_x = 0.0
camera_offset_y = 0.0
game_alive = True
game_score = 0.0
spawn_timer = 3.0
want_restart = False
last_time = 0.0


def is_in_water(obj):
    hw = obj.rect.width / 2
    hh = obj.rect.height / 2
    for w in water_tiles:
        whw = w.tile_w / 2
        whh = w.tile_h / 2
        if (obj.x - hw < w.x + whw and obj.x + hw > w.x - whw
                and obj.y - hh < w.y + whh and obj.y + hh > w.y - whh):
            return True
    return False


def to_iso(wx, wy, sw, sh):
    iso_x = (wx - wy) + sh / 2
    iso_y = (wx + wy) / 2 + (sh - sw) / 4
    return iso_x, iso_y


water_tiles = []


class IsoGround(libgame.Element):

    def __init__(self, color, x, y, w, h, block_height=0, ground_type="ground"):
        super().__init__(pygame.Rect(x, y, w, h))
        self.gravity = 0
        self.color = color
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.depth = 5
        self.type = ground_type
        self.tile_w = w
        self.tile_h = h
        self.block_height = block_height
        self.finalize()

    def do_paint(self, screen):
        sw, sh = screen.get_size()
        cx, cy = self.x, self.y
        hw, hh = self.tile_w / 2, self.tile_h / 2
        top = to_iso(cx - hw, cy - hh, sw, sh)
        right = to_iso(cx + hw, cy - hh, sw, sh)
        bottom = to_iso(cx + hw, cy + hh, sw, sh)
        left = to_iso(cx - hw, cy + hh, sw, sh)
        points = [top, right, bottom, left]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        if max(xs) < -64 or min(xs) > sw + 64 or max(ys) < -64 or min(ys) > sh + 64:
            return
        bh = self.block_height
        if bh > 0:
            dark = tuple(max(0, int(c * 0.55)) for c in self.color)
            darker = tuple(max(0, int(c * 0.35)) for c in self.color)
            pygame.draw.polygon(screen, darker, [
                left, bottom,
                (bottom[0], bottom[1] + bh),
                (left[0], left[1] + bh),
            ])
            pygame.draw.polygon(screen, dark, [
                right, bottom,
                (bottom[0], bottom[1] + bh),
                (right[0], right[1] + bh),
            ])
        pygame.draw.polygon(screen, self.color, points)
        if self.tile_w <= TILE * 2:
            outline = tuple(max(0, c - 25) for c in self.color)
            pygame.draw.polygon(screen, outline, points, 1)


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
        sdx, sdy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            sdx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            sdx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            sdy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            sdy += 1
        if sdx != 0 and sdy != 0:
            sdx *= 0.707
            sdy *= 0.707
        self.vx = (sdx * 0.5 + sdy) * speed
        self.vy = (-sdx * 0.5 + sdy) * speed
        if is_in_water(self):
            self.vx *= 0.4
            self.vy *= 0.4
        self.dontadjust = True

    def do_paint(self, screen):
        sw, sh = screen.get_size()
        state = int(self.distance / 4) % 4
        iso_vx = self.vx - self.vy
        iso_vy = (self.vx + self.vy) / 2
        if abs(iso_vy) > abs(iso_vx):
            base = "manN" if iso_vy < 0 else "manS"
        else:
            base = "manW" if iso_vx < 0 else "manE"
        img = self.images[base + str(state)]
        ix, iy = to_iso(self.x, self.y, sw, sh)
        screen.blit(img, img.get_rect(center=(int(ix), int(iy))))


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
        sw, sh = screen.get_size()
        state = int(self.distance / 4) % 4
        iso_vx = self.vx - self.vy
        iso_vy = (self.vx + self.vy) / 2
        if abs(iso_vy) > abs(iso_vx):
            d = "N" if iso_vy < 0 else "S"
        else:
            d = "W" if iso_vx < 0 else "E"
        img = self._sprites[f"z{d}{state}"]
        ix, iy = to_iso(self.x, self.y, sw, sh)
        screen.blit(img, img.get_rect(center=(int(ix), int(iy))))

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
        if is_in_water(self):
            self.vx *= 0.4
            self.vy *= 0.4
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
    global player, zombie_spawns_grid, camera_offset_x, camera_offset_y
    global game_alive, game_score, spawn_timer, last_time
    game_alive = True
    game_score = 0.0
    spawn_timer = 3.0
    last_time = 0.0
    camera_offset_x = 0.0
    camera_offset_y = 0.0

    width, height = scene.window_size
    objects: List[libgame.Element] = []
    zombie_spawns_grid = []
    water_tiles.clear()

    grass = IsoGround((80, 150, 60), 0, 0, MAP_COLS * TILE, MAP_ROWS * TILE)
    grass.depth = 1
    objects.append(grass)

    player = None

    for row_i, row in enumerate(GAME_MAP):
        for col_i, ch in enumerate(row):
            wx = col_i * TILE
            wy = row_i * TILE
            if ch == "X":
                objects.append(IsoGround((100, 85, 75), wx, wy, TILE, TILE, block_height=10))
            elif ch == "W":
                w_tile = IsoGround((40, 100, 190), wx, wy, TILE, TILE, ground_type="water")
                objects.append(w_tile)
                water_tiles.append(w_tile)
            elif ch == "T":
                objects.append(IsoGround((30, 110, 40), wx, wy, TILE, TILE, block_height=6))
            elif ch == "P":
                player = Player(wx + TILE // 2, wy + TILE // 2)
            elif ch == "Z":
                zombie_spawns_grid.append((col_i, row_i))

    objects.append(player)

    for col, row in zombie_spawns_grid:
        zx = col * TILE + TILE // 2
        zy = row * TILE + TILE // 2
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
    global camera_offset_x, camera_offset_y

    if last_time == 0.0:
        last_time = scene.time_game
    dt = scene.time_game - last_time
    last_time = scene.time_game

    if game_alive:
        game_score += dt

        spawn_timer -= dt
        if spawn_timer <= 0 and zombie_spawns_grid:
            col, row = random.choice(zombie_spawns_grid)
            zx = col * TILE + TILE // 2 - camera_offset_x
            zy = row * TILE + TILE // 2 - camera_offset_y
            new_z = Zombie2D(zx, zy, player)
            scene.objects.append(new_z)
            scene.objects_by_depth.append(new_z)
            spawn_timer = max(0.3, 1.5 - game_score * 0.05)

        to_remove = []
        for obj in scene.objects:
            if obj.type == "zombie":
                zdx = obj.x - player.x
                zdy = obj.y - player.y
                dist2 = zdx * zdx + zdy * zdy
                if dist2 < 100:
                    game_alive = False
                elif dist2 > 640000:
                    to_remove.append(obj)
        for obj in to_remove:
            scene.objects.remove(obj)
            if obj in scene.objects_by_depth:
                scene.objects_by_depth.remove(obj)

    width, height = scene.window_size
    dx = player.rect.centerx - width // 2
    dy = player.rect.centery - height // 2
    if abs(dx) > 1 or abs(dy) > 1:
        for obj in scene.objects:
            if obj.type != "hud":
                obj.x -= dx
                obj.y -= dy
                obj.adjust_position_from_center()
        camera_offset_x += dx
        camera_offset_y += dy

    scene.objects_by_depth.sort(key=lambda o: (o.depth, o.x + o.y))

    return True


if __name__ == "__main__":
    want_restart = True
    while want_restart:
        want_restart = False
        game = libgame.Scene(
            width=800,
            height=600,
            init=game_init,
            controller=game_controller,
            prepaint=game_prepaint,
        )
        RUN = True
        while RUN:
            RUN = game.mainloop()
    print(f"Fin apres {libgame.loops} frames")
