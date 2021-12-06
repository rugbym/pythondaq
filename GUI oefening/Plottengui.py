import sys
from typing import ChainMap
from PyQt5 import QtWidgets
from asteval import Interpreter


aeval = Interpreter()
import pyqtgraph as pg
import numpy as np
from numpy import pi, tan
from pyqtgraph import Qt
from pyqtgraph.widgets.ComboBox import ComboBox

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):

        # roep de __init__() aan van de parent class
        super().__init__()
        self.functions = {
            "sin(x)": lambda x: np.sin(x),
            "tan(x)": lambda x: np.tan(x),
            "exp(x)": lambda x: np.exp(x),
            "x": lambda x: x,
            "$x^2$": lambda x: x ** 2,
            "$x^3$": lambda x: x ** 3,
            "$\frac{1}{x}$": lambda x: 1 / x,
        }
        # elk QMainWindow moet een central widget hebben
        # hierbinnen maak je een layout en hang je andere widgets
        central_widget = QtWidgets.QWidget()

        self.setCentralWidget(central_widget)
        # voeg geneste layouts en widgets toe
        vbox = QtWidgets.QVBoxLayout(central_widget)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        # eerste vbox
        v_in_hbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(v_in_hbox)
        label = QtWidgets.QLabel("Enter starting value")
        v_in_hbox.addWidget(label)
        self.start_box = QtWidgets.QSpinBox()
        v_in_hbox.addWidget(self.start_box)

        self.start_box.setRange(0, 100)
        # 2de vbox
        v_in_hbox2 = QtWidgets.QVBoxLayout()
        hbox.addLayout(v_in_hbox2)
        label2 = QtWidgets.QLabel("Enter ending value")
        v_in_hbox2.addWidget(label2)
        self.stop_box = QtWidgets.QSpinBox()
        v_in_hbox2.addWidget(self.stop_box)

        self.stop_box.setRange(self.start_box.value(), 100)
        self.stop_box.setValue(6)
        # derde vbox
        v_in_hbox3 = QtWidgets.QVBoxLayout()
        hbox.addLayout(v_in_hbox3)
        label3 = QtWidgets.QLabel("Set number of points")

        v_in_hbox3.addWidget(label3)
        self.numpoints = QtWidgets.QSpinBox()
        v_in_hbox3.addWidget(self.numpoints)
        self.numpoints.setRange(0, 10000)
        self.numpoints.setValue(100)

        # het plotten
        hbox2 = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox2)
        self.plot_widget = pg.PlotWidget()

        self.plot_widget.setLabel("left", "sin(x)")
        self.plot_widget.setLabel("bottom", "x [radians]")
        hbox2.addWidget(self.plot_widget)

        vbox_settings = QtWidgets.QVBoxLayout()
        hbox2.addLayout(vbox_settings)
        # functiekiezer
        # self.comboboxfuncs = QtWidgets.QComboBox()

        # self.comboboxfuncs.addItems(
        #     ["tan(x)", "sin(x)", "exp(x)", "x", "$x^2$", "$x^3$", "$\frac{1}{x}$"]
        # )
        # vbox_settings.addWidget(self.comboboxfuncs)
        self.textedit = QtWidgets.QLineEdit()
        vbox_settings.addWidget(self.textedit)

        self.comboboxkleuren = QtWidgets.QComboBox()
        self.comboboxkleuren.addItems(["blauw", "zwart", "roze"])
        vbox_settings.addWidget(self.comboboxkleuren)
        quit_button = QtWidgets.QPushButton("Quit program")
        vbox_settings.addWidget(quit_button)
        # signal
        self.comboboxkleuren.currentIndexChanged.connect(self.plot)
        # self.comboboxfuncs.currentIndexChanged.connect(self.plot)
        self.textedit.textChanged.connect(self.functie)
        self.start_box.valueChanged.connect(self.plot)
        self.stop_box.valueChanged.connect(self.plot)
        self.numpoints.valueChanged.connect(self.plot)
        quit_button.clicked.connect(self.quit_program)

    def functie(self, text):
        self.text = text
        self.plot()

    def plot(self):
        self.kleuren = {"blauw": "b", "zwart": "k", "roze": "m"}
        self.plot_widget.clear()
        # y = aeval.symtable[self.textedit.toPlainText()]

        # func = self.functions[self.comboboxfuncs.currentText()]
        # print(aeval.symtable[self.textedit.toPlainText()])
        self.code = (
            """def func(x): 
                    return """
            + f"""{self.text}"""
        )
        aeval(self.code)

        self.x_vals = np.linspace(
            self.start_box.value(), self.stop_box.value(), self.numpoints.value()
        )
        aeval.symtable["x_vals"] = self.x_vals
        self.plot_widget.plot(
            self.x_vals,
            aeval("func(x_vals)"),
            symbol=None,
            pen={"color": self.kleuren[self.comboboxkleuren.currentText()], "width": 5},
        )

    def add_button_clicked(self):
        self.textedit.append("You clicked me.")

    def hello_world_clicked(self):
        self.textedit.append("Hello, world")

    def quit_program(self):
        self.close()

    def change_range(self, begin, end):
        self.x_vals = np.linspace(begin, end, 100)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

    def quit_program(self):
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
