import math

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget

from .theme import AMBER, BG_DARK, CYAN, CYAN_DIM, CYAN_GLOW, GREEN, GRID_COLOR

STATE_COLORS = {
    "idle": QColor(CYAN),
    "listening": QColor(GREEN),
    "thinking": QColor(AMBER),
    "speaking": QColor(CYAN_GLOW),
}


class HudBackground(QWidget):
    """Faint grid + corner brackets, drawn behind all other widgets."""

    def paintEvent(self, event):  # noqa: N802 (Qt override)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(BG_DARK))

        grid_pen = QPen(QColor(GRID_COLOR))
        grid_pen.setWidth(1)
        p.setPen(grid_pen)
        step = 44
        for x in range(0, self.width(), step):
            p.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            p.drawLine(0, y, self.width(), y)

        bracket_pen = QPen(QColor(CYAN_DIM))
        bracket_pen.setWidth(2)
        p.setPen(bracket_pen)
        length = 26
        margin = 10
        w, h = self.width(), self.height()
        corners = [
            (margin, margin, 1, 1),
            (w - margin, margin, -1, 1),
            (margin, h - margin, 1, -1),
            (w - margin, h - margin, -1, -1),
        ]
        for x, y, dx, dy in corners:
            p.drawLine(x, y, x + dx * length, y)
            p.drawLine(x, y, x, y + dy * length)
        p.end()


class ArcReactorWidget(QWidget):
    """Central animated core: rotating ring segments around a pulsing
    core, colored/paced by the assistant's current state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0.0
        self._pulse = 0.0
        self._pulse_dir = 1
        self.state = "idle"
        self.setMinimumSize(240, 240)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(30)

    def set_state(self, state: str):
        self.state = state if state in STATE_COLORS else "idle"

    def _tick(self):
        speed = {"idle": 0.5, "listening": 1.6, "thinking": 3.4, "speaking": 2.1}.get(self.state, 0.5)
        self._angle = (self._angle + speed) % 360
        self._pulse += 0.045 * self._pulse_dir
        if self._pulse >= 1.0:
            self._pulse, self._pulse_dir = 1.0, -1
        elif self._pulse <= 0.0:
            self._pulse, self._pulse_dir = 0.0, 1
        self.update()

    def paintEvent(self, event):  # noqa: N802
        w, h = self.width(), self.height()
        size = min(w, h)
        cx, cy = w / 2, h / 2
        color = STATE_COLORS[self.state]

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        glow = QRadialGradient(cx, cy, size / 2)
        c1 = QColor(color)
        c1.setAlpha(int(50 + 60 * self._pulse))
        glow.setColorAt(0.0, c1)
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(glow)
        p.drawEllipse(QRectF(cx - size / 2, cy - size / 2, size, size))

        outer_r = size * 0.42
        p.save()
        p.translate(cx, cy)
        p.rotate(self._angle)
        pen = QPen(color, size * 0.014, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        segments = 12
        for i in range(segments):
            start_angle = int(i * (360 / segments) * 16)
            span = int((360 / segments) * 0.6 * 16)
            p.drawArc(QRectF(-outer_r, -outer_r, outer_r * 2, outer_r * 2), start_angle, span)
        p.restore()

        mid_r = size * 0.31
        p.save()
        p.translate(cx, cy)
        p.rotate(-self._angle * 1.4)
        pen2 = QPen(QColor(color).lighter(120), size * 0.008)
        p.setPen(pen2)
        p.drawEllipse(QRectF(-mid_r, -mid_r, mid_r * 2, mid_r * 2))
        for i in range(4):
            a = math.radians(i * 90)
            p.drawLine(
                int(mid_r * math.cos(a)), int(mid_r * math.sin(a)),
                int((mid_r + size * 0.025) * math.cos(a)), int((mid_r + size * 0.025) * math.sin(a)),
            )
        p.restore()

        core_r = size * (0.13 + 0.02 * self._pulse)
        core_grad = QRadialGradient(cx, cy, core_r)
        core_grad.setColorAt(0.0, QColor("#ffffff"))
        core_grad.setColorAt(0.45, color)
        core_grad.setColorAt(1.0, QColor(color).darker(220))
        p.setBrush(core_grad)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QRectF(cx - core_r, cy - core_r, core_r * 2, core_r * 2))
        p.end()


class GaugeRing(QWidget):
    """Small circular dial, e.g. for CPU / RAM / DISK usage."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.label = label
        self.value = 0.0
        self.setMinimumSize(108, 108)

    def set_value(self, v: float):
        self.value = max(0.0, min(100.0, v))
        self.update()

    def paintEvent(self, event):  # noqa: N802
        w, h = self.width(), self.height()
        size = min(w, h) - 10
        cx, cy = w / 2, h / 2
        rect = QRectF(cx - size / 2, cy - size / 2, size, size)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        track_pen = QPen(QColor(CYAN_DIM), max(3.0, size * 0.06))
        track_pen.setCapStyle(Qt.RoundCap)
        p.setPen(track_pen)
        p.drawArc(rect, 90 * 16, -300 * 16)

        val_pen = QPen(QColor(CYAN_GLOW), max(3.0, size * 0.06))
        val_pen.setCapStyle(Qt.RoundCap)
        p.setPen(val_pen)
        span = -300 * (self.value / 100.0)
        p.drawArc(rect, 90 * 16, int(span * 16))

        p.setPen(QColor(CYAN_GLOW))
        f = QFont("Consolas", max(8, int(size * 0.17)))
        f.setBold(True)
        p.setFont(f)
        p.drawText(rect, Qt.AlignCenter, f"{int(self.value)}%")

        p.setPen(QColor(CYAN))
        f2 = QFont("Consolas", max(7, int(size * 0.11)))
        p.setFont(f2)
        label_rect = QRectF(rect.x(), rect.bottom() - 2, rect.width(), size * 0.2)
        p.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, self.label)
        p.end()
