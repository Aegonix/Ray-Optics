import pygame
from pygame.font import SysFont
from pygame.math import Vector2
import pygame_widgets
from pygame_widgets.slider import Slider
from math import sqrt, trunc
from random import choice
from button import Button

# from sympy import Eq, solve
# from sympy.abc import x, y
from numpy.linalg import solve
from itertools import combinations

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
WIDTH = 1200
HEIGHT = 700
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Concave Mirror")
font = SysFont("JetBrains Mono", 20)

n_slider = Slider(win, 950, 170, 200, 15, min=2, max=20, handleColour=WHITE)
n_label = font.render("Number of Rays:", True, WHITE)
f_slider = Slider(
    win, 950, 270, 200, 15, min=50, max=300, initial=150, handleColour=WHITE
)
f_label = font.render("Focal Length:", True, WHITE)
u_slider = Slider(win, 950, 370, 200, 15, min=50, max=450, handleColour=WHITE)
u_label = font.render("Object Distance:", True, WHITE)
h_slider = Slider(win, 950, 470, 200, 15, min=0, max=200, handleColour=WHITE)
h_label = font.render("Object Height:", True, WHITE)
F_label = font.render("F", True, WHITE)
C_label = font.render("C", True, WHITE)


class Object:
    images = []

    def __init__(self, mirror) -> None:
        self.distance = u_slider.getValue()
        self.height = h_slider.getValue()
        self.x = mirror.pole.x - self.distance
        self.y = mirror.pole.y - self.height
        self.mirror = mirror

    def update(self):
        self.__init__(self.mirror)

    def draw(self):
        self.update()
        pygame.draw.aaline(win, RED, (self.x, self.mirror.pole.y), (self.x, self.y), 5)


class ConcaveMirror:
    picked_points = []
    reflected_vectors = {}

    def __init__(self) -> None:
        self.f = int(f_slider.getValue())  # type: ignore
        self.radius = 2 * self.f
        self.pole = Vector2(450, 350)
        pygame.draw.aaline(win, WHITE, (0, self.pole.y), (900, self.pole.y))
        self.rect = pygame.Rect(
            self.pole.x - 2 * self.radius,
            self.pole.y - self.radius,
            2 * self.radius,
            2 * self.radius,
        )
        self.points = self.get_points()

    def get_points(self):
        x_vals = range(int(self.pole.x - self.f) * 100, (int(self.pole.x) * 100))
        x_vals = [x / 100 for x in x_vals]
        points = []
        for x in x_vals:
            points.append(
                Vector2(x, self.pole.y - 2 * sqrt(-self.f * (x - self.pole.x)))
            )
            points.append(
                Vector2(x, self.pole.y + 2 * sqrt(-self.f * (x - self.pole.x)))
            )

        return sorted(points, key=lambda point: point.y)

    def update(self):
        self.__init__()

    def draw(self):
        self.update()
        pygame.draw.aalines(win, WHITE, False, self.points)

    def derivative(self, point):
        if point.y > self.pole.y:
            return -self.f / sqrt(-self.f * (point.x - self.pole.x))

        return self.f / sqrt(-self.f * (point.x - self.pole.x))


def pick_points(mirror, object):
    mirror.picked_points = []
    for _ in range(n_slider.getValue()):
        mirror.picked_points.append(Vector2(choice(mirror.points)))

    reflect(mirror, object)


def draw_rays(mirror, object):
    for point in mirror.picked_points:
        pygame.draw.aaline(win, WHITE, (object.x, object.y), point)

    for pos in object.images:
        pos = [round(x, 0) for x in pos]
        pygame.draw.circle(win, RED, pos, 5)

    for point, vector in mirror.reflected_vectors.items():
        point = Vector2(point)
        vector = Vector2(point.x - 900, (point.x - 900) / vector.x * vector.y)
        draw_dotted(point, point - vector)
        pygame.draw.aaline(win, WHITE, point, point + vector)


def draw_dotted(p1: Vector2, p2: Vector2):
    dist = p1.distance_to(p2)
    slope = (p1 - p2) / dist
    for i in range(0, trunc(dist / 10) + 1, 2):
        start = p1 - (slope * i * 10)
        end = p1 - (slope * (i + 1) * 10)
        pygame.draw.aaline(win, WHITE, start, end)


def reflect(mirror: ConcaveMirror, object: Object):
    object.images = []
    equations = []
    mirror.reflected_vectors = {}
    for point in mirror.picked_points:
        tangent = Vector2(1, mirror.derivative(point))

        normal = Vector2(tangent.y, -tangent.x)

        incident_vector = Vector2(point.x - object.x, point.y - object.y)
        reflected_vector = incident_vector.reflect(normal)
        mirror.reflected_vectors[(point.x, point.y)] = reflected_vector

        p = point + reflected_vector
        m = (point.y - p.y) / (point.x - p.x)
        equation = {"a": [m, -1], "b": [(m * p.x) - p.y]}
        equations.append(equation)

    for eq1, eq2 in combinations(equations, 2):
        solution = solve([eq1["a"], eq2["a"]], [eq1["b"], eq2["b"]])
        object.images.append(Vector2(list(solution.flatten())))


def draw(mirror, object, draw_button, events):
    win.fill(BLACK)
    win.blit(n_label, (950, 130))
    n_value = font.render(str(n_slider.getValue()), True, WHITE)
    win.blit(n_value, (1050 - n_value.get_width() / 2, 194))
    win.blit(f_label, (950, 230))
    f_value = font.render(str(f_slider.getValue()), True, WHITE)
    win.blit(f_value, (1050 - f_value.get_width() / 2, 294))
    win.blit(u_label, (950, 330))
    u_value = font.render(str(u_slider.getValue()), True, WHITE)
    win.blit(u_value, (1050 - u_value.get_width() / 2, 394))
    win.blit(h_label, (950, 430))
    h_value = font.render(str(h_slider.getValue()), True, WHITE)
    win.blit(h_value, (1050 - h_value.get_width() / 2, 494))
    win.blit(F_label, (mirror.pole.x - mirror.f - C_label.get_width() / 2, 360))
    win.blit(
        C_label,
        (mirror.rect.centerx - C_label.get_width() / 2, mirror.rect.centery + 10),
    )
    mirror.draw()
    object.draw()
    draw_button.update(win)
    draw_rays(mirror, object)
    pygame.draw.circle(win, WHITE, (mirror.pole.x - mirror.radius, mirror.pole.y), 5)
    pygame.draw.circle(win, WHITE, (mirror.pole.x - mirror.f, mirror.pole.y), 5)
    pygame_widgets.update(events)
    pygame.display.flip()


def main():
    running = True
    mirror = ConcaveMirror()
    object = Object(mirror)
    draw_button = Button(
        950, 530, 50, 200, BLACK, "Draw Rays", lambda: pick_points(mirror, object)
    )
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()

        draw(mirror, object, draw_button, events)


if __name__ == "__main__":
    main()
