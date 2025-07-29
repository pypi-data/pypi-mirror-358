from OpenGL.GL import *
import numpy as np
from .shader import basic_shader
from PIL import Image
import ctypes
import math
import time

_default_shader = None
_last_bound_shader = [None]
_last_bound_vao = [None]

def get_default_shader():
    global _default_shader
    if _default_shader is None:
        _default_shader = basic_shader()
        _default_shader.uniforms = {
            "uModel": glGetUniformLocation(_default_shader.program, "uModel"),
            "uUVTiling": glGetUniformLocation(_default_shader.program, "uUVTiling"),
            "uUVOffset": glGetUniformLocation(_default_shader.program, "uUVOffset"),
            "uTexture": glGetUniformLocation(_default_shader.program, "uTexture"),
            "useTexture": glGetUniformLocation(_default_shader.program, "useTexture"),
        }
    return _default_shader

def safe_use_shader(shader):
    if _last_bound_shader[0] != shader:
        glUseProgram(shader.program)
        _last_bound_shader[0] = shader

def safe_bind_vao(vao):
    if _last_bound_vao[0] != vao:
        glBindVertexArray(vao)
        _last_bound_vao[0] = vao

def get_model_matrix(position, scale):
    model = np.identity(4, dtype=np.float32)
    model[0, 0], model[1, 1], model[2, 2] = scale
    model[:3, 3] = position  # poprawione na kolumnę 3
    return model

