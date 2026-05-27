from __future__ import annotations

import os

from PySide6.QtCore import Qt, QSize, Slot, QUrl, QRectF, QPointF
from PySide6.QtGui import (
    QFont,
    QColor,
    QPainter,
    QLinearGradient,
    QPen,
    QBrush,
    QPixmap,
    QRadialGradient,
    QIcon,
)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QMessageBox, QFileDialog,
    QComboBox, QSlider, QDoubleSpinBox, QGroupBox, QGridLayout,
    QRadioButton, QButtonGroup, QTextEdit, QFrame, QSpinBox, QCheckBox,  QGraphicsDropShadowEffect, QSizePolicy,  QScrollArea
)

from PySide6.QtMultimedia import (
    QAudioOutput,
    QMediaPlayer,
)

from backend import AppState, MachineController
from pathlib import Path

BG_PRIMARY = "#0F172A"
BG_SECONDARY = "#1E293B"

PRIMARY_BLUE = "#2563EB"
ENERGON_RED = "#DC2626"
CYBERTRON_CYAN = "#38BDF8"

TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"

SUCCESS_GREEN = "#22C55E"

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
# TYPOGRAPHY HELPERS
# =========================================================

def _title_label(text: str) -> QLabel:
    """
    Main hero/page title.

    Used for:
    - application branding
    - main page headers
    - cinematic launcher titles
    """

    lbl = QLabel(text)

    font = QFont("Orbitron")
    font.setPointSize(24)
    font.setBold(True)

    lbl.setFont(font)

    lbl.setWordWrap(True)

    lbl.setStyleSheet(f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            background: transparent;
            letter-spacing: 2px;
            padding-bottom: 4px;
            border: none;
        }}
    """)

    return lbl


def _section_label(text: str) -> QLabel:
    """
    Secondary hierarchy label.

    Used for:
    - section headers
    - subtitles
    - grouped parameter titles
    """

    lbl = QLabel(text)

    font = QFont("Inter")
    font.setPointSize(16)
    font.setBold(True)

    lbl.setFont(font)

    lbl.setWordWrap(True)

    lbl.setStyleSheet(f"""
        QLabel {{
            color: {CYBERTRON_CYAN};
            background: transparent;
            padding-bottom: 2px;
            border: none;
        }}
    """)

    return lbl


def _subtle_label(text: str) -> QLabel:
    """
    Descriptive/support text.

    Used for:
    - helper descriptions
    - subtitles
    - contextual information
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
            background: transparent;
            line-height: 1.5;
            border: none;
        }}
    """)

    return lbl



INFO_TEXT = """
<p>
Greetings, operator.
</p>

<p>
I am Optimus Prime, autonomous command interface
for advanced microfiber fabrication and industrial
precision control.
</p>

<p>
This system was engineered to coordinate machine
operations, fiber generation, motion control,
and fabrication workflows with precision,
reliability, and discipline.
</p>

<p>
Every parameter configured and every trajectory
executed represents the convergence of engineering,
innovation, and purpose.
</p>

<p style="margin-top:12px; color:#60A5FA;">
<i>
"There are mysteries to the universe we were never meant to solve. But who we are, and why we are here, are not among them. Those answers, we carry inside us."
</i>
<br>
— Optimus Prime
</p>

