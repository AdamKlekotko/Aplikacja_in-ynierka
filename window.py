from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from Impedance_App.connection_port import *
from serial import SerialException
import serial.tools.list_ports
import re
sys.path.append('./')


sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
        # Print the error and traceback
    print(exctype, value, traceback)
        # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

    # Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

serial._SerialException = serial.SerialException

def my_serial_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    serial._SerialException(exctype, value, traceback)
    serial.exit(1)

serial.SerialException = my_serial_hook


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Impedance control'
        self.left = 100
        self.top = 100
        self.width = 200
        self.height = 120
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createGridLayout()
        self.setWindowIcon(QIcon('imp_logo.png'))
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)
        self.show()

    def createGridLayout(self):

        self.horizontalGroupBox = QGroupBox("Measurement configuration")

        self.button = QPushButton('Select data directory', self)
        self.button.setToolTip('This is an directory selector button')
        self.button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.button.clicked.connect(self.pick_dir)

        self.start_button = QPushButton('Start measure', self)
        self.start_button.setToolTip('This is an measure button')
        self.start_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.start_button.clicked.connect(self.on_click)

        self.times_text = QLabel('Times:',self)
        var_times='0'
        self.onlyInt=QIntValidator()
        self.times_value=QLineEdit(var_times,parent=self)
        self.times_value.setValidator(self.onlyInt)

        self.start_freq_text = QLabel('Start frequency [Hz]:', self)
        var_start_freq = '0'
        self.start_freq_value = QLineEdit(var_start_freq, parent=self)
        self.start_freq_value.setValidator(self.onlyInt)

        self.end_freq_text = QLabel('End frequency [Hz]:', self)
        var_end_freq = '0'
        self.end_freq_value = QLineEdit(var_end_freq, parent=self)
        self.end_freq_value.setValidator(self.onlyInt)

        self.step_freq_text = QLabel('Measurement step [Hz]:', self)
        var_step_freq = '0'
        self.step_freq_value = QLineEdit(var_step_freq, parent=self)
        self.step_freq_value.setValidator(self.onlyInt)

        self.port_text = QLabel('Select port:', self)
        list=serial.tools.list_ports.comports()
        connected=[]
        for obj in list:
            connected.append(obj.device)

        self.com_port_combo = QComboBox(self)
        self.com_port_combo.addItems(connected)

        self.dir_label_text = QLabel('Directory:', self)
        self.dir_path = QLabel('NOT SELECTED', self)

        layout = QGridLayout()
        layout.setColumnStretch(1, 2)
        #layout.setColumnStretch(2, 2)

        layout.setRowStretch(6,2)
        layout.setRowStretch(7,2)

        layout.addWidget(self.start_freq_text, 0, 0)
        layout.addWidget(self.start_freq_value, 0, 1)
        layout.addWidget(self.end_freq_text , 1, 0)
        layout.addWidget(self.end_freq_value, 1, 1)
        layout.addWidget(self.step_freq_text, 2, 0)
        layout.addWidget(self.step_freq_value, 2, 1)
        layout.addWidget(self.times_text, 3, 0)
        layout.addWidget(self.times_value, 3, 1)
        layout.addWidget(self.port_text, 4, 0)
        layout.addWidget(self.com_port_combo, 4, 1)
        layout.addWidget(self.dir_label_text, 5, 0)
        layout.addWidget(self.dir_path, 5, 1)
        layout.addWidget(self.button, 6, 0,1,2)
        layout.addWidget(self.start_button, 7, 0, 1, 2)

        self.horizontalGroupBox.setLayout(layout)

    def pick_dir(self,):
        folder_path = QFileDialog.getExistingDirectory(None,"Select directory for your files")
        self.dir_path.setText(folder_path)
    def set_measurment(self):
        result = [self.dir_path.text()]
        result.append(int(self.times_value.text()))
        result.append(float(self.start_freq_value.text()))
        result.append(float(self.end_freq_value.text()))
        result.append(float(self.step_freq_value.text()))
        return result

    @pyqtSlot()
    def on_click(self):
        self.new_port = Connection_Port(port=self.com_port_combo.currentText())
        measurement_values = self.set_measurment()
        self.new_port.complex_measure(measurement_values[0], measurement_values[2], measurement_values[3],
                                      measurement_values[4], measurement_values[1])

        try:
            self.new_port = Connection_Port(port=self.com_port_combo.currentText())
            #start_time = time.time()
            measurement_values=self.set_measurment()
            self.new_port.complex_measure(measurement_values[0],measurement_values[2],measurement_values[3],measurement_values[4],measurement_values[1])
            #end_time=time.time()
            #if ( (end_time-start_time) > new_port.serial_port.timeout):
             #   raise Dupa_error
        except ZeroDivisionError:
            print("Zero error")
            self.error_user = QMessageBox()
            self.error_user.setText("Zero Division Error")
            self.error_user.setIcon(QMessageBox.Critical)
            self.error_user.setInformativeText("Make sure that all values are correct")
            self.error_user.setStandardButtons(QMessageBox.Ok)
            self.error_user.setWindowTitle("Error occurred")
            self.error_user.setWindowIcon(QIcon('imp_logo.png'))
            self.error_user.show()

        except SerialException :
            self.error_user_serial = QMessageBox()
            self.error_user_serial.setText("Connection Error!!!")
            self.error_user_serial.setIcon(QMessageBox.Critical)
            self.error_user_serial.setInformativeText("Turn on your device or move closer")
            self.error_user_serial.setStandardButtons(QMessageBox.Ok)
            self.error_user_serial.setWindowTitle("Error occurred")
            self.error_user_serial.setWindowIcon(QIcon('imp_logo.png'))
            self.error_user_serial.show()
        except TypeError:
            self.type_error_message = QMessageBox()
            self.type_error_message.setText("Type Error")
            self.type_error_message.setIcon(QMessageBox.Critical)
            self.type_error_message.setInformativeText("Check all of values(correct type)")
            self.type_error_message.setStandardButtons(QMessageBox.Ok)
            self.type_error_message.setWindowTitle("Error occurred")
            self.type_error_message.setWindowIcon(QIcon('imp_logo.png'))
            self.type_error_message.show()






