from PyQt5 import QtWidgets, uic
import sys


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        # roep de __init__() aan van de parent class
        super().__init__()
        uic.loadUi(open("gui_designer.ui"), self)
        self.textedit = QtWidgets.QTextEdit()
        # Slots and signals
        self.clear_button.clicked.connect(self.textedit.clear)
        self.add_button.clicked.connect(self.add_button_clicked)

    def add_button_clicked(self):
        self.textedit.append("You clicked me.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
