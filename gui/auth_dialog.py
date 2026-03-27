from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setModal(True)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Введите пароль для доступа:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        self.button = QPushButton("Войти")
        self.button.clicked.connect(self.check_password)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.accepted_flag = False

    def check_password(self):
        from utils.hash_utils import verify_password
        if verify_password(self.password_input.text()):
            self.accepted_flag = True
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный пароль!")
            self.reject()