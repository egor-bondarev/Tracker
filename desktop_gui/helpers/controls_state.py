from dataclasses import dataclass
from PyQt5.QtWidgets import QPushButton, QLineEdit

@dataclass
class MainWindowControls:
    btn_start: QPushButton
    btn_finish: QPushButton
    task_desc: QLineEdit
