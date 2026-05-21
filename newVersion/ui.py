from __future__ import annotations

from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QFont, QPainter, QPen, QColor, QBrush
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QMessageBox, QFileDialog,
    QComboBox, QSlider, QDoubleSpinBox, QGroupBox, QGridLayout,
    QRadioButton, QButtonGroup, QTextEdit, QFrame, QSpinBox, QCheckBox
)

from backend import AppState, MachineController

INFO_TEXT = (
   "Optimus Prime - Nanofiber Fabrication System v3.0 - Develop by Samuel Sampaio Diniz"
)

def _title_label(text: str) -> QLabel:
    lbl = QLabel(text)
    f = QFont()
    f.setPointSize(20)
    f.setBold(True)
    lbl.setFont(f)
    return lbl

def _subtle_label(text: str) -> QLabel:
    lbl = QLabel(text)
    f = QFont()
    f.setPointSize(10)
    f.setBold(False)
    lbl.setFont(f)
    lbl.setStyleSheet("color: #666;")
    return lbl


class RectanglePreview(QWidget):
    def __init__(self, controller: "MachineController", state: "AppState") -> None:
        super().__init__()
        self.controller = controller
        self.state = state
        self.setMinimumHeight(240)
        self.state.changed.connect(self.update) # This is the reactive redraw system.

    def paintEvent(self, event) -> None:
        BED_W = 170.0
        BED_H = 250.0

        p = self.state.params
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        margin = 16.0

        avail_w = max(10.0, float(self.width()) - 2 * margin)
        avail_h = max(10.0, float(self.height()) - 2 * margin)
        side = max(10.0, min(avail_w, avail_h))

        # the preview want a square ratio, so it chooses the small dimension to guarantee. for example 
        # avail_w = 600
        # avail_h = 300
        # side will be 300
        # the preview becomes 300x300

        ox = (float(self.width()) - side) / 2.0
        oy = (float(self.height()) - side) / 2.0

        # converts from mm to pixel
        def mx(x_mm: float) -> float:
            return ox + (x_mm / BED_W) * side

        def my(y_mm: float) -> float:
            return oy + side - (y_mm / BED_H) * side
        
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(Qt.NoBrush))
        
        # Usable and safe area outline
        sx0 = float(p.safe_x_min)
        sx1 = float(p.safe_x_max)
        sy0 = float(p.safe_y_min)
        sy1 = float(p.safe_y_max)

        painter.setPen(QPen(QColor(120, 180, 255), 2)) 
        painter.setBrush(QBrush(Qt.NoBrush))
        rx = mx(sx0)
        ry = my(sy1)
        rw = mx(sx1) - mx(sx0)
        rh = my(sy0) - my(sy1)

        # the safer rectangle
        painter.drawRect(rx, ry, rw, rh)
        
        # inside rectangle
        painter.drawRect(rx + 65, ry + 65, 80 , 80)

        # Requested rectangle
        try:
            rectangles = self.controller._get_active_rectangles()
            valid = True

        except Exception:
            rectangles = []
            valid = False

        painter.setPen(QPen(QColor("#22C55E" if valid else "#EF4444"), 2))

        for axis, rect in rectangles:

            x0, x1, y0, y1 = rect

            rrx = mx(x0)
            rry = my(y1)
            rrw = mx(x1) - mx(x0)
            rrh = my(y0) - my(y1)
            painter.drawRect(rrx, rry, rrw, rrh)
 



