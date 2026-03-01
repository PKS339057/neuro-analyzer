import sys
import os

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def load_stylesheet(app):
    qss_path = os.path.join(os.path.dirname(__file__), 'ui', 'styles.qss')
    try:
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Предупреждение: файл стилей не найден ({qss_path})")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
