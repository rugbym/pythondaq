from PyQt5 import QtWidgets, uic, QtCore
import sys
import time
from pyqtgraph import Qt
from pythondaq.models.PVExperiment import PVExperiment as PVE
from pythondaq.models.PVExperiment import listing
import numpy as np
import pyqtgraph as pg
import pandas as pd
from PyQt5.QtWidgets import QAction, QHBoxLayout, QMenu, QVBoxLayout

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
        for item in listing():
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
        self.fit_state = False
        self.startvalues = False
        self.setWindowTitle("PV Experiment Program")
        self.central_widget = QtWidgets.QWidget()

        self.central_widget.setMinimumSize(800, 600)
        self.central_hbox = QHBoxLayout()
        self.central_widget.setLayout(self.central_hbox)

        self.tabs = QtWidgets.QTabWidget()
        self.central_hbox.addWidget(self.tabs)
        self.setCentralWidget(self.central_widget)

        # Adding tabs and statusbar to main Window
        # self.tab1UI()
        self.permanent_controls()
        self.U_U_plottab()
        self.I_U_plottab()
        self.P_R_plottab()
        self._createMenuBar()
        self._createStatusBar()
        # Code to open a dialogue which prompts to enter the port
        #
        self.show_dialog()

        # plot timer
        self.timer = QtCore.QTimer()
        # Calls plot and measurement status every 100ms
        # self.timer.timeout.connect(self.plot_it)
        self.timer.timeout.connect(self.measurement_status)
        # self.timer.timeout.connect()
        self.timer.start(100)

        # All slots and signals of all tabs
        self.exit.triggered.connect(self.close)
        self.select_port.triggered.connect(self.show_dialog)
        self.select_port.triggered.connect(self._write_StatusBar)
        self.save.triggered.connect(self.save_data)

        self.plot_clear_button.clicked.connect(self.clear_plots)
        self.starting_values_button.clicked.connect(self.get_startingvalues)
        self.start_button.clicked.connect(self.call_scan)
        self.quit_button.clicked.connect(self.quit_program)
        self.save_button.clicked.connect(self.save_data)
        self.fit_button.clicked.connect(self.fit_call)

    def show_dialog(self):
        """Opens the dialog to select the port with."""
        self.dialog = PortSelection(self)
        self.dialog.exec_()
        self.port = self.dialog.port
        if self.device != None:
            self.device.close_session()
        self.device = PVE(port=self.port)
        self._write_StatusBar()
        self.clear_plots()
        self.start_voltage.setValue(0)
        self.end_voltage.setValue(3.3)

    def permanent_controls(self):

        vbox_settings = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.central_hbox)
        vbox_widget = QtWidgets.QWidget()
        vbox_widget.setLayout(vbox_settings)

        self.central_hbox.addWidget(vbox_widget)
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

        self.fit_results = QtWidgets.QLabel("Fit_results")
        self.fit_n = QtWidgets.QLineEdit()
        self.fit_n.setReadOnly(True)
        self.fit_I_l = QtWidgets.QLineEdit()
        self.fit_I_l.setReadOnly(True)
        self.fit_I_0 = QtWidgets.QLineEdit()
        self.fit_I_0.setReadOnly(True)
        self.fit_redchi = QtWidgets.QLineEdit()
        self.fit_redchi.setReadOnly(True)

        # All buttons
        self.plot_clear_button = QtWidgets.QPushButton("Clear all Plots")
        self.plot_clear_button.setFixedSize(300, 40)
        self.plot_clear_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.starting_values_button = QtWidgets.QPushButton("Get approx. start values")
        self.starting_values_button.setFixedSize(300, 40)
        self.starting_values_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.start_button = QtWidgets.QPushButton("Start measurement")
        self.start_button.setFixedSize(300, 40)
        self.start_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.save_button = QtWidgets.QPushButton("Save measurements")
        self.save_button.setFixedSize(300, 40)
        self.save_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.quit_button = QtWidgets.QPushButton("Quit program")
        self.quit_button.setFixedSize(300, 40)
        self.quit_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.fit_button = QtWidgets.QPushButton("Fit")
        self.fit_button.setFixedSize(300, 40)
        self.fit_button.setLayoutDirection(QtCore.Qt.RightToLeft)

        # Adding spinboxes to the options
        options.addRow(self.status_measurementbar)
        options.addRow("Start voltage:", self.start_voltage)
        options.addRow("End voltage:", self.end_voltage)
        options.addRow("Number of steps:", self.nsteps)
        options.addRow("Number of measurements:", self.num_measurements)
        options.addRow(self.fit_results)
        options.addRow("n:", self.fit_n)
        options.addRow("I_l", self.fit_I_l)
        options.addRow("I_0", self.fit_I_0)
        options.addRow("red χ2", self.fit_redchi)

        # adding buttons
        vbox_settings.addWidget(self.plot_clear_button)
        vbox_settings.addWidget(self.starting_values_button)
        vbox_settings.addWidget(self.start_button)
        # vbox_settings.addWidget(self.save_button)
        # vbox_settings.addWidget(self.quit_button)
        vbox_settings.addWidget(self.fit_button)

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

    def measurement_status(self):
        """Shows the measurement status above the measurement settings"""
        if self.device._scan_thread == None:
            self.status_measurementbar.setText("No measurement done")
        elif self.device._scan_thread.is_alive():
            self.status_measurementbar.setText("Measuring...")
            self.plot_it()
        elif not self.device._scan_thread.is_alive():
            self.fit_button.setDisabled(False)
            self.status_measurementbar.setText("Measurement done")
            if self.startvalues:
                self.start_voltage.setValue(self.device.startvalue)
                self.end_voltage.setValue(self.device.stopvalue)
                self.startvalues = False

    def clear_plots(self):
        self.U_U_plot.clear()
        self.I_U_plot.clear()
        self.P_R_plot.clear()

    def U_U_plottab(self):
        """Tab where the Upv-U0-plot is displayed"""
        self.U_U_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.U_U_tab, "U_0 vs U_pv")
        hbox = QtWidgets.QHBoxLayout()
        self.U_U_plot = pg.PlotWidget()
        hbox.addWidget(self.U_U_plot)
        self.U_U_tab.setLayout(hbox)

    def I_U_plottab(self):
        """Tab where I-U-plot is displayed"""
        self.I_U_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.I_U_tab, "I vs U")
        self.I_U_plot = pg.PlotWidget()
        hbox = QHBoxLayout()
        self.I_U_tab.setLayout(hbox)
        hbox.addWidget(self.I_U_plot)

    def P_R_plottab(self):
        self.P_U_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.P_U_tab, "P vs R")
        hbox = QHBoxLayout()
        self.P_U_tab.setLayout(hbox)
        self.P_R_plot = pg.PlotWidget()
        hbox.addWidget(self.P_R_plot)

    def get_startingvalues(self):
        """Function to generate starting values based on the slope of the Upv-Uzero graph"""
        self.fit_state = False
        self.fit_button.setDisabled(True)
        self.startvalues = True
        self.device.start_scan(65, 2, 0.7, 2.8, startvalues=self.startvalues)
        self.status_measurementbar.setText("Getting values")

    def call_scan(self):
        """Function that calls the scan
        Writes the time it has taken to perform the total scan to the measurement bar.
        Also calls the plot function to create the plot."""
        self.fit_state = False
        self.fit_button.setDisabled(True)
        self.device.start_scan(
            self.nsteps.value(),
            self.num_measurements.value(),
            self.start_voltage.value(),
            self.end_voltage.value(),
        )
        self.status_measurementbar.setText("Measuring")

        # self.device.close_session()
        # self.status_measurementbar.clear()
        # self.status_measurementbar.setText(f"Measurement done in {end-begin:.2f}s")

    def U_U_plot_code(self):
        """Code for plotting the U-U Plot"""
        self.U_U_plot.clear()
        self.U_U_plot.setRange(
            xRange=(self.start_voltage.value(), self.end_voltage.value()), yRange=(0, 6)
        )
        self.U_U_plot.setLabel("left", "U_pv (V)")
        self.U_U_plot.setLabel("bottom", "U_0 (V)")

        error_U_U = pg.ErrorBarItem(
            x=np.array(self.device.U_zero_list),
            y=np.array(self.device.U_list),
            height=2 * np.array(self.device.U_err_list),
            # width=2 * np.array(self.device.U_zero_list),
        )
        self.U_U_plot.addItem(error_U_U)

        self.U_U_plot.plot(
            np.array(self.device.U_zero_list),
            np.array(self.device.U_list),
            pen=None,
            symbol="o",
            symbolPen=pg.mkPen(color=(0, 0, 255), width=0),
            symbolBrush=pg.mkBrush(0, 0, 255, 255),
            symbolSize=6,
        )
        if self.device._scan_thread != None:
            if (
                self.device._scan_thread.is_alive() == True
                and len(self.device.U_list) > 5
            ) and self.startvalues == True:
                slopeline = lambda x, a, b: a * x + b
                x = np.linspace(self.device.x[0] - 0.2, self.device.x[0] + 0.2, 10)
                y = slopeline(x, self.device.slope, self.device.intercept)
                self.U_U_plot.plot(x, y, pen=pg.mkPen(color=(255, 0, 0), width=2))

    def I_U_plot_code(self):
        self.I_U_plot.clear()
        self.I_U_plot.setLabel("left", "I (A)")
        self.I_U_plot.setLabel("bottom", "Upv (V)")

        error_I_U = pg.ErrorBarItem(
            x=np.array(self.device.U_list),
            y=np.array(self.device.I_list),
            height=2 * np.array(self.device.I_err_list),
            width=2 * np.array(self.device.U_err_list),
        )
        self.I_U_plot.addItem(error_I_U)

        self.I_U_plot.plot(
            np.array(self.device.U_list),
            np.array(self.device.I_list),
            pen=None,
            symbol="o",
            symbolPen=pg.mkPen(color=(0, 0, 255), width=0),
            symbolBrush=pg.mkBrush(0, 0, 255, 255),
            symbolSize=6,
        )
        if self.fit_state == True:
            self.I_U_plot.plot(
                self.device.fit_plot_list[0],
                self.device.fit_plot_list[1],
                pen=pg.mkPen(color=(255, 0, 0), width=2),
            )

        if self.device.get_max_point == True:
            self.I_U_plot.plot(
                [self.device.U_list[self.device.maximum_power_loc]],
                [self.device.I_list[self.device.maximum_power_loc]],
                symbol="x",
                symbolPen=pg.mkPen(color=(255, 0, 0)),
            )
            self.device.get_max_point = False
            self.label_value = pg.TextItem("", **{"color": "#FFF"})
            self.I_U_plot.addItem(self.label_value)
            self.label_value.setPos(
                QtCore.QPointF(
                    self.device.U_list[self.device.maximum_power_loc],
                    self.device.I_list[self.device.maximum_power_loc],
                )
            )
            self.label_value.setText("maximum power")

    def P_R_plot_code(self):
        self.P_R_plot.clear()
        self.P_R_plot.setLabel("left", "P (W)")
        self.P_R_plot.setLabel("bottom", "R_mosfet (\u2126)")
        error = pg.ErrorBarItem(
            x=np.array(self.device.R_MOSFET_list),
            y=np.array(self.device.P_list),
            height=2 * np.array(self.device.P_err_list),
            width=2 * np.array(self.device.R_MOSFET_err_list),
        )
        self.P_R_plot.addItem(error)

        self.P_R_plot.plot(
            np.array(self.device.R_MOSFET_list),
            np.array(self.device.P_list),
            pen=None,
            symbol="o",
            symbolPen=pg.mkPen(color=(0, 0, 255), width=0),
            symbolBrush=pg.mkBrush(0, 0, 255, 255),
            symbolSize=6,
        )
        if self.device.get_max_point == True:
            self.P_R_plot.plot(
                [self.device.R_MOSFET_list[self.device.maximum_power_loc]],
                [self.device.P_list[self.device.maximum_power_loc]],
                symbol="x",
                symbolPen=pg.mkPen(color=(255, 0, 0)),
            )
            self.device.get_max_point = False

    def plot_it(self):
        """Plots the measurement data using the data stored in the model.
        Draws the three plots"""
        # make the Uzero Upv plot
        self.U_U_plot_code()
        # make the I U plot
        self.I_U_plot_code()
        # make the P R plot
        self.P_R_plot_code()

    def fit_call(self):
        """Calls fit and functions to display results"""
        self.device.fit_it()
        self.fit_state = True
        self.plot_it()
        self.fit_redchi.setText(f"{self.device.fit.redchi:.3f}")
        self.fit_I_0.setText(
            f"{self.device.I_0*1000:.3f}\u00B1 {self.device.I_0_error*1000:.3f} mA"
        )
        self.fit_I_l.setText(
            f"{self.device.I_l*1000:.3f}\u00B1 {self.device.I_l_error*1000:.3f} mA"
        )
        self.fit_n.setText(f"{self.device.n:.2f}\u00B1 {self.device.n_error:.2f}")

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
