from PyQt5 import QtWidgets, uic, QtCore
import sys
import time
from pyqtgraph import Qt
from pythondaq.models.PVExperiment import PVExperiment as PVE
from pythondaq.models.PVExperiment import listing
import numpy as np
import pyqtgraph as pg
import pandas as pd
from PyQt5.QtWidgets import QMenu, QVBoxLayout

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class PortSelection(QtWidgets.QDialog):
    """Dialogue screen to first ask for the port and then open the main program"""

    def __init__(self, parent=None):
        super(PortSelection, self).__init__(parent)
        self.setWindowTitle("Choose port")
        self.resize(400, 200)
        layout = QVBoxLayout(self)

        self.ports_combobox = QtWidgets.QComboBox()
        for item in listing(app=True):
            self.ports_combobox.addItem(f"{item}")

        layout.addWidget(self.ports_combobox)
        self.port_select_button = QtWidgets.QPushButton("Choose port")

        layout.addWidget(self.port_select_button)
        self.port_select_button.clicked.connect(self.store_port)
        self.port_select_button.clicked.connect(self.open_main_app)

    def store_port(self):
        self.port = self.ports_combobox.currentText()

    def open_main_app(self):

        self.close()


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        # calls the __init__ of the parent class
        super(UserInterface, self).__init__(parent)

        central_widget = QtWidgets.QWidget()

        central_widget.setMinimumSize(800, 600)
        self.tabs = QtWidgets.QTabWidget(central_widget)
        self.setCentralWidget(self.tabs)

        # Adding tabs and statusbar to main Window
        self.tab1UI()
        self.tab2UI()
        self._createStatusBar()

        # Code to open a dialogue which prompts to enter the port
        #
        self.dialog = PortSelection(self)
        self.dialog.exec_()
        self.port = self.dialog.port

        # All slots and signals of all tabs
        self.port_select_button.clicked.connect(self.store_port)
        self.port_select_button.clicked.connect(self._write_StatusBar)
        self.port_select_button.clicked.connect(self.tabIndex0)
        self.start_button.clicked.connect(self.upv_uzero_scan)
        self.quit_button.clicked.connect(self.quit_program)
        self.save_button.clicked.connect(self.save_data)
    def _createMenuBar(self):
        
    def tabIndex0(self):
        """Changes the tab Index to the measuring tab."""
        self.tabs.setCurrentIndex(1)

    def _createStatusBar(self):
        """Creates the statusbar on the bottom of the screen"""
        self.statusbar = self.statusBar()

    def _write_StatusBar(self):
        """Writes the ID String of the connected device to the statusbar. Device is typically an Arduino device.
        Device ID is written when the connect port button on tab 1 is pressed"""
        self.device = PVE(port=self.port)
        self.statusbar.showMessage(f"Connected device: {self.device.deviceinfo()}")
        self.device.close_session()

    def tab1UI(self):

        """Creates the tab in the window where one can select the port.
        Shows a combobox with all connected devices and a button to confirm the selected port"""
        self.tab1 = QtWidgets.QWidget()
        self.tabs.addTab(self.tab1, "Tab 1")
        layout = QtWidgets.QVBoxLayout()

        self.ports_combobox = QtWidgets.QComboBox()
        for item in listing(app=True):
            self.ports_combobox.addItem(f"{item}")

        layout.addWidget(self.ports_combobox)
        self.port_select_button = QtWidgets.QPushButton("Choose port")

        layout.addWidget(self.port_select_button)

        self.tab1.setLayout(layout)
        self.tabs.setTabText(0, "Choose device")

    def tab2UI(self):
        self.tab2 = QtWidgets.QWidget()
        self.tabs.addTab(self.tab2, "Tab 2")
        hbox = QtWidgets.QHBoxLayout()

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel("left", "Current over LED (mA)")
        self.plot_widget.setLabel("bottom", "Voltage over LED (V)")

        hbox.addWidget(self.plot_widget)
        # adding all the options, buttons and settings
        vbox_settings = QtWidgets.QVBoxLayout()
        # vbox_settings.setStretch()
        hbox.addLayout(vbox_settings)
        #
        options = QtWidgets.QFormLayout()

        vbox_settings.addLayout(options)

        self.status_measurementbar = QtWidgets.QLineEdit("No measurement done yet")
        self.status_measurementbar.setReadOnly(True)

        self.start_voltage = QtWidgets.QDoubleSpinBox()
        self.start_voltage.setSingleStep(0.01)
        self.start_voltage.setRange(0, 3.3)

        self.end_voltage = QtWidgets.QDoubleSpinBox()
        self.end_voltage.setSingleStep(0.01)
        self.end_voltage.setValue(3.3)
        self.end_voltage.setRange(0, 3.3)

        self.nsteps = QtWidgets.QSpinBox()
        self.nsteps.setValue(50)
        self.nsteps.setRange(10, 1023)

        self.num_measurements = QtWidgets.QSpinBox()
        self.num_measurements.setValue(1)
        self.num_measurements.setMinimum(1)

        self.start_button = QtWidgets.QPushButton("Start measurement")
        self.start_button.setFixedSize(200, 40)
        self.start_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.save_button = QtWidgets.QPushButton("Save measurements")
        self.save_button.setFixedSize(200, 40)
        self.save_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.quit_button = QtWidgets.QPushButton("Quit program")
        self.quit_button.setFixedSize(200, 40)
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

    def store_port(self):
        self.port = self.ports_combobox.currentText()

    def measurementbarstatus(self):
        self.status_measurementbar.clear()
        self.status_measurementbar.setText("Measuring...")

    def upv_uzero_scan(self):
        self.device = PVE(port=self.port)
        self.device.u_pv_u_zero()
        self.u_zerolist, self.u_pvlist = self.device.u_zerolist, self.device.u_pvlist
        self.device.close_session()

        self.plot_it()

    def call_scan(self):
        begin = time.time()
        self.device = PVE(port=self.port)
        if self.num_measurements.value() <= 1:
            self.error = False
            self.I, self.U = [], []

            for I, U in self.device.sweep_values(100):
                self.I.append(I * 1000), self.U.append(U)

        if self.num_measurements.value() > 1:
            self.error = True

            self.proccessed = self.device.error(
                self.num_measurements.value(),
                self.nsteps.value(),
                self.start_voltage.value(),
                self.end_voltage.value(),
            )
            self.I, self.U = (
                self.proccessed["mean current (A)"],
                self.proccessed["mean voltage (V)"],
            )
            self.I_error, self.U_error = (
                self.proccessed["error current"],
                self.proccessed["error voltage"],
            )

        end = time.time()
        self.device.close_session()
        self.status_measurementbar.clear()
        self.status_measurementbar.setText(f"Measurement done in {end-begin:.2f}s")
        self.plot_it()

    def plot_it(self):
        self.plot_widget.clear()
        if self.num_measurements.value() > 1:
            error = pg.ErrorBarItem(
                x=self.U,
                y=self.I,
                height=2 * self.I_error,
                width=2 * self.U_error,
            )
            self.plot_widget.addItem(error)

        self.plot_widget.plot(
            self.u_zerolist,
            self.u_pvlist,
            pen=None,
            symbol="o",
            symbolPen=pg.mkPen(color=(0, 0, 255), width=0),
            symbolBrush=pg.mkBrush(0, 0, 255, 255),
            symbolSize=6,
        )

    def save_data(self):
        """Saves the scan in a csv by opening system save file dialog."""
        if self.error == None:
            QtWidgets.QDialog()
        else:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                filter="CSV files (*.csv)"
            )
            self.device.csv_maker(self.error, filename=filename)

    def quit_program(self):
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
