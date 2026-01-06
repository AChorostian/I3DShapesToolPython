from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtGui import QAction
from gui.gl_view import GLView
from gui.control_panel import ControlPanel
import os, time
import xml.etree.ElementTree as ET
from core.i3d_fileset import I3d_fileset
from gui.gl_view import DEFAULT_VIEW_LINES, DEFAULT_VIEW_ROTX, DEFAULT_VIEW_ROTY, DEFAULT_VIEW_ZOOM

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ---- Main window ----
        self.i3d_fileset = None
        self.gl_view = GLView()
        self.controls = ControlPanel(self.gl_view)
        self.update_window_title()

        # ---- Status Bar ----
        self.status_bar = self.statusBar()
        self.configureStatusBar()

        # ---- Menu Bar ----
        self.menu_bar = self.menuBar()
        self.configureMenuFile()
        # self.configureMenuEdit() # TODO
        self.configureMenuView()
        self.configureMenuHelp()

        # ---- Splitter ----
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.controls)
        splitter.addWidget(self.gl_view)

        splitter.setStretchFactor(0, 1)  # Controls smaller
        splitter.setStretchFactor(1, 3)  # GL bigger

        self.setCentralWidget(splitter)

    def update_window_title(self):
        title = "I3D Shapes Tool Python"

        if self.i3d_fileset is not None:

            if self.i3d_fileset.file_i3d_shapes is not None:
                title += " | " + self.i3d_fileset.file_i3d_shapes

            if self.i3d_fileset.file_i3d is not None:
                title += " | " + self.i3d_fileset.file_i3d

            if self.i3d_fileset.file_xml is not None:
                title += " | " + self.i3d_fileset.file_xml

        self.setWindowTitle(title)

    def load_files(self, files):

        new_i3d_fileset = I3d_fileset()
        
        validation_message = new_i3d_fileset.validate_files(files)
        if validation_message is not None:
            warning = QMessageBox()
            warning.setWindowTitle("File load Error")
            general_text = "\n\nYou can open:\n* single .i3d.shapes file\n* set of .i3d.shapes and .i3d files\n* set of 3 files: .i3d, .i3d.shapes and .xml"
            warning.setText(validation_message + general_text)
            warning.exec()
            return

        self.loading_box = QDialog(self)
        self.loading_box.setWindowTitle("Loading files")

        layout = QVBoxLayout()
        info = QLabel("Loading .i3d.shapes file header")
        layout.addWidget(info)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.loading_box.setLayout(layout)
        self.loading_box.setModal(False)
        self.loading_box.show()
        QApplication.processEvents()  # force initial paint

        os.chdir(new_i3d_fileset.working_directory)

        new_i3d_fileset.load_file_i3d_shapes()
        count = new_i3d_fileset.i3d_shapes_entities_count
        for i in range(count):
            info.setText(f"Loading entity {i+1}/{count} from .i3d.shapes file")
            new_i3d_fileset.load_file_i3d_shapes_part()
            percent = int(i / count * 100)
            self.progress.setValue(percent)
            QApplication.processEvents()

        self.loading_box.close()
        QApplication.processEvents()

        self.gl_view.update_shapes(new_i3d_fileset.i3d_shapes_entities)
        self.controls.load_list()

        self.i3d_fileset = new_i3d_fileset
        self.update_window_title()


    def configureStatusBar(self):
        self.label_zoom = QLabel("Zoom ")
        self.label_rotx = QLabel("Rotx ")
        self.label_roty = QLabel("Roty ")
        self.status_bar.addPermanentWidget(self.label_zoom)
        self.status_bar.addPermanentWidget(self.label_rotx)
        self.status_bar.addPermanentWidget(self.label_roty)

    def configureMenuFile(self):
        menu_file = self.menu_bar.addMenu('&File')

        self.menu_file_open = QAction("Open", self)
        self.menu_file_open.triggered.connect(self.menu_file_open_event)
        menu_file.addAction(self.menu_file_open)

        self.menu_file_export = QAction("Export...", self)
        self.menu_file_export.triggered.connect(self.menu_file_export_event)
        menu_file.addAction(self.menu_file_export)

        # self.action_save = QAction("Save", self) # TODO saving back to .i3d.shapes
        # TODO add 2 export options: actually selected shapes into one mesh or each shape separately

    def menu_file_open_event(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("I3D files (*.i3d *.i3d.shapes *xml)")
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            self.load_files(fileNames)

    def menu_file_export_event(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Export")
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("What do you want to export?"))
        rb1 = QRadioButton("All Shapes")
        rb2 = QRadioButton("Selected Shapes")
        rb1.setChecked(True)
        group = QButtonGroup(dialog)
        group.addButton(rb1)
        group.addButton(rb2)
        layout.addWidget(rb1)
        layout.addWidget(rb2)
        layout.addSpacing(10)

        layout.addWidget(QLabel("into?"))
        rb3 = QRadioButton("One file")
        rb4 = QRadioButton("Separate files")
        rb3.setChecked(True)
        group = QButtonGroup(dialog)
        group.addButton(rb3)
        group.addButton(rb4)
        layout.addWidget(rb3)
        layout.addWidget(rb4)
        layout.addSpacing(15)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            export_mode = "all" if rb1.isChecked() else "selected"
            file_mode = "one" if rb3.isChecked() else "separate"

            start_dir = os.getcwd()
            single_filename = "export"
            
            if (file_mode == "one"):
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Export file",
                    f"{start_dir}/{single_filename}.obj",
                    "Wavefront OBJ (*.obj);;Stereolithography STL (*.stl)"
                )
                if file_path:
                    print(f"Save ONE file to: {file_path} using {export_mode} mode")

            else:
                dir_path = QFileDialog.getExistingDirectory(
                    self,
                    "Select export directory",
                    start_dir
                )
                if dir_path:
                    print(f"Save MULTI files to: {dir_path} using {export_mode} mode")


    def configureMenuView(self):
        menu_view = self.menu_bar.addMenu('&View')

        self.menu_view_lines = QAction("Show lines", self)
        self.menu_view_lines.setCheckable(True)
        self.menu_view_lines.setChecked(DEFAULT_VIEW_LINES)
        self.menu_view_lines.triggered.connect(self.menu_view_lines_event)
        if self.gl_view is not None:
            self.gl_view.wireframe = self.menu_view_lines.isChecked()
        menu_view.addAction(self.menu_view_lines)

        self.menu_view_reset = QAction("Reset", self)
        self.menu_view_reset.triggered.connect(self.menu_view_reset_event)
        menu_view.addAction(self.menu_view_reset)

    def menu_view_lines_event(self):
        if self.gl_view is not None:
            self.gl_view.wireframe = self.menu_view_lines.isChecked()
            self.gl_view.update()

    def menu_view_reset_event(self):
        if self.gl_view is not None:
            self.gl_view.reset_camera()

    def configureMenuHelp(self):
        menu_help = self.menu_bar.addMenu('&Help')
        self.menu_help_about = QAction("About", self)
        menu_help.addAction(self.menu_help_about)



def launch_gui(files=None):
    app = QApplication([])
    win = MainWindow()
    win.resize(1280, 800)
    win.show()
    if files is not None:
        win.load_files(files)
    app.exec()

