from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QSplitter, QVBoxLayout, QLabel, QStatusBar
from PySide6.QtCore import Qt
from gui.gl_view import GLView
from gui.control_panel import ControlPanel



class StatusBar(QStatusBar):
    def __init__(self, gl_view):
        super().__init__()
        self.gl_view = gl_view

    



class MainWindow(QMainWindow):
    def __init__(self, scene):
        super().__init__()

        self.setWindowTitle("I3D Shapes Tool")

        # status bar
        self.status_bar = self.statusBar()
        zoom = QLabel("Zoom ")
        rotx = QLabel("Rotx ")
        roty = QLabel("Roty ")
        self.status_bar.addPermanentWidget(zoom)
        self.status_bar.addPermanentWidget(rotx)
        self.status_bar.addPermanentWidget(roty)
        labels = [zoom,rotx,roty]

        # menu bar
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        edit_menu = menu_bar.addMenu('&Edit')
        help_menu = menu_bar.addMenu('&Help')

        # ---- OpenGL View ----
        self.gl_view = GLView(scene, labels)

        # ---- Controls Panel ----
        self.controls = ControlPanel(scene, self.gl_view)

        # ---- Splitter ----
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.gl_view)
        splitter.addWidget(self.controls)

        splitter.setStretchFactor(0, 4)  # GL bigger
        splitter.setStretchFactor(1, 1)  # Controls smaller

        self.setCentralWidget(splitter)


def launch_gui(scene=None):
    app = QApplication([])
    win = MainWindow(scene)
    win.resize(1280, 800)
    win.show()
    app.exec()