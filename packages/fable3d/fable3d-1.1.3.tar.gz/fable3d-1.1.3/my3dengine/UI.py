import my3dengine as m3d
from OpenGL.GL import *
import numpy as np
from .shader import create_ui_shader
import ctypes

class UI:
    def __init__(self, window_width, window_height):
        self.w = window_width
        self.h = window_height
        self.shader = create_ui_shader()

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # Bufor na max 6 wierzchołków * 2 float (x,y)
        glBufferData(GL_ARRAY_BUFFER, 6 * 2 * 4, None, GL_DYNAMIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.rects = []  # lista prostokątów do narysowania

    def rect(self, x, y, width, height, color):
        # dodaj prostokąt do listy, nie rysuj od razu
        self.rects.append((x, y, width, height, color))

    def draw(self):
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)
        loc_color = glGetUniformLocation(self.shader, "uColor")
        loc_win = glGetUniformLocation(self.shader, "uWindowSize")
        glUniform2f(loc_win, self.w, self.h)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        for x, y, w, h, color in self.rects:
            vertices = np.array([
                x,     y,
                x + w, y,
                x,     y + h,
                x + w, y,
                x + w, y + h,
                x,     y + h,
            ], dtype=np.float32)

            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            glUniform4fv(loc_color, 1, color)
            glDrawArrays(GL_TRIANGLES, 0, 6)

        glBindVertexArray(0)
        glUseProgram(0)

        self.rects.clear()  # po narysowaniu czyścimy listę
