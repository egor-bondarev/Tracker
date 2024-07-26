import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui.design import Ui_MainWindow

class TrackerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

def main():
    app = QApplication(sys.argv)
    window = TrackerApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
