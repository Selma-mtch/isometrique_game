from __future__ import annotations
import pygame
import math
from typing import List, Tuple, Dict, Optional, Callable
from time import sleep

loops = 0


class Element:
    next_id = 1
    images: Dict[str, pygame.Surface] = {}
    sounds: Dict[str, pygame.mixer.Sound] = {}

    @classmethod
    def get_id(cls):
        a = cls.next_id
        cls.next_id += 1
        return a

    @classmethod
    def load_image(cls, filename: str) -> pygame.Surface:
        if filename not in cls.images:
            cls.images[filename] = pygame.image.load("assets/" + filename + ".png")
        return cls.images[filename].convert_alpha()

    @classmethod
    def register_image(cls, filename: str, img: pygame.Surface) -> None:
        if filename not in cls.images:
            cls.images[filename] = img

    @classmethod
    def load_sound(cls, filename: str) -> pygame.mixer.Sound:
        if filename not in cls.sounds:
            cls.sounds[filename] = pygame.mixer.Sound("assets/" + filename + ".wav")
        return cls.sounds[filename]

    @classmethod
    def real_side(cls, side: str, opposite: bool) -> str:
        if opposite:
            if side == "left":
                side = "right"
            elif side == "right":
                side = "left"
            elif side == "top":
                side = "bottom"
            elif side == "bottom":
                side = "top"
        return side

    @classmethod
    def linearcollision(cls, v1: float, m1: float, v2: float, m2: float) -> float:
        """Computes perfectly elastic collision in a one-dimensional context.
        Takes mass, former velocity for two objects and returns two new velocities."""
        return (m1 * v1 - m2 * v1 + 2 * m2 * v2) / (m1 + m2)

    def debug(self):
        pass

    def __init__(self, r: pygame.Rect) -> None:
        self.rect = r
        self.image: Optional[pygame.Surface] = None
        self.vx = 0.0
        self.vy = 0.0
        self.x = 0.0
        self.y = 0.0
        self.ax = 0.0
        self.ay = 0.0
        self.gravity = 200.0
        self.distance = 0.0
        self.type = "default"
        self.depth = 10
        self.id = Element.get_id()
        self.dontadjust = False
        self.mass = 10000
        self.elasticity = 0
        self.solids: List[str] = []

    def find_collision_side(
        self, obj: Element, etime: float
    ) -> List[Tuple[str, float, float, "Element", "Element"]]:
        infinity = float("inf")
        # global loops
        t_left = infinity
        t_right = infinity
        t_top = infinity
        t_bottom = infinity
        sw = self.rect.width / 2
        sh = self.rect.height / 2
        ow = obj.rect.width / 2
        oh = obj.rect.height / 2
        mindeltaspeed = 0.01
        maxtime = 2 * etime
        deltavx = self.vx - obj.vx
        deltavy = self.vy - obj.vy
        # Check if there is collision
        # This test supposes an important thing: at least one frame
        # happens when the objects do intersect.
        # If two objects have a relative speed too high, one can go
        # through the other and there will be no collision
        if not (
            self.x - sw < obj.x + ow
            and self.x + sw > obj.x - ow
            and self.y - sh < obj.y + oh
            and self.y + sh > obj.y - oh
        ):
            return []
        # Check collision from left and right if there is some real speed
        if abs(deltavx) > mindeltaspeed:
            if deltavx < 0:
                left_a = self.x - sw - self.vx * etime
                right_b = obj.x + ow - obj.vx * etime
                t_left = (right_b - left_a) / deltavx
                if abs(t_left) > maxtime:
                    t_left = infinity
            else:
                right_a = self.x + sw - self.vx * etime
                left_b = obj.x - ow - obj.vx * etime
                t_right = (left_b - right_a) / deltavx
                if abs(t_right) > maxtime:
                    t_right = infinity

        if abs(deltavy) * etime > mindeltaspeed:
            if deltavy > 0:
                bottom_a = self.y + sh - self.vy * etime
                top_b = obj.y - oh - obj.vy * etime
                t_bottom = (top_b - bottom_a) / (self.vy - obj.vy)
                if abs(t_bottom) > maxtime:
                    t_bottom = infinity

            else:
                top_a = self.y - sh - self.vy * etime
                bottom_b = obj.y + oh - obj.vy * etime
                t_top = (bottom_b - top_a) / (self.vy - obj.vy)
                if abs(t_top) > maxtime:
                    t_top = infinity
        collisions: List[Tuple[str, float, float, "Element", "Element"]] = []
        t_min = min(t_top, t_bottom, t_left, t_right)
        if t_min == infinity:
            return collisions
        if t_left == t_min:
            l_left = left_a + t_left * self.vx
            collisions.append(("left", t_left, l_left, self, obj))
        if t_right == t_min:
            l_right = right_a + t_right * self.vx
            collisions.append(("right", t_right, l_right, self, obj))
        if t_top == t_min:
            l_top = top_a + t_top * self.vy
            collisions.append(("top", t_top, l_top, self, obj))
        if t_bottom == t_min:
            l_bottom = bottom_a + t_bottom * self.vy
            collisions.append(("bottom", t_bottom, l_bottom, self, obj))
        return collisions

    def __str__(self):
        return f"{self.type} {self.id} at {self.x},{self.y} v={self.vx},{self.vy}"

    def play_sound(self, filename):
        s = Element.load_sound(filename)
        print('Playing "' + filename + '"')
        s.play()

    def finalize(self):
        print(f"Created a {self.type} {self.id} at ({self.x,self.y})")

    def do_paint(self, screen):
        if self.rect == None:
            return
        if self.image:
            screen.blit(self.image, self.rect)

    def do_accelerate(self, etime):
        self.oldx = self.x
        self.oldy = self.y
        self.vx += self.ax * etime
        self.vy += (self.ay + self.gravity) * etime

    def do_event(self, event: pygame.event.Event) -> bool:
        return True

    def do_move(self, etime):
        dx = self.vx * etime
        dy = self.vy * etime
        self.x += dx
        self.y += dy
        self.distance += abs(dx) + abs(dy)  # Not real distance, but good enough
        self.adjust_position_from_center()
        self.oldvx = self.vx
        self.oldvy = self.vy

    def do_adjustspeed(self, etime):
        if self.dontadjust:
            self.dontadjust = False
            return
        self.vx = (self.x - self.oldx) / etime
        self.vy = (self.y - self.oldy) / etime

    def do_detect(
        self, objects: list[Element], etime: float
    ) -> List[Tuple[str, float, float, "Element", "Element"]]:
        collisions: List[Tuple[str, float, float, "Element", "Element"]] = []
        if self.rect is None:
            return collisions
        for obj in objects:
            if obj.id == self.id:
                continue
            if obj.rect is None:
                continue
            collisions.extend(self.detect(obj, etime))
        return collisions

    def detect(
        self, obj: Element, etime: float
    ) -> List[Tuple[str, float, float, "Element", "Element"]]:
        if obj.type in self.solids:
            return self.find_collision_side(obj, etime)
        return []

    def bump_from(
        self,
        side: str,
        overtime: float,
        where: float,
        opposite: bool,
        other: Element,
    ) -> bool:
        # First, we ignore elements that we don't bump into
        if other.type not in self.solids:
            return False
        # Compute real side
        side = Element.real_side(side, opposite)
        # For one frame, we don't want speed to be measured, because we are going to
        # define a new speed anyway
        self.dontadjust = True
        oldvy = self.vy
        oldvx = self.vx
        if side == "left" or side == "right":
            newspeed = Element.linearcollision(
                self.vx, self.mass, other.oldvx, other.mass
            )
            if side == "left":
                self.x = where + self.rect.width / 2
            else:
                self.x = where - self.rect.width / 2
            self.vx = newspeed * self.elasticity
            self.y -= self.vy * overtime
        elif side == "top" or side == "bottom":
            newspeed = Element.linearcollision(
                self.vy, self.mass, other.oldvy, other.mass
            )
            if side == "top":
                self.y = where + self.rect.height / 2
            else:
                self.y = where - self.rect.height / 2
            self.vy = newspeed * self.elasticity
            self.x -= self.vx * overtime
        self.adjust_position_from_center()
        return True

    def adjust_position_from_rect(self):
        self.x, self.y = self.rect.center

    def adjust_position_from_center(self):
        self.rect.center = int(self.x), int(self.y)


