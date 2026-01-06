import numpy as np
from OpenGL.GL import *


class GLMesh:
    def __init__(self, shape, center=False):
        self.shape = shape
        self.name = str(shape.id) + ". " + shape.name
        self.vertices = np.array(shape.positions, dtype=np.float32)
        self.indices = np.array(
            [i - 1 for tri in shape.triangles for i in tri],
            dtype=np.uint32
        )

        self.vertex_count = len(self.vertices)
        self.index_count = len(self.indices)

        self.vbo = None
        self.ebo = None

        if center:
            self.vertices -= self.vertices.mean(axis=0)

        self.display = True

    def upload(self):
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def draw(self):

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glEnableClientState(GL_VERTEX_ARRAY)

        glVertexPointer(3, GL_FLOAT, 0, None)
        if self.display:
            glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def set_display(self, b):
        self.display = b