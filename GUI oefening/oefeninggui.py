import sys
from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
from numpy import pi

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        # roep de __init__() aan van de parent class
        super().__init__()
        # elk QMainWindow moet een central widget hebben
        # hierbinnen maak je een layout en hang je andere widgets
        central_widget = QtWidgets.QWidget()

        self.setCentralWidget(central_widget)
        # voeg geneste layouts en widgets toe
        vbox = QtWidgets.QVBoxLayout(central_widget)
        self.textedit = QtWidgets.QTextEdit()
        vbox.addWidget(self.textedit)

        hbox = QtWidgets.QHBoxLayout()

        vbox.addLayout(hbox)

        clear_button = QtWidgets.QPushButton("Clear")
        hbox.addWidget(clear_button)
        add_button = QtWidgets.QPushButton("Add text")
        hbox.addWidget(add_button)
        second_button = QtWidgets.QPushButton("Hello, world")
        hbox.addWidget(second_button)
        quit_button = QtWidgets.QPushButton("Quit program")
        hbox.addWidget(quit_button)
        # Slots and signals
        clear_button.clicked.connect(self.textedit.clear)
        self.plot_widget = pg.PlotWidget()
        x = np.linspace(-pi, pi, 100)
        self.plot_widget.plot(x, np.sin(x), symbol=None, pen={"color": "k", "width": 5})
        self.plot_widget.setLabel("left", "sin(x)")
        self.plot_widget.setLabel("bottom", "x [radians]")

        snd_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(snd_hbox)
        snd_hbox.addWidget(self.plot_widget)
        add_button.clicked.connect(self.add_button_clicked)
        second_button.clicked.connect(self.hello_world_clicked)
        quit_button.clicked.connect(self.quit_program)

    def add_button_clicked(self):
        self.textedit.append("You clicked me.")

    def hello_world_clicked(self):
        self.textedit.append("Hello, world")

    def quit_program(self):
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
