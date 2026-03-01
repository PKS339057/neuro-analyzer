from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty


class StateCard(QFrame):
    def __init__(self, title, color="#00D47E", parent=None):
        super().__init__(parent)
        self._color = color
        self._animated_value = 0.0
        self._anim = None
        self._build_ui(title)

    # ── Qt-свойство для анимации ──────────────────────────────────────────

    def _get_anim_value(self):
        return self._animated_value

    def _set_anim_value(self, v: float):
        self._animated_value = v
        self.lbl_value.setText(f"{v:.0f}%")

    animatedValue = pyqtProperty(float, _get_anim_value, _set_anim_value)

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self, title):
        self.setStyleSheet("""
            StateCard {
                background-color: #2D2D2D;
                border: 2px solid #3A3A3A;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        self.lbl_title = QLabel(title)
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet(
            "color: #AAAAAA; font-size: 12px; font-weight: bold;"
            " letter-spacing: 1px; background: transparent; border: none;"
        )

        self.lbl_value = QLabel("—")
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_value.setStyleSheet(
            f"color: {self._color}; font-size: 48px; font-weight: bold;"
            " background: transparent; border: none;"
        )

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)

    # ── Публичный API ─────────────────────────────────────────────────────

    def set_value(self, target: float):
        """Анимированно обновляет значение от 0 до target за 800 мс."""
        self._anim = QPropertyAnimation(self, b"animatedValue")
        self._anim.setDuration(800)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(float(target))
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()
