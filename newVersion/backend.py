from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

from PySide6.QtCore import QObject, Signal, QThread, Slot

import json
import time
import threading

try:
    import serial
    from serial.tools import list_ports
except Exception:
    serial = None
    list_ports = None

from reportlab.pdfgen import canvas


# ----------------------------- Data Model -----------------------------

@dataclass
class Params:
    # --- Mode ---
    # Legacy: usa a lógica antiga (cups + orientation Horizontal/Vertical/Both)
    # CustomCentered: usa L/W/spacing centralizado na área segura (safe bounds)

    # --- Legacy draw params (GUI.py semantics) ---

    # --- Motion / deposition ---
    speed: int = 1500                # mm/min
    droplet_amount: float = 1.0      # E units
    z_hop: float = 10.0              # mm
    pause_ms: int = 0                # ms (G4 P...)
    z_offset: float = 0.4            # mm

    afterdrop: bool = True
    clean: bool = True

    # --- Syringe bookkeeping ---
    syringe_current_amount: float = 0.0
    syringe_droplet_units: int = 5

    # --- CustomCentered safe bounds (seu retângulo seguro) ---
    safe_x_min: float = 0
    safe_x_max: float = 170
    safe_y_min: float = 20.0
    safe_y_max: float = 250.0

    # --- Rectangle anchor (bottom-left corner of draw rectangle) ---
    start_x: float = 0
    start_y: float = 0
    # --- CustomCentered parameters ---
    fiber_orientation: str = "Horizontal"  # Horizontal | Vertical
    fiber_length: float = 80.0            # L (mm)
    fiber_width: float = 40.0             # W (mm)
    fiber_spacing: float = 1.0            # S (mm) distância entre fibras

class SyringeEmptyError(Exception):
    pass

class AppState(QObject):
    changed = Signal()
    log = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.params = Params()

    # its called from UI when user changes some attr and it writes the value 
    def set_param(self, name: str, value: Any) -> None:
        if not hasattr(self.params, name):
            raise AttributeError(f"Unknown param: {name}")
        setattr(self.params, name, value)
        self.changed.emit()

    def to_project_dict(self) -> Dict[str, Any]:
        p = self.params
        return {
            "Speed": int(p.speed),
            "Droplet Amount": float(p.droplet_amount),
            "Z-Hop": float(p.z_hop),
            "Pause (ms)": int(p.pause_ms),
            "Z-Offset": float(p.z_offset),
            "Afterdrop": bool(p.afterdrop),
            "Clean": bool(p.clean),

            "Syringe Current Amount": float(p.syringe_current_amount),
            "Syringe Droplet Units": int(p.syringe_droplet_units),

            "Safe X Min": float(p.safe_x_min),
            "Safe X Max": float(p.safe_x_max),
            "Safe Y Min": float(p.safe_y_min),
            "Safe Y Max": float(p.safe_y_max),

            "Start X": float(p.start_x),
            "Start Y": float(p.start_y),

            "Fiber Orientation": str(p.fiber_orientation),
            "Fiber Length": float(p.fiber_length),
            "Fiber Width": float(p.fiber_width),
            "Fiber Spacing": float(p.fiber_spacing),
        }

    def apply_project_dict(self, data: Dict[str, Any]) -> None:
        p = self.params

        p.speed = int(data.get("Speed", p.speed))
        p.droplet_amount = float(data.get("Droplet Amount", p.droplet_amount))
        p.z_hop = float(data.get("Z-Hop", p.z_hop))
        p.pause_ms = int(data.get("Pause (ms)", p.pause_ms))
        p.z_offset = float(data.get("Z-Offset", p.z_offset))
        p.afterdrop = bool(data.get("Afterdrop", p.afterdrop))
        p.clean = bool(data.get("Clean", p.clean))

        p.syringe_current_amount = float(data.get("Syringe Current Amount", p.syringe_current_amount))
        p.syringe_droplet_units = int(data.get("Syringe Droplet Units", p.syringe_droplet_units))

        p.safe_x_min = float(data.get("Safe X Min", p.safe_x_min))
        p.safe_x_max = float(data.get("Safe X Max", p.safe_x_max))
        p.safe_y_min = float(data.get("Safe Y Min", p.safe_y_min))
        p.safe_y_max = float(data.get("Safe Y Max", p.safe_y_max))

        p.start_x = float(data.get("Start X", p.start_x))
        p.start_y = float(data.get("Start Y", p.start_y))

        p.fiber_orientation = str(data.get("Fiber Orientation", p.fiber_orientation))
        p.fiber_length = float(data.get("Fiber Length", p.fiber_length))
        p.fiber_width = float(data.get("Fiber Width", p.fiber_width))
        p.fiber_spacing = float(data.get("Fiber Spacing", p.fiber_spacing))

        self.changed.emit()

