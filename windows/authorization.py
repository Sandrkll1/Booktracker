import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import qdarkstyle
from loader import db


class Authorization(QMainWindow):

    def __init__(self, *args, main_window=None):
        super(Authorization, self).__init__(*args)
        uic.loadUi(".\\design\\Authorization.ui", self)

        self.main_window = main_window
        self.showPasswordCheckBox.stateChanged.connect(self.show_password)
        self.registerButton.clicked.connect(self.show_registration)
        self.loginButton.clicked.connect(self.login)

    def show_password(self):
        if self.showPasswordCheckBox.isChecked():
            self.passwordEdit.setEchoMode(QLineEdit.Normal)
        else:
            self.passwordEdit.setEchoMode(QLineEdit.Password)

    def show_registration(self):
        if self.main_window is not None:
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.registration)

    def login(self):
        username = self.usernameEdit.text()
        password = self.passwordEdit.text()

        if len(username.strip()) == 0 or len(password.strip()) == 0:
            QMessageBox.information(self, "Error", "Please fill all fields")
        else:
            if db.check_user(username, password):
                self.main_window.mainMenu.set_user_id(db.get_user(username)[0])
                self.main_window.stacked_widget.setCurrentWidget(self.main_window.mainMenu)
            else:
                QMessageBox.warning(self, "Warning", "Wrong username or password")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = Authorization()
    window.show()
    sys.exit(app.exec_())
