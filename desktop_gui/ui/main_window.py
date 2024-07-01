from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from controllers.main_controller import MainController
from helpers.controls_state import MainWindowControls

class ControlButton(QPushButton):
    def __init__(self, icon_path, tooltip, parent=None):
        super().__init__(parent)

        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setToolTip(tooltip)
        self.setFixedSize(24, 24)
        self.setStyleSheet("QPushButton { border: none; }")

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        controller = MainController()

        self.setWindowTitle('Tracker')
        self.setGeometry(100, 100, 200, 82)

        self.task_desc = QLineEdit(self)
        self.start_button = ControlButton('./desktop_gui/assets/play.png', 'Start task', self)
        self.stop_button = ControlButton('./desktop_gui/assets/stop.png', 'Stop task', self)

        main_window_controls = MainWindowControls(
            btn_start=self.start_button,
            btn_finish=self.stop_button,
            task_desc=self.task_desc)

        self.task_desc.move(10,10)
        self.task_desc.resize(180, 20)
        self.task_desc.textEdited.connect(
            lambda: controller.check_description_length(main_window_controls))

        self.start_button.move(58, 40)
        self.start_button.clicked.connect(lambda: controller.start_task(main_window_controls))
        self.start_button.setEnabled(False)

        self.stop_button.move(100, 40)
        self.stop_button.clicked.connect(lambda: controller.stop_task(main_window_controls))
        self.stop_button.setEnabled(False)

        self.show()
