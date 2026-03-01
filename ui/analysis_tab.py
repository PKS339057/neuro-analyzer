import sys
import os

import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QMessageBox, QFrame, QLabel
)
from PyQt6.QtCore import Qt

import pyqtgraph as pg

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.spectral_analyzer import compute_psd, compute_band_powers
from core.state_classifier import compute_state_indices, generate_conclusion


# ── Цвета и диапазоны ритмов ──────────────────────────────────────────────
BAND_COLORS = {
    'Delta': '#4477CC',
    'Theta': '#9966CC',
    'Alpha': '#44AA66',
    'Beta':  '#DDAA00',
    'Gamma': '#CC4444',
}

BAND_REGIONS = [
    ('Delta', 0.5,  4.0),
    ('Theta', 4.0,  8.0),
    ('Alpha', 8.0,  13.0),
    ('Beta',  13.0, 30.0),
    ('Gamma', 30.0, 50.0),
]


class AnalysisTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._signal_tab = None
        self._build_ui()

    def set_signal_tab(self, signal_tab):
        """Связывает вкладку с источником данных (SignalTab)."""
        self._signal_tab = signal_tab

    # ── Построение интерфейса ─────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # ── Кнопка запуска ────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        self.btn_analyze = QPushButton("Запустить анализ")
        self.btn_analyze.setFixedWidth(180)
        self.btn_analyze.clicked.connect(self._on_analyze)
        top_bar.addWidget(self.btn_analyze)
        top_bar.addStretch()
        root.addLayout(top_bar)

        # ── Графики: PSD слева, Pie справа ───────────────────────────────
        charts_row = QHBoxLayout()
        charts_row.setSpacing(12)
        charts_row.addWidget(self._build_psd_widget(), stretch=3)
        charts_row.addWidget(self._build_pie_widget(), stretch=2)
        root.addLayout(charts_row)

        # ── Легенда ритмов (между графиками и заключением) ────────────────
        root.addWidget(self._build_legend_widget())

        # ── Заключение ────────────────────────────────────────────────────
        self.conclusion_text = QTextEdit()
        self.conclusion_text.setReadOnly(True)
        self.conclusion_text.setPlaceholderText(
            "Нажмите «Запустить анализ» для получения заключения..."
        )
        root.addWidget(self.conclusion_text)

    def _build_psd_widget(self):
        pg.setConfigOption('background', '#1A1A1A')
        pg.setConfigOption('foreground', '#CCCCCC')

        self.psd_widget = pg.PlotWidget()
        self.psd_widget.setLabel('left',   'Мощность', units='мкВ²/Гц')
        self.psd_widget.setLabel('bottom', 'Частота',  units='Гц')
        self.psd_widget.showGrid(x=True, y=True, alpha=0.3)
        self.psd_widget.setXRange(0, 50, padding=0)
        self.psd_widget.setLogMode(y=True)
        self.psd_widget.setMinimumHeight(260)

        for name, lo, hi in BAND_REGIONS:
            color = BAND_COLORS[name]

            # Цветной фоновый регион
            region = pg.LinearRegionItem(
                values=[lo, hi],
                brush=pg.mkBrush(color + '28'),
                movable=False,
            )
            region.setZValue(-10)
            self.psd_widget.addItem(region)

            # Центральная линия с текстовой меткой (обе добавляются в plot)
            center_line = pg.InfiniteLine(
                pos=(lo + hi) / 2, angle=90, pen=None
            )
            pg.InfLineLabel(
                center_line,
                text=name,
                position=0.95,
                color=color,
                fill=None,
            )
            self.psd_widget.addItem(center_line)  # label видна только так

            # Граничная вертикальная линия
            boundary = pg.InfiniteLine(
                pos=hi, angle=90,
                pen=pg.mkPen(color, width=1, style=Qt.PenStyle.DashLine)
            )
            self.psd_widget.addItem(boundary)

        self.psd_curve = self.psd_widget.plot(
            pen=pg.mkPen('#FFFFFF', width=1.5)
        )
        return self.psd_widget

    def _build_pie_widget(self):
        self._fig = Figure(facecolor='#1A1A1A')
        # Занимаем всю площадь фигуры — легенда теперь снаружи
        self._fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasQTAgg(self._fig)
        self._canvas.setMinimumWidth(220)
        self._canvas.setMinimumHeight(220)
        self._draw_empty_pie()
        return self._canvas

    def _build_legend_widget(self):
        """Строка с цветными метками ритмов, видимая при любом размере."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(0)
        layout.addStretch()

        self._legend_labels: dict[str, QLabel] = {}
        for i, (band, color) in enumerate(BAND_COLORS.items()):
            lbl = QLabel(f"■  {band}  —")
            lbl.setStyleSheet(
                f"color: {color}; font-size: 12px; padding: 0 10px 0 0;"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            self._legend_labels[band] = lbl
            layout.addWidget(lbl)

        layout.addStretch()
        return container

    # ── Обработчик анализа ────────────────────────────────────────────────

    def _on_analyze(self):
        if self._signal_tab is None:
            return

        time, signal, fs = self._signal_tab.get_data()

        if time is None or signal is None:
            QMessageBox.warning(
                self, "Нет данных",
                "Сначала загрузите ЭЭГ-файл на вкладке «Сигнал»."
            )
            return

        duration    = time[-1] - time[0]
        freqs, psd  = compute_psd(signal, fs)
        band_powers = compute_band_powers(freqs, psd)
        state       = compute_state_indices(band_powers)
        conclusion  = generate_conclusion(band_powers, state, duration)

        self._update_psd(freqs, psd)
        self._update_pie(band_powers)
        self._update_legend(band_powers)
        self.conclusion_text.setPlainText(conclusion)

    # ── Обновление виджетов ───────────────────────────────────────────────

    def _update_psd(self, freqs, psd):
        mask = (freqs >= 0) & (freqs <= 50)
        self.psd_curve.setData(freqs[mask], psd[mask])
        self.psd_widget.setXRange(0, 50, padding=0)

    def _update_pie(self, band_powers):
        self._ax.clear()
        self._ax.set_facecolor('#1A1A1A')
        self._fig.patch.set_facecolor('#1A1A1A')

        labels  = list(band_powers.keys())
        sizes   = [max(v, 0.01) for v in band_powers.values()]
        colors  = [BAND_COLORS[k] for k in labels]
        explode = [0.03] * len(labels)

        _, _, autotexts = self._ax.pie(
            sizes,
            labels=None,
            colors=colors,
            explode=explode,
            autopct='%1.1f%%',
            startangle=140,
            pctdistance=0.75,
            wedgeprops={'linewidth': 1.0, 'edgecolor': '#1A1A1A'},
            textprops={'color': '#FFFFFF', 'fontsize': 9},
        )
        # Легенды внутри фигуры больше нет — она в _build_legend_widget
        self._canvas.draw()

    def _update_legend(self, band_powers):
        for band, pct in band_powers.items():
            if band in self._legend_labels:
                self._legend_labels[band].setText(f"■  {band}  {pct:.1f}%")

    def _draw_empty_pie(self):
        self._ax.clear()
        self._ax.set_facecolor('#1A1A1A')
        self._fig.patch.set_facecolor('#1A1A1A')
        self._ax.text(
            0.5, 0.5, 'Нет данных',
            ha='center', va='center',
            color='#555555', fontsize=12,
            transform=self._ax.transAxes,
        )
        self._canvas.draw()