class Ground(Element):
    def __init__(
        self, color: Tuple[int, int, int], x: float, y: float, w: float, h: float
    ):
        super().__init__(pygame.Rect(x, y, w, h))
        self.gravity = 0
        self.color = color
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.depth = 10
        self.type = "ground"
        self.finalize()

    def do_paint(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class Tree(Element):
    def __init__(self, x: float, y: float, depth: int):
        if depth <= 0:
            depth = 1
        if depth > 20:
            depth = 20
        img = pygame.transform.smoothscale_by(Element.load_image("tree"), depth / 10)
        super().__init__(img.get_rect())
        self.image: pygame.Surface = img
        self.gravity = 0
        self.x = x
        self.y = y - self.rect.height / 2
        self.adjust_position_from_center
        self.depth = depth
        self.type = "tree"
        self.finalize()

    def do_paint(self, screen):
        screen.blit(self.image, self.rect)


class Rock(Element):
    def __init__(self, x: float, y: float, vx: float = 0, vy: float = 0):
        img = Element.load_image("small_rock")
        super().__init__(img.get_rect())
        self.image: pygame.Surface = img
        Element.load_sound("rock")
        Element.load_sound("rock2")
        self.vx = vx
        self.vy = vy
        self.rect.center = int(x), int(y)
        self.x, self.y = x, y
        self.type = "rock"
        self.solids = ["rock", "ground"]
        self.finalize()

    def do_paint(self, screen):
        screen.blit(self.image, self.rect)

    # bump_from : consequences of bump coming from side "side", at coordinate "where"
    def bump_from(
        self,
        side: str,
        overtime: float,
        where: float,
        opposite: bool,
        other: Element,
    ) -> bool:
        # First, we ignore elements that we don't bump into
        if other.type not in self.solids:
            return False
        # Compute real side
        side = Element.real_side(side, opposite)
        # For one frame, we don't want speed to be measured, because we are going to
        # define a new speed anyway
        self.dontadjust = True
        oldvy = self.vy
        oldvx = self.vx
        if side == "left":
            self.x = where + self.rect.width / 2
            self.vx = 0
            self.y -= self.vy * overtime
        elif side == "right":
            self.x = where - self.rect.width / 2
            self.vx = 0
            self.y -= self.vy * overtime
        elif side == "top":
            self.y = where + self.rect.height / 2
            self.vy = 0
            self.x -= self.vx * overtime
        elif side == "bottom":
            self.y = where - self.rect.height / 2
            self.vy = 0
            self.x -= self.vx * overtime
        if other.type == "ground":
            if oldvy > 0.5 * self.gravity:
                if oldvy > self.gravity:
                    self.play_sound("rock")
                else:
                    self.play_sound("rock2")
        self.adjust_position_from_center()
        return True


class Ball(Element):
    def __init__(self, x: float, y: float, vx: float = 0, vy: float = 0):
        img = Element.load_image("small_ball")
        super().__init__(img.get_rect())
        self.image = img
        assert img is not None
        self.rect = img.get_rect()
        self.vx = vx
        self.vy = vy
        self.rect.center = int(x), int(y)
        self.x, self.y = x, y
        self.type = "ball"
        self.elasticity = 1
        self.mass = 1
        self.solids = ["rock", "ground", "ball", "walker"]
        self.finalize()

    def do_paint(self, screen):
        screen.blit(self.image, self.rect)


class BlueBall(Ball):
    def __init__(self, *args, **kargs):
        img = Element.load_image("small_ball")
        super().__init__(*args, **kargs)
        self.image = Element.load_image("small_ball2")
        self.rect = self.image.get_rect()
        self.elasticity = 0.9
        self.finalize()


class AutoWalker(Element):
    def __init__(self, x: float, y: float, vx: float = 0, vy: float = 0):
        base = Element.load_image("bonhomme_haut")
        av = Element.load_image("bonhomme_av")
        ar = Element.load_image("bonhomme_ar")
        rect = base.get_rect()
        w, h = rect.size
        super().__init__(rect)
        self.images: Dict[str, pygame.Surface] = {}
        for i in range(9):
            if i == 0:
                pav, par = av, ar
            else:
                pav = pygame.transform.rotate(av, 6 * i)
                par = pygame.transform.rotate(ar, -6 * i)
            avr = pav.get_rect()
            arr = par.get_rect()
            avr.center = rect.center
            arr.center = rect.center
            merged_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            merged_surface.blit(base, rect)
            merged_surface.blit(pav, avr)
            merged_surface.blit(par, arr)
            opposite = pygame.transform.flip(merged_surface, True, False)
            Element.register_image("walker" + str(i), merged_surface)
            Element.register_image("walkerX" + str(i), opposite)
            self.images["walker" + str(i)] = merged_surface
            self.images["walkerX" + str(i)] = opposite
            if i > 0 and i < 8:
                Element.register_image("walker" + str(16 - i), merged_surface)
                Element.register_image("walkerX" + str(16 - i), opposite)
                self.images["walker" + str(16 - i)] = merged_surface
                self.images["walkerX" + str(16 - i)] = opposite
        self.image = self.images["walker0"]
        Element.load_sound("blop")
        self.last_state: int = 0
        self.distance: float = 0
        self.vx = vx
        self.vy = vy
        self.rect.center = int(x), int(y)
        self.x, self.y = x, y
        self.type = "walker"
        self.solids: List[str] = ["ground", "rock", "walker"]
        self.mass = 100
        self.elasticity = 0
        self.finalize()

    def do_paint(self, screen):
        state = int(self.distance / 8) % 16
        if self.vx > 0:
            base = "walkerX"
        else:
            base = "walker"
        screen.blit(self.images[base + str(state)], self.rect)

    def do_accelerate(self, etime):
        if self.vy == 0:
            self.vx = math.copysign(
                min(300, abs(50 * math.ceil(self.vx / 50))), self.vx
            )
        return super().do_accelerate(etime)

    def do_event(self, event):
        if event.key == pygame.K_ESCAPE and self.vy == 0:
            return False
        if event.key == pygame.K_SPACE and self.vy == 0:
            self.dontadjust = True
            self.vy = -350
        if event.key == pygame.K_LEFT and self.vy == 0:
            self.vx -= 50
        if event.key == pygame.K_RIGHT and self.vy == 0:
            self.vx += 50
        if event.key == pygame.K_SPACE and self.vy == 0:
            self.dontadjust = True
            self.vy = -350
        return True

    def bump_from(
        self,
        side: str,
        overtime: float,
        where: float,
        opposite: bool,
        other: Element,
    ) -> bool:
        if (side == "left" or side == "right") and other.type in self.solids:
            self.play_sound("blop")
            self.dontadjust = True
            realside = Element.real_side(side, opposite)
            if realside == "left":
                self.vx = 100
            else:
                self.vx = -100
            return True
        return super().bump_from(side, overtime, where, opposite, other)


class Walker2D(Element):
    def __init__(self, x: float, y: float):
        base = Element.load_image("man")
        self.base = base
        rect = pygame.Rect(0, 0, 16, 16)
        w, h = rect.size
        super().__init__(rect)
        self.images: Dict[str, pygame.Surface] = {}
        for i, xx in enumerate(["N", "E", "S", "W"]):
            for pos in range(4):
                img_name = f"man{xx}{pos}"
                xpos = pos
                if pos == 3:
                    xpos = 1
                merged_surface = pygame.Surface.subsurface(base, xpos * w, i * h, w, h)
                print(base, xpos * w, i * h, w, h)
                self.images[img_name] = merged_surface
                Element.register_image(img_name, merged_surface)
        self.image = self.images["manN0"]
        self.last_state: int = 0
        self.distance: float = 0
        self.vx = 0
        self.vy = 0
        self.rect.center = int(x), int(y)
        self.x, self.y = x, y
        self.type = "walker2d"
        self.solids: List[str] = ["ground"]
        self.mass = 100
        self.elasticity = 0
        self.gravity = 0
        self.speedbase = 10
        self.finalize()

    def do_paint(self, screen):
        state = int(self.distance / 4) % 4
        if self.vy < 0:
            base = "manN"
        elif self.vx < 0:
            base = "manW"
        elif self.vx > 0:
            base = "manE"
        else:
            base = "manS"
        name = base + str(state)
        screen.blit(self.images[name], self.rect)

    def do_accelerate(self, etime):
        if abs(self.vy) > abs(self.vx):
            self.vx = 0
            self.vy = math.copysign(
                min(300, self.speedbase * round(self.vy / self.speedbase)),
                self.vy,
            )
        else:
            self.vy = 0
            self.vx = math.copysign(
                min(300, self.speedbase * round(self.vx / self.speedbase)),
                self.vx,
            )
        return super().do_accelerate(etime)

    def do_event(self, event):
        speed_base = self.speedbase
        if event.key == pygame.K_ESCAPE:
            return False
        if event.key == pygame.K_LEFT:
            self.vx -= speed_base
            self.vy = 0
            self.dontadjust = True
        if event.key == pygame.K_RIGHT:
            self.vx += speed_base
            self.vy = 0
            self.dontadjust = True
        if event.key == pygame.K_UP:
            self.vy -= speed_base
            self.vx = 0
            self.dontadjust = True
        if event.key == pygame.K_DOWN:
            self.vy += speed_base
            self.vx = 0
            self.dontadjust = True
        if event.key == pygame.K_SPACE:
            self.vy = 0
            self.vx = 0
            self.dontadjust = True
        return True


class Scene:
    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        init: Optional[Callable[["Scene"], List[Element]]] = None,
        controller: Optional[
            Callable[[List[Element], pygame.event.Event], bool]
        ] = None,
        prepaint: Optional[Callable[["Scene"], bool]] = None,
        tick=60,
    ) -> None:
        pygame.init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.tick = tick
        self.time_game: float = 0.0
        self.window_size = width, height
        self.screen = pygame.display.set_mode(self.window_size)
        self.objects: List[Element] = []
        if init is not None:
            self.objects = init(self)
        self.prepaint = prepaint
        self.objects_by_depth = sorted(self.objects, key=lambda x: x.depth)
        self.objects.sort(key=lambda x: x.id)
        self.controller = controller

    def startupdelay(self, t: float) -> None:
        pygame.display.flip()
        sleep(t)

    def mainloop(self) -> bool:
        global loops
        objects = self.objects
        old_time = self.time_game
        self.time_game = pygame.time.get_ticks() / 1000
        etime = self.time_game - old_time
        loops += 1
        # Tick limit
        if self.tick > 0:
            self.clock.tick(self.tick)
        for event in pygame.event.get():
            if self.controller is not None:
                res = self.controller(objects, event)
                if not res:
                    return False
            if event.type == pygame.QUIT:
                return False
        for obj in objects:
            obj.debug()
            obj.do_accelerate(etime)
        for obj in objects:
            obj.do_move(etime)
        search_collisions = True
        while search_collisions:
            collisions = []
            for obj in objects:
                collisions.extend(obj.do_detect(objects, etime))
            collisions.sort(key=lambda x: x[2])
            if len(collisions) == 0:
                search_collisions = False
                continue
            # Deal with first collision only
            # This could be enhanced a lot, but if there are not too many collisions
            # we should be fine
            side, deltatime, where, subject, other = collisions[0]
            # Debug collision
            debug = False
            overtime = etime - deltatime
            if debug:
                print(
                    f"{loops} There is a {side} collision between {subject.type} {subject.id} and {other.type} {other.id}."
                )
                print(
                    f"{loops} Timing: {etime} (deltatime: {deltatime}, overtime: {overtime})"
                )
                print(
                    loops,
                    subject.type + " " + str(subject.id),
                    subject.x,
                    subject.y,
                    subject.x - subject.rect.width / 2,
                    subject.x + subject.rect.width / 2,
                    subject.vx,
                )
                print(
                    loops,
                    other.type + " " + str(other.id),
                    other.x,
                    other.y,
                    other.x - other.rect.width / 2,
                    other.x + other.rect.width / 2,
                    other.vx,
                )
                print(loops, "Bumping subject")
            res_subject = subject.bump_from(side, overtime, where, False, other)
            if debug:
                print(
                    loops,
                    subject.type + " " + str(subject.id),
                    subject.x,
                    subject.y,
                    subject.x - subject.rect.width / 2,
                    subject.x + subject.rect.width / 2,
                    subject.vx,
                )
                print(loops, "Bumping other")
            res_other = other.bump_from(side, overtime, where, True, subject)
            if debug:
                print(
                    loops,
                    other.type + " " + str(other.id),
                    other.x,
                    other.y,
                    other.x - other.rect.width / 2,
                    other.x + other.rect.width / 2,
                    other.vx,
                )
            if res_subject:
                subject.do_move(overtime)
            if res_other:
                other.do_move(overtime)
            if debug:
                print(
                    loops,
                    subject.type + " " + str(subject.id),
                    subject.x,
                    subject.y,
                    subject.x - subject.rect.width / 2,
                    subject.x + subject.rect.width / 2,
                    subject.vx,
                )
                print(
                    loops,
                    other.type + " " + str(other.id),
                    other.x,
                    other.y,
                    other.x - other.rect.width / 2,
                    other.x + other.rect.width / 2,
                    other.vx,
                )
        for obj in objects:
            obj.do_adjustspeed(etime)
        if self.prepaint is not None:
            res = self.prepaint(self)
            if not res:
                return False
        self.screen.fill((0, 0, 0))
        for obj in self.objects_by_depth:
            obj.do_paint(self.screen)
        pygame.display.flip()
        return True
