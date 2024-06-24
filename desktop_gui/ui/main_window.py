from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit
from api.requests import ApiClient
#from PyQt6 import QtWidgets

class MainWindow(QMainWindow):

        
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Example')
        self.setGeometry(100, 100, 300, 100)
        #self.setBaseSize(100, 200)

        #self.central_widget = QWidget()
        #self.setCentralWidget(self.central_widget)
        #self.layout = QVBoxLayout(self.central_widget)
        
        self.username_label = QLabel("username:", self)
        self.username_label.move(5,8)
        self.username_label.resize(70,10)
        #self.layout.addWidget(self.url_label)
        
        self.username_input = QLineEdit(self)
        self.username_input.move(80,5)
        self.username_input.resize(120, 20)
        
        self.username_input.text()
        #self.layout.addWidget(self.url_input)
        
        self.post_button = QPushButton('POST', self)
        self.post_button.move(200, 2)
        self.post_button.clicked.connect(self.send_post_request)
        #self.layout.addWidget(self.get_button)
        
        self.id_input = QLineEdit(self)
        self.id_input.move(5,40)
        self.id_input.resize(70, 20)
        
        
        
        
        self.post_button = QPushButton('GET', self)
        self.post_button.move(80, 40)
        self.post_button.clicked.connect(self.send_get_request)
        
        self.show_rewult = QTextEdit(self)
        self.show_rewult.move(200, 40)
        self.show_rewult.resize(120, 200)
        
        self.show()
        
    def send_post_request(self):
        url = 'http://0.0.0.0:8000/sample/add2db/'
        data = {"username": self.username_input.text()}  # Replace with actual data as needed
        response = ApiClient.post(url, data)
        print(response)
        #self.response_display.setPlainText(response)
    
    def send_get_request(self):
        url = f'http://0.0.0.0:8000/sample/{self.id_input.text()}'
        response = ApiClient.get(url)
        print(response)
        self.show_rewult.setText(response)
