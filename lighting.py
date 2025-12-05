# lighting.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# 0 - полдень, 1 - восход, 2 - закат, 3 - ночь
time_of_day: int = 0

# Позиция солнца / луны (источник света)
SUN_POS = [0.0, 300.0, 0.0]


def set_time_of_day(idx: int) -> None:
    """
    Установить время суток:
      0 — полдень
      1 — восход
      2 — закат
      3 — ночь
    Любое число за пределами 0..3 будет обрезано.
    """
    global time_of_day
    if idx < 0:
        idx = 0
    if idx > 3:
        idx = 3
    time_of_day = idx


def get_sun_position() -> tuple[float, float, float]:
    """
    Текущая позиция солнца/луны (используем для расчёта теней и отрисовки шара).
    """
    return (float(SUN_POS[0]), float(SUN_POS[1]), float(SUN_POS[2]))


def setup_lighting() -> None:
    """
    Настраиваем GL_LIGHT0 как солнце/луну + фон по текущему времени суток.
    Вызывать минимум один раз при инициализации и затем каждый кадр (на случай,
    если время суток поменялось).
    """
    global time_of_day, SUN_POS

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)

    if time_of_day == 0:
        # Полдень — высокое яркое солнце
        SUN_POS = [0.0, 300.0, 0.0]
        ambient = (0.30, 0.30, 0.35, 1.0)
        diffuse = (1.0, 1.0, 0.95, 1.0)
        specular = (0.8, 0.8, 0.7, 1.0)
        glClearColor(0.47, 0.73, 1.0, 1.0)

    elif time_of_day == 1:
        # Восход — солнце ниже, тёплый свет
        SUN_POS = [-250.0, 180.0, 160.0]
        ambient = (0.25, 0.18, 0.18, 1.0)
        diffuse = (1.0, 0.7, 0.4, 1.0)
        specular = (0.9, 0.8, 0.6, 1.0)
        glClearColor(0.90, 0.60, 0.40, 1.0)

    elif time_of_day == 2:
        # Закат — с другой стороны, тоже низко
        SUN_POS = [250.0, 180.0, -160.0]
        ambient = (0.22, 0.16, 0.20, 1.0)
        diffuse = (1.0, 0.6, 0.5, 1.0)
        specular = (0.9, 0.7, 0.7, 1.0)
        glClearColor(0.85, 0.45, 0.50, 1.0)

    else:
        # Ночь — луна высоко, холодный свет
        SUN_POS = [0.0, 260.0, 0.0]
        ambient = (0.06, 0.06, 0.12, 1.0)
        diffuse = (0.30, 0.30, 0.55, 1.0)
        specular = (0.50, 0.50, 0.80, 1.0)
        glClearColor(0.02, 0.02, 0.07, 1.0)

    light_pos = (SUN_POS[0], SUN_POS[1], SUN_POS[2], 1.0)
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)

    # Глобальный фоновый свет
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.15, 0.15, 0.20, 1.0))


def init_lighting() -> None:
    """
    Инициализация подсистемы освещения.
    Сейчас просто вызывает setup_lighting().
    """
    setup_lighting()


def draw_sun_or_moon() -> None:
    """
    Рисуем светило:
      - днём/закат/восход — жёлтоватое солнце;
      - ночью — белёсая луна.
    """
    global SUN_POS, time_of_day

    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)

    glPushMatrix()
    glTranslatef(SUN_POS[0], SUN_POS[1], SUN_POS[2])

    if time_of_day == 3:
        # ночь — луна
        glColor3f(0.9, 0.9, 1.0)
    else:
        # солнце
        glColor3f(1.0, 0.9, 0.4)

    glutSolidSphere(10.0, 24, 24)
    glPopMatrix()

    glPopAttrib()
