# camera.py
from math import sin, cos, radians

from OpenGL.GL import *
from OpenGL.GLU import *


class Camera:
    def __init__(self,
                 target=(0.0, 170.0, 0.0),
                 distance=160.0,
                 yaw=45.0,
                 pitch=45.0):
        """
        Орбитальная камера вокруг точки target.
        yaw   — поворот по горизонту (в градусах)
        pitch — угол по вертикали (в градусах)
        """
        self.target_x, self.target_y, self.target_z = target
        self.distance = distance
        self.yaw = yaw
        self.pitch = pitch

    def apply(self):
        """
        Вычисляет позицию камеры по yaw/pitch/distance и вызывает gluLookAt.
        Вызывать в начале кадра перед рендером сцены.
        """
        rh = radians(self.yaw)
        rv = radians(self.pitch)

        cam_x = self.target_x + self.distance * cos(rv) * sin(rh)
        cam_y = self.target_y + self.distance * sin(rv)
        cam_z = self.target_z + self.distance * cos(rv) * cos(rh)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gluLookAt(cam_x, cam_y, cam_z,
                  self.target_x, self.target_y, self.target_z,
                  0.0, 1.0, 0.0)

    def orbit(self, d_yaw: float, d_pitch: float):
        """Повернуть камеру вокруг цели."""
        self.yaw += d_yaw
        self.pitch += d_pitch
        self.yaw %= 360.0
        self.pitch %= 360.0

    def zoom(self, delta: float):
        """Приблизить/отдалить камеру."""
        self.distance += delta
        if self.distance < 20.0:
            self.distance = 20.0
        if self.distance > 500.0:
            self.distance = 500.0

    def set_target(self, x: float, y: float, z: float):
        """Сменить точку, вокруг которой вращаемся (на будущее под самолёт)."""
        self.target_x = x
        self.target_y = y
        self.target_z = z
