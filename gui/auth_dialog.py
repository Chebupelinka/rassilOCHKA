from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from core.config_manager import ConfigManager
from gui.first_start_dialog import FirstStartDialog

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в программу")
        self.setModal(True)
        self.accepted_flag = False
        self.config_data = None

        if not ConfigManager.is_configured():
            self.first_dialog = FirstStartDialog()
            if self.first_dialog.exec() == QDialog.Accepted and self.first_dialog.config_data:
                self.config_data = self.first_dialog.config_data
                self.accepted_flag = True
                # Принудительно обрабатываем события, чтобы диалог успел закрыться
                from PySide6.QtWidgets import QApplication
                QApplication.processEvents()
                self.accept()
            else:
                self.reject()
            return

        # Обычный запуск: запрос мастер-пароля
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Введите мастер-пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.button = QPushButton("Войти")
        self.button.clicked.connect(self.check_password)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def check_password(self):
        master = self.password_input.text()
        data = ConfigManager.load_config(master)
        if data:
            self.config_data = data
            self.accepted_flag = True
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный мастер-пароль!")