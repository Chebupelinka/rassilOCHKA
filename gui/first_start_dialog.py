from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QMessageBox, QFormLayout)
from core.config_manager import ConfigManager

class FirstStartDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Первоначальная настройка")
        self.setModal(True)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Укажите данные для отправки писем и установите мастер-пароль.\n"
                                "Мастер-пароль будет использоваться для входа в программу."))

        form = QFormLayout()
        self.sender_email = QLineEdit()
        self.sender_email.setPlaceholderText("ваша_почта@gmail.com")
        self.app_password = QLineEdit()
        self.app_password.setPlaceholderText("16-символьный пароль приложения")
        self.app_password.setEchoMode(QLineEdit.Password)
        self.master_password = QLineEdit()
        self.master_password.setEchoMode(QLineEdit.Password)
        self.master_password.setPlaceholderText("придумайте пароль")
        self.master_password_confirm = QLineEdit()
        self.master_password_confirm.setEchoMode(QLineEdit.Password)
        self.master_password_confirm.setPlaceholderText("повторите пароль")

        form.addRow("Ваш mail адрес:", self.sender_email)
        form.addRow("Пароль приложения Gmail:", self.app_password)
        form.addRow("Мастер-пароль:", self.master_password)
        form.addRow("Подтверждение мастер-пароля:", self.master_password_confirm)
        layout.addLayout(form)

        self.save_btn = QPushButton("Сохранить и продолжить (перезапустите приложение)")
        self.save_btn.clicked.connect(self.save_config)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)
        self.config_data = None

    def save_config(self):
        sender = self.sender_email.text().strip()
        app_pass = self.app_password.text().strip()
        master = self.master_password.text()
        confirm = self.master_password_confirm.text()

        if not sender or not app_pass or not master:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля.")
            return
        if master != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return
        if len(master) < 4:
            QMessageBox.warning(self, "Ошибка", "Мастер-пароль должен быть не менее 4 символов.")
            return

        ConfigManager.save_config(master, sender, app_pass)
        # Проверим, что всё сохранилось корректно
        data = ConfigManager.load_config(master)
        if data:
            self.config_data = data
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить конфигурацию.")