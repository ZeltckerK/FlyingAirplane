# clouds.py
"""
Облака в небе над сценой.

Логика примерно как у деревьев/домиков:
- храним координаты облаков в МИРОВЫХ координатах (x_world, z_world),
- при отрисовке вычитаем WORLD_OFFSET, чтобы мир «ездил» под самолётом,
- когда облако слишком далеко — переставляем его вперёд по курсу.
"""

import random
import math
from typing import List, Tuple

from OpenGL.GL import *

from terrain import get_world_offset, terrain_height_world

# (x_world, z_world, scale, height)
CLOUDS: List[Tuple[float, float, float, float]] = []

# радиусы зоны вокруг самолёта
CLOUD_RADIUS_MIN = 80.0
CLOUD_RADIUS_MAX = 260.0

# высоты появления облаков
CLOUD_HEIGHT_MIN = 80.0
CLOUD_HEIGHT_MAX = 160.0

# сектор вперёд по курсу (в градусах)
FRONT_ARC_DEG = 80.0


def _draw_cloud_billboard(size: float):
    """
    Простой «пух» из нескольких перекрывающихся прямоугольников.
    Рисуем в локальных координатах вокруг (0,0,0).
    """
    half = size * 0.5

    # основной «слой» облака
    glBegin(GL_QUADS)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-half, 0.0, -half)
    glVertex3f(half, 0.0, -half)
    glVertex3f(half, 0.0, half)
    glVertex3f(-half, 0.0, half)
    glEnd()

    # доп. «пухи» для объёмности
    glPushMatrix()
    glTranslatef(-half * 0.3, 0.0, half * 0.3)
    glScalef(0.7, 1.0, 0.7)
    glBegin(GL_QUADS)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-half, 0.0, -half)
    glVertex3f(half, 0.0, -half)
    glVertex3f(half, 0.0, half)
    glVertex3f(-half, 0.0, half)
    glEnd()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(half * 0.3, 0.0, -half * 0.2)
    glScalef(0.6, 1.0, 0.6)
    glBegin(GL_QUADS)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-half, 0.0, -half)
    glVertex3f(half, 0.0, -half)
    glVertex3f(half, 0.0, half)
    glVertex3f(-half, 0.0, half)
    glEnd()
    glPopMatrix()


def _random_cloud_world(cx: float, cz: float) -> Tuple[float, float, float, float]:
    """
    Случайная позиция облака в кольце вокруг (cx, cz).
    """
    angle = random.uniform(0.0, 2.0 * math.pi)
    r = math.sqrt(random.uniform(CLOUD_RADIUS_MIN ** 2, CLOUD_RADIUS_MAX ** 2))
    x = cx + math.sin(angle) * r
    z = cz + math.cos(angle) * r
    scale = random.uniform(15.0, 30.0)
    height = random.uniform(CLOUD_HEIGHT_MIN, CLOUD_HEIGHT_MAX)
    return x, z, scale, height


def init_clouds():
    """
    Сгенерировать стартовое поле облаков вокруг самолёта.
    """
    global CLOUDS
    random.seed(2025)
    CLOUDS = []

    plane_x, plane_z = get_world_offset()

    count = 40
    for _ in range(count):
        CLOUDS.append(_random_cloud_world(plane_x, plane_z))


def update_clouds(plane_yaw_deg: float):
    """
    Переставляем облака, которые слишком далеко от самолёта, вперёд по курсу.
    """
    global CLOUDS

    plane_x, plane_z = get_world_offset()
    yaw_rad = math.radians(plane_yaw_deg)
    front_arc_rad = math.radians(FRONT_ARC_DEG)

    def respawn_in_front() -> Tuple[float, float, float, float]:
        angle = yaw_rad + random.uniform(-front_arc_rad, front_arc_rad)
        r = random.uniform(CLOUD_RADIUS_MIN, CLOUD_RADIUS_MAX)
        x = plane_x + math.sin(angle) * r
        z = plane_z + math.cos(angle) * r
        scale = random.uniform(15.0, 30.0)
        height = random.uniform(CLOUD_HEIGHT_MIN, CLOUD_HEIGHT_MAX)
        return x, z, scale, height

    new_clouds = []
    max_r2 = CLOUD_RADIUS_MAX ** 2
    for (x, z, s, h) in CLOUDS:
        dx = x - plane_x
        dz = z - plane_z
        if dx * dx + dz * dz > max_r2:
            new_clouds.append(respawn_in_front())
        else:
            new_clouds.append((x, z, s, h))

    CLOUDS = new_clouds


def draw_clouds():
    """
    Отрисовываем облака. Они чуть полупрозрачные и всегда выше рельефа.
    """
    wx, wz = get_world_offset()

    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glDisable(GL_LIGHTING)

    for (xw, zw, size, height) in CLOUDS:
        # гарантируем, что облако выше рельефа
        y = max(height, terrain_height_world(xw, zw) + CLOUD_HEIGHT_MIN)

        glPushMatrix()
        # из мировых координат -> в локальные (как в scenery)
        glTranslatef(xw - wx, y, zw - wz)

        glColor4f(1.0, 1.0, 1.0, 0.8)
        _draw_cloud_billboard(size)

        glPopMatrix()

    glPopAttrib()
