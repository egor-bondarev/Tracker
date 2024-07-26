from PyQt5 import QtCore, QtGui, QtWidgets
from controllers.main_controller import MainController
from helpers.controls_state import MainWindowControls
from helpers.settings import Settings

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        settings = Settings()
        controller = MainController(settings.get_url())

        MainWindow.setObjectName("Tracker")
        MainWindow.resize(200, 80)

        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("centralwidget")

        self.line_edit = QtWidgets.QLineEdit(self.central_widget)
        self.line_edit.setGeometry(QtCore.QRect(10, 10, 180, 20))
        self.line_edit.setObjectName("lineEdit")
        self.line_edit.textChanged.connect(
            lambda: controller.check_description_length(self.main_window_controls))
        self.line_edit.textEdited.connect(
            lambda: controller.check_description_length(self.main_window_controls))

        self.start_button = QtWidgets.QPushButton(self.central_widget)
        self.start_button.setEnabled(True)
        self.start_button.setGeometry(QtCore.QRect(60, 40, 30, 30))
        self.start_button.setAutoFillBackground(False)
        self.start_button.setStyleSheet("border: none;")
        self.start_button.setText("")
        self.start_button.setToolTip('Start task')

        start_button_icon = QtGui.QIcon()
        start_button_icon.addPixmap(QtGui.QPixmap("./desktop_gui/assets/play_black.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.start_button.setIcon(start_button_icon)
        self.start_button.setIconSize(QtCore.QSize(24, 24))
        self.start_button.setAutoExclusive(False)
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(lambda: controller.start_task(self.main_window_controls))
        self.start_button.setEnabled(False)

        self.finish_button = QtWidgets.QPushButton(self.central_widget)
        self.finish_button.setEnabled(True)
        self.finish_button.setGeometry(QtCore.QRect(110, 40, 30, 30))
        self.finish_button.setAutoFillBackground(False)
        self.finish_button.setStyleSheet("border: none;")
        self.finish_button.setText("")
        self.finish_button.setToolTip('Stop task')

        finish_button_icon = QtGui.QIcon()
        finish_button_icon.addPixmap(QtGui.QPixmap("./desktop_gui/assets/stop_black.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.finish_button.setIcon(finish_button_icon)
        self.finish_button.setIconSize(QtCore.QSize(24, 24))
        self.finish_button.setAutoExclusive(False)
        self.finish_button.setObjectName("finishButton")
        self.finish_button.clicked.connect(lambda: controller.stop_task(self.main_window_controls))
        self.finish_button.setEnabled(False)

        self.main_window_controls = MainWindowControls(
            btn_start=self.start_button,
            btn_finish=self.finish_button,
            task_desc=self.line_edit)

        MainWindow.setCentralWidget(self.central_widget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Tracker", "Tracker"))
