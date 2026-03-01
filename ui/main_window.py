from PyQt6.QtWidgets import QMainWindow, QTabWidget

from ui.signal_tab import SignalTab
from ui.analysis_tab import AnalysisTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroState Analyzer")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.signal_tab   = SignalTab()
        self.analysis_tab = AnalysisTab()

        # Передаём ссылку на signal_tab, чтобы analysis_tab мог забрать данные
        self.analysis_tab.set_signal_tab(self.signal_tab)

        self.tabs.addTab(self.signal_tab,   "Сигнал")
        self.tabs.addTab(self.analysis_tab, "Анализ")

        self.setCentralWidget(self.tabs)
