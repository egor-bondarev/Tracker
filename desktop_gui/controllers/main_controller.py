from helpers.controls_state import MainWindowControls
import datetime

class MainController():

    def start_task(self, main_window_control: MainWindowControls):
        # url = 'http://0.0.0.0:8000/sample/add2db/'
        # data = {"username": self.username_input.text()}  # Replace with actual data as needed
        # response = ApiClient.post(url, data)
        print('Request_1')
        print(datetime.datetime.now())

        self.change_widget_state(main_window_control, True)

    def stop_task(self, main_window_control: MainWindowControls):
        # url = f'http://0.0.0.0:8000/sample/{self.id_input.text()}'
        # response = ApiClient.get(url)
        if main_window_control.btn_start.isEnabled():
            print('Request_1')
        else:
            print('Request_2')
        self.change_widget_state(main_window_control, False)

    def change_widget_state(self, main_window_control: MainWindowControls, task_is_active: bool):
        if task_is_active:
            main_window_control.btn_start.setEnabled(not task_is_active)
            main_window_control.task_desc.setEnabled(not task_is_active)
        else:
            main_window_control.task_desc.setEnabled(not task_is_active)
            main_window_control.task_desc.setFocus()
            main_window_control.task_desc.setText('')
            self.check_description_length(main_window_control)

    def check_description_length(self, main_window_control: MainWindowControls, limit:int = 50):
        if len(main_window_control.task_desc.text()) > 0:
            main_window_control.task_desc.setText(main_window_control.task_desc.text()[:limit])
            main_window_control.btn_start.setEnabled(True)
            main_window_control.btn_finish.setEnabled(True)
        else:
            main_window_control.btn_start.setEnabled(False)
            main_window_control.btn_finish.setEnabled(False)        
