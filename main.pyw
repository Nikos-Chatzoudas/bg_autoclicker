import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QLineEdit, QRadioButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import win32gui, win32con, win32api
import time
import keyboard

class ProcessSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.keyboard_listener = KeyboardListener(self)
        self.keyboard_listener.start()

    def initUI(self):
        self.setWindowTitle('Background Autoclicker')
        self.setGeometry(100, 100, 300, 300)

        self.label_process = QLabel('Select a process:', self)
        self.label_process.setAlignment(Qt.AlignCenter)

        self.comboBox = QComboBox(self)
        self.comboBox.setGeometry(50, 50, 200, 30)

        self.refreshButton = QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.populate_processes)

        self.label_interaction = QLabel('Interaction:', self)
        self.label_interaction.setAlignment(Qt.AlignCenter)

        self.coord_label = QLabel('Coordinates (x, y):', self)
        self.coord_label.setAlignment(Qt.AlignCenter)

        self.x_coord = QLineEdit(self)
        self.x_coord.setPlaceholderText('X coordinate')

        self.y_coord = QLineEdit(self)
        self.y_coord.setPlaceholderText('Y coordinate')

        self.left_click_radio = QRadioButton('Left Click', self)
        self.right_click_radio = QRadioButton('Right Click', self)
        self.left_click_radio.setChecked(True)

        self.okButton = QPushButton('Start (F4)', self)
        self.okButton.clicked.connect(self.start_spam_click)

        self.stopButton = QPushButton('Stop (F5)', self)
        self.stopButton.clicked.connect(self.stop_spam_click)
        self.stopButton.setEnabled(False)

        self.delay_label = QLabel('Delay between clicks (ms):', self)
        self.delay_label.setAlignment(Qt.AlignCenter)

        self.delay_input = QLineEdit(self)
        self.delay_input.setPlaceholderText('Enter delay in milliseconds (default is 100ms)')

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.left_click_radio)
        radio_layout.addWidget(self.right_click_radio)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.okButton)
        button_layout.addWidget(self.stopButton)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label_process)
        self.layout.addWidget(self.comboBox)
        self.layout.addWidget(self.refreshButton)
        self.layout.addWidget(self.label_interaction)
        self.layout.addWidget(self.coord_label)
        self.layout.addWidget(self.x_coord)
        self.layout.addWidget(self.y_coord)
        self.layout.addLayout(radio_layout)
        self.layout.addWidget(self.delay_label)
        self.layout.addWidget(self.delay_input)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

        self.populate_processes()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.perform_spam_click)

    def populate_processes(self):
        self.comboBox.clear()
        self.process_handles = {}
        win32gui.EnumWindows(self.enum_windows_callback, None)
        for title, handle in self.process_handles.items():
            self.comboBox.addItem(title, handle)

    def enum_windows_callback(self, hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                self.process_handles[title] = hwnd

    def start_spam_click(self):
        self.okButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        delay = int(self.delay_input.text()) if self.delay_input.text().isdigit() else 100  
        self.timer.start(delay)

    def stop_spam_click(self):
        self.okButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.timer.stop()

    def perform_spam_click(self):
        selected_index = self.comboBox.currentIndex()
        if selected_index != -1:
            title = self.comboBox.currentText()
            hwnd = self.process_handles[title]
            x = int(self.x_coord.text()) if self.x_coord.text().isdigit() else 0
            y = int(self.y_coord.text()) if self.y_coord.text().isdigit() else 0
            click_type = win32con.WM_LBUTTONDOWN if self.left_click_radio.isChecked() else win32con.WM_RBUTTONDOWN
            self.run_interaction(hwnd, x, y, click_type)
            self.run_interaction(hwnd, x, y, click_type + 1)

    def run_interaction(self, hwnd, x, y, click_type):
        lParam = win32api.MAKELONG(x, y)
        
        # Send mouse button down message
        win32api.SendMessage(hwnd, click_type, win32con.MK_LBUTTON if click_type == win32con.WM_LBUTTONDOWN else win32con.MK_RBUTTON, lParam)
        time.sleep(0.01) 
        
        # Send mouse button up message
        win32api.SendMessage(hwnd, click_type + 1, 0, lParam) 

class KeyboardListener(QThread):
    trigger_start = pyqtSignal()
    trigger_stop = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trigger_start.connect(parent.start_spam_click)
        self.trigger_stop.connect(parent.stop_spam_click)

    def run(self):
        keyboard.add_hotkey('f4', self.trigger_start.emit)
        keyboard.add_hotkey('f5', self.trigger_stop.emit)
        keyboard.wait()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    selector = ProcessSelector()
    selector.show()
    sys.exit(app.exec_())