# ----------------------------- Drawing Worker -----------------------------

class DrawingWorker(QObject):

    finished = Signal()
    error = Signal(str)
    status = Signal(str)

    def __init__(self, controller: "MachineController") -> None:
        super().__init__()
        self.controller = controller

    @Slot() # marks a funtion that can receive signals and hadle
    def run(self) -> None:
        try:
            self.controller._run_drawing_loop(self.status)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


# ----------------------------- Controller -----------------------------

class MachineController(QObject):
    connection_changed = Signal(bool)  # emit signal with a bool value inside

    drawing_running_changed = Signal(bool)
    drawing_paused_changed = Signal(bool)

    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.ser: Optional["serial.Serial"] = None  # type: ignore[name-defined]

        # drawing infra
        self._drawing_thread: Optional[QThread] = None
        self._worker: Optional[DrawingWorker] = None

        self._pause_event = threading.Event()
        self._pause_event.set()  # not paused
        self._stop_event = threading.Event()

    def log(self, msg: str) -> None:
        self.state.log.emit(msg)

    # ---------- Project I/O ----------
    def save_project(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.state.to_project_dict(), f, indent=2)
        self.log("Project saved")

    def load_project(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.state.apply_project_dict(data)
        self.log("Loaded project")

    # ---------- PDF ----------
    def save_pdf(self, path: str) -> None:
        p = self.state.params
        x_min, x_max, y_min, y_max, xc, yc = self._safe_center()

        summary_dict = {
            "Orientation": p.fiber_orientation,
            "Speed": f"{p.speed} mm/min",
            "Z-Offset": f"{p.z_offset} mm",
            "Z-Hop": f"{p.z_hop} mm",
            "Pause": f"{p.pause_ms} ms",
            "Droplet Amount": f"{p.droplet_amount} (E units)",
            "Afterdrop": "on" if p.afterdrop else "off",
            "Clean": "on" if p.clean else "off",

            "Safe Area X": f"[{x_min}, {x_max}]",
            "Safe Area Y": f"[{y_min}, {y_max}]",
            "Safe Center": f"({xc:.2f}, {yc:.2f})",

            "Fiber Length": f"{p.fiber_length} mm",
            "Fiber Width": f"{p.fiber_width} mm",
            "Fiber Spacing": f"{p.fiber_spacing} mm",

            "Syringe Current Amount": f"{p.syringe_current_amount}",
            "Syringe Droplet Units": f"{p.syringe_droplet_units}",
        }

        c = canvas.Canvas(path)  # create PDF file

        c.setFont("Helvetica-Bold", 24)  # set title font
        c.drawString(40, 800, "Project Summary")  # draw title at top
        c.setFont("Helvetica", 14)  # set font for content

        y = 760  # starting vertical position (below title)

        for k, v in summary_dict.items():
            c.drawString(40, y, f"{k}: {v}")  # write one line (key: value)
            y -= 24  # move down for next line

            if y < 60:  # if near bottom of page
                c.showPage()  # create new page
                c.setFont("Helvetica", 14)  # reset font after page break
                y = 800  # reset position to top

        c.save()  # finalize and save PDF file
        self.log("PDF saved")  # log message

        # ---------- Serial ----------
    def _find_printer_port(self, baudrate: int = 115200) -> Optional[str]:
        # checks if pyserial is installed
        if list_ports is None:
            return None
        
        for port in list(list_ports.comports()):  # get all avaible ports
            dev = getattr(port, "device", None)  # gets ports device
            if not dev:       # if its not valid, just skip
                continue
            try:   
                if serial is None:
                    return None
                s = serial.Serial(dev, baudrate=baudrate, timeout=1) #try to open a port, if it work, return the port
                s.close() # close, because its just a test
                return dev
            except Exception:
                continue
        return None
    
    def connect(self, baudrate: int = 115200) -> bool:
        # Ensure pyserial is available in the current environment
        if serial is None:
            self.log("pyserial not available (install pyserial).")
            return False

        # Attempt to automatically detect an available serial port
        port = self._find_printer_port(baudrate=baudrate)
        if not port:
            # No valid serial device detected (printer may be disconnected or driver missing)
            self.log("No serial port found.")
            return False

        try:
            # Open serial connection to the detected port
            self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)

            # Many 3D printers (e.g., Marlin-based) reset when a serial connection is opened.
            # A short delay is required to allow the firmware to reboot and become responsive.
            time.sleep(2.0)

            # Clear any residual data in buffers caused by the reset or previous communication
            try:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except Exception:
                # Buffer reset may fail on some drivers/OS combinations; safe to ignore
                pass

            # Notify UI that connection is established BEFORE sending commands
            # This ensures UI state is updated even if subsequent commands take time
            self.connection_changed.emit(True)

            self.log(f"Connected to the printer on {port}")
            self.log("Homing printer...")

            # Perform mandatory homing (G28) after connection to ensure a known reference state
            # This is critical for safe and repeatable motion operations
            self._send_and_wait_ok("G28", timeout_s=120.0)

            self.log("Homing done")
            return True
        
        except Exception as e:
            # Handle any failure during connection or initialization
            self.log(f"Could not connect: {e}")

            # Ensure serial resource is properly released on failure
            try:
                if self.ser is not None:
                    self.ser.close()
            except Exception:
                pass

            # Reset internal state and notify UI of disconnection
            self.ser = None
            self.connection_changed.emit(False)
            return False
        
    def disconnect(self) -> bool:
        try:
            # Ensure any ongoing drawing process is safely stopped before closing the connection
            self.stop_drawing()

            # Close the serial connection if it is active
            if self.ser is not None:
                self.ser.close()
                self.ser = None  # Reset reference to indicate no active connection

            # Notify UI about the disconnection state
            self.connection_changed.emit(False)

            # Log successful disconnection
            self.log("Disconnected from the printer")
            return True

        except Exception as e:
            # Handle unexpected errors during disconnection
            self.log(f"Could not disconnect: {e}")
            return False
        
    def _send_and_wait_ok(self, command: str, timeout_s: float = 30.0) -> None:
        """
        Send a single G-code command and block until an 'ok' response is received.
        """
        # Ensure an active serial connection exists
        if self.ser is None:
            raise RuntimeError("No connection to the printer")

        # Send command with newline termination
        self.ser.write((command + "\n").encode("utf-8"))

        # Set timeout deadline
        deadline = time.time() + timeout_s
        last_nonempty = None  # Keep last meaningful response for debugging

        # Read responses until 'ok', error, or timeout
        while time.time() < deadline:
            raw = self.ser.readline()
            if not raw:
                continue  # Ignore empty reads

            line = raw.decode(errors="ignore").strip()
            if not line:
                continue  # Ignore blank lines

            last_nonempty = line
            low = line.lower()

            # Success: command completed
            if low == "ok" or low.startswith("ok"):
                return

            # Printer still processing
            if "busy" in low:
                continue

            # Firmware reported error
            if "error" in low:
                raise RuntimeError(f"Firmware error after '{command}': {line}")

        # No response within timeout
        raise TimeoutError(
            f"Timeout waiting for ok after: {command}"
            + (f" (last: {last_nonempty})" if last_nonempty else "")
        )
    
    