import sdl2
import sdl2.ext
from OpenGL.GL import *
import time
from sdl2 import SDL_GL_SetSwapInterval
from .key import Key
import numpy as np
import OpenGL.GL

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def to_list(self):
        return [self.x, self.y, self.z]

    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"

def debug_init():
    @staticmethod
    def init():
        # Włącz przezroczystość (alpha blending)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Włącz test głębokości (żeby obiekty były dobrze rysowane w 3D)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)  # Domyślnie można zostawić, ale warto jawnie ustawić

        # Włącz odrzucanie tylnych ścianek (culling)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)  # Możesz też użyć GL_FRONT, jeśli robisz np. odbicia
        glFrontFace(GL_CCW)  # Counter-clockwise - domyślnie standard OpenGL

        # Głębia na 1.0 - domyślnie, ale dobrze ustawić jawnie
        glClearDepth(1.0)

        # V-Sync
        SDL_GL_SetSwapInterval(1)  # 1 = włączony VSync, 0 = wyłączony (lepszy FPS, może tearing)

        # Gładkie linie i wielokąty (opcjonalne, zależnie od potrzeb)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        # Antyaliasing multisampling (jeśli masz MSAA ustawione w SDL_GL)
        glEnable(GL_MULTISAMPLE)

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

@staticmethod
def init():
    glEnable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_CULL_FACE)
    glFrontFace(GL_CCW)
    glClearDepth(1.0)
    SDL_GL_SetSwapInterval(1)

@staticmethod
def get_fullscreen():
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)  # upewniamy się że SDL wystartował
    mode = sdl2.SDL_DisplayMode()
    if sdl2.SDL_GetDesktopDisplayMode(0, mode) != 0:
        raise RuntimeError("Nie udało się pobrać trybu ekranu")
    return mode.w, mode.h

class Window:
    def __init__(self, title, width, height):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.width = width
        self.height = height
        self.window = sdl2.SDL_CreateWindow(
            title.encode("utf-8"),
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            width,
            height,
            sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN,
        )
        self.context = sdl2.SDL_GL_CreateContext(self.window)

        glViewport(0, 0, width, height)

        self.mouse_locked = True
        sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_TRUE)
        sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)

    def is_key_pressed(self, key: Key) -> bool:
        keys = sdl2.SDL_GetKeyboardState(None)
        return keys[key] != 0

    def toggle_mouse_lock(self):
        self.mouse_locked = not self.mouse_locked
        if self.mouse_locked:
            sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_TRUE)
            sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)
        else:
            sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_FALSE)
            sdl2.SDL_ShowCursor(sdl2.SDL_ENABLE)

    def prepare_frame(self):
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

    def run(self, update_callback=None, cameras=[]):
        last_time = time.time()
        event = sdl2.SDL_Event()
        running = True
        while running:
            while sdl2.SDL_PollEvent(event):
                if event.type == sdl2.SDL_QUIT:
                    running = False
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.scancode == sdl2.SDL_SCANCODE_ESCAPE:
                        self.toggle_mouse_lock()

            now = time.time()
            dt = now - last_time
            last_time = now

            self.prepare_frame()
            if update_callback:
                update_callback(dt, self)

            sdl2.SDL_GL_SwapWindow(self.window)
            glFlush()

        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()
