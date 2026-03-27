import sys
from PySide6.QtWidgets import QApplication
from gui.auth_dialog import AuthDialog
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    auth = AuthDialog()
    if auth.exec_() == AuthDialog.Accepted and auth.accepted_flag:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()