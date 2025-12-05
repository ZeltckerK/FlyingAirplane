# shader.py
from OpenGL.GL import *

def load_shader(path):
    with open(path, "r") as f:
        return f.read()

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not status:
        raise RuntimeError(glGetShaderInfoLog(shader).decode())

    return shader

def create_program(vertex_path, fragment_path):
    vert_src = load_shader(vertex_path)
    frag_src = load_shader(fragment_path)

    vert = compile_shader(vert_src, GL_VERTEX_SHADER)
    frag = compile_shader(frag_src, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vert)
    glAttachShader(program, frag)
    glLinkProgram(program)

    status = glGetProgramiv(program, GL_LINK_STATUS)
    if not status:
        raise RuntimeError(glGetProgramInfoLog(program).decode())

    glDeleteShader(vert)
    glDeleteShader(frag)

    return program
