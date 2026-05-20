from __future__ import annotations

from PySide6.QtCore import (
    Qt,
    QSize,
    Slot,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)

from PySide6.QtGui import (
    QFont,
    QColor,
    QPainter,
    QLinearGradient,
    QPen,
    QBrush,
    QPixmap,
    QIcon,
)

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QSlider,
    QDoubleSpinBox,
    QGroupBox,
    QGridLayout,
    QRadioButton,
    QButtonGroup,
    QTextEdit,
    QFrame,
    QSpinBox,
    QCheckBox,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QScrollArea,
)

from PySide6.QtSvgWidgets import QSvgWidget

from backend import AppState, MachineController

# ??? REVIEW LATER NEED TO PUT SOME INFORMATION
INFO_TEXT = (
   ""
) 

# =========================================================
# COLORS
# =========================================================

BG_PRIMARY = "#0F172A"
BG_SECONDARY = "#1E293B"

PRIMARY_BLUE = "#2563EB"
ENERGON_RED = "#DC2626"
CYBERTRON_CYAN = "#06B6D4"

TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"

SUCCESS_GREEN = "#22C55E"

# =========================================================
# TYPOGRAPHY HELPERS
# =========================================================

def _title_label(text: str) -> QLabel:
    """
    Main section/page title.
    Used for:
    - page headers
    - dashboard titles
    - major sections
    """

    lbl = QLabel(text)

    font = QFont("Orbitron")
    font.setPointSize(24)
    font.setBold(True)

    lbl.setFont(font)

    lbl.setStyleSheet(f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            letter-spacing: 1px;
            padding-bottom: 4px;
        }}
    """)

    return lbl

def _section_label(text: str) -> QLabel:
    """
    Medium hierarchy label.
    Used for:
    - card titles
    - grouped parameters
    - subsection headers
    """

    lbl = QLabel(text)

    font = QFont("Inter")
    font.setPointSize(15)
    font.setBold(True)

    lbl.setFont(font)

    lbl.setStyleSheet(f"""
        QLabel {{
            color: {PRIMARY_BLUE};
            padding-bottom: 2px;
        }}
    """)

    return lbl

def _subtle_label(text: str) -> QLabel:
    """
    Secondary descriptive text.
    Used for:
    - helper descriptions
    - captions
    - info text
    """

    lbl = QLabel(text)

    font = QFont("Inter")
    font.setPointSize(10)
    font.setBold(False)

    lbl.setFont(font)

    lbl.setWordWrap(True)

    lbl.setStyleSheet(f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            line-height: 1.4;
        }}
    """)

    return lbl

def _value_label(text: str = "--") -> QLabel:
    """
    Telemetry/value label.
    Used for:
    - machine status
    - coordinates
    - syringe amount
    - dynamic values
    """

    lbl = QLabel(text)

    font = QFont("Rajdhani")
    font.setPointSize(16)
    font.setBold(True)

    lbl.setFont(font)

    lbl.setStyleSheet(f"""
        QLabel {{
            color: {CYBERTRON_CYAN};
            background-color: {BG_SECONDARY};
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 6px 10px;
        }}
    """)

    return lbl


# =========================================================
# BUTTON HELPERS
# =========================================================

def _primary_button(text: str) -> QPushButton:
    """
    Main action button.
    Used for:
    - Start
    - Next
    - Connect
    """

    btn = QPushButton(text)

    font = QFont("Inter")
    font.setPointSize(11)
    font.setBold(True)

    btn.setFont(font)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(44)

    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {PRIMARY_BLUE};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 18px;
        }}

        QPushButton:hover {{
            background-color: #3B82F6;
        }}

        QPushButton:pressed {{
            background-color: #1D4ED8;
        }}
    """)

    return btn

def _secondary_button(text: str) -> QPushButton:
    """
    Secondary industrial button.
    Used for:
    - Load
    - Export
    - Info
    """

    btn = QPushButton(text)

    font = QFont("Inter")
    font.setPointSize(10)
    font.setBold(True)

    btn.setFont(font)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(42)

    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {BG_SECONDARY};
            color: {TEXT_PRIMARY};
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px 18px;
        }}

        QPushButton:hover {{
            border: 1px solid {PRIMARY_BLUE};
            background-color: #273549;
        }}

        QPushButton:pressed {{
            background-color: #111827;
        }}
    """)

    return btn

