from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal


# (название, lowcut, highcut) — None означает "без фильтра"
FILTER_PRESETS = [
    ("Без фильтра",       None,  None),
    ("0.5-30 Hz (общий)", 0.5,   30.0),
    ("8-13 Hz (Alpha)",   8.0,   13.0),
    ("13-30 Hz (Beta)",   13.0,  30.0),
]


class FilterPanel(QWidget):
    # lowcut, highcut — числа или None для режима "без фильтра"
    filter_changed = pyqtSignal(object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Фильтр:"))

        self.combo = QComboBox()
        self.combo.setFixedWidth(200)
        for name, _, _ in FILTER_PRESETS:
            self.combo.addItem(name)
        self.combo.currentIndexChanged.connect(self._on_changed)

        layout.addWidget(self.combo)
        layout.addStretch()

    def _on_changed(self, index):
        _, lowcut, highcut = FILTER_PRESETS[index]
        self.filter_changed.emit(lowcut, highcut)

    def reset(self):
        """Сбрасывает в 'Без фильтра' без генерации сигнала."""
        self.combo.blockSignals(True)
        self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)
