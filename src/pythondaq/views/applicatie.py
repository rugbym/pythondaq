from PyQt5 import QtGui, QtWidgets, uic, QtCore
import sys
import time


# from pyqtgraph import Qt
from pythondaq.models.DiodeExperiment import DiodeExperiment as DE
from pythondaq.models.DiodeExperiment import listing
import numpy as np
import pyqtgraph as pg
import pandas as pd
from PyQt5.QtWidgets import QAction, QDialog, QMenu, QVBoxLayout

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class PortSelection(QtWidgets.QDialog):
    """Dialogue screen to first ask for the port and then open the main program"""

    def __init__(self, parent=None):
        super(PortSelection, self).__init__(parent)
        self.setWindowTitle("Device selection dialog")
        self.resize(240, 200)
        layout = QVBoxLayout(self)

        self.poorten_text = QtWidgets.QLabel("Available ports:")
        self.poorten_text.setFixedSize(240, 15)
        self.poorten = QtWidgets.QComboBox()
        for item in listing(app=True):
            self.poorten.addItem(f"{item}")
        self.poorten.setMaximumWidth(240)
        self.poorten.setMinimumWidth(150)

        self.port_select_button = QtWidgets.QPushButton("Choose port")
        self.text = QtWidgets.QLabel("Port can be changed in program.")
        self.text.setFixedSize(240, 20)

        layout.addWidget(self.poorten_text)
        layout.addWidget(self.poorten)
        layout.addWidget(self.text)
        layout.addWidget(self.port_select_button)
        self.port_select_button.setMaximumWidth(240)

        self.port_select_button.clicked.connect(self.store_port)
        self.port_select_button.clicked.connect(self.open_main_app)

    def store_port(self):
        self.port = self.poorten.currentText()

    def open_main_app(self):
        """Simply closes the dialog"""
        self.close()


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        # calls the __init__ of the parent class
        super(UserInterface, self).__init__(parent)
        self.device = None
        self.setWindowTitle("LED Experiment Program")
        self.central_widget = QtWidgets.QWidget()

        self.central_widget.setMinimumSize(800, 600)
        self.tabs = QtWidgets.QTabWidget(self.central_widget)
        self.setCentralWidget(self.tabs)

        # Adding tabs and statusbar to main Window
        # self.tab1UI()
        self.tab2UI()
        self._createMenuBar()
        self._createStatusBar()
        # Code to open a dialogue which prompts to enter the port
        #
        self.show_dialog()

        # plot timer
        self.plot_timer = QtCore.QTimer()
        # Calls plot every 100ms
        self.plot_timer.timeout.connect(self.plot_it)
        self.plot_timer.start(100)
        # All slots and signals of all tabs
        self.exit.triggered.connect(self.close)
        self.select_port.triggered.connect(self.show_dialog)
        self.select_port.triggered.connect(self._write_StatusBar)
        self.save.triggered.connect(self.save_data)

        self.start_button.clicked.connect(self.call_scan)
        self.quit_button.clicked.connect(self.quit_program)
        self.save_button.clicked.connect(self.save_data)

    def show_dialog(self):
        """Opens the dialog to select the port with."""
        self.dialog = PortSelection(self)
        self.dialog.exec_()
        self.port = self.dialog.port
        if self.device != None:
            self.device.close_session()
        self.device = DE(port=self.port)
        self._write_StatusBar()

    def tabIndex0(self):
        """Changes the tab Index to the measuring tab."""
        self.tabs.setCurrentIndex(1)

    def _createMenuBar(self):
        """Creates the menu bar with different options to choose from."""
        menuBar = self.menuBar()
        # File menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        self.exit = QAction("Exit", self)
        self.save = QAction("Save", self)
        fileMenu.addAction(self.save)
        fileMenu.addAction(self.exit)

        deviceMenu = QMenu("&Devices", self)
        menuBar.addMenu(deviceMenu)
        self.select_port = QAction("Select Port", self)
        deviceMenu.addAction(self.select_port)

    def _createStatusBar(self):
        """Creates the statusbar on the bottom of the screen."""
        self.statusbar = self.statusBar()
        self.device_info = QtWidgets.QLabel()
        self.statusbar.addWidget(self.device_info)

    def _write_StatusBar(self):
        """Writes the ID String of the connected device to the statusbar. Device is typically an Arduino device.
        Device ID is written when the connect port button on tab 1 is pressed"""
        self.device_info.clear()
        self.device_info.setText(f"Connected device: {self.device.deviceinfo()}")

    def tab1UI(self):
        """Creates the tab in the window where one can select the port.
        Shows a combobox with all connected devices and a button to confirm the selected port
        Has become irrelevant with use of dialog box."""
        self.tab1 = QtWidgets.QWidget()
        self.tabs.addTab(self.tab1, "Tab 1")
        layout = QtWidgets.QVBoxLayout()

        self.poorten = QtWidgets.QComboBox()
        for item in listing(app=True):
            self.poorten.addItem(f"{item}")

        layout.addWidget(self.poorten)
        self.port_select_button = QtWidgets.QPushButton("Choose port")

        layout.addWidget(self.port_select_button)

        self.tab1.setLayout(layout)
        self.tabs.setTabText(0, "Choose device")

    def tab2UI(self):
        """The main tab where all the scanning parameters are shown."""
        self.tab2 = QtWidgets.QWidget()
        self.tabs.addTab(self.tab2, "Measurements")
        hbox = QtWidgets.QHBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel("left", "Current over LED (mA)")
        self.plot_widget.setLabel("bottom", "Voltage over LED (V)")

        hbox.addWidget(self.plot_widget)

        vbox_settings = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_settings)
        options = QtWidgets.QFormLayout()
        vbox_settings.addLayout(options)

        self.status_measurementbar = QtWidgets.QLineEdit("No measurement done yet")
        self.status_measurementbar.setReadOnly(True)
        self.status_measurementbar.setMaximumWidth(240)
        self.start_voltage = QtWidgets.QDoubleSpinBox()
        self.start_voltage.setSingleStep(0.01)
        self.start_voltage.setRange(0, 3.3)
        self.start_voltage.setMaximumWidth(240)
        self.end_voltage = QtWidgets.QDoubleSpinBox()
        self.end_voltage.setSingleStep(0.01)
        self.end_voltage.setValue(3.3)
        self.end_voltage.setRange(0, 3.3)
        self.end_voltage.setMaximumWidth(240)

        self.nsteps = QtWidgets.QSpinBox()
        self.nsteps.setValue(50)
        self.nsteps.setRange(10, 1023)
        self.nsteps.setMaximumWidth(240)

        self.num_measurements = QtWidgets.QSpinBox()
        self.num_measurements.setValue(1)
        self.num_measurements.setMinimum(1)
        self.num_measurements.setMaximumWidth(240)

        self.start_button = QtWidgets.QPushButton("Start measurement")
        self.start_button.setFixedSize(300, 40)
        self.start_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.save_button = QtWidgets.QPushButton("Save measurements")
        self.save_button.setFixedSize(300, 40)
        self.save_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.quit_button = QtWidgets.QPushButton("Quit program")
        self.quit_button.setFixedSize(300, 40)
        self.quit_button.setLayoutDirection(QtCore.Qt.RightToLeft)

        options.addRow("Measurement status", self.status_measurementbar)
        options.addRow("Start voltage:", self.start_voltage)
        options.addRow("End voltage:", self.end_voltage)
        options.addRow("Number of steps:", self.nsteps)
        options.addRow("Number of measurements:", self.num_measurements)

        vbox_settings.addWidget(self.start_button)
        vbox_settings.addWidget(self.save_button)
        vbox_settings.addWidget(self.quit_button)

        self.tabs.setTabText(1, "Measurements")
        self.tab2.setLayout(hbox)

    def call_scan(self):
        """Function that calls the scan
        Writes the time it has taken to perform the total scan to the measurement bar.
        Also calls the plot function to create the plot."""

        begin = time.time()

        self.device.start_scan(
            self.nsteps.value(),
            self.num_measurements.value(),
            self.start_voltage.value(),
            self.end_voltage.value(),
        )

        end = time.time()
        # self.device.close_session()
        self.status_measurementbar.clear()
        self.status_measurementbar.setText(f"Measurement done in {end-begin:.2f}s")

    def plot_it(self):
        """Plots the measurement data using the data stored in the model."""
        self.plot_widget.clear()

        error = pg.ErrorBarItem(
            x=np.array(self.device.U_list),
            y=np.array(self.device.I_list) * 1000,
            height=2 * np.array(self.device.I_err_list) * 1000,
            width=2 * np.array(self.device.U_err_list),
        )
        self.plot_widget.addItem(error)

        self.plot_widget.plot(
            np.array(self.device.U_list),
            np.array(self.device.I_list) * 1000,
            pen=None,
            symbol="o",
            symbolPen=pg.mkPen(color=(0, 0, 255), width=0),
            symbolBrush=pg.mkBrush(0, 0, 255, 255),
            symbolSize=6,
        )

    def save_data(self):
        """Saves the scan in a csv by opening system save file dialog."""

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="CSV files (*.csv)")
        self.device.csv_maker(filename=filename)

    def quit_program(self):
        """Closes the program"""
        self.device.close_session()
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
