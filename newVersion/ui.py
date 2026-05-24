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
    QIcon,
)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QMessageBox, QFileDialog,
    QComboBox, QSlider, QDoubleSpinBox, QGroupBox, QGridLayout,
    QRadioButton, QButtonGroup, QTextEdit, QFrame, QSpinBox, QCheckBox,  QGraphicsDropShadowEffect, QSizePolicy
)

from PySide6.QtMultimedia import (
    QAudioOutput,
    QMediaPlayer,
)

from backend import AppState, MachineController

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
# THERMOMETER WIDGET (UPDATED VERSION)
# =========================================================

class ThermometerWidget(QWidget):

    def __init__(
        self,
        state: "AppState",
        parent=None
    ) -> None:

        super().__init__(parent)

        self.state = state

        self.setMinimumSize(180, 620)

        self.state.changed.connect(
            self.update
        )

    # =====================================================
    # PAINT
    # =====================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect()

        # =================================================
        # TEMPERATURE
        # =================================================

        temp = max(
            0.0,
            min(
                50.0,
                float(
                    self.state.params.current_temperature
                )
            )
        )

        ratio = temp / 50.0

        # =================================================
        # COLORS
        # =================================================

        cyan = QColor(
            0,
            220,
            255
        )

        amber = QColor(
            255,
            180,
            0
        )

        red = QColor(
            255,
            70,
            70
        )

        if temp < 20:

            fill_color = cyan

        elif temp < 35:

            fill_color = amber

        else:

            fill_color = red

        # =================================================
        # RESPONSIVE GEOMETRY
        # =================================================

        tube_w = min(
            rect.width() * 0.26,
            72
        )

        tube_h = rect.height() * 0.74

        tube_x = (
            rect.width() - tube_w
        ) / 2

        tube_y = rect.height() * 0.06

        # =================================================
        # OUTER FRAME
        # =================================================

        outer_rect = QRectF(
            tube_x,
            tube_y,
            tube_w,
            tube_h
        )

        # outer glow
        glow_color = QColor(
            fill_color
        )

        glow_color.setAlpha(25)

        painter.setPen(Qt.NoPen)

        painter.setBrush(glow_color)

        painter.drawRoundedRect(
            outer_rect.adjusted(
                -10,
                -10,
                10,
                10
            ),
            36,
            36
        )

        # frame
        painter.setBrush(
            QColor(8, 15, 28, 240)
        )

        painter.setPen(
            QPen(
                QColor(80, 170, 255),
                2
            )
        )

        painter.drawRoundedRect(
            outer_rect,
            36,
            36
        )

        # =================================================
        # INNER CHANNEL
        # =================================================

        margin = 14

        channel_rect = QRectF(
            outer_rect.left() + margin,
            outer_rect.top() + margin,
            outer_rect.width() - margin * 2,
            outer_rect.height() - margin * 2
        )

        painter.setBrush(
            QColor(0, 0, 0, 90)
        )

        painter.setPen(Qt.NoPen)

        painter.drawRoundedRect(
            channel_rect,
            18,
            18
        )

        # =================================================
        # HOT ZONE
        # =================================================

        hot_zone_h = (
            channel_rect.height() * 0.2
        )

        hot_zone_rect = QRectF(
            channel_rect.left(),
            channel_rect.top(),
            channel_rect.width(),
            hot_zone_h
        )

        hot_gradient = QLinearGradient(
            hot_zone_rect.topLeft(),
            hot_zone_rect.bottomLeft()
        )

        hot_gradient.setColorAt(
            0.0,
            QColor(255, 0, 0, 45)
        )

        hot_gradient.setColorAt(
            1.0,
            QColor(255, 0, 0, 0)
        )

        painter.setBrush(
            hot_gradient
        )

        painter.drawRoundedRect(
            hot_zone_rect,
            18,
            18
        )

        # =================================================
        # SEGMENTS
        # =================================================

        segment_count = 18

        spacing = 5

        segment_h = (
            channel_rect.height()
            - spacing * (segment_count - 1)
        ) / segment_count

        active_segments = int(
            segment_count * ratio
        )

        for i in range(segment_count):

            yy = (
                channel_rect.bottom()
                - (segment_h + spacing) * (i + 1)
            )

            segment_rect = QRectF(
                channel_rect.left() + 5,
                yy,
                channel_rect.width() - 10,
                segment_h
            )

            # inactive
            if i >= active_segments:

                painter.setBrush(
                    QColor(255, 255, 255, 12)
                )

                painter.setPen(Qt.NoPen)

                painter.drawRoundedRect(
                    segment_rect,
                    8,
                    8
                )

                continue

            # glow
            glow = QColor(fill_color)

            glow.setAlpha(60)

            painter.setBrush(glow)

            painter.drawRoundedRect(
                segment_rect.adjusted(
                    -2,
                    -2,
                    2,
                    2
                ),
                10,
                10
            )

            # active segment
            gradient = QLinearGradient(
                segment_rect.topLeft(),
                segment_rect.bottomLeft()
            )

            gradient.setColorAt(
                0.0,
                QColor(255, 255, 255, 80)
            )

            gradient.setColorAt(
                0.15,
                fill_color.lighter(135)
            )

            gradient.setColorAt(
                1.0,
                fill_color
            )

            painter.setBrush(gradient)

            painter.setPen(Qt.NoPen)

            painter.drawRoundedRect(
                segment_rect,
                8,
                8
            )

        # =================================================
        # REACTOR BASE
        # =================================================

        base_w = tube_w * 1.6

        base_h = 34

        base_x = (
            rect.width() - base_w
        ) / 2

        base_y = outer_rect.bottom() + 18

        base_rect = QRectF(
            base_x,
            base_y,
            base_w,
            base_h
        )

        base_gradient = QLinearGradient(
            base_rect.topLeft(),
            base_rect.bottomLeft()
        )

        base_gradient.setColorAt(
            0.0,
            QColor(24, 40, 64)
        )

        base_gradient.setColorAt(
            1.0,
            QColor(8, 14, 26)
        )

        painter.setBrush(base_gradient)

        painter.setPen(
            QPen(
                QColor(80, 170, 255),
                2
            )
        )

        painter.drawRoundedRect(
            base_rect,
            12,
            12
        )

        # =================================================
        # INNER CORE REFLECTION
        # =================================================

        reflection_rect = QRectF(
            channel_rect.left() + 5,
            channel_rect.top() + 5,
            channel_rect.width() * 0.22,
            channel_rect.height()
        )

        reflection_gradient = QLinearGradient(
            reflection_rect.topLeft(),
            reflection_rect.topRight()
        )

        reflection_gradient.setColorAt(
            0.0,
            QColor(255, 255, 255, 45)
        )

        reflection_gradient.setColorAt(
            1.0,
            QColor(255, 255, 255, 0)
        )

        painter.setBrush(
            reflection_gradient
        )

        painter.setPen(Qt.NoPen)

        painter.drawRoundedRect(
            reflection_rect,
            18,
            18
        )

        # =================================================
        # SIDE SCALE
        # =================================================

        scale_font = QFont(
            "Inter",
            9,
            QFont.Bold
        )

        painter.setFont(scale_font)

        scale_values = [
            0,
            10,
            20,
            30,
            40,
            50
        ]

        for value in scale_values:

            yy = (
                channel_rect.bottom()
                - (channel_rect.height() * (value / 50.0))
            )

            # tick line
            painter.setPen(
                QPen(
                    QColor(120, 180, 255, 120),
                    1
                )
            )

            painter.drawLine(
                outer_rect.right() + 6,
                yy,
                outer_rect.right() + 18,
                yy
            )

            # label
            painter.setPen(
                QColor(140, 190, 255)
            )

            painter.drawText(
                QRectF(
                    outer_rect.right() + 24,
                    yy - 10,
                    40,
                    20
                ),
                Qt.AlignLeft,
                f"{value}"
            )

        # =================================================
        # CURRENT TEMP TEXT
        # =================================================

        temp_font = QFont(
            "Orbitron",
            18,
            QFont.Bold
        )

        painter.setFont(temp_font)

        painter.setPen(fill_color)

        painter.drawText(
            QRectF(
                0,
                base_rect.bottom() + 18,
                rect.width(),
                36
            ),
            Qt.AlignCenter,
            f"{temp:.1f} °C"
        )

        # =================================================
        # STATUS
        # =================================================

        if temp < 20:

            status = "COOL"

        elif temp < 35:

            status = "STABLE"

        else:

            status = "HEATING"

        status_font = QFont(
            "Inter",
            10,
            QFont.Bold
        )

        painter.setFont(status_font)

        painter.setPen(
            QColor(200, 200, 200)
        )

        painter.drawText(
            QRectF(
                0,
                base_rect.bottom() + 52,
                rect.width(),
                24
            ),
            Qt.AlignCenter,
            status
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
        self.setMinimumSize(QSize(980, 780))

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
        # self.page_summary = SummaryPage(self)
        # self.page_connection = ConnectionPage(self)
        
        self._add_page("Welcome", self.page_welcome)
        self._add_page("Fiber Layout", self.page_fiber_layout)
        self._add_page("Draw Settings", self.page_draw_settings)
        self._add_page("Temperature", self.page_temperature)
        # self._add_page("Summary", self.page_summary)
        # self._add_page("Connection", self.page_connection)

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)

        self._set_project_mode(False)
        self.sidebar.setCurrentRow(0)

        # self.controller.connection_changed.connect(self.page_connection.on_connection_changed)
        # self.state.log.connect(self.page_connection.append_log)

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
        mapping = {"Welcome": 0, "Fiber Layout": 1, "Draw Settings": 2, "Temperature": 3, "Connection": 4, "Log": 5}
        self.sidebar.setCurrentRow(mapping[name])
        # its the same as: user clicked in Draw, so the sidebar changes and emits a signal, the Qt gets this signal and changes the page - see a full explanation on helpfullDocuments/aboutCurrentVersionFunctions

    def start_new_project(self) -> None:
        self._set_project_mode(True)
        self.setWindowTitle("Nanofiber Machine - New Project")
        self.go("Fiber Layout")
        self.controller.log("New project")
    
    def load_project_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "JSON files (*.json)")
        if not path:
            return
        try:
            self.controller.load_project(path)
            self._set_project_mode(True)
            self.setWindowTitle(f"Nanofiber Machine - {path.split('/')[-1]}")
            self.go("Draw")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load project:\n{e}")

    def save_project_dialog(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON files (*.json)")
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            self.controller.save_project(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save project:\n{e}")

    def save_pdf_dialog(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF files (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        try:
            self.controller.save_pdf(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save PDF:\n{e}")

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
            lambda: self.mw.go("Syringe")
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
            (self.amount, p.droplet_amount),
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
            bool(p.afterdrop)
        )

        self.btn_afterdrop.blockSignals(False)

        self.btn_clean.blockSignals(True)

        self.btn_clean.setChecked(
            bool(p.clean)
        )
        
        self.btn_clean.blockSignals(False)
        self._update_toggle_texts()



class TemperaturePage(QWidget):

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

        # =====================================================
        # MAIN PANEL
        # =====================================================

        self.main_panel = QFrame()

        self.main_panel.setObjectName(
            "mainPanel"
        )

        root.addWidget(
            self.main_panel
        )

        panel_layout = QVBoxLayout(
            self.main_panel
        )

        panel_layout.setContentsMargins(
            28,
            28,
            28,
            28
        )

        panel_layout.setSpacing(24)

        # =====================================================
        # TITLE
        # =====================================================

        self.title = QLabel(
            "THERMAL CORE CONTROL"
        )

        self.title.setObjectName(
            "pageTitle"
        )

        panel_layout.addWidget(
            self.title
        )

        # =====================================================
        # CENTER AREA
        # =====================================================

        center_layout = QHBoxLayout()

        center_layout.setSpacing(28)

        # =====================================================
        # LEFT — REACTOR PANEL
        # =====================================================

        self.reactor_panel = QFrame()

        self.reactor_panel.setObjectName(
            "reactorPanel"
        )

        reactor_layout = QVBoxLayout(
            self.reactor_panel
        )

        reactor_layout.setContentsMargins(
            24,
            24,
            24,
            24
        )

        reactor_layout.setSpacing(16)

        reactor_title = QLabel(
            "THERMAL REACTOR"
        )

        reactor_title.setObjectName(
            "reactorTitle"
        )

        reactor_layout.addWidget(
            reactor_title,
            alignment=Qt.AlignCenter
        )

        self.thermometer = ThermometerWidget(
            self.state
        )

        reactor_layout.addWidget(
            self.thermometer,
            alignment=Qt.AlignCenter
        )

        center_layout.addWidget(
            self.reactor_panel,
            3
        )

        # =====================================================
        # RIGHT — TELEMETRY COLUMN
        # =====================================================

        telemetry_container = QFrame()

        telemetry_container.setObjectName(
            "telemetryContainer"
        )

        telemetry_layout = QVBoxLayout(
            telemetry_container
        )

        telemetry_layout.setContentsMargins(
            32,
            8,
            8,
            8
        )

        telemetry_layout.setSpacing(20)

        # =====================================================
        # CURRENT TEMPERATURE
        # =====================================================

        current_card = self.create_telemetry_card(
            "CURRENT TEMPERATURE"
        )

        self.current_temp_label = QLabel(
            "0.0 °C"
        )

        self.current_temp_label.setObjectName(
            "temperatureValue"
        )

        current_card.layout().addWidget(
            self.current_temp_label
        )

        telemetry_layout.addWidget(
            current_card
        )

        # =====================================================
        # TARGET TEMPERATURE
        # =====================================================

        target_card = self.create_telemetry_card(
            "TARGET TEMPERATURE"
        )

        self.target_temp = QDoubleSpinBox()

        self.target_temp.setRange(
            0.0,
            50.0
        )

        self.target_temp.setDecimals(1)

        self.target_temp.setSingleStep(
            0.5
        )

        self.target_temp.setSuffix(
            " °C"
        )

        self.target_temp.valueChanged.connect(
            lambda v: self.state.set_target_temperature(
                float(v)
            )
        )

        target_card.layout().addWidget(
            self.target_temp
        )

        telemetry_layout.addWidget(
            target_card
        )

        # =====================================================
        # STATUS
        # =====================================================

        status_card = self.create_telemetry_card(
            "THERMAL STATUS"
        )

        self.status_label = QLabel(
            "IDLE"
        )

        self.status_label.setObjectName(
            "statusValue"
        )

        status_card.layout().addWidget(
            self.status_label
        )

        telemetry_layout.addWidget(
            status_card
        )

        # =====================================================
        # THERMAL COMMAND
        # =====================================================

        command_card = self.create_telemetry_card(
            "THERMAL COMMAND"
        )

        self.btn_apply = QPushButton(
            "APPLY TEMPERATURE"
        )

        self.btn_apply.setObjectName(
            "engineeringButton"
        )

        self.btn_apply.setFixedHeight(
            56
        )

        self.btn_apply.clicked.connect(
            self.apply_temperature
        )

        command_card.layout().addWidget(
            self.btn_apply
        )

        telemetry_layout.addWidget(
            command_card
        )

        telemetry_layout.addStretch()

        center_layout.addWidget(
            telemetry_container,
            2
        )

        panel_layout.addLayout(
            center_layout
        )

        # =====================================================
        # FOOTER
        # =====================================================

        footer = QHBoxLayout()

        footer.setContentsMargins(
            4,
            6,
            4,
            0
        )

        self.footer_label = QLabel(
            "THERMAL MONITORING ACTIVE"
        )

        self.footer_label.setObjectName(
            "footerLabel"
        )

        footer.addWidget(
            self.footer_label
        )

        footer.addStretch()

        self.btn_next = QPushButton(
            "NEXT →"
        )

        self.btn_next.setFixedSize(
            220,
            56
        )

        self.btn_next.clicked.connect(
            lambda: self.mw.go("Main")
        )

        footer.addWidget(
            self.btn_next,
            alignment=Qt.AlignRight
        )

        panel_layout.addLayout(
            footer
        )

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet("""

        QWidget {
            color: white;
            font-family: Inter;
            font-size: 14px;
        }

        /* =====================================================
           MAIN PANEL
        ===================================================== */

        QFrame#mainPanel {

            background: rgba(8, 15, 28, 220);

            border: 1px solid rgba(0, 180, 255, 90);

            border-radius: 28px;
        }

        /* =====================================================
           TITLE
        ===================================================== */

        QLabel#pageTitle {

            font-size: 42px;

            font-weight: 900;

            color: white;

            letter-spacing: 3px;

            padding-bottom: 8px;
        }

        /* =====================================================
           REACTOR PANEL
        ===================================================== */

        QFrame#reactorPanel {

            background: rgba(4, 10, 20, 180);

            border: 1px solid rgba(0, 180, 255, 60);

            border-radius: 24px;
        }

        QLabel#reactorTitle {

            color: rgb(0, 220, 255);

            font-size: 12px;

            font-weight: 800;

            letter-spacing: 4px;
        }

        /* =====================================================
           TELEMETRY CONTAINER
        ===================================================== */

        QFrame#telemetryContainer {

            border-left:
                1px solid rgba(0, 180, 255, 40);
        }

        /* =====================================================
           TELEMETRY CARDS
        ===================================================== */

        QFrame#telemetryCard {

            background: rgba(14, 24, 38, 235);

            border: 1px solid rgba(0, 200, 255, 70);

            border-radius: 18px;
        }

        QLabel#telemetryTitle {

            color: rgb(0, 220, 255);

            font-size: 11px;

            font-weight: 800;

            letter-spacing: 2px;
        }

        /* =====================================================
           VALUES
        ===================================================== */

        QLabel#temperatureValue {

            color: rgb(255, 120, 120);

            font-size: 64px;

            font-weight: 900;

            letter-spacing: 2px;
        }

        QLabel#statusValue {

            font-size: 28px;

            font-weight: 900;

            letter-spacing: 3px;
        }

        QLabel#footerLabel {

            color: rgb(0, 220, 255);

            font-size: 12px;

            font-weight: 700;

            letter-spacing: 2px;
        }

        /* =====================================================
           SPINBOX
        ===================================================== */

        QDoubleSpinBox {

            background: transparent;

            border: none;

            color: white;

            font-size: 30px;

            font-weight: 800;

            padding-top: 12px;

            padding-bottom: 12px;

            min-height: 48px;
        }

        /* =====================================================
           SPINBOX BUTTONS
        ===================================================== */

        QDoubleSpinBox::up-button {

            subcontrol-origin: border;

            subcontrol-position: top right;

            width: 24px;

            border: none;

            background: transparent;

            margin-right: 8px;
        }

        QDoubleSpinBox::down-button {

            subcontrol-origin: border;

            subcontrol-position: bottom right;

            width: 24px;

            border: none;

            background: transparent;

            margin-right: 8px;
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

        /* =====================================================
           PRIMARY BUTTON
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

            border-radius: 16px;

            color: white;

            font-size: 15px;

            font-weight: 700;

            letter-spacing: 2px;

            padding: 12px 24px;
        }

        QPushButton:hover {

            border: 1px solid rgb(100, 240, 255);

            background: rgba(0, 180, 255, 255);
        }

        /* =====================================================
           ENGINEERING BUTTON
        ===================================================== */

        QPushButton#engineeringButton {

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

        QPushButton#engineeringButton:hover {

            background: rgba(255, 170, 0, 220);

            border: 1px solid rgb(255, 220, 120);
        }

        """)

        # =====================================================
        # STATE
        # =====================================================

        self.state.changed.connect(
            self._sync_from_state
        )

        self._sync_from_state()

    # =========================================================
    # TELEMETRY CARD
    # =========================================================

    def create_telemetry_card(
        self,
        title: str
    ) -> QWidget:

        card = QFrame()

        card.setObjectName(
            "telemetryCard"
        )

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        layout.setSpacing(10)

        label = QLabel(title)

        label.setObjectName(
            "telemetryTitle"
        )

        layout.addWidget(label)

        return card

    # =========================================================
    # APPLY TEMPERATURE
    # =========================================================

    def apply_temperature(self):

        temp = float(
            self.target_temp.value()
        )

        self.controller.set_temperature(
            temp
        )

    # =========================================================
    # BACKGROUND
    # =========================================================

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
    # PAGE SHOW
    # =========================================================

    def showEvent(self, event):

        super().showEvent(event)

        self.controller.enable_temperature_reporting(
            2
        )

    # =========================================================
    # PAGE HIDE
    # =========================================================

    def hideEvent(self, event):

        super().hideEvent(event)

        self.controller.disable_temperature_reporting()

    # =========================================================
    # STATE UPDATE
    # =========================================================

    @Slot()
    def _sync_from_state(self):

        p = self.state.params

        temp = float(
            p.current_temperature
        )

        self.current_temp_label.setText(
            f"{temp:.1f} °C"
        )

        self.target_temp.blockSignals(
            True
        )

        self.target_temp.setValue(
            float(p.target_temperature)
        )

        self.target_temp.blockSignals(
            False
        )

        # =====================================================
        # STATUS
        # =====================================================

        status = str(
            p.temperature_status
        )

        self.status_label.setText(
            status
        )

        if status == "HEATING":

            color = (
                "rgb(255, 80, 80)"
            )

        elif status == "STABLE":

            color = (
                "rgb(255, 180, 0)"
            )

        elif status == "COOLING":

            color = (
                "rgb(0, 220, 255)"
            )

        else:

            color = (
                "rgb(180, 180, 180)"
            )

        self.status_label.setStyleSheet(
            f'''
            QLabel {{
                color: {color};
                font-size: 28px;
                font-weight: 900;
                letter-spacing: 3px;
            }}
            '''
        )
    

        


