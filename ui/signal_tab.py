import sys
import os

import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
import pyqtgraph as pg

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.eeg_loader import load_csv
from core.signal_processor import bandpass_filter
from ui.widgets.filter_panel import FilterPanel
from ui.widgets.signal_player import SignalPlayer


class SignalTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.time = None
        self.signal_raw = None      # исходный сигнал (не фильтрованный)
        self.signal_display = None  # отображаемый сигнал (может быть фильтрованным)
        self.fs = None
        self._build_ui()

    # ── Построение интерфейса ─────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # ── Верхняя панель: кнопка + фильтр ──────────────────────────────
        top_bar = QHBoxLayout()

        self.btn_load = QPushButton("Загрузить файл")
        self.btn_load.setFixedWidth(160)
        self.btn_load.clicked.connect(self._on_load)
        top_bar.addWidget(self.btn_load)

        top_bar.addSpacing(24)

        self.filter_panel = FilterPanel()
        self.filter_panel.filter_changed.connect(self._on_filter_changed)
        top_bar.addWidget(self.filter_panel)
        top_bar.addStretch()

        root.addLayout(top_bar)

        # ── График ───────────────────────────────────────────────────────
        pg.setConfigOption('background', '#1A1A1A')
        pg.setConfigOption('foreground', '#CCCCCC')

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Амплитуда', units='мкВ')
        self.plot_widget.setLabel('bottom', 'Время', units='сек')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setMinimumHeight(360)

        self.plot_curve = self.plot_widget.plot(pen=pg.mkPen('#00D47E', width=1))

        # Вертикальная линия текущей позиции плеера
        self.position_line = pg.InfiniteLine(
            angle=90, movable=False,
            pen=pg.mkPen(color='#FF6B6B', width=2)
        )
        self.position_line.setVisible(False)
        self.plot_widget.addItem(self.position_line)

        root.addWidget(self.plot_widget)

        # ── Плеер ─────────────────────────────────────────────────────────
        player_frame = QFrame()
        player_frame.setObjectName("info_panel")
        player_layout = QVBoxLayout(player_frame)
        player_layout.setContentsMargins(12, 8, 12, 8)

        self.player = SignalPlayer()
        self.player.position_changed.connect(self._on_position_changed)
        player_layout.addWidget(self.player)

        root.addWidget(player_frame)

        # ── Панель информации ─────────────────────────────────────────────
        info_frame = QFrame()
        info_frame.setObjectName("info_panel")
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_layout.setSpacing(40)

        self.lbl_duration  = QLabel("Длительность: —")
        self.lbl_fs        = QLabel("Частота дискретизации: —")
        self.lbl_amplitude = QLabel("Амплитуда: —")

        for lbl in (self.lbl_duration, self.lbl_fs, self.lbl_amplitude):
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
            info_layout.addWidget(lbl)

        info_layout.addStretch()
        root.addWidget(info_frame)

    # ── Обработчики событий ───────────────────────────────────────────────

    def _on_load(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть CSV файл", "", "CSV файлы (*.csv);;Все файлы (*)"
        )
        if not path:
            return

        try:
            self.time, self.signal_raw, self.fs = load_csv(path)
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка загрузки",
                f"Не удалось прочитать файл:\n{e}\n\n"
                "Убедитесь, что файл имеет формат CSV с разделителем ';'."
            )
            return

        duration = self.time[-1] - self.time[0]
        if duration < 10.0:
            QMessageBox.warning(
                self, "Короткая запись",
                f"Длительность записи: {duration:.1f} сек.\n"
                "Для корректного спектрального анализа рекомендуется\n"
                "минимум 10 секунд сигнала."
            )

        self.signal_display = self.signal_raw.copy()

        # Сброс фильтра без лишних пересчётов
        self.filter_panel.reset()

        # Инициализируем плеер и линию позиции
        self.player.set_data(self.time, self.fs)
        self.position_line.setValue(self.time[0])
        self.position_line.setVisible(True)

        self._update_plot()
        self._update_info()

    def _on_filter_changed(self, lowcut, highcut):
        if self.signal_raw is None:
            return

        if lowcut is None:
            self.signal_display = self.signal_raw.copy()
        else:
            try:
                self.signal_display = bandpass_filter(
                    self.signal_raw, lowcut, highcut, self.fs
                )
            except Exception as e:
                print(f"Ошибка фильтрации: {e}")
                self.signal_display = self.signal_raw.copy()

        self._update_plot()

    def _on_position_changed(self, index):
        if self.time is not None:
            self.position_line.setValue(self.time[index])

    # ── Обновление графика и информации ──────────────────────────────────

    def _update_plot(self):
        t = self.time
        s = self.signal_display
        n = len(t)

        # Прореживание: не более 50 000 точек для плавной отрисовки
        if n > 50_000:
            step = n // 50_000
            t = t[::step]
            s = s[::step]

        self.plot_curve.setData(t, s)
        self.plot_widget.setXRange(t[0], t[-1], padding=0.01)
        self.plot_widget.setYRange(s.min(), s.max(), padding=0.05)

    def _update_info(self):
        duration = self.time[-1] - self.time[0]
        self.lbl_duration.setText(f"Длительность:  {duration:.2f} сек")
        self.lbl_fs.setText(f"Частота дискретизации:  {self.fs:.2f} Гц")
        self.lbl_amplitude.setText(
            f"Амплитуда:  {self.signal_raw.min():.4f} — {self.signal_raw.max():.4f} мкВ"
        )

    # ── Публичный API для других вкладок ─────────────────────────────────

    def get_data(self):
        """Возвращает исходные данные для вкладки Анализ."""
        return self.time, self.signal_raw, self.fs
