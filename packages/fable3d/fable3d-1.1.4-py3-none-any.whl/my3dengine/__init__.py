import os
import sys

# Automatyczna ścieżka do SDL2.dll
dll_path = os.path.abspath(os.path.dirname(__file__))
os.environ["PYSDL2_DLL_PATH"] = dll_path

from .key import Key
from .core import Window, Vector3, get_fullscreen, init, normalize
from .camera import Camera
from .mesh import Mesh
from .UI import UI
from .audio import AudioSource, AudioListener, update_audio_system, BackgroundMusic
from .scene import Scene

__all__ = ['Window', 'Camera', 'Mesh', 'Key', 'UI', 'audio', 'scene']