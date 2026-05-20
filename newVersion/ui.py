from __future__ import annotations

from PySide6.QtCore import QUrl

from PySide6.QtMultimedia import (
    QAudioOutput,
    QMediaPlayer,
)

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



