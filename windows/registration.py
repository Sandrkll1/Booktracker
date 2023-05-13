import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import qdarkstyle
from loader import db


class Registration(QMainWindow):

    def __init__(self, *args, main_window=None):
        super(Registration, self).__init__(*args)
        uic.loadUi(".\\design\\Registration.ui", self)

        self.main_window = main_window

        self.showPasswordCheckBox.stateChanged.connect(self.show_password)
        self.loginButton.clicked.connect(self.show_login)
        self.registerButton.clicked.connect(self.register)

    def show_password(self):
        if self.showPasswordCheckBox.isChecked():
            self.passwordEdit.setEchoMode(QLineEdit.Normal)
        else:
            self.passwordEdit.setEchoMode(QLineEdit.Password)

    def show_login(self):
        if self.main_window is not None:
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.authorization)

    def register(self):
        username = self.usernameEdit.text()
        password = self.passwordEdit.text()

        if len(username.strip()) == 0 or len(password.strip()) == 0:
            QMessageBox.information(self, "Error", "Please fill all fields")
            return

        if db.user_in_db(username):
            QMessageBox.information(self, "Error", "User already exists")

        else:
            db.add_user(username, password)
            self.main_window.mainMenu.set_user_id(db.get_user(username)[0])
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.mainMenu)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = Registration()
    window.show()
    sys.exit(app.exec_())
