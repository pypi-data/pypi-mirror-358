class Scene:
    def __init__(self):
        self.meshes = []

    def add(self, mesh):
        self.meshes.append(mesh)

    def draw(self, cam_pos, cam_dir, fov_deg=70, view_proj_matrix=None, debug=False):
        for mesh in self.meshes:
            mesh.draw(cam_pos, cam_dir, fov_deg, view_proj_matrix, debug)