<p style="font-size:10px; color:#64748B;">
Developed by Samuel Sampaio Diniz<br>
under the supervision of Dr. Andrew Shyrakenko.
</p>
"""

# =========================================================
# REACTOR THERMOMETER WIDGET
# =========================================================

class ReactorThermometerWidget(QWidget):

    def __init__(self, state: AppState) -> None:
        super().__init__()

        self.state = state

        self.current_temp = float(
            self.state.params.current_temperature
        )

        self.setMinimumWidth(320)
        self.setMinimumHeight(480)

        self.state.temperature_changed.connect(
            self.on_temperature_changed
        )

    @Slot(float)
    def on_temperature_changed(
        self,
        value: float
    ):
        self.current_temp = float(value)
        self.update()

    def _temperature_color(self) -> QColor:

        t = self.current_temp

        if t < 10:
            return QColor("#2563EB")

        elif t < 25:
            return QColor("#00BFFF")

        elif t < 35:
            return QColor("#FF9F1A")

        return QColor("#FF3B30")

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True
        )

        w = self.width()
        h = self.height()

        # =====================================================
        # SAFE AREA
        # =====================================================

        pad = 34

        outer = QRectF(
            pad,
            pad,
            w - pad * 2,
            h - pad * 2
        )

        # =====================================================
        # MAIN PANEL
        # =====================================================

        panel_gradient = QLinearGradient(
            outer.topLeft(),
            outer.bottomRight()
        )

        panel_gradient.setColorAt(
            0,
            QColor(4, 14, 28, 240)
        )

        panel_gradient.setColorAt(
            1,
            QColor(2, 8, 18, 240)
        )

        painter.setPen(
            QPen(
                QColor(0, 180, 255, 120),
                2
            )
        )

        painter.setBrush(panel_gradient)

        painter.drawRoundedRect(
            outer,
            28,
            28
        )

        # =====================================================
        # THERMOMETER
        # =====================================================

        tube_w = outer.width() * 0.10
        tube_h = outer.height() * 0.72

        tube_x = outer.center().x() - tube_w / 2
        tube_y = outer.top() + 60

        tube_rect = QRectF(
            tube_x,
            tube_y,
            tube_w,
            tube_h
        )

        # glow
        painter.setPen(Qt.NoPen)

        painter.setBrush(
            QColor(0, 180, 255, 30)
        )

        painter.drawRoundedRect(
            tube_rect.adjusted(-10, -10, 10, 10),
            tube_w,
            tube_w
        )

        # border
        painter.setPen(
            QPen(
                QColor(120, 220, 255, 200),
                5
            )
        )

        painter.setBrush(
            QColor(10, 18, 30, 230)
        )

        painter.drawRoundedRect(
            tube_rect,
            tube_w / 2,
            tube_w / 2
        )

        # =====================================================
        # INTERNAL CHAMBER
        # =====================================================

        chamber = tube_rect.adjusted(
            8,
            8,
            -8,
            -8
        )

        painter.setPen(Qt.NoPen)

        painter.setBrush(
            QColor(0, 0, 0, 200)
        )

        painter.drawRoundedRect(
            chamber,
            chamber.width() / 2,
            chamber.width() / 2
        )

        # =====================================================
        # FILL
        # =====================================================

        ratio = max(
            0.0,
            min(
                1.0,
                self.current_temp / 50.0
            )
        )

        fill_h = chamber.height() * ratio

        fill_rect = QRectF(
            chamber.left(),
            chamber.bottom() - fill_h,
            chamber.width(),
            fill_h
        )

        color = self._temperature_color()

        gradient = QLinearGradient(
            fill_rect.topLeft(),
            fill_rect.bottomLeft()
        )

        gradient.setColorAt(
            0,
            color.lighter(180)
        )

        gradient.setColorAt(
            1,
            color.darker(170)
        )

        painter.setBrush(gradient)

        painter.drawRoundedRect(
            fill_rect,
            chamber.width() / 2,
            chamber.width() / 2
        )

        # =====================================================
        # SCALE
        # =====================================================

        scale_x = tube_rect.left() - 30

        painter.setPen(
            QPen(
                QColor(180, 220, 255, 180),
                2
            )
        )

        font = QFont("Inter")
        font.setPointSize(12)

        painter.setFont(font)

        for i in range(0, 51, 10):

            y = chamber.bottom() - (
                chamber.height() * (i / 50.0)
            )

            painter.drawLine(
                int(scale_x),
                int(y+1),
                int(scale_x + 15),
                int(y+1)
            )

            painter.drawText(
                QRectF(
                    scale_x - 52,
                    y - 12,
                    40,
                    24
                ),
                Qt.AlignRight | Qt.AlignVCenter,
                f"{i} °C"
            )

        # =====================================================
        # REACTOR BASE
        # =====================================================

        base_size = tube_w * 1.55

        base_rect = QRectF(
            outer.center().x() - base_size / 2,
            tube_rect.bottom() - 24,
            base_size,
            base_size
        )

        base_gradient = QRadialGradient(
            base_rect.center(),
            base_size / 1.8
        )

        base_gradient.setColorAt(
            0,
            color
        )

        base_gradient.setColorAt(
            1,
            QColor(60, 20, 0)
        )

        painter.setBrush(base_gradient)

        painter.setPen(
            QPen(
                QColor(120, 220, 255, 180),
                4
            )
        )

        painter.drawEllipse(base_rect)

        # =====================================================
        # LABELS
        # =====================================================

        label_rect = QRectF(
            outer.left(),
            outer.bottom() - 82,
            outer.width(),
            60
        )

        painter.setPen(
            QColor("#F8FAFC")
        )

        value_font = QFont("Orbitron")

        value_font.setPointSize(18)
        value_font.setBold(True)

        painter.setFont(value_font)

        painter.drawText(
            label_rect,
            Qt.AlignCenter,
            f"{self.current_temp:.1f} °C"
        )

        # =====================================================
        # SIDE LABELS
        # =====================================================

        side_font = QFont("Inter")
        side_font.setPointSize(11)
        side_font.setBold(True)

        painter.setFont(side_font)

        labels = [
            ("HOT", "#FF3B30", 0.15),
            ("WARM", "#FF9500", 0.35),
            ("OPTIMAL", "#FFD60A", 0.52),
            ("COOL", "#00BFFF", 0.72),
            ("COLD", "#2563EB", 0.90),
        ]

        sx = min(
            tube_rect.right() + 28,
            outer.right() - 90
        )

        for text, c, ratio_y in labels:

            y = chamber.top() + (
                chamber.height() * ratio_y
            )

            painter.setPen(QColor(c))

            painter.drawLine(
                int(tube_rect.right() + 12),
                int(y),
                int(sx - 8),
                int(y)
            )

            painter.drawText(
                QRectF(
                    sx,
                    y - 12,
                    100,
                    24
                ),
                Qt.AlignLeft | Qt.AlignVCenter,
                text
            )

class RectanglePreview(QWidget):
    def __init__(self, controller: "MachineController", state: "AppState") -> None:
        super().__init__()
        self.controller = controller
        self.state = state
        self.setMinimumSize(300, 300)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.state.changed.connect(self.update) # This is the reactive redraw system.

    def paintEvent(self, event) -> None:

        BED_W = 170.0
        BED_H = 250.0

        p = self.state.params

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # =========================================================
        # SAFE PADDING
        # =========================================================

        padding = 40.0

        avail_w = self.width() - padding * 2
        avail_h = self.height() - padding * 2

        if avail_w <= 0 or avail_h <= 0:
            return

        # =========================================================
        # KEEP BED ASPECT RATIO
        # =========================================================

        bed_ratio = BED_W / BED_H
        area_ratio = avail_w / avail_h

        if area_ratio > bed_ratio:
            # limited by height
            draw_h = avail_h
            draw_w = draw_h * bed_ratio
        else:
            # limited by width
            draw_w = avail_w
            draw_h = draw_w / bed_ratio

        ox = (self.width() - draw_w) / 2.0
        oy = (self.height() - draw_h) / 2.0

        # =========================================================
        # MM → PIXEL CONVERSION
        # =========================================================

        def mx(x_mm: float) -> float:
            return ox + (x_mm / BED_W) * draw_w

        def my(y_mm: float) -> float:
            return oy + draw_h - (y_mm / BED_H) * draw_h

        # =========================================================
        # PANEL BACKGROUND
        # =========================================================

        bg_rect = QRectF(
            ox - 10,
            oy - 10,
            draw_w + 20,
            draw_h + 20
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 40))
        painter.drawRoundedRect(bg_rect, 18, 18)

        # =========================================================
        # SAFE AREA
        # =========================================================

        sx0 = float(p.safe_x_min)
        sx1 = float(p.safe_x_max)
        sy0 = float(p.safe_y_min)
        sy1 = float(p.safe_y_max)

        rx = mx(sx0)
        ry = my(sy1)

        rw = mx(sx1) - mx(sx0)
        rh = my(sy0) - my(sy1)

        safe_rect = QRectF(rx, ry, rw, rh)

        painter.setPen(QPen(QColor(120, 180, 255), 2))
        painter.setBrush(Qt.NoBrush)

        painter.drawRoundedRect(safe_rect, 4, 4)

        # =========================================================
        # CENTER RECTANGLE (RESPONSIVE)
        # =========================================================

        center_w = rw * 0.28
        center_h = rh * 0.18

        center_rect = QRectF(
            rx + (rw - center_w) / 2,
            ry + (rh - center_h) / 2,
            center_w,
            center_h
        )

        painter.drawRoundedRect(center_rect, 4, 4)

        # =========================================================
        # ACTIVE RECTANGLES
        # =========================================================

        try:
            rectangles = self.controller._get_active_rectangles()
            valid = True

        except Exception:
            rectangles = []
            valid = False

        painter.setPen(
            QPen(
                QColor("#00FF9C" if valid else "#FF4D4D"),
                2
            )
        )

        for axis, rect in rectangles:

            x0, x1, y0, y1 = rect

            rrx = mx(x0)
            rry = my(y1)

            rrw = mx(x1) - mx(x0)
            rrh = my(y0) - my(y1)

            rect_obj = QRectF(
                rrx,
                rry,
                rrw,
                rrh
            )

            painter.drawRoundedRect(rect_obj, 3, 3)
 

class MainWindow(QMainWindow):
    def __init__(self, state: AppState, controller: MachineController) -> None:
        super().__init__()
        self.state = state
        self.controller = controller

        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()

        self.player.setAudioOutput(self.audio_output)

        # optional volume
        self.audio_output.setVolume(0.5)

        # load music file
        music_path = os.path.abspath("assets/info_music.mp3")

        self.player.setSource(
            QUrl.fromLocalFile(music_path)
        )

        self.player.pause()

        self.setWindowTitle("Optimus Prime - Microfiber Machine Interface v3.0")
        self.setMinimumSize(QSize(1100, 780))

        icon_path = os.path.abspath(
            "assets/optimus_icon.ico"
        )

        self.setWindowIcon(
            QIcon(icon_path)
        )

        root = QWidget()
        
        # QHBoxLayout = horizontal
        root_layout = QHBoxLayout(root) 

        # remove padding and margin
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        sidebar_container = QWidget()
        

        sidebar_container.setStyleSheet(f"""
            background-color: #F8FAFC;
        """)

        separator = QFrame()

        separator.setFixedWidth(2)

        separator.setStyleSheet(f"""
            background-color: rgba(148, 163, 184, 90);
        """)

        sidebar_layout = QVBoxLayout(sidebar_container)

        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)


        sidebar_header = QWidget()

        sidebar_header.setStyleSheet(f"""
            QWidget {{
                background-color: #E2E8F0;
            }}
        """)

        header_layout = QHBoxLayout(sidebar_header)

        header_layout.setContentsMargins(20, 24, 20, 24)
        header_layout.setAlignment(Qt.AlignVCenter)

        header_layout.setSpacing(14)

        logo = QLabel()

        pix = QPixmap("assets/optimus_icon.ico")

        logo.setPixmap(
            pix.scaled(
                42,
                42,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        logo.setFixedSize(42, 42)

        text_container = QWidget()

        text_layout = QVBoxLayout(text_container)

        text_layout.setContentsMargins(0, 0, 0, 0)

        text_layout.setSpacing(2)

        brand_title = QLabel("OPTIMUS PRIME")

        brand_subtitle = QLabel(
            "Microfiber Machine Interface"
        )

        brand_subtitle.setStyleSheet(f"""
            QLabel {{
                color: #475569;
                font-size: 11px;
                font-weight: 500;
            }}
        """)

        brand_title.setStyleSheet(f"""
            QLabel {{
                color: #0F172A;
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 2px;
            }}
        """)

        text_layout.addWidget(brand_title)
        text_layout.addWidget(brand_subtitle)

        header_layout.addWidget(logo)
        header_layout.addWidget(text_container)
        

        self.sidebar = QListWidget()
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: #F8FAFC;
                border: none;
                padding-top: 24px;
                padding-left: 10px;
                padding-right: 10px;
                outline: 0;
            }}

            QListWidget::item {{
                background-color: transparent;
                color: #0F172A;
                border-radius: 12px;
                padding: 14px 22px;
                margin-bottom: 8px;
                font-size: 14px;
                font-weight: 600;
                margin-left: 6px;
                margin-right: 6px;
            }}

            QListWidget::item:selected {{
                background-color: #DBEAFE;
                color: #0F172A;
                border-left: 4px solid #2563EB;
            }}

            QListWidget::item:hover {{
                background-color: #E2E8F0;
                color: #0F172A;
            }}
        """)

        self.sidebar.setFixedWidth(240)
        sidebar_font = QFont("Inter")
        sidebar_font.setPointSize(11)
        sidebar_font.setBold(False)
        self.sidebar.setFont(sidebar_font)

        # remove default border
        self.sidebar.setFrameShape(QFrame.NoFrame) 
        self.sidebar.setSpacing(6)

        # multiple pages stacked on top of each other
        self.stack = QStackedWidget()

        sidebar_layout.addWidget(sidebar_header)
        sidebar_layout.addWidget(self.sidebar)
        root_layout.addWidget(sidebar_container)
        root_layout.addWidget(separator)
        root_layout.addWidget(self.stack, 1)
        
        # MainWindow
        # └── root QWidget
        #     └── QHBoxLayout
        #         ├── QListWidget (sidebar)
        #         └── QStackedWidget (pages)

        self.page_welcome = WelcomePage(self)
        self.page_fiber_layout = FiberLayoutPage(self)
        self.page_draw_settings = DrawSettingsPage(self)
        self.page_temperature = TemperaturePage(self)
        self.page_summary = SummaryPage(self)
        self.page_connection = ConnectionPage(self)
        
        self._add_page("Welcome", self.page_welcome)
        self._add_page("Fiber Layout", self.page_fiber_layout)
        self._add_page("Draw Settings", self.page_draw_settings)
        self._add_page("Temperature", self.page_temperature)
        self._add_page("Summary", self.page_summary)
        self._add_page("Connection", self.page_connection)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)

        self._set_project_mode(False)
        self.sidebar.setCurrentRow(0)

        self.controller.connection_changed.connect(self.page_connection.on_connection_changed)
        self.state.log.connect(self.page_connection.append_log)

    def _add_page(
            self, 
            title: str, 
            widget: QWidget,
            icon: QIcon | None = None,) -> None:
        self.stack.addWidget(widget)
        item = QListWidgetItem(title)

        if icon is not None:
            item.setIcon(icon)
        self.sidebar.addItem(item)

    # enables/disables sidebar pages
    def _set_project_mode(self, enabled: bool) -> None:
        for i in range(1, self.sidebar.count()):
            item = self.sidebar.item(i)
            item.setFlags(item.flags() | Qt.ItemIsEnabled if enabled else item.flags() & ~Qt.ItemIsEnabled)

    def go(self, name: str) -> None:
        mapping = {"Welcome": 0, "Fiber Layout": 1, "Draw Settings": 2, "Temperature": 3, "Summary": 4, "Connection": 5}
        self.sidebar.setCurrentRow(mapping[name])
        # its the same as: user clicked in Draw, so the sidebar changes and emits a signal, the Qt gets this signal and changes the page - see a full explanation on helpfullDocuments/aboutCurrentVersionFunctions

    def start_new_project(self) -> None:
        self._set_project_mode(True)
        self.setWindowTitle("Nanofiber Machine - New Project")
        self.go("Fiber Layout")
        self.controller.log("New project")
    
    def load_project_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Project",
            "",
            "JSON files (*.json)"
        )

        if not path:
            return

        ok = self.controller.load_project(path)

        if not ok:

            QMessageBox.critical(
                self,
                "Error",
                "Could not load project."
            )

            return

        self._set_project_mode(True)

        self.setWindowTitle(
            f"Nanofiber Machine - {Path(path).name}"
        )

        self.go("Draw")

    def save_project_dialog(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON files (*.json)")
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        ok = self.controller.save_project(path)

        if not ok:
            QMessageBox.critical(
                self,
                "Error",
                "Could not save project."
            )

    def save_pdf_dialog(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF files (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        ok = self.controller.save_pdf(path)

        if not ok:
            QMessageBox.critical(self, "Error", f"Could not save PDF")

    def show_info(self) -> None:
        self.player.stop()
        self.player.setPosition(107000)
        self.player.play()

        msg = QMessageBox(self)

        msg.setWindowTitle("Optimus Prime")
        msg.setText(INFO_TEXT)

        # remove default info icon
        msg.setIcon(QMessageBox.NoIcon)

        icon_path = os.path.abspath("assets/optimus_icon.ico")

        # custom window icon
        msg.setWindowIcon(
            QIcon(icon_path)
        )

        # custom content icon
        msg.setIconPixmap(
            QPixmap(icon_path).scaled(
                96,
                96,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        msg.exec()

        self.player.stop()

class WelcomePage(QWidget):
    def __init__(self, mw: MainWindow) -> None:
        super().__init__()
        self.mw = mw

        self.bg = QPixmap(
            "assets/optimus_bg.jpeg"
        )

        root = QVBoxLayout(self)

        root.setContentsMargins(40, 40, 40, 40)

        # top spacer
        root.addStretch()

        hero = QFrame()

        hero.setMaximumWidth(720)

        hero.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(15, 23, 42, 205);
                border: 1px solid rgba(255,255,255,20);
                border-radius: 24px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 180))

        hero.setGraphicsEffect(shadow)

        hero_layout = QVBoxLayout(hero)

        hero_layout.setContentsMargins(50, 50, 50, 50)

        hero_layout.setSpacing(24)


        title = _title_label("OPTIMUS PRIME")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(f"""
            QLabel {{
                color: white;
                background: transparent;
                letter-spacing: 4px;
                border: none;
            }}
        """)

        subtitle = _section_label(
            "MicroFiber Machine Interface"
        )

        subtitle.setAlignment(Qt.AlignCenter)

        desc = _subtle_label(
            "Advanced robotics interface "
            "for precision microfiber fabrication "
            "and machine control."
        )

        desc.setAlignment(Qt.AlignCenter)

        desc.setMaximumWidth(520)

        btn_row = QHBoxLayout()

        btn_row.setSpacing(18)

        self.btn_new = _primary_button("New")
        self.btn_load = _secondary_button("Load")
        self.btn_info = _secondary_button("Info")

        self.btn_new.setFixedSize(180, 48)
        self.btn_load.setFixedSize(180, 48)
        self.btn_info.setFixedSize(120, 42)

        btn_row.addWidget(self.btn_new)
        btn_row.addWidget(self.btn_load)

        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        hero_layout.addWidget(desc)

        hero_layout.addSpacing(12)

        hero_layout.addLayout(btn_row)

        hero_layout.addWidget(
            self.btn_info,
            0,
            Qt.AlignCenter,
        )

        # center panel
        root.addWidget(
            hero,
            0,
            Qt.AlignCenter,
        )

        # bottom spacer
        root.addStretch()
        self.btn_new.clicked.connect(self.mw.start_new_project)
        self.btn_load.clicked.connect(self.mw.load_project_dialog)
        self.btn_info.clicked.connect(self.mw.show_info)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        scaled = self.bg.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

        x = (self.width() - scaled.width()) / 2
        y = (self.height() - scaled.height()) / 2

        painter.drawPixmap(
            int(x),
            int(y),
            scaled,
        )

        # allow Qt to paint child widgets/layouts correctly
        super().paintEvent(event)


class FiberLayoutPage(QWidget):
    def __init__(self, mw: MainWindow) -> None:
        super().__init__()

        self.mw = mw
        self.state = mw.state
        self.controller = mw.controller

        self.bg = QPixmap("assets/layout_bg.png")

        # =========================================================
        # MAIN LAYOUT
        # =========================================================

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        # =========================================================
        # LEFT PANEL — PARAMETERS
        # =========================================================

        left_panel = QFrame()
        left_panel.setObjectName("controlPanel")
        left_panel.setFixedWidth(360)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(22, 22, 22, 22)
        left_layout.setSpacing(18)

        title = QLabel("FIBER LAYOUT")
        title.setObjectName("pageTitle")
        left_layout.addWidget(title)

        # =========================================================
        # INPUTS
        # =========================================================

        self.fiber_orientation = QComboBox()
        self.fiber_orientation.addItems(["Horizontal", "Vertical", "Both"])
        self.fiber_orientation.currentTextChanged.connect(
            lambda t: self.state.set_param("fiber_orientation", t)
        )

        self.fiber_length = QDoubleSpinBox()
        self.fiber_length.setDecimals(2)
        self.fiber_length.setRange(0.0, 10000.0)
        self.fiber_length.setSingleStep(1.0)
        self.fiber_length.valueChanged.connect(
            lambda v: self.state.set_param("fiber_length", float(v))
        )

        self.fiber_width = QDoubleSpinBox()
        self.fiber_width.setDecimals(2)
        self.fiber_width.setRange(0.0, 10000.0)
        self.fiber_width.setSingleStep(1.0)
        self.fiber_width.valueChanged.connect(
            lambda v: self.state.set_param("fiber_width", float(v))
        )

        self.fiber_spacing = QDoubleSpinBox()
        self.fiber_spacing.setDecimals(2)
        self.fiber_spacing.setRange(0.01, 10000.0)
        self.fiber_spacing.setSingleStep(0.1)
        self.fiber_spacing.valueChanged.connect(
            lambda v: self.state.set_param("fiber_spacing", float(v))
        )

        self.start_x = QDoubleSpinBox()
        self.start_x.setDecimals(2)
        self.start_x.setRange(-1000.0, 1000.0)
        self.start_x.setSingleStep(1.0)
        self.start_x.valueChanged.connect(
            lambda v: self.state.set_param("start_x", float(v))
        )

        self.start_y = QDoubleSpinBox()
        self.start_y.setDecimals(2)
        self.start_y.setRange(-1000.0, 1000.0)
        self.start_y.setSingleStep(1.0)
        self.start_y.valueChanged.connect(
            lambda v: self.state.set_param("start_y", float(v))
        )

        # =========================================================
        # PARAMETER CARDS
        # =========================================================

        left_layout.addWidget(
            self.create_param_widget(
                "Orientation",
                self.fiber_orientation
            )
        )

        left_layout.addWidget(
            self.create_param_widget(
                "Length (mm)",
                self.fiber_length
            )
        )

        left_layout.addWidget(
            self.create_param_widget(
                "Width (mm)",
                self.fiber_width
            )
        )

        left_layout.addWidget(
            self.create_param_widget(
                "Spacing (mm)",
                self.fiber_spacing
            )
        )

        left_layout.addWidget(
            self.create_param_widget(
                "Starting X (mm)",
                self.start_x
            )
        )

        left_layout.addWidget(
            self.create_param_widget(
                "Starting Y (mm)",
                self.start_y
            )
        )

        left_layout.addStretch()

        # =========================================================
        # NEXT BUTTON
        # =========================================================

        self.btn_next = QPushButton("NEXT →")
        self.btn_next.setFixedHeight(52)
        self.btn_next.clicked.connect(
            lambda: self.mw.go("Draw Settings")
        )

        left_layout.addWidget(self.btn_next)

        # =========================================================
        # RIGHT PANEL — PREVIEW
        # =========================================================

        right_panel = QFrame()
        right_panel.setObjectName("previewPanel")

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(18)

        preview_title = QLabel("USABLE DRAWING AREA")
        preview_title.setObjectName("previewTitle")

        right_layout.addWidget(preview_title)

        self.preview = RectanglePreview(
            self.controller,
            self.state
        )

      
        self.preview.setObjectName("previewWidget")

        right_layout.addWidget(self.preview, 1)

        # =========================================================
        # ADD PANELS
        # =========================================================

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

        # =========================================================
        # STYLE
        # =========================================================

        self.setStyleSheet("""
        
        QWidget {
            color: white;
            font-family: Inter;
            font-size: 14px;
        }

        /* =====================================================
           LEFT CONTROL PANEL
        ===================================================== */

        QFrame#controlPanel {
            background: rgba(8, 15, 28, 220);
            border: 1px solid rgba(0, 180, 255, 90);
            border-radius: 22px;
        }

        /* =====================================================
           RIGHT PREVIEW PANEL
        ===================================================== */

        QFrame#previewPanel {
            background: rgba(5, 12, 22, 190);
            border: 1px solid rgba(0, 180, 255, 70);
            border-radius: 24px;
        }

        /* =====================================================
           TITLES
        ===================================================== */

        QLabel#pageTitle {
            font-size: 34px;
            font-weight: 800;
            color: white;
            letter-spacing: 2px;
            padding-bottom: 12px;
        }

        QLabel#previewTitle {
            font-size: 13px;
            font-weight: 700;
            color: rgb(0, 220, 255);
            letter-spacing: 3px;
        }

        /* =====================================================
           PARAMETER CARD
        ===================================================== */

        QFrame#paramCard {
            background: rgba(14, 24, 38, 235);
            border: 1px solid rgba(0, 200, 255, 70);
            border-radius: 16px;
        }

        QLabel#paramTitle {
            color: rgb(0, 220, 255);
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            padding-left: 2px;
        }

        /* =====================================================
           INPUTS
        ===================================================== */

        QDoubleSpinBox,
        QComboBox {
            background: transparent;
            border: none;
            color: white;
            font-size: 18px;
            font-weight: 500;
            padding-top: 6px;
            padding-bottom: 4px;
        }

        QDoubleSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 22px;
            border: none;
            background: transparent;
            margin-right: 6px;
        }
                           
        QDoubleSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 22px;
            border: none;
            background: transparent;
            margin-right: 6px;
        }
                           
        QDoubleSpinBox::up-arrow {
            image: url(assets/arrow_up_cyan.svg);
            width: 14px;
            height: 14px;
        }
                           
        QDoubleSpinBox::down-arrow {
            image: url(assets/arrow_down_cyan.svg);
            width: 14px;
            height: 14px;
        }
                           
        QDoubleSpinBox::up-button:hover,
        QDoubleSpinBox::down-button:hover {
            background: rgba(0, 220, 255, 20);
            border-radius: 6px;
        }

        QComboBox::drop-down {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 22px;
            border: none;
            background: transparent;
            padding-right: 6px;
        }

        QComboBox::down-arrow {
            image: url(assets/arrow_down_cyan.svg);
            width: 14px;
            height: 14px;
        }

        QComboBox::drop-down:hover {
            background: rgba(0, 220, 255, 20);
            border-radius: 6px;
        }                  

        QComboBox QAbstractItemView {
            background: rgb(10, 18, 30);
            color: white;
            font-size: 14px;
            font-family: Inter;               
            selection-background-color: rgb(0, 120, 255);
            border: 1px solid rgb(0, 180, 255);
        }

        QComboBox QAbstractItemView::item:hover {
            background: rgba(0, 220, 255, 35);
            color: rgb(0, 220, 255);
            border: none;
        }

                           
        
        /* =====================================================
           BUTTON
        ===================================================== */

        QPushButton {
            background: qlineargradient(
                x1:0, y1:0,
                x2:1, y2:0,
                stop:0 rgba(0, 110, 255, 220),
                stop:1 rgba(0, 180, 255, 220)
            );

            border: 1px solid rgb(0, 220, 255);
            border-radius: 16px;

            color: white;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 2px;

            padding: 12px;
        }

        QPushButton:hover {
            border: 1px solid rgb(100, 240, 255);
            background: rgba(0, 180, 255, 255);
        }

        QPushButton:pressed {
            padding-top: 14px;
        }

        /* =====================================================
           PREVIEW
        ===================================================== */

        QWidget#previewWidget {
            background: rgba(0, 0, 0, 80);
            border-radius: 22px;
            border: 1px solid rgba(0, 180, 255, 60);
        }

        """)

        # =========================================================
        # STATE SYNC
        # =========================================================

        self.state.changed.connect(self._sync_from_state)

        self._sync_from_state()

    # =============================================================
    # PARAM CARD
    # =============================================================

    def create_param_widget(
        self,
        title: str,
        widget: QWidget
    ) -> QWidget:

        container = QFrame()
        container.setObjectName("paramCard")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        label = QLabel(title.upper())
        label.setObjectName("paramTitle")

        layout.addWidget(label)
        layout.addWidget(widget)

        return container

    # =============================================================
    # BACKGROUND
    # =============================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        scaled = self.bg.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

        x = (self.width() - scaled.width()) / 2
        y = (self.height() - scaled.height()) / 2

        painter.drawPixmap(
            int(x),
            int(y),
            scaled,
        )

        super().paintEvent(event)

    # =============================================================
    # STATE UPDATE
    # =============================================================

    @Slot()
    def _sync_from_state(self) -> None:

        p = self.state.params

        self.fiber_orientation.blockSignals(True)
        self.fiber_orientation.setCurrentText(
            str(p.fiber_orientation)
        )
        self.fiber_orientation.blockSignals(False)

        for w, val in [
            (self.fiber_length, p.fiber_length),
            (self.fiber_width, p.fiber_width),
            (self.fiber_spacing, p.fiber_spacing),
            (self.start_x, p.start_x),
            (self.start_y, p.start_y),
        ]:

            w.blockSignals(True)
            w.setValue(float(val))
            w.blockSignals(False)


class DrawSettingsPage(QWidget):

    def __init__(self, mw: MainWindow) -> None:
        super().__init__()

        self.mw = mw
        self.state = mw.state
        self.controller = mw.controller

        self.bg = QPixmap("assets/layout_bg.png")

        # =========================================================
        # MAIN LAYOUT
        # =========================================================

        root = QHBoxLayout(self)

        root.setContentsMargins(
            24,
            24,
            24,
            24
        )

        root.setSpacing(24)

        # =========================================================
        # MAIN PANEL
        # =========================================================

        panel = QFrame()

        panel.setObjectName(
            "controlPanel"
        )

        panel_layout = QVBoxLayout(panel)

        panel_layout.setContentsMargins(
            28,
            28,
            28,
            28
        )

        panel_layout.setSpacing(22)

        # =========================================================
        # TITLE
        # =========================================================

        title = QLabel("DRAW SETTINGS")

        title.setObjectName(
            "pageTitle"
        )

        panel_layout.addWidget(title)

        # =========================================================
        # GRID
        # =========================================================

        grid = QGridLayout()

        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        # =========================================================
        # SPEED CONTROLS
        # =========================================================

        self.speed = QSpinBox()

        self.speed.setRange(
            100,
            5000
        )

        self.speed.setSingleStep(100)

        self.speed.valueChanged.connect(
            lambda v: self.state.set_param(
                "speed",
                int(v)
            )
        )

        self.btn_slow = QPushButton("SLOW")
        self.btn_medium = QPushButton("MEDIUM")
        self.btn_fast = QPushButton("FAST")

        self.btn_slow.clicked.connect(
            lambda: self.speed.setValue(800)
        )

        self.btn_medium.clicked.connect(
            lambda: self.speed.setValue(1800)
        )

        self.btn_fast.clicked.connect(
            lambda: self.speed.setValue(3200)
        )

        speed_container = QFrame()
        speed_container.setObjectName("paramCard")

        speed_layout = QVBoxLayout(speed_container)

        speed_layout.setContentsMargins(
            18,
            16,
            18,
            16
        )

        speed_layout.setSpacing(14)

        speed_title = QLabel("SPEED")
        speed_title.setObjectName("paramTitle")

        speed_layout.addWidget(speed_title)

        preset_layout = QHBoxLayout()

        preset_layout.setSpacing(10)

        preset_layout.addWidget(self.btn_slow)
        preset_layout.addWidget(self.btn_medium)
        preset_layout.addWidget(self.btn_fast)

        speed_layout.addLayout(preset_layout)

        speed_layout.addWidget(
            self.create_inline_param(
                "CUSTOM SPEED (MM/MIN)",
                self.speed
            )
        )

        # =========================================================
        # DROPLET AMOUNT
        # =========================================================

        self.amount = QDoubleSpinBox()

        self.amount.setDecimals(3)
        self.amount.setRange(0.0, 1000.0)
        self.amount.setSingleStep(0.1)

        self.amount.valueChanged.connect(
            lambda v: self.state.set_param(
                "droplet_amount",
                float(v)
            )
        )

        # =========================================================
        # PAUSE
        # =========================================================

        self.pause_ms = QSpinBox()

        self.pause_ms.setRange(
            0,
            600000
        )

        self.pause_ms.valueChanged.connect(
            lambda v: self.state.set_param(
                "pause_ms",
                int(v)
            )
        )

        # =========================================================
        # Z-HOP
        # =========================================================

        self.zhop = QDoubleSpinBox()

        self.zhop.setDecimals(2)
        self.zhop.setRange(0.0, 1000.0)
        self.zhop.setSingleStep(0.5)

        self.zhop.valueChanged.connect(
            lambda v: self.state.set_param(
                "z_hop",
                float(v)
            )
        )

        # =========================================================
        # Z-OFFSET
        # =========================================================

        self.zoffset = QDoubleSpinBox()

        self.zoffset.setDecimals(3)
        self.zoffset.setRange(-1000.0, 1000.0)
        self.zoffset.setSingleStep(0.01)

        self.zoffset.valueChanged.connect(
            lambda v: self.state.set_param(
                "z_offset",
                float(v)
            )
        )

        # =========================================================
        # TOGGLE BUTTONS
        # =========================================================

        self.btn_afterdrop = QPushButton(
            "AFTERDROP"
        )

        self.btn_afterdrop.setObjectName(
            "toggleButton"
        )

        self.btn_afterdrop.setCheckable(True)

        self.btn_afterdrop.toggled.connect(
            lambda v: self.state.set_param(
                "afterdrop",
                bool(v)
            )
        )

        self.btn_afterdrop.toggled.connect(
            lambda _: self._update_toggle_texts()
        )

        self.btn_clean = QPushButton(
            "CLEAN"
        )

        self.btn_clean.setObjectName(
            "toggleButton"
        )

        self.btn_clean.setCheckable(True)

        self.btn_clean.toggled.connect(
            lambda v: self.state.set_param(
                "clean",
                bool(v)
            )
        )

        self.btn_clean.toggled.connect(
            lambda _: self._update_toggle_texts()
        )

        # =========================================================
        # TEST BUTTON
        # =========================================================

        self.btn_test_z = QPushButton(
            "TEST Z-OFFSET"
        )

        self.btn_test_z.setObjectName(
            "secondaryAction"
        )

        self.btn_test_z.setFixedSize(240, 52)

        self.btn_test_z.clicked.connect(
            self.controller.test_zoffset
        )

        # =========================================================
        # NEXT BUTTON
        # =========================================================

        self.btn_next = QPushButton(
            "NEXT →"
        )

        self.btn_next.setFixedSize(240, 52)
        

        self.btn_next.clicked.connect(
            lambda: self.mw.go("Temperature")
        )

        # =========================================================
        # GRID INSERTION
        # =========================================================

        grid.addWidget(
            speed_container,
            0,
            0,
            1,
            2
        )

        grid.addWidget(
            self.create_param_widget(
                "Droplet Amount",
                self.amount
            ),
            1,
            0
        )

        grid.addWidget(
            self.create_param_widget(
                "Pause (ms)",
                self.pause_ms
            ),
            1,
            1
        )

        grid.addWidget(
            self.create_param_widget(
                "Z-Hop (mm)",
                self.zhop
            ),
            2,
            0
        )

        grid.addWidget(
            self.create_toggle_widget(
                self.btn_afterdrop
            ),
            2,
            1
        )

        grid.addWidget(
            self.create_param_widget(
                "Z-Offset (mm)",
                self.zoffset
            ),
            3,
            0
        )

        grid.addWidget(
            self.create_toggle_widget(
                self.btn_clean
            ),
            3,
            1
        )

        # =========================================================
        # TEST BUTTON ROW
        # =========================================================

        test_row = QHBoxLayout()

        test_row.addWidget(
            self.btn_test_z,
            alignment=Qt.AlignLeft
        )

        test_row.addStretch()

        grid.addLayout(
            test_row,
            4,
            0,
            1,
            2
        )

        # =========================================================
        # NEXT BUTTON ROW
        # =========================================================

        next_row = QHBoxLayout()

        next_row.addStretch()

        next_row.addWidget(
            self.btn_next,
            alignment=Qt.AlignRight
        )

        grid.addLayout(
            next_row,
            5,
            0,
            1,
            2
        )

        panel_layout.addLayout(grid)

        root.addWidget(panel)

        # =========================================================
        # STYLE
        # =========================================================

        self.setStyleSheet("""

        QWidget {
            color: white;
            font-family: Inter;
            font-size: 14px;
        }

        /* =====================================================
           PANEL
        ===================================================== */

        QFrame#controlPanel {
            background: rgba(8, 15, 28, 220);

            border: 1px solid rgba(0, 180, 255, 90);

            border-radius: 24px;
        }

        /* =====================================================
           TITLES
        ===================================================== */

        QLabel#pageTitle {
            font-size: 34px;
            font-weight: 800;

            color: white;

            letter-spacing: 2px;

            padding-bottom: 12px;
        }

        QLabel#paramTitle {
            color: rgb(0, 220, 255);

            font-size: 11px;
            font-weight: 800;

            letter-spacing: 2px;

            padding-left: 2px;
        }

        /* =====================================================
           PARAMETER CARD
        ===================================================== */

        QFrame#paramCard {
            background: rgba(14, 24, 38, 235);

            border: 1px solid rgba(0, 200, 255, 70);

            border-radius: 16px;
        }

        /* =====================================================
           INPUTS
        ===================================================== */

        QDoubleSpinBox,
        QSpinBox {
            background: transparent;
            border: none;
            color: white;
            font-size: 18px;
            font-weight: 500;
            padding-top: 6px;
            padding-bottom: 2px;
        }

        /* =====================================================
           SPINBOX BUTTONS
        ===================================================== */

        QDoubleSpinBox::up-button,
        QSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;

            width: 22px;

            border: none;

            background: transparent;

            margin-right: 6px;
        }

        QDoubleSpinBox::down-button,
        QSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;

            width: 22px;

            border: none;

            background: transparent;

            margin-right: 6px;
        }

        QDoubleSpinBox::up-arrow,
        QSpinBox::up-arrow {
            image: url(assets/arrow_up_cyan.svg);

            width: 14px;
            height: 14px;
        }

        QDoubleSpinBox::down-arrow,
        QSpinBox::down-arrow {
            image: url(assets/arrow_down_cyan.svg);

            width: 14px;
            height: 14px;
        }

        /* =====================================================
           BUTTONS
        ===================================================== */

        QPushButton {
            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 110, 255, 220),
                stop:1 rgba(0, 180, 255, 220)
            );

            border: 1px solid rgb(0, 220, 255);

            border-radius: 14px;

            color: white;

            font-size: 14px;
            font-weight: 700;

            letter-spacing: 1px;

            padding: 12px;
        }

        QPushButton:hover {
            border: 1px solid rgb(100, 240, 255);

            background: rgba(0, 180, 255, 255);
        }

        QPushButton:pressed {
            padding-top: 14px;
        }

        /* =====================================================
        SECONDARY ENGINEERING BUTTON
        ===================================================== */

        QPushButton#secondaryAction {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(255, 140, 0, 180),
                stop:1 rgba(255, 180, 0, 180)
            );

            border: 1px solid rgb(255, 190, 50);

            color: white;
        }

        QPushButton#secondaryAction:hover {

            background: rgba(255, 170, 0, 220);

            border: 1px solid rgb(255, 220, 120);
        }

        /* =====================================================
        TOGGLE OFF
        ===================================================== */

        QPushButton#toggleButton:!checked {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(160, 20, 20, 220),
                stop:1 rgba(220, 40, 40, 220)
            );

            border: 1px solid rgb(255, 80, 80);

            color: white;
        }

        /* =====================================================
        TOGGLE ON
        ===================================================== */

        QPushButton#toggleButton:checked {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 150, 90, 220),
                stop:1 rgba(0, 210, 120, 220)
            );

            border: 1px solid rgb(120, 255, 180);

            color: white;
        }

        """)

        # =========================================================
        # STATE
        # =========================================================

        self.state.changed.connect(
            self._sync_from_state
        )

        self._sync_from_state()

    # =============================================================
    # PARAM CARD
    # =============================================================

    def create_param_widget(
        self,
        title: str,
        widget: QWidget
    ) -> QWidget:

        container = QFrame()

        container.setObjectName(
            "paramCard"
        )

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            16,
            12,
            16,
            12
        )

        layout.setSpacing(4)

        label = QLabel(
            title.upper()
        )

        label.setObjectName(
            "paramTitle"
        )

        layout.addWidget(label)
        layout.addWidget(widget)

        return container

    # =============================================================
    # INLINE PARAM
    # =============================================================

    def create_inline_param(
        self,
        title: str,
        widget: QWidget
    ) -> QWidget:

        container = QWidget()

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(4)

        label = QLabel(title)

        label.setObjectName(
            "paramTitle"
        )

        layout.addWidget(label)
        layout.addWidget(widget)

        return container
    
    def _update_toggle_texts(self):

        self.btn_afterdrop.setText(
            f"AFTERDROP • {'ON' if self.btn_afterdrop.isChecked() else 'OFF'}"
        )

        self.btn_clean.setText(
            f"CLEAN • {'ON' if self.btn_clean.isChecked() else 'OFF'}"
        )

    # =============================================================
    # TOGGLE CARD
    # =============================================================

    def create_toggle_widget(
        self,
        button: QPushButton
    ) -> QWidget:

        container = QFrame()

        container.setObjectName(
            "paramCard"
        )

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        layout.addStretch()

        layout.addWidget(button)

        layout.addStretch()

        return container

    # =============================================================
    # BACKGROUND
    # =============================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        scaled = self.bg.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

        x = (
            self.width() - scaled.width()
        ) / 2

        y = (
            self.height() - scaled.height()
        ) / 2

        painter.drawPixmap(
            int(x),
            int(y),
            scaled,
        )

        super().paintEvent(event)

    # =============================================================
    # STATE UPDATE
    # =============================================================

    @Slot()
    def _sync_from_state(self) -> None:

        p = self.state.params

        widgets = [
            (self.speed, p.speed),
            (self.pause_ms, p.pause_ms),
            (self.zhop, p.z_hop),
            (self.zoffset, p.z_offset),
        ]

        for w, val in widgets:

            w.blockSignals(True)

            w.setValue(val)

            w.blockSignals(False)

        self.btn_afterdrop.blockSignals(True)

        self.btn_afterdrop.setChecked(
            bool(p.clean)
        )

        self.btn_afterdrop.blockSignals(False)

        self.btn_clean.blockSignals(True)

        self.btn_clean.setChecked(
            bool(p.clean)
        )
        
        self.btn_clean.blockSignals(False)
        self._update_toggle_texts()


# =========================================================
# TEMPERATURE PAGE
# =========================================================

class TemperaturePage(QWidget):

    def __init__(self, mw: MainWindow) -> None:
        super().__init__()

        self.mw = mw
        self.state = mw.state
        self.controller = mw.controller

        self.bg = QPixmap("assets/layout_bg.png")

        # =====================================================
        # ROOT
        # =====================================================

        root = QHBoxLayout(self)

        root.setContentsMargins(
            24,
            24,
            24,
            24
        )

        root.setSpacing(22)

        # =====================================================
        # LEFT PANEL
        # =====================================================

        left_panel = QFrame()

        left_panel.setObjectName(
            "controlPanel"
        )

        left_panel.setMinimumWidth(360)

        left_layout = QVBoxLayout(left_panel)

        left_layout.setContentsMargins(
            28,
            28,
            28,
            28
        )

        left_layout.setSpacing(18)

        title = QLabel("THERMAL CONTROL")

        title.setObjectName(
            "pageTitle"
        )

        left_layout.addWidget(title)

        # =====================================================
        # CURRENT / TARGET GRID
        # =====================================================

        temp_grid = QGridLayout()

        temp_grid.setHorizontalSpacing(18)
        temp_grid.setVerticalSpacing(18)

        # CURRENT CARD

        current_card = QFrame()

        current_card.setObjectName(
            "paramCard"
        )

        current_layout = QVBoxLayout(current_card)

        current_layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        current_layout.setSpacing(8)

        current_label = QLabel("CURRENT")

        current_label.setObjectName(
            "paramTitle"
        )

        self.current_temp = QLabel("0.0 °C")

        self.current_temp.setObjectName(
            "paramValue"
        )

        current_layout.addWidget(current_label)
        current_layout.addWidget(self.current_temp)

        # TARGET CARD

        target_card = QFrame()

        target_card.setObjectName(
            "paramCard"
        )

        target_layout = QVBoxLayout(target_card)

        target_layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        target_layout.setSpacing(8)

        target_label = QLabel("TARGET")

        target_label.setObjectName(
            "paramTitle"
        )

        self.target_temp = QLabel("25.0 °C")

        self.target_temp.setObjectName(
            "paramValueBlue"
        )

        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_temp)

        temp_grid.addWidget(current_card, 0, 0)
        temp_grid.addWidget(target_card, 0, 1)

        left_layout.addStretch()
        left_layout.addLayout(temp_grid)

        # =====================================================
        # STATUS
        # =====================================================

        self.status_badge = QLabel("IDLE")

        self.status_badge.setObjectName(
            "statusBadge"
        )

        self.status_badge.setAlignment(
            Qt.AlignCenter
        )

        self.status_badge.setFixedSize(
            140,
            42
        )

        status_container = QWidget()

        status_layout = QHBoxLayout(status_container)

        status_layout.setContentsMargins(0, 0, 0, 0)

        status_layout.addStretch()
        status_layout.addWidget(self.status_badge)
        status_layout.addStretch()

        left_layout.addWidget(status_container)


        # =====================================================
        # INPUT
        # =====================================================

        self.target_input = QDoubleSpinBox()

        self.target_input.setRange(
            0,
            50
        )

        self.target_input.setDecimals(2)

        self.target_input.setSingleStep(0.5)

        self.target_input.setValue(
            float(
                self.state.params.target_temperature
            )
        )

        input_card = self.create_param_widget(
            "SET TARGET TEMPERATURE",
            self.target_input
        )

        left_layout.addSpacing(12)

        left_layout.addWidget(input_card)

        
        # =====================================================
        # APPLY BUTTON
        # =====================================================

        self.btn_apply = QPushButton(
            "APPLY TARGET"
        )

        self.btn_apply.setObjectName(
            "applyButton"
        )

        self.btn_apply.setFixedHeight(54)
        self.btn_apply.setFixedWidth(300)

        self.btn_apply.clicked.connect(
            self.apply_temperature
        )

        apply_container = QWidget()

        apply_layout = QHBoxLayout(apply_container)

        apply_layout.setContentsMargins(0, 0, 0, 0)

        apply_layout.addWidget(
            self.btn_apply,
            alignment=Qt.AlignLeft
        )

        left_layout.addWidget(apply_container)

        left_layout.addStretch()
        
        # =====================================================
        # MONITOR CARD
        # =====================================================

        monitor = QFrame()

        monitor.setObjectName(
            "monitorCard"
        )

        mon_layout = QHBoxLayout(monitor)

        mon_layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        mon_layout.setSpacing(12)

        info_icon = QLabel("i")

        info_icon.setObjectName(
            "monitorIcon"
        )

        info_icon.setAlignment(
            Qt.AlignCenter
        )

        info_icon.setFixedSize(
            38,
            38
        )

        mon_layout.addWidget(info_icon)

        txt_layout = QVBoxLayout()

        txt_layout.setSpacing(4)

        t1 = QLabel(
            "Monitoring active via M155"
        )

        t1.setObjectName(
            "monitorTitle"
        )

        t2 = QLabel(
            "Temperature feedback enabled"
        )

        t2.setObjectName(
            "monitorSubtitle"
        )

        txt_layout.addWidget(t1)
        txt_layout.addWidget(t2)

        mon_layout.addLayout(txt_layout)

        

        dot = QFrame()

        dot.setFixedSize(10, 10)

        dot.setStyleSheet("""
            background: rgb(0, 255, 120);
            border-radius: 5px;
        """)

        mon_layout.addWidget(dot)

        left_layout.addSpacing(18)

        left_layout.addWidget(monitor)

        left_layout.addStretch()

        # =====================================================
        # NEXT BUTTON
        # =====================================================

        self.btn_next = QPushButton(
            "NEXT →"
        )

        self.btn_next.setObjectName(
            "nextButton"
        )

        self.btn_next.setFixedHeight(54)
        self.btn_next.setFixedWidth(300)

        self.btn_next.clicked.connect(lambda: self.mw.go("Summary"))

        next_container = QWidget()

        next_layout = QHBoxLayout(next_container)

        next_layout.setContentsMargins(0, 0, 0, 0)

        next_layout.addWidget(
            self.btn_next,
            alignment=Qt.AlignRight
        )

        left_layout.addWidget(next_container)

        # =====================================================
        # RIGHT PANEL
        # =====================================================

        right_panel = QFrame()

        right_panel.setObjectName(
            "reactorPanel"
        )

        right_layout = QVBoxLayout(right_panel)

        right_layout.setContentsMargins(
            16,
            16,
            16,
            16
        )

        self.thermometer = ReactorThermometerWidget(
            self.state
        )

        right_layout.addWidget(
            self.thermometer,
            1
        )

        # =====================================================
        # ADD PANELS
        # =====================================================

        root.addWidget(
            left_panel,
            2
        )

        root.addWidget(
            right_panel,
            1
        )

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

        QWidget {
            color: white;
            font-family: Inter;
        }

        QFrame#controlPanel,
        QFrame#reactorPanel {

            background: rgba(8, 15, 28, 220);

            border: 1px solid rgba(0, 180, 255, 90);

            border-radius: 24px;
        }

        QLabel#pageTitle {

            font-size: 32px;
            font-weight: 800;

            color: white;

            letter-spacing: 2px;
        }

        QLabel#paramTitle {

            color: rgb(0, 220, 255);

            font-size: 11px;

            font-weight: 800;

            letter-spacing: 2px;
        }

        QLabel#paramValue {

            font-size: 16px;

            font-weight: 700;

            color: white;
        }

        QLabel#paramValueBlue {

            font-size: 16px;

            font-weight: 700;

            color: white;
        }

        QLabel#statusBadge {

            background: rgba(0, 180, 255, 40);

            border: 1px solid rgba(0, 220, 255, 120);

            border-radius: 12px;

            font-size: 14px;

            font-weight: 800;

            letter-spacing: 2px;
        }

        QFrame#paramCard {

            background: rgba(14, 24, 38, 235);

            border: 1px solid rgba(0, 200, 255, 70);

            border-radius: 16px;
        }

        QDoubleSpinBox {
            background: transparent;
            border: none;
            color: white;
            font-size: 18px;
            font-weight: 500;
            padding-top: 6px;
            padding-bottom: 2px;
        }
                           
        QDoubleSpinBox::up-button{
            subcontrol-origin: border;
            subcontrol-position: top right;

            width: 22px;

            border: none;

            background: transparent;

            margin-right: 6px;
        }

        QDoubleSpinBox::down-button{
            subcontrol-origin: border;
            subcontrol-position: bottom right;

            width: 22px;

            border: none;

            background: transparent;

            margin-right: 6px;
        }

        QDoubleSpinBox::up-arrow{
            image: url(assets/arrow_up_cyan.svg);

            width: 14px;
            height: 14px;
        }

        QDoubleSpinBox::down-arrow{
            image: url(assets/arrow_down_cyan.svg);

            width: 14px;
            height: 14px;
        }

        QPushButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 110, 255, 220),
                stop:1 rgba(0, 180, 255, 220)
            );

            border: 1px solid rgb(0, 220, 255);

            border-radius: 16px;

            font-size: 14px;

            font-weight: 800;

            letter-spacing: 2px;
        }

        QPushButton:hover {

            background: rgba(0, 180, 255, 255);
        }
        
        QPushButton#applyButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(255, 140, 0, 180),
                stop:1 rgba(255, 180, 0, 180)
            );

            border: 1px solid rgb(255, 190, 50);

            color: white;
        }

        QPushButton#applyButton:hover {

            background: rgba(255, 170, 0, 220);

            border: 1px solid rgb(255, 220, 120);
        }

        QPushButton#nextButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 110, 255, 220),
                stop:1 rgba(0, 180, 255, 220)
            );

            border: 1px solid rgb(0, 220, 255);

            color: white;
        }

        QPushButton#nextButton:hover {

            background: rgb(0, 140, 255);
        }

        QFrame#monitorCard {

            background: rgba(6, 18, 34, 200);

            border: 1px solid rgba(120, 180, 255, 50);

            border-radius: 18px;
        }

        QLabel#monitorIcon {

            border: 2px solid rgb(0, 180, 255);

            border-radius: 19px;

            color: rgb(0, 180, 255);

            font-size: 16px;

            font-weight: 900;
        }

        QLabel#monitorTitle {

            color: white;

            font-size: 16px;
        }

        QLabel#monitorSubtitle {

            color: rgb(130, 150, 170);

            font-size: 12px;
        }


        """)

        self.state.changed.connect(
            self.sync_from_state
        )

        self.sync_from_state()

    def create_param_widget(
        self,
        title: str,
        widget: QWidget
    ) -> QWidget:

        container = QFrame()

        container.setObjectName(
            "paramCard"
        )

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        layout.setSpacing(4)

        label = QLabel(title)

        label.setObjectName(
            "paramTitle"
        )

        layout.addWidget(label)
        layout.addWidget(widget)

        return container

    def apply_temperature(self):

        self.controller.set_temperature(
            float(
                self.target_input.value()
            )
        )

    @Slot()
    def sync_from_state(self):

        p = self.state.params

        self.current_temp.setText(
            f"{p.current_temperature:.1f} °C"
        )

        self.target_temp.setText(
            f"{p.target_temperature:.1f} °C"
        )

        self.target_input.blockSignals(True)

        self.target_input.setValue(
            float(p.target_temperature)
        )

        self.target_input.blockSignals(False)

        status = str(
            p.temperature_status
        )

        self.status_badge.setText(status)

        colors = {
            "IDLE": "#64748B",
            "HEATING": "#F59E0B",
            "STABLE": "#22C55E",
            "COOLING": "#38BDF8",
        }

        color = colors.get(
            status,
            "#64748B"
        )

        self.status_badge.setStyleSheet(f'''
            QLabel {{
                background: rgba(0, 0, 0, 60);
                border: 1px solid {color};
                border-radius: 12px;
                color: {color};
                font-size: 14px;
                font-weight: 800;
                letter-spacing: 2px;
            }}
        ''')

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        scaled = self.bg.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

        x = (
            self.width() - scaled.width()
        ) / 2

        y = (
            self.height() - scaled.height()
        ) / 2

        painter.drawPixmap(
            int(x),
            int(y),
            scaled,
        )

        super().paintEvent(event)


# =========================================================
# SUMMARY PAGE
# =========================================================

class SummaryPage(QWidget):

    def __init__(self, mw: MainWindow) -> None:
        super().__init__()

        self.mw = mw

        self.state = mw.state
        self.controller = mw.controller

        self.bg = QPixmap(
            "assets/layout_bg.png"
        )

        # =====================================================
        # ROOT
        # =====================================================

        root = QVBoxLayout(self)

        root.setContentsMargins(
            24,
            24,
            24,
            24
        )

        root.setSpacing(22)

        # =====================================================
        # TITLE
        # =====================================================

        title = QLabel("SUMMARY")

        title.setObjectName(
            "pageTitle"
        )

        root.addWidget(title)

        # =====================================================
        # SCROLL AREA
        # =====================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        self.content_layout = QVBoxLayout(content)

        self.content_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.content_layout.setSpacing(18)

        scroll.setWidget(content)

        root.addWidget(scroll, 0)
        scroll.setMaximumHeight(480)

        # =====================================================
        # DRAW SETTINGS
        # =====================================================

        self.draw_section = self.create_section(
            "DRAW SETTINGS"
        )

        self.draw_items = {}

        draw_params = [
            ("Speed", "speed"),
            ("Pause", "pause_ms"),
            ("Z-Hop", "z_hop"),
            ("Z-Offset", "z_offset"),
            ("Clean", "clean"),
        ]

        for label, key in draw_params:

            row, value = self.create_summary_item(
                label
            )

            self.draw_section.layout().addWidget(row)

            self.draw_items[key] = value

        self.content_layout.addWidget(
            self.draw_section
        )

        # =====================================================
        # TEMPERATURE
        # =====================================================

        self.temp_section = self.create_section(
            "TEMPERATURE"
        )

        self.temp_items = {}

        temp_params = [
            ("Current Temperature", "current_temperature"),
            ("Target Temperature", "target_temperature"),
            ("Status", "temperature_status"),
        ]

        for label, key in temp_params:

            row, value = self.create_summary_item(
                label
            )

            self.temp_section.layout().addWidget(row)

            self.temp_items[key] = value

        self.content_layout.addWidget(
            self.temp_section
        )

        # =====================================================
        # DRAW CONFIGURATION
        # =====================================================

        self.config_section = self.create_section(
            "DRAW CONFIGURATION"
        )

        self.config_items = {}

        config_params = [
            ("Fiber Orientation", "fiber_orientation"),
            ("Fiber Length", "fiber_length"),
            ("Fiber Width", "fiber_width"),
            ("Fiber Spacing", "fiber_spacing"),
            ("Start X", "start_x"),
            ("Start Y", "start_y"),
        ]

        for label, key in config_params:

            row, value = self.create_summary_item(
                label
            )

            self.config_section.layout().addWidget(row)

            self.config_items[key] = value

        self.content_layout.addWidget(
            self.config_section
        )

        self.content_layout.addStretch()

        # =====================================================
        # ACTION BUTTONS
        # =====================================================

        actions = QWidget()

        actions_layout = QHBoxLayout(actions)

        actions_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        actions_layout.setSpacing(14)

        self.btn_load = QPushButton(
            "LOAD"
        )

        self.btn_load.setObjectName(
            "loadButton"
        )

        self.btn_load.setFixedSize(
            170,
            42
        )

        self.btn_save_pdf = QPushButton(
            "SAVE PDF"
        )

        self.btn_save_pdf.setObjectName(
            "pdfButton"
        )

        self.btn_save_pdf.setFixedSize(
            190,
            42
        )

        self.btn_save_project = QPushButton(
            "SAVE PROJECT"
        )

        self.btn_save_project.setObjectName(
            "saveButton"
        )

        self.btn_save_project.setFixedSize(
            240,
            42
        )

        actions_layout.addWidget(
            self.btn_load
        )

        actions_layout.addWidget(
            self.btn_save_pdf
        )

        actions_layout.addWidget(
            self.btn_save_project
        )

        actions_layout.addStretch()

        root.addWidget(actions)

        self.btn_save_project.clicked.connect(self.mw.save_project_dialog)

        self.btn_save_pdf.clicked.connect(self.mw.save_pdf_dialog)

        self.btn_load.clicked.connect(self.mw.load_project_dialog)

        # =====================================================
        # NEXT BUTTON ROW
        # =====================================================

        next_row = QWidget()

        next_layout = QHBoxLayout(next_row)

        next_layout.setContentsMargins(
            0,
            0,
            10,
            0
        )

        self.btn_next = QPushButton(
            "NEXT  →"
        )

        self.btn_next.setObjectName(
            "nextButton"
        )

        self.btn_next.setFixedSize(
            220,
            54
        )

        self.btn_next.clicked.connect(
            lambda: self.mw.go("Connection")
        )

        next_layout.addStretch()

        next_layout.addWidget(
            self.btn_next
        )

        root.addWidget(next_row)
        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

        QWidget {
            color: white;
            font-family: Inter;
        }

        QLabel#pageTitle {

            font-size: 36px;

            font-weight: 900;

            letter-spacing: 3px;

            color: white;
        }

        QScrollArea {

            background: transparent;

            border: none;
        }

        QScrollArea > QWidget > QWidget {

            background: transparent;
        }
                           
        QScrollBar:vertical {

            background: transparent;

            width: 10px;

            margin: 0px;
        }

        QScrollBar::handle:vertical {

            background: rgba(0, 180, 255, 90);

            border-radius: 5px;

            min-height: 40px;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {

            height: 0px;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {

            background: transparent;
        }

        QFrame#summarySection {

            background: rgba(8, 15, 28, 220);

            border: 1px solid rgba(0, 180, 255, 70);

            border-radius: 22px;
        }

        QLabel#sectionTitle {

            color: rgb(0, 220, 255);

            font-size: 14px;

            font-weight: 800;

            letter-spacing: 2px;
        }

        QFrame#summaryItem {

            background: rgba(4, 10, 20, 180);

            border: 1px solid rgba(120, 180, 255, 40);

            border-radius: 14px;
        }

        QLabel#itemLabel {

            color: rgb(180, 200, 220);

            font-size: 14px;
        }

        QLabel#itemValue {

            color: rgb(235, 240, 248);

            font-size: 15px;

            font-weight: 600;
        }

        QPushButton {

            border-radius: 18px;

            font-size: 14px;

            font-weight: 800;

            letter-spacing: 2px;
        }

        QPushButton#loadButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 120, 220, 220),
                stop:1 rgba(0, 200, 255, 220)
            );

            border: 1px solid rgb(100, 220, 255);

            color: white;
        }

        QPushButton#loadButton:hover {

            background: rgba(0, 190, 255, 255);

            border: 1px solid rgb(180, 240, 255);
        }

        QPushButton#pdfButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 120, 220, 220),
                stop:1 rgba(0, 200, 255, 220)
            );

            border: 1px solid rgb(100, 220, 255);

            color: white;
        }

        QPushButton#pdfButton:hover {

            background: rgba(0, 190, 255, 255);

            border: 1px solid rgb(180, 240, 255);
        }

        QPushButton#saveButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 150, 90, 220),
                stop:1 rgba(0, 210, 120, 220)
            );

            border: 1px solid rgb(120, 255, 180);

            color: white;
        }

        QPushButton#saveButton:hover {

            background: rgba(20, 170, 90, 255);
        }

        QPushButton#nextButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 110, 255, 220),
                stop:1 rgba(0, 180, 255, 220)
            );

            border: 1px solid rgb(0, 220, 255);

            color: white;
        }

        QPushButton#nextButton:hover {

            background: rgb(0, 140, 255);
        }

        """)

        self.state.changed.connect(
            self.sync_from_state
        )

        self.sync_from_state()

    def create_section(
        self,
        title: str
    ) -> QFrame:

        section = QFrame()

        section.setObjectName(
            "summarySection"
        )

        layout = QVBoxLayout(section)

        layout.setContentsMargins(
            22,
            20,
            22,
            20
        )

        layout.setSpacing(14)

        title_label = QLabel(title)

        title_label.setObjectName(
            "sectionTitle"
        )

        layout.addWidget(title_label)

        return section

    def create_summary_item(
        self,
        label: str
    ):

        row = QFrame()

        row.setObjectName(
            "summaryItem"
        )

        layout = QHBoxLayout(row)

        layout.setContentsMargins(
            18,
            12,
            18,
            12
        )

        label_widget = QLabel(label)

        label_widget.setObjectName(
            "itemLabel"
        )

        value_widget = QLabel("--")

        value_widget.setObjectName(
            "itemValue"
        )

        layout.addWidget(label_widget)

        layout.addStretch()

        layout.addWidget(value_widget)

        return row, value_widget

    @Slot()
    def sync_from_state(self):

        p = self.state.params

        values = {

            "speed":
                f"{p.speed} mm/min",

            "pause_ms":
                f"{p.pause_ms} ms",

            "z_hop":
                f"{p.z_hop:.2f} mm",

            "z_offset":
                f"{p.z_offset:.3f} mm",

            "clean":
                "ON" if p.clean else "OFF",

            "current_temperature":
                f"{p.current_temperature:.1f} °C",

            "target_temperature":
                f"{p.target_temperature:.1f} °C",

            "temperature_status":
                str(p.temperature_status),

            "fiber_orientation":
                str(p.fiber_orientation),

            "fiber_length":
                f"{p.fiber_length:.1f} mm",

            "fiber_width":
                f"{p.fiber_width:.1f} mm",

            "fiber_spacing":
                f"{p.fiber_spacing:.2f} mm",

            "start_x":
                f"{p.start_x:.1f} mm",

            "start_y":
                f"{p.start_y:.1f} mm",
        }

        for key, label in self.draw_items.items():

            label.setText(
                values.get(key, "--")
            )

        for key, label in self.temp_items.items():

            label.setText(
                values.get(key, "--")
            )

        for key, label in self.config_items.items():

            label.setText(
                values.get(key, "--")
            )

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        scaled = self.bg.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

        x = (
            self.width() - scaled.width()
        ) / 2

        y = (
            self.height() - scaled.height()
        ) / 2

        painter.drawPixmap(
            int(x),
            int(y),
            scaled,
        )

        super().paintEvent(event)

