from PySide6.QtOpenGLWidgets import QOpenGLWidget
from gui.gl_mesh import GLMesh
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective

DEFAULT_VIEW_LINES = True
DEFAULT_VIEW_ROTX = 20
DEFAULT_VIEW_ROTY = -30
DEFAULT_VIEW_ZOOM = 3.0

class GLView(QOpenGLWidget):
    def __init__(self, shapes=[], labels=None):
        super().__init__()
        self.meshes = [GLMesh(s) for s in shapes]

        # camera
        self.labels = labels
        self.reset_camera()
        self.last_pos = None

        self.wireframe = DEFAULT_VIEW_LINES

    def update_shapes(self, shapes):
        self.meshes = [GLMesh(s) for s in shapes]
        for m in self.meshes:
            m.upload()
        self.reset_camera()

    def reset_camera(self):
        self.rot_x = DEFAULT_VIEW_ROTX
        self.rot_y = DEFAULT_VIEW_ROTY
        self.distance = DEFAULT_VIEW_ZOOM
        self.update()

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, w / max(h, 1), 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslatef(0, 0, -self.distance)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)

        glColor3f(1, 1, 1)
        
        if not self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        for m in self.meshes:
            m.draw()


    def mousePressEvent(self, event):
        self.last_pos = event.position()

    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return

        dx = event.position().x() - self.last_pos.x()
        dy = event.position().y() - self.last_pos.y()

        self.rot_x += dy * 0.5
        self.rot_y += dx * 0.5

        self.last_pos = event.position()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.distance -= delta * 0.01
        self.distance = max(0.5, self.distance)
        self.update()