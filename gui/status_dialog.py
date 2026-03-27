from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QProgressBar, QPushButton

class StatusDialog(QDialog):
    def __init__(self, emails):
        super().__init__()
        self.setWindowTitle("Отправка писем")
        self.resize(500, 400)
        layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.progress = QProgressBar()
        self.progress.setRange(0, len(emails))
        layout.addWidget(self.progress)
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)
        self.total = len(emails)
        self.sent = 0

    def add_status(self, to, success, message):
        status = "✅" if success else "❌"
        self.log.append(f"{status} {to}: {message}")
        if success:
            self.sent += 1
        self.progress.setValue(self.sent)

    def update_progress(self, sent, total):
        self.sent = sent
        self.progress.setValue(sent)

    def finished(self):
        self.log.append("=== Отправка завершена ===")
        self.close_btn.setEnabled(True)