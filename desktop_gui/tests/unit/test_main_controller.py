
import sys

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from tests.helpers import generator
from tests.unit import asserts

def test_default_state():
    # TODO: move to conftest
    app = QApplication(sys.argv)
    main_window = MainWindow()

    asserts.assert_default_state(main_window.main_window_controls)

def test_start_task():

    # TODO: how to move it to conftest without error:
    # TODO: RuntimeError: wrapped C/C++ object of type QLineEdit has been deleted
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.task_desc.setText(generator.random_data())
    main_window.start_button.click()
    asserts.assert_task_started(main_window.main_window_controls)

def test_start_then_finish_task():
    # TODO: move to conftest
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.task_desc.setText(generator.random_data())
    main_window.start_button.click()
    main_window.stop_button.click()
    asserts.assert_default_state(main_window.main_window_controls)

def test_finish_without_start_task():
    # TODO: move to conftest
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.task_desc.setText(generator.random_data())
    main_window.stop_button.click()
    asserts.assert_default_state(main_window.main_window_controls)

def test_empty_task_desc():
    # TODO: move to conftest
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.task_desc.setText(generator.random_data())
    asserts.assert_ready_to_start_state(main_window.main_window_controls)

    main_window.task_desc.setText('')
    asserts.assert_default_state(main_window.main_window_controls)

def test_one_symbol_task_desc():
    # TODO: move to conftest
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.task_desc.setText(generator.custom_string(1))
    asserts.assert_ready_to_start_state(main_window.main_window_controls)

def test_max_length_task_desc():
    # TODO: move to conftest
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.task_desc.setText(generator.custom_string(50))
    asserts.assert_ready_to_start_state(main_window.main_window_controls)

def test_more_then_max_length_task_desc():
    # TODO: move to conftest
    app = QApplication(sys.argv)
    main_window = MainWindow()

    input_string = generator.custom_string(51)
    main_window.task_desc.setText(input_string)

    asserts.assert_ready_to_start_state(main_window.main_window_controls)
    assert input_string[:50] == main_window.task_desc.text()
