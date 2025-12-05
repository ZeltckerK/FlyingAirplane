# main.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from shader import create_program

from camera import Camera
from terrain import init_terrain, draw_terrain
from scenery import (
    init_scenery,
    draw_scenery,
    update_scenery,
    # draw_scenery_shadows,  # если когда-нибудь вернёшь тени
)
from airplane import Airplane
from lighting import (
    init_lighting,
    setup_lighting,
    draw_sun_or_moon,
    set_time_of_day,
    get_sun_position,
)
from clouds import init_clouds, update_clouds, draw_clouds

window_width = 1280
window_height = 720

camera: Camera | None = None
airplane: Airplane | None = None
_last_time_ms: int = 0
shader_program = None  # ID шейдерной программы (пока не используем в рендере)


# ============================================================
#                   ИНИЦИАЛИЗАЦИЯ OPENGL
# ============================================================
def init_gl():
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    # солнце, луна, свет (пока через фиксированный конвейер)
    init_lighting()


# ============================================================
#                      ОТРИСОВКА КАДРА
# ============================================================
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # обновляем свет под выбранный режим дня
    setup_lighting()

    yaw = 0.0
    if camera is not None and airplane is not None:
        ax, ay, az = airplane.get_position()
        camera.set_target(ax, ay + 15.0, az)
        yaw = airplane.yaw

    # применяем камеру
    if camera is not None:
        camera.apply()

    # === земля ===
    draw_terrain(yaw)

    # === тени для деревьев (если когда-нибудь включишь) ===
    # sun_pos = get_sun_position()
    # draw_scenery_shadows(sun_pos)

    # === деревья и дома ===
    draw_scenery()

    # === облака ===
    draw_clouds()

    # === солнце / луна ===
    draw_sun_or_moon()

    # === самолёт ===
    if airplane is not None:
        airplane.draw()

    glutSwapBuffers()


# ============================================================
#                      ИЗМЕНЕНИЕ РАЗМЕРА
# ============================================================
def reshape(w, h):
    global window_width, window_height
    window_width = max(1, w)
    window_height = max(1, h)

    glViewport(0, 0, window_width, window_height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(window_width) / float(window_height), 0.1, 5000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


# ============================================================
#                УПРАВЛЕНИЕ КАМЕРОЙ (СТРЕЛКИ)
# ============================================================
def special_keys(key, x, y):
    global camera

    if camera is None:
        return

    if key == GLUT_KEY_LEFT:
        camera.orbit(-3.0, 0.0)
    elif key == GLUT_KEY_RIGHT:
        camera.orbit(3.0, 0.0)
    elif key == GLUT_KEY_UP:
        camera.orbit(0.0, 3.0)
    elif key == GLUT_KEY_DOWN:
        camera.orbit(0.0, -3.0)
    elif key == GLUT_KEY_PAGE_UP:
        camera.zoom(-5.0)
    elif key == GLUT_KEY_PAGE_DOWN:
        camera.zoom(5.0)


# ============================================================
#               УПРАВЛЕНИЕ САМОЛЁТОМ (WASD)
# ============================================================
def keyboard(key, x, y):
    global airplane, camera

    # ESC — выход
    if key == b'\x1b':
        glutLeaveMainLoop()
        return

    # время суток
    if key == b'1':
        set_time_of_day(0)  # полдень
        return
    elif key == b'2':
        set_time_of_day(1)  # восход
        return
    elif key == b'3':
        set_time_of_day(2)  # закат
        return
    elif key == b'4':
        set_time_of_day(3)  # ночь
        return

    if airplane is None:
        return

    # === управление самолётом ===
    if key in (b'a', b'A'):
        airplane.change_yaw(3.0)        # влево
    elif key in (b'd', b'D'):
        airplane.change_yaw(-3.0)       # вправо
    elif key in (b'w', b'W'):
        airplane.change_pitch(3.0)      # нос вверх
    elif key in (b's', b'S'):
        airplane.change_pitch(-3.0)     # нос вниз
    elif key in (b'q', b'Q'):
        airplane.change_roll(3.0)
    elif key in (b'e', b'E'):
        airplane.change_roll(-3.0)

    elif key in (b'+', b'='):
        # скорость + (ускоряемся)
        airplane.change_speed(5.0)
        # одновременно приближаем камеру
        if camera is not None:
            camera.zoom(-5.0)

    elif key in (b'-', b'_'):
        # скорость - (замедляемся)
        airplane.change_speed(-5.0)
        # отдаляем камеру
        if camera is not None:
            camera.zoom(5.0)

    elif key == b' ':
        airplane.reset_orientation()


# ============================================================
#                    ОБНОВЛЕНИЕ ЛОГИКИ
# ============================================================
def idle():
    global _last_time_ms, airplane

    now = glutGet(GLUT_ELAPSED_TIME)
    if _last_time_ms == 0:
        dt = 0.0
    else:
        dt = (now - _last_time_ms) / 1000.0
    _last_time_ms = now

    if airplane is not None:
        airplane.update(dt)
        update_scenery(airplane.yaw)
        update_clouds(airplane.yaw)

    glutPostRedisplay()


# ============================================================
#                      СТАРТ ПРОГРАММЫ
# ============================================================
def main():
    global shader_program
    global camera, airplane, _last_time_ms

    # GLUT и окно (контекст OpenGL должен быть создан ДО create_program)
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Kursach: flying airplane with clouds")

    # камера
    camera = Camera(
        target=(0.0, 40.0, 0.0),
        distance=160.0,
        yaw=45.0,
        pitch=30.0
    )

    # самолёт
    airplane = Airplane()
    _last_time_ms = 0

    # OpenGL subsystems
    init_gl()
    init_terrain()
    init_scenery()
    init_clouds()

    # создаём шейдерную программу (пока не используем её в отрисовке,
    # но она есть в проекте для отчёта и дальнейшего развития)
    shader_program = create_program("basic.vert", "basic.frag")

    # callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutSpecialFunc(special_keys)
    glutKeyboardFunc(keyboard)

    glutMainLoop()


if __name__ == "__main__":
    main()
