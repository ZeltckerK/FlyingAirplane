# scenery.py
"""Деревья и домики на «бесконечной» земле.

- Объекты храним в МИРОВЫХ координатах (x_world, z_world).
- Самолёт стоит около (0, 0) в локальных координатах, а мир смещается
  на WORLD_OFFSET_X/Z (см. terrain.move_world).
- При отрисовке сдвигаем всю растительность на -WORLD_OFFSET, чтобы
  она визуально ехала под самолётом.
- update_scenery() реализует «беговую дорожку»: объекты, которые
  слишком далеко, перекидываем вперёд по курсу самолёта.
"""

import random
import math

from OpenGL.GL import *

from terrain import terrain_height_world, get_world_offset

TREES: list[tuple[float, float, float]] = []
HOUSES: list[tuple[float, float, float]] = []

SCENERY_RADIUS_MIN = 40.0
SCENERY_RADIUS_MAX = 160.0
FRONT_ARC_DEG = 70.0


def _draw_unit_cube():
    glBegin(GL_QUADS)

    # Front
    glNormal3f(0, 0, 1)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)

    # Back
    glNormal3f(0, 0, -1)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)

    # Left
    glNormal3f(-1, 0, 0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)

    # Right
    glNormal3f(1, 0, 0)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)

    # Top
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)

    # Bottom
    glNormal3f(0, -1, 0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)

    glEnd()


def _draw_cylinder(radius=0.5, height=1.0, slices=12):
    angle_step = 2.0 * math.pi / float(slices)
    glBegin(GL_QUAD_STRIP)
    for i in range(slices + 1):
        a = i * angle_step
        nx = math.cos(a)
        nz = math.sin(a)
        x = radius * nx
        z = radius * nz
        glNormal3f(nx, 0.0, nz)
        glVertex3f(x, 0.0, z)
        glVertex3f(x, height, z)
    glEnd()


def _random_point_in_ring_world(
    cx: float, cz: float,
    r_min: float, r_max: float
) -> tuple[float, float]:
    """Случайная точка в кольце вокруг (cx, cz)."""
    angle = random.uniform(0.0, 2.0 * math.pi)
    r = math.sqrt(random.uniform(r_min * r_min, r_max * r_max))
    x = cx + math.sin(angle) * r
    z = cz + math.cos(angle) * r
    return x, z


def init_scenery():
    """Генерируем начальное наполнение вокруг самолёта."""
    global TREES, HOUSES

    random.seed(1234)
    TREES = []
    HOUSES = []

    plane_x, plane_z = get_world_offset()

    tree_count = 260
    for _ in range(tree_count):
        x, z = _random_point_in_ring_world(
            plane_x, plane_z,
            SCENERY_RADIUS_MIN, SCENERY_RADIUS_MAX
        )
        scale = random.uniform(0.8, 1.6)
        TREES.append((x, z, scale))

    house_count = 12
    for _ in range(house_count):
        x, z = _random_point_in_ring_world(
            plane_x, plane_z,
            SCENERY_RADIUS_MIN + 20.0, SCENERY_RADIUS_MAX
        )
        scale = random.uniform(1.2, 1.8)
        HOUSES.append((x, z, scale))


def _draw_tree(world_x: float, world_z: float, scale: float):
    y = terrain_height_world(world_x, world_z)

    glPushMatrix()
    glTranslatef(world_x, y, world_z)
    glScalef(scale, scale, scale)

    # ствол
    glColor3f(0.38, 0.26, 0.15)
    _draw_cylinder(radius=0.12, height=1.5, slices=10)

    # крона
    glTranslatef(0.0, 1.5, 0.0)
    glColor3f(0.05, 0.45, 0.15)
    glScalef(1.6, 1.6, 1.6)
    _draw_unit_cube()
    glTranslatef(0.0, 0.8, 0.0)
    glScalef(0.7, 0.7, 0.7)
    _draw_unit_cube()

    glPopMatrix()


def _draw_house(world_x: float, world_z: float, scale: float):
    y = terrain_height_world(world_x, world_z)

    glPushMatrix()
    glTranslatef(world_x, y, world_z)
    glScalef(scale, scale, scale)

    glColor3f(0.75, 0.7, 0.65)
    glScalef(4.0, 3.0, 4.0)
    _draw_unit_cube()

    glTranslatef(0.0, 0.7, 0.0)
    glScalef(1.0, 0.6, 1.0)
    glColor3f(0.45, 0.15, 0.12)
    _draw_unit_cube()

    glPopMatrix()


