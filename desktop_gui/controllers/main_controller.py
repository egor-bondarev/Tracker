''' Controller for main window. '''

from datetime import datetime
import requests
from helpers.controls_state import MainWindowControls

class MainController():
    ''' Main controller clas.. '''

    def __init__(self, record_service_url, task_id = 0):
        self.url = record_service_url
        self.task_id = task_id

    def start_task(self, main_window_control: MainWindowControls):
        ''' New record. '''

        data = {"description": main_window_control.task_desc.text(),
                "timestamp": f"{datetime.now()}",
                "is_task_finished": "false"
                }
        response = requests.post(url=f'{self.url}/add-record/new/', json=data, timeout=5000)

        self.task_id = response.json()["id"]
        self.change_widget_state(main_window_control, True)

    def stop_task(self, main_window_control: MainWindowControls):
        ''' Finish record. '''

        if main_window_control.btn_start.isEnabled():
            data = {"description": main_window_control.task_desc.text(),
                "timestamp": f"{datetime.now()}",
                "is_task_finished": "true"
                }
            response = requests.post(url=f'{self.url}/add-record/new/', json=data, timeout=5000)
        else:
            data = {"id": self.task_id,
                "timestamp": f"{datetime.now()}"
                }
            response = requests.post(url=f'{self.url}/add-record/finish/', json=data, timeout=5000)
        self.change_widget_state(main_window_control, False)

    def change_widget_state(self, main_window_control: MainWindowControls, task_is_active: bool):
        ''' Change widget state after actions. '''

        if task_is_active:
            main_window_control.btn_start.setEnabled(not task_is_active)
            main_window_control.task_desc.setEnabled(not task_is_active)
        else:
            main_window_control.task_desc.setEnabled(not task_is_active)
            main_window_control.task_desc.setFocus()
            main_window_control.task_desc.setText('')
            self.check_description_length(main_window_control)

    def check_description_length(self, main_window_control: MainWindowControls, limit:int = 50):
        ''' Limit for description length. '''

        if len(main_window_control.task_desc.text()) > 0:
            main_window_control.task_desc.setText(main_window_control.task_desc.text()[:limit])
            main_window_control.btn_start.setEnabled(True)
            main_window_control.btn_finish.setEnabled(True)
        else:
            main_window_control.btn_start.setEnabled(False)
            main_window_control.btn_finish.setEnabled(False)        
