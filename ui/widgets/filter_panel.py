from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QDoubleSpinBox
)
from PyQt6.QtCore import pyqtSignal


# (название, lowcut, highcut, band_name)
# lowcut/highcut == "custom" → активируется ручной ввод
# band_name != None → при выборе будет отрисована огибающая этой волны
FILTER_PRESETS = [
    ("Без фильтра",              None,   None,   None),
    ("0.5–30 Гц (общий)",        0.5,    30.0,   None),
    ("Delta  (0.5–4 Гц)",        0.5,    4.0,    "Delta"),
    ("Theta  (4–8 Гц)",          4.0,    8.0,    "Theta"),
    ("Alpha  (8–13 Гц)",         8.0,    13.0,   "Alpha"),
    ("Mu  (8–12 Гц)",            8.0,    12.0,   "Mu"),
    ("Beta  (13–30 Гц)",         13.0,   30.0,   "Beta"),
    ("Gamma  (30–50 Гц)",        30.0,   50.0,   "Gamma"),
    ("Lambda  (4–5 Гц)",         4.0,    5.0,    "Lambda"),
    ("Kappa  (10–12 Гц)",        10.0,   12.0,   "Kappa"),
    ("Задать самостоятельно",    "custom", "custom", None),
]

_CUSTOM_IDX = len(FILTER_PRESETS) - 1


class FilterPanel(QWidget):
    """
    Панель выбора полосового фильтра.

    Сигнал filter_changed(lowcut, highcut, band_name):
      - lowcut / highcut: числа (Гц) или None (без фильтра)
      - band_name: строка ('Alpha', 'Beta', …) или None
    """
    filter_changed = pyqtSignal(object, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Фильтр:"))

        self.combo = QComboBox()
        self.combo.setFixedWidth(210)
        for name, *_ in FILTER_PRESETS:
            self.combo.addItem(name)
        self.combo.currentIndexChanged.connect(self._on_combo_changed)
        layout.addWidget(self.combo)

        layout.addSpacing(6)
        layout.addWidget(QLabel("от"))

        self.spin_low = QDoubleSpinBox()
        self.spin_low.setRange(0.1, 499.9)
        self.spin_low.setValue(0.5)
        self.spin_low.setDecimals(1)
        self.spin_low.setSuffix(" Гц")
        self.spin_low.setFixedWidth(90)
        self.spin_low.setEnabled(False)
        self.spin_low.editingFinished.connect(self._on_custom_changed)
        layout.addWidget(self.spin_low)

        layout.addWidget(QLabel("до"))

        self.spin_high = QDoubleSpinBox()
        self.spin_high.setRange(0.2, 500.0)
        self.spin_high.setValue(30.0)
        self.spin_high.setDecimals(1)
        self.spin_high.setSuffix(" Гц")
        self.spin_high.setFixedWidth(90)
        self.spin_high.setEnabled(False)
        self.spin_high.editingFinished.connect(self._on_custom_changed)
        layout.addWidget(self.spin_high)

        layout.addStretch()

    # ── Слоты ─────────────────────────────────────────────────────────────

    def _on_combo_changed(self, index):
        _, lowcut, highcut, band_name = FILTER_PRESETS[index]
        is_custom = (lowcut == "custom")

        self.spin_low.setEnabled(is_custom)
        self.spin_high.setEnabled(is_custom)

        if not is_custom:
            # Показываем значения пресета в спинбоксах (не активны)
            self.spin_low.blockSignals(True)
            self.spin_high.blockSignals(True)
            if lowcut is not None:
                self.spin_low.setValue(float(lowcut))
                self.spin_high.setValue(float(highcut))
            self.spin_low.blockSignals(False)
            self.spin_high.blockSignals(False)

            self.filter_changed.emit(lowcut, highcut, band_name)
        # При выборе "Задать самостоятельно" ждём ввода в спинбоксах

    def _on_custom_changed(self):
        lo = self.spin_low.value()
        hi = self.spin_high.value()
        if lo < hi:
            self.filter_changed.emit(lo, hi, None)

    # ── Публичный API ─────────────────────────────────────────────────────

    def reset(self):
        """Сбрасывает в «Без фильтра» без генерации сигнала."""
        self.combo.blockSignals(True)
        self.combo.setCurrentIndex(0)
        self.spin_low.setEnabled(False)
        self.spin_high.setEnabled(False)
        self.combo.blockSignals(False)