class Mesh:
    def __init__(self, vertices, shader=None):
        self.shader = shader or get_default_shader()
        if not hasattr(self.shader, "uniforms"):
            self.shader.uniforms = {
                "uModel": glGetUniformLocation(self.shader.program, "uModel"),
                "uUVTiling": glGetUniformLocation(self.shader.program, "uUVTiling"),
                "uUVOffset": glGetUniformLocation(self.shader.program, "uUVOffset"),
                "uTexture": glGetUniformLocation(self.shader.program, "uTexture"),
                "useTexture": glGetUniformLocation(self.shader.program, "useTexture"),
            }

        self.vertex_count = len(vertices) // 8
        self.position = np.zeros(3, dtype=np.float32)
        self.scale = np.ones(3, dtype=np.float32)
        self.texture = None
        self.uv_tiling = np.ones(2, dtype=np.float32)
        self.uv_offset = np.zeros(2, dtype=np.float32)

        self._last_position = np.array([np.nan, np.nan, np.nan], dtype=np.float32)
        self._last_scale = np.array([np.nan, np.nan, np.nan], dtype=np.float32)

        self._uniforms_uploaded_once = False

        self._init_buffers(vertices)

    def copy(self):
        new = Mesh.__new__(Mesh)
        new.__dict__ = self.__dict__.copy()
        new.position = self.position.copy()
        new.scale = self.scale.copy()
        new._last_position = np.array([np.nan, np.nan, np.nan], dtype=np.float32)
        new._last_scale = np.array([np.nan, np.nan, np.nan], dtype=np.float32)

        self._uniforms_uploaded_once = False
        return new

    def is_in_fov(self, cam_pos, cam_dir, fov_deg):
        half_fov_rad = math.radians(fov_deg * 1.2)
        cam_dir = cam_dir / np.linalg.norm(cam_dir)
        to_obj = self.position - cam_pos
        dist = np.linalg.norm(to_obj)
        if dist == 0:
            return True
        to_obj_dir = to_obj / dist
        angle = math.acos(np.clip(np.dot(cam_dir, to_obj_dir), -1, 1))
        return angle <= half_fov_rad

    def _init_buffers(self, vertices):
        data = np.array(vertices, dtype=np.float32)
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

        stride = 8 * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def set_uv_transform(self, tiling=(1.0, 1.0), offset=(0.0, 0.0)):
        self.uv_tiling[:] = tiling
        self.uv_offset[:] = offset

    def upload_uniforms(self):
        if (not self._uniforms_uploaded_once or
                not (np.array_equal(self.position, self._last_position) and
                     np.array_equal(self.scale, self._last_scale))):
            model = get_model_matrix(self.position, self.scale)
            uniforms = self.shader.uniforms
            glUniformMatrix4fv(uniforms["uModel"], 1, GL_FALSE, model.T)
            glUniform2fv(uniforms["uUVTiling"], 1, self.uv_tiling)
            glUniform2fv(uniforms["uUVOffset"], 1, self.uv_offset)

            self._last_position = self.position.copy()
            self._last_scale = self.scale.copy()
            self._uniforms_uploaded_once = True

    def draw(self, cam_pos=None, cam_dir=None, fov_deg=70, view_proj_matrix=None, debug=False):
        if debug:
            print(f"Draw called for mesh at {self.position}")

        if cam_pos is not None:
            dist = np.linalg.norm(self.position - cam_pos)
            if dist > 600:  # ustaw granicę zależnie od sceny
                return

        # if cam_pos is not None and cam_dir is not None:
            # if not self.is_in_fov(cam_pos, cam_dir, fov_deg + 50):  # +10° tolerancji
                # return

        safe_use_shader(self.shader)
        self.upload_uniforms()

        uniforms = self.shader.uniforms
        if self.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glUniform1i(uniforms["uTexture"], 0)
            glUniform1i(uniforms["useTexture"], 1)
        else:
            glUniform1i(uniforms["useTexture"], 0)

        safe_bind_vao(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

        if debug:
            print(f"[DEBUG] Mesh at {self.position} został narysowany.")

    def set_texture(self, path):
        image = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')
        img_data = np.array(image, dtype=np.uint8)

        if self.texture:
            glDeleteTextures(1, [self.texture])

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def set_position(self, x, y, z):
        self.position[:] = [x, y, z]

    def set_scale(self, x, y, z):
        self.scale[:] = [x, y, z]

    def scale_uniform(self, factor):
        self.scale[:] = factor

    def destroy(self):
        if hasattr(self, 'vao') and glDeleteVertexArrays:
            glDeleteVertexArrays(1, [self.vao])
            glDeleteBuffers(1, [self.vbo])
        if self.texture and glDeleteTextures:
            glDeleteTextures(1, [self.texture])


    # =========================
    # ======== models =========
    # =========================

    @staticmethod
    def from_obj(path, color=(1, 1, 1)):
        positions = []
        texcoords = []
        faces = []

        with open(path, "r") as f:
            for line in f:
                if line.startswith("v "):  # vertex position
                    parts = line.strip().split()
                    positions.append(tuple(map(float, parts[1:4])))
                elif line.startswith("vt "):  # texture coordinate
                    parts = line.strip().split()
                    texcoords.append(tuple(map(float, parts[1:3])))
                elif line.startswith("f "):  # face
                    parts = line.strip().split()[1:]
                    face = []
                    for p in parts:
                        vals = p.split('/')
                        vi = int(vals[0]) - 1
                        ti = int(vals[1]) - 1 if len(vals) > 1 and vals[1] else 0
                        face.append((vi, ti))
                    faces.append(face)

        verts = []
        for face in faces:
            if len(face) >= 3:
                for i in range(1, len(face) - 1):
                    for idx in [0, i, i + 1]:
                        vi, ti = face[idx]
                        pos = positions[vi]
                        uv = texcoords[ti] if texcoords else (0.0, 0.0)
                        verts.extend([*pos, *color, *uv])

        return Mesh(verts, basic_shader())

    @staticmethod
    def cube(color=(1, 1, 1)):
        # Pozycje wierzchołków sześcianu
        p = [(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),  # front
             (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)]  # back

        # UV mapowanie na jedną ścianę (powtarzane dla każdej)
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)]

        # Indeksy do rysowania ścian (każda ściana: 2 trójkąty)
        faces = [
            (0, 1, 2, 3),  # front
            (5, 4, 7, 6),  # back
            (4, 0, 3, 7),  # left
            (1, 5, 6, 2),  # right
            (3, 2, 6, 7),  # top
            (4, 5, 1, 0)  # bottom
        ]

        verts = []
        for face in faces:
            idx = [face[0], face[1], face[2], face[0], face[2], face[3]]
            uv_idx = [0, 1, 2, 0, 2, 3]
            for i in range(6):
                pos = p[idx[i]]
                tex = uv[uv_idx[i]]
                verts.extend([*pos, *color, *tex])

        return Mesh(verts, basic_shader())

    @staticmethod
    def sphere(radius=0.5, lat_segments=16, lon_segments=16, color=(1, 1, 1)):
        verts = []
        for i in range(lat_segments):
            theta1 = np.pi * (i / lat_segments - 0.5)
            theta2 = np.pi * ((i + 1) / lat_segments - 0.5)
            for j in range(lon_segments):
                phi1 = 2 * np.pi * (j / lon_segments)
                phi2 = 2 * np.pi * ((j + 1) / lon_segments)

                def get_pos(theta, phi):
                    return (
                        radius * np.cos(theta) * np.cos(phi),
                        radius * np.sin(theta),
                        radius * np.cos(theta) * np.sin(phi)
                    )

                # Wierzchołki
                p1 = get_pos(theta1, phi1)
                p2 = get_pos(theta2, phi1)
                p3 = get_pos(theta2, phi2)
                p4 = get_pos(theta1, phi2)

                # UV mapping (prosty sferyczny)
                uv1 = (j / lon_segments, i / lat_segments)
                uv2 = (j / lon_segments, (i + 1) / lat_segments)
                uv3 = ((j + 1) / lon_segments, (i + 1) / lat_segments)
                uv4 = ((j + 1) / lon_segments, i / lat_segments)

                # Trójkąty
                for vtx, uv in zip([p1, p2, p3], [uv1, uv2, uv3]):
                    verts.extend([*vtx, *color, *uv])
                for vtx, uv in zip([p1, p3, p4], [uv1, uv3, uv4]):
                    verts.extend([*vtx, *color, *uv])
        return Mesh(verts, basic_shader())

    @staticmethod
    def capsule(radius=0.25, height=1.0, segments=16, color=(1, 1, 1)):
        verts = []
        half = height / 2

        # === Cylinder środkowy ===
        for j in range(segments):
            theta1 = 2 * np.pi * (j / segments)
            theta2 = 2 * np.pi * ((j + 1) / segments)

            x1, z1 = np.cos(theta1), np.sin(theta1)
            x2, z2 = np.cos(theta2), np.sin(theta2)

            p1 = (radius * x1, -half, radius * z1)
            p2 = (radius * x1, half, radius * z1)
            p3 = (radius * x2, half, radius * z2)
            p4 = (radius * x2, -half, radius * z2)

            uv = [(j / segments, 0.0), (j / segments, 0.5), ((j + 1) / segments, 0.5), ((j + 1) / segments, 0.0)]
            for vtx, tex in zip([p1, p2, p3], [uv[0], uv[1], uv[2]]):
                verts.extend([*vtx, *color, *tex])
            for vtx, tex in zip([p1, p3, p4], [uv[0], uv[2], uv[3]]):
                verts.extend([*vtx, *color, *tex])

        # === Półsfera górna ===
        for i in range(segments // 2):
            theta1 = (np.pi / 2) * (i / (segments // 2))
            theta2 = (np.pi / 2) * ((i + 1) / (segments // 2))
            for j in range(segments):
                phi1 = 2 * np.pi * (j / segments)
                phi2 = 2 * np.pi * ((j + 1) / segments)

                def pos(theta, phi):
                    return (
                        radius * np.cos(theta) * np.cos(phi),
                        radius * np.sin(theta) + half,
                        radius * np.cos(theta) * np.sin(phi)
                    )

                p1 = pos(theta1, phi1)
                p2 = pos(theta2, phi1)
                p3 = pos(theta2, phi2)
                p4 = pos(theta1, phi2)

                uv1 = (j / segments, 0.5 + (i / (segments * 2)))
                uv2 = (j / segments, 0.5 + ((i + 1) / (segments * 2)))
                uv3 = ((j + 1) / segments, 0.5 + ((i + 1) / (segments * 2)))
                uv4 = ((j + 1) / segments, 0.5 + (i / (segments * 2)))

                for vtx, tex in zip([p1, p2, p3], [uv1, uv2, uv3]):
                    verts.extend([*vtx, *color, *tex])
                for vtx, tex in zip([p1, p3, p4], [uv1, uv3, uv4]):
                    verts.extend([*vtx, *color, *tex])

        # === Półsfera dolna ===
        for i in range(segments // 2):
            theta1 = (np.pi / 2) * (i / (segments // 2))
            theta2 = (np.pi / 2) * ((i + 1) / (segments // 2))
            for j in range(segments):
                phi1 = 2 * np.pi * (j / segments)
                phi2 = 2 * np.pi * ((j + 1) / segments)

                def pos(theta, phi):
                    return (
                        radius * np.cos(theta) * np.cos(phi),
                        -radius * np.sin(theta) - half,
                        radius * np.cos(theta) * np.sin(phi)
                    )

                p1 = pos(theta1, phi1)
                p2 = pos(theta2, phi1)
                p3 = pos(theta2, phi2)
                p4 = pos(theta1, phi2)

                uv1 = (j / segments, 0.5 - (i / (segments * 2)))
                uv2 = (j / segments, 0.5 - ((i + 1) / (segments * 2)))
                uv3 = ((j + 1) / segments, 0.5 - ((i + 1) / (segments * 2)))
                uv4 = ((j + 1) / segments, 0.5 - (i / (segments * 2)))

                # UWAGA: zamieniona kolejność rysowania — PRAWIDŁOWY winding
                for vtx, tex in zip([p1, p3, p2], [uv1, uv3, uv2]):
                    verts.extend([*vtx, *color, *tex])
                for vtx, tex in zip([p1, p4, p3], [uv1, uv4, uv3]):
                    verts.extend([*vtx, *color, *tex])

        return Mesh(verts, basic_shader())

    @staticmethod
    def plane(size=1.0, color=(1, 1, 1)):
        hs = size / 2
        positions = [(-hs, 0, -hs), (hs, 0, -hs), (hs, 0, hs), (-hs, 0, hs)]
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        indices = [(0, 1, 2), (0, 2, 3)]  # front
        back_indices = [(2, 1, 0), (3, 2, 0)]  # back side (odwrócone)

        verts = []
        for face in indices + back_indices:
            for idx in face:
                verts.extend([*positions[idx], *color, *uvs[idx]])
        return Mesh(verts, basic_shader())

    @staticmethod
    def water(
            size=10.0,
            resolution=64,
            wave_speed=0.03,
            wave_height=0.1,
            wave_scale=(0.3, 0.4),
            second_wave=True,
            color=(0.2, 0.5, 1.0),
            backface=True
    ):
        half = size / 2
        step = size / resolution
        verts = []

        for z in range(resolution):
            for x in range(resolution):
                x0 = -half + x * step
                x1 = x0 + step
                z0 = -half + z * step
                z1 = z0 + step

                u0, u1 = x / resolution, (x + 1) / resolution
                v0, v1 = z / resolution, (z + 1) / resolution

                pos = [(x0, 0.0, z0), (x1, 0.0, z0), (x1, 0.0, z1), (x0, 0.0, z1)]
                uv = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]

                # Indeksy dla frontu i ewentualnie backface
                indices = [(0, 1, 2), (0, 2, 3)]
                if backface:
                    indices += [(2, 1, 0), (3, 2, 0)]

                for a, b, c in indices:
                    for i in [a, b, c]:
                        verts.extend([*pos[i], *color, *uv[i]])

        mesh = Mesh(verts, basic_shader())
        mesh._water_size = size
        mesh._water_res = resolution
        mesh._water_time = 0.0
        mesh._wave_speed = wave_speed
        mesh._wave_height = wave_height
        mesh._wave_scale = wave_scale
        mesh._second_wave = second_wave
        mesh._water_verts = np.array(verts, dtype=np.float32).reshape(-1, 8)

        # Wysokości bazowe (y)
        mesh._water_initial_y = mesh._water_verts[:, 1].copy()

        # Dynamiczny buffer
        glBindBuffer(GL_ARRAY_BUFFER, mesh.vbo)
        glBufferData(GL_ARRAY_BUFFER, mesh._water_verts.nbytes, mesh._water_verts.flatten(), GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        def update_water():
            mesh._water_time += mesh._wave_speed
            verts = mesh._water_verts
            X = verts[:, 0]
            Z = verts[:, 2]

            # Fale
            verts[:, 1] = (
                                  np.sin(X * mesh._wave_scale[0] + mesh._water_time) +
                                  (np.cos(Z * mesh._wave_scale[1] + mesh._water_time) if mesh._second_wave else 0.0)
                          ) * (mesh._wave_height * 0.5)

            glBindBuffer(GL_ARRAY_BUFFER, mesh.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, verts.nbytes, verts.flatten())
            glBindBuffer(GL_ARRAY_BUFFER, 0)

        mesh.update_water = update_water
        return mesh

    def update_water(self):
        if not hasattr(self, '_original_vertices'):
            return

        verts = self._original_vertices.copy()
        t = time.time() - self._start_time

        for i in range(0, len(verts), 8):
            x = verts[i]
            z = verts[i + 2]
            verts[i + 1] = math.sin(x * 0.5 + t) * 0.2 + math.cos(z * 0.5 + t) * 0.2

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, verts.nbytes, verts)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
