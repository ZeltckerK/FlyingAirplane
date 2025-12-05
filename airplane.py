from math import sin, cos, radians

from OpenGL.GL import *

from terrain import terrain_height, move_world


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


def _draw_cuboid_geom(cx, cy, cz, sx, sy, sz):
    """Геометрия параллелепипеда БЕЗ установки цвета."""
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    glScalef(sx, sy, sz)
    _draw_unit_cube()
    glPopMatrix()


def _draw_cuboid_colored(cx, cy, cz, sx, sy, sz, color):
    """Параллелепипед с цветом."""
    glColor3f(*color)
    _draw_cuboid_geom(cx, cy, cz, sx, sy, sz)


class Airplane:
    """Самолёт. Мир двигается под ним."""

    def __init__(self):
        self.x = 0.0
        self.z = 0.0
        self.y = 40.0

        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0

        self.speed = 60.0
        self.min_speed = 10.0
        self.max_speed = 200.0

        # минимальная высота над землёй и максимальная высота полёта
        self.min_alt_above_ground = 20.0
        self.max_altitude = 120.0   # самолёт выше не поднимется (солнце/луна всё равно выше)

        self.climb_factor = 2.0

    def get_position(self):
        return self.x, self.y, self.z

    def change_yaw(self, delta_deg: float):
        self.yaw = (self.yaw + delta_deg) % 360.0

    def change_pitch(self, delta_deg: float):
        self.pitch += delta_deg
        if self.pitch > 45.0:
            self.pitch = 45.0
        if self.pitch < -45.0:
            self.pitch = -45.0

    def change_roll(self, delta_deg: float):
        self.roll += delta_deg
        if self.roll > 60.0:
            self.roll = 60.0
        if self.roll < -60.0:
            self.roll = -60.0

    def change_speed(self, delta: float):
        self.speed += delta
        if self.speed < self.min_speed:
            self.speed = self.min_speed
        if self.speed > self.max_speed:
            self.speed = self.max_speed

    def reset_orientation(self):
        self.pitch = 0.0
        self.roll = 0.0

    def update(self, dt: float):
        if dt <= 0.0:
            return

        rad_yaw = radians(self.yaw)
        rad_pitch = radians(self.pitch)

        forward_x = sin(rad_yaw) * cos(rad_pitch)
        forward_y = sin(rad_pitch)
        forward_z = cos(rad_yaw) * cos(rad_pitch)

        dx = forward_x * self.speed * dt
        dz = forward_z * self.speed * dt

        # нос вверх (pitch > 0) → самолёт набирает высоту
        dy = -forward_y * self.speed * dt * self.climb_factor

        # мир едет под самолётом
        move_world(dx, dz)

        new_y = self.y + dy
        ground_y = terrain_height(self.x, self.z)
        min_y = ground_y + self.min_alt_above_ground

        if new_y < min_y:
            new_y = min_y
        if new_y > self.max_altitude:
            new_y = self.max_altitude

        self.y = new_y

    # --------- геометрия самолёта ---------

    def _draw_model_geom(self, colored: bool):
        """
        Рисуем модель самолёта.
        colored = True  → используем цвета деталей;
        colored = False → цвет задаётся снаружи.
        """
        if colored:
            dc = _draw_cuboid_colored
        else:
            def dc(x, y, z, sx, sy, sz, color):
                _draw_cuboid_geom(x, y, z, sx, sy, sz)

        # фюзеляж
        dc(0.0, 0.0, 0.0, 1.2, 1.2, 7.0, (0.85, 0.86, 0.90))
        # нос
        dc(0.0, 0.0, 4.5, 0.9, 0.9, 1.8, (0.80, 0.82, 0.88))
        # кабина
        dc(0.0, 0.35, 4.4, 0.7, 0.4, 0.8, (0.15, 0.25, 0.45))
        # хвост
        dc(0.0, 0.0, -4.5, 0.9, 0.9, 2.5, (0.83, 0.84, 0.88))

        wing_color = (0.90, 0.92, 0.95)
        dc(-3.8, -0.1, 0.0, 5.5, 0.2, 2.0, wing_color)
        dc(3.8, -0.1, 0.0, 5.5, 0.2, 2.0, wing_color)

        edge_color = (0.75, 0.77, 0.80)
        dc(-6.4, -0.1, 0.0, 0.5, 0.22, 2.1, edge_color)
        dc(6.4, -0.1, 0.0, 0.5, 0.22, 2.1, edge_color)

        dc(0.0, 0.3, -5.2, 3.0, 0.18, 1.4, wing_color)
        dc(0.0, 1.6, -5.0, 0.6, 2.2, 1.2, (0.82, 0.83, 0.88))

        engine_color = (0.45, 0.47, 0.50)
        dc(-2.2, -0.9, 0.4, 0.9, 0.9, 1.8, engine_color)
        dc(2.2, -0.9, 0.4, 0.9, 0.9, 1.8, engine_color)
        intake_color = (0.20, 0.22, 0.25)
        dc(-2.2, -0.9, 1.4, 0.8, 0.8, 0.3, intake_color)
        dc(2.2, -0.9, 1.4, 0.8, 0.8, 0.3, intake_color)

    def draw(self):
        glPushMatrix()

        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.yaw, 0.0, 1.0, 0.0)
        glRotatef(self.pitch, 1.0, 0.0, 0.0)
        glRotatef(self.roll, 0.0, 0.0, 1.0)
        glScalef(2.0, 2.0, 2.0)

        self._draw_model_geom(colored=True)

        glPopMatrix()