def _danger_button(text: str) -> QPushButton:
    """
    Critical action button.
    Used for:
    - Emergency stop
    - Disconnect
    - Reset
    """

    btn = QPushButton(text)

    font = QFont("Inter")
    font.setPointSize(10)
    font.setBold(True)

    btn.setFont(font)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(42)

    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {ENERGON_RED};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 18px;
        }}

        QPushButton:hover {{
            background-color: #EF4444;
        }}

        QPushButton:pressed {{
            background-color: #B91C1C;
        }}
    """)

    return btn


# =========================================================
# CARD / PANEL HELPERS
# =========================================================

def _card() -> QFrame:
    """
    Main industrial card container.
    Used for:
    - grouped controls
    - dashboard panels
    - machine info sections
    """

    frame = QFrame()

    frame.setObjectName("Card")

    frame.setStyleSheet(f"""
        QFrame#Card {{
            background-color: {BG_SECONDARY};
            border: 1px solid #334155;
            border-radius: 16px;
        }}
    """)

    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(24)
    shadow.setOffset(0, 4)
    shadow.setColor(QColor(0, 0, 0, 90))

    frame.setGraphicsEffect(shadow)

    return frame


# =========================================================
# STATUS HELPERS
# =========================================================

def _status_label(text: str, color: str = SUCCESS_GREEN) -> QLabel:
    """
    Status badge label.
    Used for:
    - Connected
    - Printing
    - Ready
    - Error
    """

    lbl = QLabel(text)

    font = QFont("Inter")
    font.setPointSize(10)
    font.setBold(True)

    lbl.setFont(font)

    lbl.setAlignment(Qt.AlignCenter)

    lbl.setStyleSheet(f"""
        QLabel {{
            background-color: {color};
            color: white;
            border-radius: 8px;
            padding: 4px 10px;
        }}
    """)

    return lbl

class RectanglePreview(QWidget):
    """
    Futuristic fabrication preview viewport.

    Visualizes:
    - safe fabrication area
    - active deposition rectangle
    - machine bed
    - validation state

    Optimus Prime Design System:
    - dark CAD viewport
    - cybertron blue overlays
    - glowing fabrication region
    - industrial telemetry aesthetic
    """

    def __init__(self, controller: "MachineController", state: "AppState") -> None:
        super().__init__()

        self.controller = controller
        self.state = state

        self.setMinimumHeight(250)

        # smoother rendering
        self.setAttribute(Qt.WA_StyledBackground, True)

        # reactive redraw system
        self.state.changed.connect(self.update)

        # futuristic panel styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #0B1120;
                border: 1px solid #334155;
                border-radius: 18px;
            }}
        """)

    def paintEvent(self, event) -> None:
        # =========================================================
        # MACHINE DIMENSIONS
        # =========================================================

        BED_W = 170.0
        BED_H = 250.0

        p = self.state.params

        # =========================================================
        # PAINTER SETUP
        # =========================================================

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        # =========================================================
        # VIEWPORT GEOMETRY
        # =========================================================

        margin = 24.0

        avail_w = max(10.0, float(self.width()) - 2 * margin)
        avail_h = max(10.0, float(self.height()) - 2 * margin)

        side = max(10.0, min(avail_w, avail_h))

        ox = (float(self.width()) - side) / 2.0
        oy = (float(self.height()) - side) / 2.0

        # =========================================================
        # MM -> SCREEN TRANSFORM
        # =========================================================

        def mx(x_mm: float) -> float:
            return ox + (x_mm / BED_W) * side

        def my(y_mm: float) -> float:
            return oy + side - (y_mm / BED_H) * side

        # =========================================================
        # MACHINE BED
        # =========================================================

        bed_gradient = QLinearGradient(0, oy, 0, oy + side)

        bed_gradient.setColorAt(0, QColor(20, 28, 45))
        bed_gradient.setColorAt(1, QColor(10, 15, 28))

        painter.setBrush(QBrush(bed_gradient))

        painter.setPen(QPen(QColor(45, 65, 95), 2))

        painter.drawRoundedRect(
            int(ox),
            int(oy),
            int(side),
            int(side),
            12,
            12,
        )

        # =========================================================
        # BACKGROUND CAD GRID
        # =========================================================

        grid_pen = QPen(QColor(35, 52, 72), 1)

        painter.setPen(grid_pen)

        divisions = 10

        for i in range(divisions + 1):

            x = ox + (i / divisions) * side
            y = oy + (i / divisions) * side

            painter.drawLine(int(x), int(oy), int(x), int(oy + side))
            painter.drawLine(int(ox), int(y), int(ox + side), int(y))

        # =========================================================
        # SAFE FABRICATION AREA
        # =========================================================

        sx0 = float(p.safe_x_min)
        sx1 = float(p.safe_x_max)

        sy0 = float(p.safe_y_min)
        sy1 = float(p.safe_y_max)

        rx = mx(sx0)
        ry = my(sy1)

        rw = mx(sx1) - mx(sx0)
        rh = my(sy0) - my(sy1)

        # glowing cybertron outline
        painter.setBrush(Qt.NoBrush)

        painter.setPen(QPen(QColor(37, 99, 235, 40), 10))
        painter.drawRoundedRect(
            int(rx),
            int(ry),
            int(rw),
            int(rh),
            10,
            10,
        )

        painter.setPen(QPen(QColor(37, 99, 235), 2))

        painter.drawRoundedRect(
            int(rx),
            int(ry),
            int(rw),
            int(rh),
            10,
            10,
        )

        # =========================================================
        # BUILD ACTIVE RECTANGLES
        # =========================================================

        try:

            # backend becomes the single source of truth
            backend_rects = self.controller._get_active_rectangles()

            # extract only rectangle geometry
            rectangles = [
                rect
                for _, rect in backend_rects
            ]

            valid = len(rectangles) > 0

        except Exception:

            rectangles = []
            valid = False

        # =========================================================
        # DRAW ACTIVE FABRICATION AREAS
        # =========================================================

        for x0, x1, y0, y1 in rectangles:

            rrx = mx(x0)
            rry = my(y1)

            rrw = mx(x1) - mx(x0)
            rrh = my(y0) - my(y1)

            # futuristic glow
            glow_color = (
                QColor(34, 197, 94, 60)
                if valid
                else QColor(220, 38, 38, 60)
            )

            main_color = (
                QColor(34, 197, 94)
                if valid
                else QColor(220, 38, 38)
            )

            fill_color = (
                QColor(34, 197, 94, 90)
                if valid
                else QColor(220, 38, 38, 90)
            )

            # outer glow
            painter.setPen(QPen(glow_color, 12))
            painter.setBrush(Qt.NoBrush)

            painter.drawRoundedRect(
                int(rrx),
                int(rry),
                int(rrw),
                int(rrh),
                10,
                10,
            )

            # main rectangle
            painter.setPen(QPen(main_color, 2))
            painter.setBrush(QBrush(fill_color))

            painter.drawRoundedRect(
                int(rrx),
                int(rry),
                int(rrw),
                int(rrh),
                10,
                10,
            )

            # center crosshair
            cx = rrx + rrw / 2
            cy = rry + rrh / 2

            painter.setPen(QPen(QColor(6, 182, 212), 1))

            painter.drawLine(
                int(cx - 12),
                int(cy),
                int(cx + 12),
                int(cy),
            )

            painter.drawLine(
                int(cx),
                int(cy - 12),
                int(cx),
                int(cy + 12),
            )

        # =========================================================
        # TELEMETRY TEXT
        # =========================================================

        font = QFont("Rajdhani")
        font.setPointSize(10)
        font.setBold(True)

        painter.setFont(font)

        painter.setPen(QColor(148, 163, 184))

        orientation = str(p.fiber_orientation)

        length = float(p.fiber_length)
        width = float(p.fiber_width)
        spacing = float(p.fiber_spacing)

        telemetry = (
            f"{orientation.upper()}  |  "
            f"L:{length:.1f}mm  |  "
            f"W:{width:.1f}mm  |  "
            f"S:{spacing:.1f}mm"
        )

        painter.drawText(
            int(ox),
            max(18, int(oy - 8)),
            telemetry,
        )

        # =========================================================
        # STATUS BADGE
        # =========================================================

        badge_text = "VALID FABRICATION AREA" if valid else "INVALID GEOMETRY"

        badge_color = (
            QColor(34, 197, 94)
            if valid
            else QColor(220, 38, 38)
        )

        badge_rect_x = max(
            12,
            ox + side - 170
        )

        badge_rect_y = min(
            oy + side + 12,
            self.height() - 40
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(badge_color))

        painter.drawRoundedRect(
            int(badge_rect_x),
            int(badge_rect_y),
            160,
            30,
            10,
            10,
        )

        painter.setPen(QColor(255, 255, 255))

        painter.drawText(
            int(badge_rect_x + 16),
            int(badge_rect_y + 20),
            badge_text,
        )



