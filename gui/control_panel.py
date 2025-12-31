from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox

WIREFRAME_DEFAULT = True


class ControlPanel(QWidget):
    def __init__(self, scene, gl_view):
        super().__init__()

        self.scene = scene
        self.gl_view = gl_view

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Controls"))

        self.wireframe = QCheckBox("Wireframe")
        self.wireframe.setChecked(WIREFRAME_DEFAULT)
        self.wireframe.stateChanged.connect(self.toggle_wireframe)
        self.gl_view.wireframe = self.wireframe.isChecked()
        layout.addWidget(self.wireframe)

        reset_btn = QPushButton("Reset View")
        reset_btn.clicked.connect(self.reset_view)
        layout.addWidget(reset_btn)

        layout.addStretch()

    def toggle_wireframe(self, state):
        self.gl_view.wireframe = bool(state)
        self.gl_view.update()

    def reset_view(self):
        self.gl_view.rot_x = 20
        self.gl_view.rot_y = -30
        self.gl_view.distance = 5
        self.gl_view.update()