class ConnectionPage(QWidget):

    def __init__(self, mw: MainWindow) -> None:
        super().__init__()

        self.mw = mw
        self.controller = mw.controller

        self.bg = QPixmap("assets/layout_bg.png")

        # =====================================================
        # ROOT
        # =====================================================

        root = QVBoxLayout(self)

        root.setContentsMargins(
            24,
            24,
            24,
            24
        )

        root.setSpacing(24)

        # =====================================================
        # HEADER
        # =====================================================

        header = QHBoxLayout()

        title = QLabel("CONNECTION")

        title.setObjectName(
            "pageTitle"
        )

        header.addWidget(title)

        header.addStretch()

        self.btn_info = QPushButton("INFO")

        self.btn_info.setObjectName(
            "infoButton"
        )

        self.btn_info.setFixedSize(
            120,
            48
        )

        self.btn_info.clicked.connect(
            self.mw.show_info
        )

        header.addWidget(
            self.btn_info
        )

        root.addLayout(header)

        # =====================================================
        # CONNECTION PANEL
        # =====================================================

        conn_panel = QFrame()

        conn_panel.setObjectName(
            "connectionPanel"
        )

        conn_layout = QHBoxLayout(conn_panel)

        conn_layout.setContentsMargins(
            24,
            18,
            24,
            18
        )

        conn_layout.setSpacing(14)

        self.btn_connect = QPushButton(
            "CONNECT"
        )

        self.btn_connect.setObjectName(
            "connectButton"
        )

        self.btn_connect.setFixedSize(
            180,
            56
        )

        self.btn_disconnect = QPushButton(
            "DISCONNECT"
        )

        self.btn_disconnect.setObjectName(
            "disconnectButton"
        )

        self.btn_disconnect.setFixedSize(
            180,
            56
        )

        self.btn_disconnect.setEnabled(False)

        self.lbl_state = QLabel(
            "DISCONNECTED"
        )

        self.lbl_state.setObjectName(
            "statusDisconnected"
        )

        conn_layout.addWidget(
            self.btn_disconnect
        )

        conn_layout.addWidget(
            self.btn_connect
        )

        conn_layout.addStretch()

        conn_layout.addWidget(
            self.lbl_state
        )

        self.status_dot = QFrame()

        self.status_dot.setObjectName(
            "statusDotDisconnected"
        )

        self.status_dot.setFixedSize(
            14,
            14
        )

        conn_layout.addWidget(
            self.status_dot
        )

        conn_layout.addStretch()

        root.addWidget(conn_panel)

        # =====================================================
        # LOG PANEL
        # =====================================================

        log_panel = QFrame()

        log_panel.setObjectName(
            "logPanel"
        )

        log_layout = QVBoxLayout(log_panel)

        log_layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        log_layout.setSpacing(12)

        log_title = QLabel(
            "MACHINE TELEMETRY"
        )

        log_title.setObjectName(
            "sectionTitle"
        )

        log_layout.addWidget(log_title)

        self.text = QTextEdit()

        self.text.setReadOnly(True)

        self.text.setPlaceholderText(
            "Machine logs and telemetry..."
        )

        self.text.setObjectName(
            "logViewer"
        )

        log_layout.addWidget(
            self.text,
            1
        )

        log_panel.setMaximumHeight(
            420
        )

        root.addWidget(log_panel)

        # =====================================================
        # ACTION BUTTONS
        # =====================================================

        actions = QWidget()

        actions_layout = QGridLayout(actions)
        actions_layout.setColumnStretch(0, 1)
        actions_layout.setColumnStretch(1, 1)
        actions_layout.setColumnStretch(2, 1)

        actions_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        actions_layout.setSpacing(16)

        self.btn_start = QPushButton(
            "DO SCIENCE"
        )

        self.btn_start.setObjectName(
            "startButton"
        )

        self.btn_start.setFixedSize(
            240,
            52
        )

        self.btn_pause = QPushButton(
            "PAUSE"
        )

        self.btn_pause.setObjectName(
            "pauseButton"
        )

        self.btn_pause.setFixedSize(
            240,
            52
        )

        self.btn_pause.setEnabled(False)

        self.btn_stop = QPushButton(
            "STOP"
        )

        self.btn_stop.setObjectName(
            "stopButton"
        )

        self.btn_stop.setFixedSize(
            240,
            52
        )

        self.btn_stop.setEnabled(False)

        self.btn_abort = QPushButton(
            "EMERGENCY STOP"
        )

        self.btn_abort.setObjectName(
            "abortButton"
        )

        self.btn_abort.setFixedSize(
            240,
            52
        )

        self.btn_abort.setEnabled(False)

        self.btn_recover = QPushButton(
            "RECOVER"
        )

        self.btn_recover.setObjectName(
            "recoverButton"
        )

        self.btn_recover.setFixedSize(
            240,
            52
        )

        self.btn_recover.setEnabled(False)

        actions_layout.setSpacing(16)
        actions_layout.setHorizontalSpacing(32)

        actions_layout.setVerticalSpacing(20)
        
        # first row
        actions_layout.addWidget(
            self.btn_abort,
            0,
            0,
            alignment=Qt.AlignCenter
        )

        actions_layout.addWidget(
            self.btn_pause,
            0,
            1,
            alignment=Qt.AlignCenter
        )

        actions_layout.addWidget(
            self.btn_start,
            0,
            2,
            alignment=Qt.AlignCenter
        )

        # second row
        actions_layout.addWidget(
            self.btn_recover,
            1,
            0,
            alignment=Qt.AlignCenter
        )

        actions_layout.addWidget(
            self.btn_stop,
            1,
            2,
            alignment=Qt.AlignCenter
        )

        root.addWidget(actions)

        # =====================================================
        # CONNECTIONS
        # =====================================================

        self.btn_connect.clicked.connect(
            self._connect
        )

        self.btn_disconnect.clicked.connect(
            self._disconnect
        )

        self.btn_start.clicked.connect(
            self._start
        )

        self.btn_pause.clicked.connect(
            self.controller.toggle_pause
        )

        self.btn_stop.clicked.connect(
            self.controller.stop_drawing
        )

        self.btn_recover.clicked.connect(
            self._recover
        )

        self.btn_abort.clicked.connect(
            self.controller.emergency_stop
        )

        self.controller.drawing_running_changed.connect(
            self._on_drawing_running
        )

        self.controller.drawing_paused_changed.connect(
            self._on_drawing_paused
        )

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

        QWidget {

            font-family: Inter;
        }

        QMessageBox {

            background: rgb(14, 20, 32);

            color: white;
        }

        QMessageBox QLabel {

            color: white;
            font-size: 14px;
        }

        QMessageBox QPushButton {

            min-width: 90px;

            min-height: 30px;

            padding: 2px 10px;

            background: rgba(20, 28, 44, 240);

            border: 1px solid rgb(0, 180, 255);

            border-radius: 10px;

            color: white;

            font-weight: 600;
        }

        QMessageBox QPushButton:hover {

            background: rgba(0, 180, 255, 60);
        }             

        QLabel#pageTitle {

            font-size: 36px;

            font-weight: 900;

            color: white;

            letter-spacing: 2px;
        }

        QLabel#sectionTitle {

            color: rgb(0, 220, 255);

            font-size: 12px;

            font-weight: 800;

            letter-spacing: 3px;
        }

        QFrame#connectionPanel,
        QFrame#logPanel {

            background: rgba(8, 15, 28, 220);

            border: 1px solid rgba(0, 180, 255, 80);

            border-radius: 24px;
        }

        QLabel#statusDisconnected {

            color: rgb(255, 80, 80);

            font-size: 16px;

            font-weight: 800;

            letter-spacing: 2px;
        }
                           
        QFrame#statusDotDisconnected {

            background: rgb(255, 70, 70);

            border-radius: 7px;
        }

        QFrame#statusDotConnected {

            background: rgb(0, 255, 140);

            border-radius: 7px;
        }
                           
        QLabel#statusConnected {

            color: rgb(0, 255, 140);

            font-size: 16px;

            font-weight: 800;

            letter-spacing: 2px;
        }

        QTextEdit#logViewer {

            background: rgba(3, 10, 20, 220);
            
            border: 1px solid rgba(0, 180, 255, 40);

            border-radius: 18px;

            padding: 14px;

            font-size: 13px;

            color: white;
        }

        QTextEdit#logViewer QScrollBar:vertical {
            background: rgba(0, 180, 255, 20);
            width: 14px;
            border-radius: 7px;
            margin: 6px;
        }

        QTextEdit#logViewer QScrollBar::handle:vertical {

            background: rgba(0, 220, 255, 180);

            border: 1px solid rgba(120, 240, 255, 180);

            border-radius: 6px;

            min-height: 40px;
        }
                           
        QTextEdit#logViewer QScrollBar::add-line:vertical,
        QTextEdit#logViewer QScrollBar::sub-line:vertical {
            height: 0px;
            background: none;
            border: none;
        }
                           
        QTextEdit#logViewer QScrollBar::add-page:vertical,
        QTextEdit#logViewer QScrollBar::sub-page:vertical {
            background: transparent;
        }

        QPushButton {

            border-radius: 18px;

            font-size: 14px;

            font-weight: 800;

            letter-spacing: 2px;
        }

        QPushButton#connectButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 150, 90, 220),
                stop:1 rgba(0, 210, 120, 220)
            );

            border: 1px solid rgb(120, 255, 180);

            color: white;
        }

        QPushButton#connectButton:hover {

            background: rgba(20, 170, 90, 255);
        }

        QPushButton#disconnectButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(160, 20, 20, 220),
                stop:1 rgba(220, 40, 40, 220)
            );

            border: 1px solid rgb(255, 80, 80);

            color: white;
        }

        QPushButton#disconnectButton:hover {

            background: rgba(170, 20, 28, 255);
        }

        QPushButton#startButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 150, 90, 220),
                stop:1 rgba(0, 210, 120, 220)
            );

            border: 1px solid rgb(120, 255, 180);

            color: white;
        }
                           
        QPushButton#startButton:hover {

            background: rgba(20, 170, 90, 255);
        }

        QPushButton#pauseButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(220, 165, 0, 220),
                stop:1 rgba(245, 195, 0, 220)
            );

            border: 1px solid rgb(255, 215, 90);

            color: white;
        }
                           
        QPushButton#pauseButton:hover {
            background: rgba(255, 200, 0, 255);

            border: 1px solid rgb(255, 220, 120);
        }

        QPushButton#abortButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(160, 20, 20, 220),
                stop:1 rgba(220, 40, 40, 220)
            );

            border: 1px solid rgb(255, 80, 80);

            color: white;
        }
                           
        QPushButton#abortButton:hover {
            background: rgba(170, 20, 28, 255);
        }
                           
        QPushButton#recoverButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 120, 220, 220),
                stop:1 rgba(0, 200, 255, 220)
            );

            border: 1px solid rgb(100, 220, 255);

            color: white;
        }

        QPushButton#recoverButton:hover {

            background: rgba(0, 190, 255, 255);

            border: 1px solid rgb(180, 240, 255);
        }

        QPushButton#stopButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(180, 100, 0, 220),
                stop:1 rgba(255, 150, 0, 220)
            );

            border: 1px solid rgb(255, 190, 80);

            color: white;
        }

        QPushButton#stopButton:hover {

            background: rgba(255, 160, 0, 255);

            border: 1px solid rgb(255, 220, 120);
        }                   
        QPushButton#infoButton {

            background: qlineargradient(
                x1:0,
                y1:0,
                x2:1,
                y2:0,

                stop:0 rgba(0, 110, 255, 220),
                stop:1 rgba(0, 180, 255, 220)
            );

            border: 1px solid rgb(0, 220, 255);

            border-radius: 14px;

            color: white;

            font-size: 13px;

            font-weight: 700;
        }
        
        QPushButton#infoButton:hover {
            border: 1px solid rgb(100, 240, 255);

            background: rgba(0, 180, 255, 255);
        }
                           
        

        """)

    @Slot()
    def _connect(self) -> None:
        ok = self.controller.connect()
        if not ok:
            QMessageBox.critical(self, "Error", "Could not connect to the printer")

    @Slot()
    def _disconnect(self) -> None:
        ok = self.controller.disconnect()
        if not ok:
            QMessageBox.critical(self, "Error", "Could not disconnect from the printer")

    @Slot(bool)
    def on_connection_changed(
        self,
        connected: bool
    ) -> None:

        if connected:

            self.lbl_state.setText(
                "CONNECTED"
            )

            self.lbl_state.setObjectName(
                "statusConnected"
            )

            self.status_dot.setObjectName(
                "statusDotConnected"
            )

            self.status_dot.style().unpolish(
                self.status_dot
            )

            self.status_dot.style().polish(
                self.status_dot
            )

            self.lbl_state.style().unpolish(
                self.lbl_state
            )

            self.lbl_state.style().polish(
                self.lbl_state
            )

            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)

        else:

            self.lbl_state.setText(
                "DISCONNECTED"
            )

            self.lbl_state.setObjectName(
                "statusDisconnected"
            )

            self.status_dot.setObjectName(
                "statusDotDisconnected"
            )

            self.status_dot.style().unpolish(
                self.status_dot
            )

            self.status_dot.style().polish(
                self.status_dot
            )

            self.lbl_state.style().unpolish(
                self.lbl_state
            )

            self.lbl_state.style().polish(
                self.lbl_state
            )

            self.btn_connect.setEnabled(True)

            self.btn_disconnect.setEnabled(False)

    @Slot()
    def _start(self) -> None:
        self.controller.start_drawing()

    @Slot()
    def _recover(self) -> None:

        ok = self.controller.recover_from_emergency_stop()

        if not ok:

            QMessageBox.critical(
                self,
                "Recovery Error",
                "Recovery procedure failed"
            )

    @Slot(bool)
    def _on_drawing_running(
        self,
        running: bool
    ) -> None:

        self.btn_start.setEnabled(
            not running
        )

        self.btn_pause.setEnabled(
            running
        )

        self.btn_stop.setEnabled(
            running
        )

        self.btn_abort.setEnabled(
            running
        )

        # recover only available when machine
        # is NOT drawing
        self.btn_recover.setEnabled(
            self.controller._emergency_stopped
        )

        if not running:

            self.btn_pause.setText(
                "PAUSE"
            )

    @Slot(bool)
    def _on_drawing_paused(
        self,
        paused: bool
    ) -> None:

        self.btn_pause.setText(
            "RESUME" if paused else "PAUSE"
        )

    @Slot(str)
    def append_log(
        self,
        msg: str
    ) -> None:

        self.text.append(msg)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        scaled = self.bg.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

        x = (
            self.width() - scaled.width()
        ) / 2

        y = (
            self.height() - scaled.height()
        ) / 2

        painter.drawPixmap(
            int(x),
            int(y),
            scaled,
        )

        super().paintEvent(event)


        