from __future__ import annotations

import os

from PySide6.QtCore import Qt, QSize, Slot
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
    QRadioButton, QButtonGroup, QTextEdit, QFrame, QSpinBox, QCheckBox,  QGraphicsDropShadowEffect
)

from PySide6.QtCore import QUrl

from PySide6.QtMultimedia import (
    QAudioOutput,
    QMediaPlayer,
)

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

from backend import AppState, MachineController

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
            "Industrial Control"
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
        self.page_draw = DrawPage(self)
        # self.page_summary = SummaryPage(self)
        # self.page_connection = ConnectionPage(self)
        
        self._add_page("Welcome", self.page_welcome)
        self._add_page("Draw", self.page_draw)
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
        mapping = {"Welcome": 0, "Draw": 1, "Syringe": 2, "Summary": 3, "Connection": 4, "Log": 5}
        self.sidebar.setCurrentRow(mapping[name])
        # its the same as: user clicked in Draw, so the sidebar changes and emits a signal, the Qt gets this signal and changes the page - see a full explanation on helpfullDocuments/aboutCurrentVersionFunctions

    def start_new_project(self) -> None:
        self._set_project_mode(True)
        self.setWindowTitle("Nanofiber Machine - New Project")
        self.go("Draw")
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


class DrawPage(QWidget):
    def __init__(self, mw: MainWindow) -> None:
        super().__init__()
        self.mw = mw
        self.state = mw.state
        self.controller = mw.controller

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 14, 18, 14)
        outer.setSpacing(10)

        outer.addWidget(_title_label("Drawing"))

        # ---------------- Rectangle parameters ----------------
        rect = QGroupBox("Layout parameters")
        rect_grid = QGridLayout(rect)
        rect_grid.setHorizontalSpacing(14)
        rect_grid.setVerticalSpacing(10)

        self.fiber_orientation = QComboBox()
        self.fiber_orientation.addItems(["Horizontal", "Vertical"])
        self.fiber_orientation.currentTextChanged.connect(lambda t: self.state.set_param("fiber_orientation", t))

        self.fiber_length = QDoubleSpinBox()
        self.fiber_length.setDecimals(2)
        self.fiber_length.setRange(0.0, 10000.0)
        self.fiber_length.setSingleStep(1.0)
        self.fiber_length.valueChanged.connect(lambda v: self.state.set_param("fiber_length", float(v)))

        self.fiber_width = QDoubleSpinBox()
        self.fiber_width.setDecimals(2)
        self.fiber_width.setRange(0.0, 10000.0)
        self.fiber_width.setSingleStep(1.0)
        self.fiber_width.valueChanged.connect(lambda v: self.state.set_param("fiber_width", float(v)))

        self.fiber_spacing = QDoubleSpinBox()
        self.fiber_spacing.setDecimals(2)
        self.fiber_spacing.setRange(0.01, 10000.0)
        self.fiber_spacing.setSingleStep(0.1)
        self.fiber_spacing.valueChanged.connect(lambda v: self.state.set_param("fiber_spacing", float(v)))

        self.start_x = QDoubleSpinBox()
        self.start_x.setDecimals(2)
        self.start_x.setRange(-1000.0, 1000.0)
        self.start_x.setSingleStep(1.0)
        self.start_x.valueChanged.connect(lambda v: self.state.set_param("start_x", float(v)))

        self.start_y = QDoubleSpinBox()
        self.start_y.setDecimals(2)
        self.start_y.setRange(-1000.0, 1000.0)
        self.start_y.setSingleStep(1.0)
        self.start_y.valueChanged.connect(lambda v: self.state.set_param("start_y", float(v)))

        rect_grid.addWidget(QLabel("Orientation"), 0, 0)
        rect_grid.addWidget(self.fiber_orientation, 0, 1)
        rect_grid.addWidget(QLabel("Length (mm)"), 1, 0)
        rect_grid.addWidget(self.fiber_length, 1, 1)
        rect_grid.addWidget(QLabel("Width (mm)"), 2, 0)
        rect_grid.addWidget(self.fiber_width, 2, 1)
        rect_grid.addWidget(QLabel("Spacing (mm)"), 3, 0)
        rect_grid.addWidget(self.fiber_spacing, 3, 1)
        rect_grid.addWidget(QLabel("Starting X (mm)"), 4, 0)
        rect_grid.addWidget(self.start_x, 4, 1)
        rect_grid.addWidget(QLabel("Starting Y (mm)"), 5, 0)
        rect_grid.addWidget(self.start_y, 5, 1)

        outer.addWidget(rect)

        outer.addWidget(_subtle_label("Usable drawing area preview"))
        self.preview = RectanglePreview(self.controller, self.state)
        outer.addWidget(self.preview)

        # ---------------- Common motion/deposition (kept) ----------------
        common = QGroupBox("Drawing parameters")
        common_grid = QGridLayout(common)
        common_grid.setHorizontalSpacing(14)
        common_grid.setVerticalSpacing(10)

        # speed slider + label
        self.speed = QSlider(Qt.Horizontal)
        self.speed.setRange(100, 5000)
        self.speed.valueChanged.connect(lambda v: self.state.set_param("speed", int(v)))
        self.speed_label = QLabel("")

        # droplet amount
        self.amount = QDoubleSpinBox()
        self.amount.setDecimals(3)
        self.amount.setRange(0.0, 1000.0)
        self.amount.setSingleStep(0.1)
        self.amount.valueChanged.connect(lambda v: self.state.set_param("droplet_amount", float(v)))

        # z-hop
        self.zhop = QDoubleSpinBox()
        self.zhop.setDecimals(2)
        self.zhop.setRange(0.0, 1000.0)
        self.zhop.setSingleStep(0.5)
        self.zhop.valueChanged.connect(lambda v: self.state.set_param("z_hop", float(v)))

        # z-offset
        self.zoffset = QDoubleSpinBox()
        self.zoffset.setDecimals(3)
        self.zoffset.setRange(-1000.0, 1000.0)
        self.zoffset.setSingleStep(0.01)
        self.zoffset.valueChanged.connect(lambda v: self.state.set_param("z_offset", float(v)))

        # pause ms
        self.pause_ms = QSpinBox()
        self.pause_ms.setRange(0, 600000)
        self.pause_ms.valueChanged.connect(lambda v: self.state.set_param("pause_ms", int(v)))

        self.chk_afterdrop = QCheckBox("Afterdrop")
        self.chk_afterdrop.toggled.connect(lambda v: self.state.set_param("afterdrop", bool(v)))

        self.chk_clean = QCheckBox("Clean")
        self.chk_clean.toggled.connect(lambda v: self.state.set_param("clean", bool(v)))

        self.btn_test_z = QPushButton("Test Z-Offset")
        self.btn_test_z.clicked.connect(self.controller.test_zoffset)

        common_grid.addWidget(QLabel("Speed"), 0, 0)
        common_grid.addWidget(self.speed, 0, 1, 1, 2)
        common_grid.addWidget(self.speed_label, 0, 3)
        common_grid.addWidget(QLabel("Droplet Amount (E units)"), 1, 0)
        common_grid.addWidget(self.amount, 1, 1)
        common_grid.addWidget(QLabel("Z-Offset (mm)"), 1, 2)
        common_grid.addWidget(self.zoffset, 1, 3)
        common_grid.addWidget(QLabel("Z-Hop (mm)"), 2, 0)
        common_grid.addWidget(self.zhop, 2, 1)
        common_grid.addWidget(QLabel("Pause (ms)"), 2, 2)
        common_grid.addWidget(self.pause_ms, 2, 3)
        common_grid.addWidget(self.chk_afterdrop, 3, 0, 1, 2)
        common_grid.addWidget(self.chk_clean, 3, 2, 1, 2)
        common_grid.addWidget(self.btn_test_z, 4, 0, 1, 4)

        outer.addWidget(common)

        # navigation
        nav = QHBoxLayout()
        nav.addStretch(1) # consume the avaible space first
        self.btn_next = QPushButton("Next →") # and then the button is placed, on the right side
        self.btn_next.clicked.connect(lambda: self.mw.go("Syringe"))
        nav.addWidget(self.btn_next)
        outer.addLayout(nav)

        # "Whenever state changes,
        # refresh the UI."
        self.state.changed.connect(self._sync_from_state)

        # initial UI population
        self._sync_from_state()

    @Slot()
    def _sync_from_state(self) -> None:
        p = self.state.params

        # rectangle
        self.fiber_orientation.blockSignals(True)
        self.fiber_orientation.setCurrentText(str(p.fiber_orientation))
        self.fiber_orientation.blockSignals(False)

        for w, val in [(self.fiber_length, p.fiber_length), (self.fiber_width, p.fiber_width), (self.fiber_spacing, p.fiber_spacing),
                      (self.start_x, p.start_x), (self.start_y, p.start_y)]:
            w.blockSignals(True)
            w.setValue(float(val))
            w.blockSignals(False)

        # common
        self.speed.blockSignals(True)
        self.speed.setValue(int(p.speed))
        self.speed.blockSignals(False)
        self.speed_label.setText(f"{int(p.speed)} mm/min")

        for w, val in [(self.amount, p.droplet_amount), (self.zhop, p.z_hop), (self.zoffset, p.z_offset)]:
            w.blockSignals(True)
            w.setValue(float(val))
            w.blockSignals(False)

        self.pause_ms.blockSignals(True)
        self.pause_ms.setValue(int(p.pause_ms))
        self.pause_ms.blockSignals(False)

        self.chk_afterdrop.blockSignals(True)
        self.chk_afterdrop.setChecked(bool(p.afterdrop))
        self.chk_afterdrop.blockSignals(False)

        self.chk_clean.blockSignals(True)
        self.chk_clean.setChecked(bool(p.clean))
        self.chk_clean.blockSignals(False)





    

        




