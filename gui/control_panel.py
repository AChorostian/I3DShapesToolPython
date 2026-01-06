from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QScrollArea
)
from PySide6.QtCore import QSize
import functools

class ControlPanel(QWidget):
    def __init__(self, gl_view):
        super().__init__()
        self.gl_view = gl_view

        self.resize(500, 0)

        # --- Scroll area ---
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        # Widget that will actually scroll
        self.scrollContent = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.addStretch()  # keeps items at top
        self.scrollArea.setWidget(self.scrollContent)

        # --- Main layout ---
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel("Shapes"))
        main_layout.addWidget(self.scrollArea)
        self.m_checkboxes = []

    def load_list(self):
        # --- remove old ---
        for i in range(len(self.m_checkboxes)):
            self.scrollLayout.removeWidget(self.m_checkboxes[i])
            self.m_checkboxes[i].deleteLater()
            self.m_checkboxes[i] = None
        self.m_checkboxes = []
        # --- add new ---
        for i in range(len(self.gl_view.meshes)):
            mesh = self.gl_view.meshes[i]

            m_checkbox = QCheckBox(mesh.name)
            m_checkbox.setChecked(True)
            m_checkbox.stateChanged.connect(functools.partial(self.toggle_m_display, mesh))

            self.scrollLayout.insertWidget(self.scrollLayout.count() - 1, m_checkbox)
            self.m_checkboxes.append(m_checkbox)

    def toggle_m_display(self, mesh, state):
        mesh.set_display(state)
        print(f"mesh: {mesh.name} : {"show" if mesh.display else "hide"}")
        self.gl_view.update()



