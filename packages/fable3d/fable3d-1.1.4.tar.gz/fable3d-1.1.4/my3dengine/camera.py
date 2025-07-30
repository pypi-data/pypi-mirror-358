from OpenGL.GL import *
from .key import Key
from .mesh import Mesh
import sdl2
import numpy as np
import ctypes

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def look_at(eye, center, up):
    f = normalize(center - eye)
    s = normalize(np.cross(f, up))
    u = np.cross(s, f)

    mat = np.identity(4, dtype=np.float32)
    mat[0, :3] = s
    mat[1, :3] = u
    mat[2, :3] = -f
    mat[:3, 3] = -np.dot(mat[:3, :3], eye)
    return mat

def perspective(fov, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fov) / 2)
    mat = np.zeros((4, 4), dtype=np.float32)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (far + near) / (near - far)
    mat[2, 3] = (2 * far * near) / (near - far)
    mat[3, 2] = -1
    return mat

class Camera:
    def __init__(self, position, target, up, fov, aspect, near=0.1, far=100.0):
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far

        self.move_speed = 5.0
        self.mouse_sensitivity = 0.003

    @property
    def view_matrix(self):
        return look_at(self.position, self.target, self.up)

    @property
    def projection_matrix(self):
        return perspective(self.fov, self.aspect, self.near, self.far)

    @property
    def view_proj_matrix(self):
        return self.projection_matrix @ self.view_matrix

    def move(self, delta):
        self.position += delta
        self.target += delta

    def handle_input(self, dt, window):
        speed = self.move_speed * dt

        forward = normalize(self.target - self.position)
        right = normalize(np.cross(forward, self.up))

        if window.is_key_pressed(Key.W):
            self.move(forward * speed)
        if window.is_key_pressed(Key.S):
            self.move(-forward * speed)
        if window.is_key_pressed(Key.A):
            self.move(-right * speed)
        if window.is_key_pressed(Key.D):
            self.move(right * speed)

        # Dodane ruchy w górę/dół
        if window.is_key_pressed(Key.SPACE):  # Spacja - do góry
            self.move(self.up * speed)
        if window.is_key_pressed(Key.LCTRL):  # Lewy Ctrl - w dół
            self.move(-self.up * speed)

        if getattr(window, "mouse_locked", True):
            xrel = ctypes.c_int()
            yrel = ctypes.c_int()
            sdl2.SDL_GetRelativeMouseState(ctypes.byref(xrel), ctypes.byref(yrel))

            yaw = -xrel.value * self.mouse_sensitivity
            pitch = -yrel.value * self.mouse_sensitivity

            def rotate(v, axis, angle):
                axis = normalize(axis)
                cos_a = np.cos(angle)
                sin_a = np.sin(angle)
                return v * cos_a + np.cross(axis, v) * sin_a + axis * np.dot(axis, v) * (1 - cos_a)

            offset = self.target - self.position
            offset = rotate(offset, self.up, yaw)
            right = normalize(np.cross(offset, self.up))
            offset = rotate(offset, right, pitch)

            self.target = self.position + offset

    def set_uniforms(self, shader_program):
        program_id = shader_program.program  # ID programu
        loc_v = glGetUniformLocation(program_id, "uView")
        loc_p = glGetUniformLocation(program_id, "uProjection")

        glUniformMatrix4fv(loc_v, 1, GL_FALSE, self.view_matrix.T)
        glUniformMatrix4fv(loc_p, 1, GL_FALSE, self.projection_matrix.T)
