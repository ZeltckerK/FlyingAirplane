# terrain.py
"""
Лёгкая "бесконечная" земля:

- Геометрия: один квадрат (plane) вокруг самолёта в ЛОКАЛЬНЫХ координатах.
- Самолёт живёт около (0, 0), камера смотрит на него.
- WORLD_OFFSET_X/Z хранят, насколько далеко "улетел" самолёт по миру.
- Текстура земли считается из МИРОВЫХ координат (x_world, z_world),
  чтобы узор скроллился под самолётом при полёте.
- Квадрат земли дополнительно сдвигаем НАЗАД по курсу самолёта,
  чтобы деревья/домики впереди не вылезали из текстуры.

Высота земли = 0.0 везде (плоская поверхность).
"""

from typing import Tuple

from OpenGL.GL import *

WORLD_OFFSET_X: float = 0.0
WORLD_OFFSET_Z: float = 0.0

# Размер квадрата земли вокруг самолёта.
HALF_SIZE = 200.0  # не трогаем, как просил

_ground_texture_id: int | None = None


def move_world(dx: float, dz: float) -> None:
    """
    Сдвигаем мир (копим координаты самолёта в WORLD_OFFSET_*).
    Вызывается из Airplane.update().
    """
    global WORLD_OFFSET_X, WORLD_OFFSET_Z
    WORLD_OFFSET_X += dx
    WORLD_OFFSET_Z += dz


def get_world_offset() -> Tuple[float, float]:
    """Возвращаем 'мировые координаты' самолёта."""
    return WORLD_OFFSET_X, WORLD_OFFSET_Z


def terrain_height(x: float, z: float) -> float:
    """Плоская земля, просто 0.0."""
    return 0.0


def terrain_height_world(wx: float, wz: float) -> float:
    """Плоская земля, просто 0.0."""
    return 0.0


def _create_checker_texture(size: int = 64) -> int:
    """
    Создаём простую текстуру ярко-зелёной травы в памяти.
    Сплошной салатовый цвет.
    """
    import numpy as np

    image = np.zeros((size, size, 3), dtype=np.uint8)

    # САЛАТОВЫЙ (яркий зелёный)
    # можешь поиграть: (120, 255, 80), (100, 255, 0) и т.п.
    bright = (22, 171, 61)  # R, G, B
    image[:, :] = bright

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Повторяем текстуру вне диапазона [0, 1]
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # ВАЖНО: используем текстуру как ЕСТЬ, без умножения на текущий цвет
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGB,
        size,
        size,
        0,
        GL_RGB,
        GL_UNSIGNED_BYTE,
        image
    )

    glBindTexture(GL_TEXTURE_2D, 0)

    return tex_id


def init_terrain() -> None:
    """Вызывается один раз в main.py после создания окна OpenGL."""
    global _ground_texture_id
    _ground_texture_id = _create_checker_texture()


def draw_terrain(yaw_deg: float = 0.0) -> None:
    """
    Рисуем одну текстурированную плоскость вокруг самолёта.

    Геометрия квадрата задаётся в ЛОКАЛЬНЫХ координатах [-HALF_SIZE, HALF_SIZE],
    но:
      - сам квадрат сдвигаем НАЗАД по курсу самолёта (yaw_deg),
      - координаты текстуры считаем из МИРОВЫХ координат:
            x_world = x_local + WORLD_OFFSET_X + offset_x
            z_world = z_local + WORLD_OFFSET_Z + offset_z
    """
    global _ground_texture_id

    if _ground_texture_id is None:
        return

    import math

    wx, wz = get_world_offset()
    size = HALF_SIZE

    # сдвиг земли назад по направлению yaw самолёта
    yaw_rad = math.radians(yaw_deg)
    OFFSET = 40.0  # как у тебя сейчас

    offset_x = -math.sin(yaw_rad) * OFFSET
    offset_z = -math.cos(yaw_rad) * OFFSET

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, _ground_texture_id)

    glPushMatrix()

    # Земля живёт в ЛОКАЛЬНЫХ координатах самолёта, смещаем только назад по yaw
    glTranslatef(offset_x, 0.0, offset_z)

    tex_scale = 20.0  # влияет на "частоту" узора / ощущение скорости

    glBegin(GL_QUADS)

    glNormal3f(0.0, 1.0, 0.0)

    corners = [
        (-size, -size),
        (size, -size),
        (size, size),
        (-size, size),
    ]

    for x_local, z_local in corners:
        xw = x_local + wx + offset_x
        zw = z_local + wz + offset_z

        glTexCoord2f(xw / tex_scale, zw / tex_scale)
        glVertex3f(x_local, 0.0, z_local)

    glEnd()

    glPopMatrix()

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
