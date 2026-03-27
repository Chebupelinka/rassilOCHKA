import os
from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                               QPushButton, QFileDialog, QMessageBox, QLabel,
                               QTextEdit, QLineEdit, QListWidget, QListWidgetItem,
                               QFormLayout, QGroupBox, QPlainTextEdit, QInputDialog,
                               QDoubleSpinBox)
from PySide6.QtCore import QThread, Signal

from core.excel_parser import ExcelParser
from core.template import MessageGenerator
from core.sender import EmailSender
from gui.status_dialog import StatusDialog

class SendThread(QThread):
    status_update = Signal(str, bool, str)
    progress_update = Signal(int, int)

    def __init__(self, sender, emails, delay_min, delay_max):
        super().__init__()
        self.sender = sender
        self.emails = emails
        self.delay_min = delay_min
        self.delay_max = delay_max

    def run(self):
        def status_cb(to, success, msg):
            self.status_update.emit(to, success, msg)
        def progress_cb(sent, total):
            self.progress_update.emit(sent, total)
        self.sender.send_batch(self.emails, self.delay_min, self.delay_max, status_cb, progress_cb)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Рассылка писем")
        self.resize(900, 700)

        self.excel_df = None
        self.generated_emails = []
        self.sender = None

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Вкладка Excel
        self.excel_tab = QWidget()
        self.setup_excel_tab()
        self.tabs.addTab(self.excel_tab, "Добавление Excel таблички")

        # Вкладка шаблона
        self.template_tab = QWidget()
        self.setup_template_tab()
        self.tabs.addTab(self.template_tab, "Шаблон сообщения")

        # Вкладка заготовок
        self.drafts_tab = QWidget()
        self.setup_drafts_tab()
        self.tabs.addTab(self.drafts_tab, "Заготовки")

    def setup_excel_tab(self):
        layout = QVBoxLayout()
        self.file_label = QLabel("Файл не выбран")
        layout.addWidget(self.file_label)

        btn_select = QPushButton("Выбрать файл Excel")
        btn_select.clicked.connect(self.select_excel)
        layout.addWidget(btn_select)

        btn_template = QPushButton("Создать шаблон Excel")
        btn_template.clicked.connect(self.create_template)
        layout.addWidget(btn_template)

        layout.addStretch()
        self.excel_tab.setLayout(layout)

    def select_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите Excel файл", "", "Excel files (*.xlsx *.xls)")
        if file_path:
            df, error = ExcelParser.load_excel(file_path)
            if error:
                QMessageBox.critical(self, "Ошибка", error)
            else:
                self.excel_df = df
                self.file_label.setText(f"Загружен: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Успех", "Файл загружен. Перейдите на вкладку 'Шаблон сообщения'.")

    def create_template(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить шаблон", "шаблон_рассылки.xlsx", "Excel files (*.xlsx)")
        if save_path:
            ExcelParser.generate_template(save_path)
            QMessageBox.information(self, "Готово", f"Шаблон сохранён: {save_path}")

    def setup_template_tab(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Тема письма:"))
        self.subject_edit = QLineEdit()
        layout.addWidget(self.subject_edit)

        layout.addWidget(QLabel("Текст письма (метки: *имя*, *дата*, *время*, *место*, *задание*):"))
        self.body_edit = QTextEdit()
        layout.addWidget(self.body_edit)

        self.generate_btn = QPushButton("Сгенерировать письма")
        self.generate_btn.clicked.connect(self.generate_emails)
        layout.addWidget(self.generate_btn)

        self.template_tab.setLayout(layout)

    def generate_emails(self):
        if self.excel_df is None:
            QMessageBox.warning(self, "Нет данных", "Сначала загрузите Excel файл.")
            return
        subject = self.subject_edit.text()
        body = self.body_edit.toPlainText()
        if not subject or not body:
            QMessageBox.warning(self, "Неполные данные", "Заполните тему и текст письма.")
            return

        generator = MessageGenerator(subject, body)
        emails, error = generator.generate(self.excel_df)
        if error:
            QMessageBox.critical(self, "Ошибка генерации", error)
            return
        if not emails:
            QMessageBox.information(self, "Нет писем", "Не удалось сгенерировать ни одного письма.")
            return

        self.generated_emails = emails
        self.tabs.setCurrentWidget(self.drafts_tab)
        self.update_drafts_list()

    def setup_drafts_tab(self):
        layout = QVBoxLayout()

        self.drafts_list = QListWidget()
        self.drafts_list.currentItemChanged.connect(self.show_draft_preview)
        layout.addWidget(self.drafts_list)

        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview)

        settings_group = QGroupBox("Настройки отправки")
        form_layout = QFormLayout()
        self.delay_min = QDoubleSpinBox()
        self.delay_min.setRange(0, 60)
        self.delay_min.setValue(1)
        self.delay_max = QDoubleSpinBox()
        self.delay_max.setRange(0, 60)
        self.delay_max.setValue(5)
        form_layout.addRow("Задержка от (сек):", self.delay_min)
        form_layout.addRow("Задержка до (сек):", self.delay_max)
        settings_group.setLayout(form_layout)
        layout.addWidget(settings_group)

        self.start_btn = QPushButton("Начать рассылку")
        self.start_btn.clicked.connect(self.start_sending)
        layout.addWidget(self.start_btn)

        self.drafts_tab.setLayout(layout)

    def update_drafts_list(self):
        self.drafts_list.clear()
        for idx, email in enumerate(self.generated_emails):
            item = QListWidgetItem(f"{idx+1}. {email['to']} – {email['subject']}")
            self.drafts_list.addItem(item)
        if self.generated_emails:
            self.drafts_list.setCurrentRow(0)

    def show_draft_preview(self, current, previous):
        if current is None:
            return
        idx = self.drafts_list.row(current)
        email = self.generated_emails[idx]
        self.preview.setPlainText(f"Кому: {email['to']}\nТема: {email['subject']}\n\n{email['body']}")

    def start_sending(self):
        if not self.generated_emails:
            QMessageBox.warning(self, "Нет писем", "Сначала сгенерируйте письма.")
            return

        sender_email, ok1 = QInputDialog.getText(self, "Отправитель", "Введите ваш Gmail адрес:")
        if not ok1 or not sender_email:
            return
        app_password, ok2 = QInputDialog.getText(self, "Пароль приложения", "Введите пароль приложения Gmail:", QLineEdit.Password)
        if not ok2 or not app_password:
            return

        self.sender = EmailSender(sender_email, app_password)
        delay_min = self.delay_min.value()
        delay_max = self.delay_max.value()

        self.status_dialog = StatusDialog(self.generated_emails)
        self.status_dialog.show()

        self.send_thread = SendThread(self.sender, self.generated_emails, delay_min, delay_max)
        self.send_thread.status_update.connect(self.status_dialog.add_status)
        self.send_thread.progress_update.connect(self.status_dialog.update_progress)
        self.send_thread.finished.connect(self.status_dialog.finished)
        self.send_thread.start()