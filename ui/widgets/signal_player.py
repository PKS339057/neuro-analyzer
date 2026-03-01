from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QComboBox, QLabel
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal


SPEEDS = [1, 2, 5, 10]
TIMER_INTERVAL_MS = 50


class SignalPlayer(QWidget):
    # Испускается при изменении позиции: передаёт текущий индекс отсчёта
    position_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.time = None
        self.fs = None
        self.current_index = 0
        self._playing = False

        self.timer = QTimer()
        self.timer.setInterval(TIMER_INTERVAL_MS)
        self.timer.timeout.connect(self._tick)

        self._build_ui()
        self._set_enabled(False)

    # ── Публичный API ─────────────────────────────────────────────────────

    def set_data(self, time, fs):
        """Загружает новые данные и сбрасывает плеер в начало."""
        self.stop()
        self.time = time
        self.fs = fs
        self.current_index = 0

        self.slider.blockSignals(True)
        self.slider.setMaximum(len(time) - 1)
        self.slider.setValue(0)
        self.slider.blockSignals(False)

        self._update_label()
        self._set_enabled(True)

    def play(self):
        if self.time is None:
            return
        if self.current_index >= len(self.time) - 1:
            self.current_index = 0
        self._playing = True
        self.timer.start()

    def pause(self):
        self._playing = False
        self.timer.stop()

    def stop(self):
        self.pause()
        self.current_index = 0
        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)
        self._update_label()
        if self.time is not None:
            self.position_changed.emit(0)

    # ── Внутренние методы ─────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # Слайдер позиции
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.valueChanged.connect(self._on_slider_moved)
        root.addWidget(self.slider)

        # Кнопки управления
        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.btn_play  = QPushButton("▶  Play")
        self.btn_pause = QPushButton("⏸  Pause")
        self.btn_stop  = QPushButton("⏹  Stop")
        for btn in (self.btn_play, self.btn_pause, self.btn_stop):
            btn.setFixedWidth(90)

        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)

        self.combo_speed = QComboBox()
        self.combo_speed.setFixedWidth(65)
        for s in SPEEDS:
            self.combo_speed.addItem(f"{s}x")

        self.lbl_position = QLabel("Позиция: — / — сек")

        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_pause)
        controls.addWidget(self.btn_stop)
        controls.addSpacing(12)
        controls.addWidget(QLabel("Скорость:"))
        controls.addWidget(self.combo_speed)
        controls.addStretch()
        controls.addWidget(self.lbl_position)

        root.addLayout(controls)

    def _tick(self):
        speed = SPEEDS[self.combo_speed.currentIndex()]
        # Количество отсчётов за один тик (50 мс реального времени)
        step = max(1, int(self.fs * (TIMER_INTERVAL_MS / 1000.0) * speed))
        self.current_index = min(self.current_index + step, len(self.time) - 1)

        self.slider.blockSignals(True)
        self.slider.setValue(self.current_index)
        self.slider.blockSignals(False)

        self._update_label()
        self.position_changed.emit(self.current_index)

        if self.current_index >= len(self.time) - 1:
            self.stop()

    def _on_slider_moved(self, value):
        """Пользователь вручную передвинул слайдер."""
        self.current_index = value
        self._update_label()
        self.position_changed.emit(value)

    def _update_label(self):
        if self.time is None:
            self.lbl_position.setText("Позиция: — / — сек")
            return
        total = self.time[-1] - self.time[0]
        current = self.time[self.current_index] - self.time[0]
        self.lbl_position.setText(f"Позиция: {current:.1f} / {total:.1f} сек")

    def _set_enabled(self, enabled):
        for w in (self.btn_play, self.btn_pause, self.btn_stop,
                  self.slider, self.combo_speed):
            w.setEnabled(enabled)