def update_scenery(plane_yaw_deg: float):
    """Обновляем позиции объектов (беговая дорожка)."""
    global TREES, HOUSES

    plane_x, plane_z = get_world_offset()
    yaw_rad = math.radians(plane_yaw_deg)
    front_arc_rad = math.radians(FRONT_ARC_DEG)

    def respawn_in_front() -> tuple[float, float]:
        angle = yaw_rad + random.uniform(-front_arc_rad, front_arc_rad)
        r = random.uniform(SCENERY_RADIUS_MIN, SCENERY_RADIUS_MAX)
        x = plane_x + math.sin(angle) * r
        z = plane_z + math.cos(angle) * r
        return x, z

    # деревья
    new_trees: list[tuple[float, float, float]] = []
    for (tx, tz, scale) in TREES:
        dx = tx - plane_x
        dz = tz - plane_z
        dist2 = dx * dx + dz * dz
        if dist2 > (SCENERY_RADIUS_MAX * SCENERY_RADIUS_MAX):
            nx, nz = respawn_in_front()
            new_trees.append((nx, nz, scale))
        else:
            new_trees.append((tx, tz, scale))
    TREES = new_trees

    # дома
    new_houses: list[tuple[float, float, float]] = []
    for (hx, hz, scale) in HOUSES:
        dx = hx - plane_x
        dz = hz - plane_z
        dist2 = dx * dx + dz * dz
        if dist2 > (SCENERY_RADIUS_MAX * SCENERY_RADIUS_MAX):
            nx, nz = respawn_in_front()
            new_houses.append((nx, nz, scale))
        else:
            new_houses.append((hx, hz, scale))
    HOUSES = new_houses


# --------- тени для деревьев и домов ---------


def _make_shadow_matrix(plane, light_pos):
    """
    Матрица проекции тени на плоскость plane от точечного источника light_pos.
    plane: (A,B,C,D) для Ax+By+Cz+D=0
    light_pos: (Lx, Ly, Lz)
    """
    A, B, C, D = plane
    Lx, Ly, Lz = light_pos
    Lw = 1.0

    dot = A * Lx + B * Ly + C * Lz + D * Lw

    mat = [0.0] * 16

    mat[0] = dot - Lx * A
    mat[4] = -Lx * B
    mat[8] = -Lx * C
    mat[12] = -Lx * D

    mat[1] = -Ly * A
    mat[5] = dot - Ly * B
    mat[9] = -Ly * C
    mat[13] = -Ly * D

    mat[2] = -Lz * A
    mat[6] = -Lz * B
    mat[10] = dot - Lz * C
    mat[14] = -Lz * D

    mat[3] = -Lw * A
    mat[7] = -Lw * B
    mat[11] = -Lw * C
    mat[15] = dot - Lw * D

    return (GLfloat * 16)(*mat)


def _draw_tree_shadow(world_x: float, world_z: float, scale: float):
    """Геометрия дерева без цветов — для тени."""
    y = terrain_height_world(world_x, world_z)

    glPushMatrix()
    glTranslatef(world_x, y, world_z)
    glScalef(scale, scale, scale)

    _draw_cylinder(radius=0.12, height=1.5, slices=10)
    glTranslatef(0.0, 1.5, 0.0)
    glScalef(1.6, 1.6, 1.6)
    _draw_unit_cube()
    glTranslatef(0.0, 0.8, 0.0)
    glScalef(0.7, 0.7, 0.7)
    _draw_unit_cube()

    glPopMatrix()


def _draw_house_shadow(world_x: float, world_z: float, scale: float):
    """Геометрия домика без цветов — для тени."""
    y = terrain_height_world(world_x, world_z)

    glPushMatrix()
    glTranslatef(world_x, y, world_z)
    glScalef(scale, scale, scale)

    glScalef(4.0, 3.0, 4.0)
    _draw_unit_cube()
    glTranslatef(0.0, 0.7, 0.0)
    glScalef(1.0, 0.6, 1.0)
    _draw_unit_cube()

    glPopMatrix()


def draw_scenery_shadows(light_pos: tuple[float, float, float]):
    """
    Рисуем тени деревьев и домиков на землю (y=0) от точечного источника light_pos.
    """
    wx, wz = get_world_offset()

    plane = (0.0, 1.0, 0.0, 0.0)  # y = 0
    shadow_mat = _make_shadow_matrix(plane, light_pos)

    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glPushMatrix()
    glMultMatrixf(shadow_mat)

    # учитываем смещение мира
    glTranslatef(-wx, 0.0, -wz)

    # один общий цвет для всех теней
    glColor4f(0.0, 0.0, 0.0, 0.45)

    for (x, z, scale) in TREES:
        _draw_tree_shadow(x, z, scale)

    for (x, z, scale) in HOUSES:
        _draw_house_shadow(x, z, scale)

    glPopMatrix()

    glDisable(GL_BLEND)
    glPopAttrib()


def draw_scenery():
    """Отрисовываем деревья и домики с учётом WORLD_OFFSET."""
    wx, wz = get_world_offset()

    glPushMatrix()
    glTranslatef(-wx, 0.0, -wz)

    for (x, z, scale) in TREES:
        _draw_tree(x, z, scale)

    for (x, z, scale) in HOUSES:
        _draw_house(x, z, scale)

    glPopMatrix()
