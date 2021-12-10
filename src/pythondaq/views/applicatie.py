from PyQt5 import QtWidgets, uic
import sys
import time
from pyqtgraph import Qt
from pythondaq.models.DiodeExperiment import DiodeExperiment as DE
from pythondaq.models.DiodeExperiment import listing
import numpy as np
import pyqtgraph as pg
import pandas as pd
from PyQt5.QtWidgets import QMenu, QVBoxLayout

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class PoortSelectie(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(PoortSelectie, self).__init__(parent)
        self.setWindowTitle("Python Menus & Toolbars")
        self.resize(400, 200)
        layout = QVBoxLayout(self)
        self.poorten = QtWidgets.QComboBox()
        for item in listing(app=True):
            self.poorten.addItem(f"{item}")

        layout.addWidget(self.poorten)
        self.button = QtWidgets.QPushButton("Choose port")

        layout.addWidget(self.button)
        self.button.clicked.connect(self.store_port)
        self.button.clicked.connect(self.open_main_app)

    def store_port(self):
        self.port = self.poorten.currentText()

    def open_main_app(self):

        self.close()


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        # roep de __init__() aan van de parent class
        super(UserInterface, self).__init__(parent)
        central_widget = QtWidgets.QWidget()

        central_widget.setMinimumSize(800, 600)
        self.tabs = QtWidgets.QTabWidget(central_widget)
        self.setCentralWidget(self.tabs)
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()

        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")

        self.tab1UI()
        self.tab2UI()
        self._createStatusBar()
        self.dialog = PoortSelectie(self)
        # self.dialog.exec_()
        # self.port = self.dialog.port
        # Slots and signals
        self.button.clicked.connect(self.store_port)
        self.button.clicked.connect(self._write_StatusBar)
        self.start_button.clicked.connect(self.call_scan)
        self.quit_button.clicked.connect(self.quit_program)
        self.save_button.clicked.connect(self.save_data)

    def _createStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready", 3000)

    def _write_StatusBar(self):
        self.device = DE(port=self.port)
        self.statusbar.showMessage(f"Connected device: {self.device.deviceinfo()}")
        self.device.close_session()

    def tab1UI(self):
        layout = QtWidgets.QVBoxLayout()

        self.poorten = QtWidgets.QComboBox()
        for item in listing(app=True):
            self.poorten.addItem(f"{item}")

        layout.addWidget(self.poorten)
        self.button = QtWidgets.QPushButton("Choose port")

        layout.addWidget(self.button)

        self.tab1.setLayout(layout)
        self.tabs.setTabText(0, "Choose device")

    def tab2UI(self):
        hbox = QtWidgets.QHBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel("left", "Current over LED (A)")
        self.plot_widget.setLabel("bottom", "Voltage over LED (V)")

        hbox.addWidget(self.plot_widget)

        vbox_settings = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox_settings)
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
        self.save_button = QtWidgets.QPushButton("Save measurements")
        self.quit_button = QtWidgets.QPushButton("Quit program")

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
        self.port = self.poorten.currentText()

    def measurementbarstatus(self):
        self.status_measurementbar.clear()
        self.status_measurementbar.setText("Measuring...")

    def call_scan(self):
        begin = time.time()
        self.device = DE(port=self.port)
        if self.num_measurements.value() <= 1:
            self.error = False
            self.I, self.U = [], []

            for I, U in self.device.sweep_values(100):
                self.I.append(I), self.U.append(U)

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
        top = self.I + 0.5 * self.I_error
        bottom = self.I - 0.5 * self.I_error
        error = pg.ErrorBarItem(x=self.U, y=self.I, top=top, bottom=bottom, beam=0.001)

        self.plot_widget.clear()
        self.plot_widget.addItem(error)
        self.plot_widget.plot(
            self.U,
            self.I,
            pen=None,
            symbol="o",
            symbolPen=pg.mkPen(color=(0, 0, 255), width=0),
            symbolBrush=pg.mkBrush(0, 0, 255, 255),
            symbolSize=5,
        )

    def save_data(self):
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
