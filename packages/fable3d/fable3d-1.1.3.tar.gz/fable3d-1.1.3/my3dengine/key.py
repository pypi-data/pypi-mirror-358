# my3dengine/key.py
import sdl2
from enum import IntEnum

class Key(IntEnum):
    # Strzałki
    UP = sdl2.SDL_SCANCODE_UP
    DOWN = sdl2.SDL_SCANCODE_DOWN
    LEFT = sdl2.SDL_SCANCODE_LEFT
    RIGHT = sdl2.SDL_SCANCODE_RIGHT

    # Klawisze literowe
    A = sdl2.SDL_SCANCODE_A
    B = sdl2.SDL_SCANCODE_B
    C = sdl2.SDL_SCANCODE_C
    D = sdl2.SDL_SCANCODE_D
    E = sdl2.SDL_SCANCODE_E
    F = sdl2.SDL_SCANCODE_F
    G = sdl2.SDL_SCANCODE_G
    H = sdl2.SDL_SCANCODE_H
    I = sdl2.SDL_SCANCODE_I
    J = sdl2.SDL_SCANCODE_J
    K = sdl2.SDL_SCANCODE_K
    L = sdl2.SDL_SCANCODE_L
    M = sdl2.SDL_SCANCODE_M
    N = sdl2.SDL_SCANCODE_N
    O = sdl2.SDL_SCANCODE_O
    P = sdl2.SDL_SCANCODE_P
    Q = sdl2.SDL_SCANCODE_Q
    R = sdl2.SDL_SCANCODE_R
    S = sdl2.SDL_SCANCODE_S
    T = sdl2.SDL_SCANCODE_T
    U = sdl2.SDL_SCANCODE_U
    V = sdl2.SDL_SCANCODE_V
    W = sdl2.SDL_SCANCODE_W
    X = sdl2.SDL_SCANCODE_X
    Y = sdl2.SDL_SCANCODE_Y
    Z = sdl2.SDL_SCANCODE_Z

    # Klawisze numeryczne
    NUMBER_0 = sdl2.SDL_SCANCODE_0
    NUMBER_1 = sdl2.SDL_SCANCODE_1
    NUMBER_2 = sdl2.SDL_SCANCODE_2
    NUMBER_3 = sdl2.SDL_SCANCODE_3
    NUMBER_4 = sdl2.SDL_SCANCODE_4
    NUMBER_5 = sdl2.SDL_SCANCODE_5
    NUMBER_6 = sdl2.SDL_SCANCODE_6
    NUMBER_7 = sdl2.SDL_SCANCODE_7
    NUMBER_8 = sdl2.SDL_SCANCODE_8
    NUMBER_9 = sdl2.SDL_SCANCODE_9

    # Klawisze funkcyjne
    F1 = sdl2.SDL_SCANCODE_F1
    F2 = sdl2.SDL_SCANCODE_F2
    F3 = sdl2.SDL_SCANCODE_F3
    F4 = sdl2.SDL_SCANCODE_F4
    F5 = sdl2.SDL_SCANCODE_F5
    F6 = sdl2.SDL_SCANCODE_F6
    F7 = sdl2.SDL_SCANCODE_F7
    F8 = sdl2.SDL_SCANCODE_F8
    F9 = sdl2.SDL_SCANCODE_F9
    F10 = sdl2.SDL_SCANCODE_F10
    F11 = sdl2.SDL_SCANCODE_F11
    F12 = sdl2.SDL_SCANCODE_F12

    # Inne ważne
    SPACE = sdl2.SDL_SCANCODE_SPACE
    ESCAPE = sdl2.SDL_SCANCODE_ESCAPE
    RETURN = sdl2.SDL_SCANCODE_RETURN
    TAB = sdl2.SDL_SCANCODE_TAB
    LSHIFT = sdl2.SDL_SCANCODE_LSHIFT
    RSHIFT = sdl2.SDL_SCANCODE_RSHIFT
    LCTRL = sdl2.SDL_SCANCODE_LCTRL
    RCTRL = sdl2.SDL_SCANCODE_RCTRL
    ALT = sdl2.SDL_SCANCODE_LALT
    BACKSPACE = sdl2.SDL_SCANCODE_BACKSPACE
    CAPSLOCK = sdl2.SDL_SCANCODE_CAPSLOCK