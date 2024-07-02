
from helpers.controls_state import MainWindowControls

def assert_task_started(main_window_controls: MainWindowControls):
    assert not main_window_controls.btn_start.isEnabled()
    assert not main_window_controls.task_desc.isEnabled()
    assert main_window_controls.btn_finish.isEnabled()
    assert main_window_controls.task_desc.text() != ''

def assert_default_state(main_window_controls: MainWindowControls):
    assert not main_window_controls.btn_start.isEnabled()
    assert main_window_controls.task_desc.isEnabled()
    assert not main_window_controls.btn_finish.isEnabled()
    assert main_window_controls.task_desc.text() == ''

def assert_ready_to_start_state(main_window_controls: MainWindowControls):
    assert main_window_controls.btn_start.isEnabled()
    assert main_window_controls.task_desc.isEnabled()
    assert main_window_controls.btn_finish.isEnabled()
    assert main_window_controls.task_desc.text() != ''
