from OpenGL.GL import *

ui_vertex_src = """
#version 330 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aUV;

out vec2 vUV;

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    vUV = aUV;
}
"""

ui_fragment_src = """
#version 330 core
in vec2 vUV;
uniform sampler2D uTexture;
uniform vec4 uColor;
uniform int useTexture;
out vec4 FragColor;

void main() {
    if (useTexture == 1)
        FragColor = texture(uTexture, vUV) * uColor;
    else
        FragColor = uColor;
}
"""

basic_vertex_src = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
layout(location = 2) in vec2 aUV;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

uniform vec2 uUVTiling;
uniform vec2 uUVOffset;

out vec3 vColor;
out vec2 vUV;

void main() {
    gl_Position = uProjection * uView * uModel * vec4(aPos, 1.0);
    vColor = aColor;
    vUV = aUV * uUVTiling + uUVOffset;
}
"""

basic_fragment_src = """
#version 330 core
in vec3 vColor;
in vec2 vUV;
uniform sampler2D uTexture;
uniform int useTexture;
out vec4 FragColor;

void main() {
    if (useTexture == 1)
        FragColor = texture(uTexture, vUV);
    else
        FragColor = vec4(vColor, 1.0);
}
"""

def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        error = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Shader compile error: {error}")
    return shader

def create_shader(vertex_src, fragment_src):
    vert = compile_shader(vertex_src, GL_VERTEX_SHADER)
    frag = compile_shader(fragment_src, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vert)
    glAttachShader(program, frag)
    glLinkProgram(program)

    if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
        error = glGetProgramInfoLog(program).decode()
        raise RuntimeError(f"Program link error: {error}")

    glDeleteShader(vert)
    glDeleteShader(frag)
    return program


class ShaderProgram:
    def __init__(self, vertex_src, fragment_src):
        self.program = create_shader(vertex_src, fragment_src)
        self.uniform_locations = {}

    def use(self):
        glUseProgram(self.program)

    def get_uniform_location(self, name):
        if name not in self.uniform_locations:
            self.uniform_locations[name] = glGetUniformLocation(self.program, name)
        return self.uniform_locations[name]

    def set_uniform_1i(self, name, value):
        glUniform1i(self.get_uniform_location(name), value)

    def set_uniform_1f(self, name, value):
        glUniform1f(self.get_uniform_location(name), value)

    def set_uniform_vec2(self, name, vec):
        glUniform2fv(self.get_uniform_location(name), 1, vec)

    def set_uniform_vec3(self, name, vec):
        glUniform3fv(self.get_uniform_location(name), 1, vec)

    def set_uniform_mat4(self, name, mat, transpose=False):
        glUniformMatrix4fv(self.get_uniform_location(name), 1, transpose, mat)

def create_ui_shader():
    return ShaderProgram(ui_vertex_src, ui_fragment_src)

def basic_shader():
    return ShaderProgram(basic_vertex_src, basic_fragment_src)
