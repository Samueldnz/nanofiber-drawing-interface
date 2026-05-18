from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

from PySide6.QtCore import QObject, Signal, QThread, Slot


import json
import time
import threading
import math

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
    fiber_orientation: str = "Horizontal"  # Horizontal | Vertical | Both
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
    
    # ---------- Drawing controls ----------
    def start_drawing(self) -> None:
        """
        Start the drawing process in a background thread.
        The actual drawing logic runs in DrawingWorker.run().
        """
        # Ensure printer is connected
        if self.ser is None:
            self.log("Error: No connection to the printer")
            return

        # Prevent multiple drawing threads
        if self._drawing_thread is not None:
            self.log("Drawing already running")
            return

        # Reset control flags (allow run, not stopped)
        self._stop_event.clear()
        self._pause_event.set()

        # Create worker thread and drawing worker
        self._drawing_thread = QThread()                 # Background thread
        self._worker = DrawingWorker(self)               # Contains drawing logic
        self._worker.moveToThread(self._drawing_thread)  # Execute worker inside thread

        # Start worker when thread starts
        self._drawing_thread.started.connect(self._worker.run)

        # Stop thread when worker finishes
        self._worker.finished.connect(self._drawing_thread.quit)

        # Clean up objects to avoid memory leaks
        self._worker.finished.connect(self._worker.deleteLater)
        self._drawing_thread.finished.connect(self._drawing_thread.deleteLater)

        # Forward worker messages to UI log
        self._worker.status.connect(self.log)

        # Handle worker errors
        self._worker.error.connect(lambda e: self.log(f"Error during Do Science!: {e}"))

        # Final cleanup callback when thread ends
        self._drawing_thread.finished.connect(self._on_drawing_finished)

        # Notify UI state
        self.drawing_running_changed.emit(True)
        self.drawing_paused_changed.emit(False)
        self.log("Start")

        # Start thread → triggers worker.run()
        self._drawing_thread.start()

    def _on_drawing_finished(self) -> None:
        self._drawing_thread = None
        self._worker = None
        self.drawing_running_changed.emit(False)
        self.drawing_paused_changed.emit(False)
        self.log("Finished")

    def pause_drawing(self) -> None:
        if self._drawing_thread is None:
            return
        self._pause_event.clear()
        self.drawing_paused_changed.emit(True)
        self.log("Paused")

    def resume_drawing(self) -> None:
        if self._drawing_thread is None:
            return
        self._pause_event.set()
        self.drawing_paused_changed.emit(False)
        self.log("Resumed")

    def toggle_pause(self) -> None:
        if self._drawing_thread is None:
            return
        if self._pause_event.is_set():
            self.pause_drawing()
        else:
            self.resume_drawing()

    def stop_drawing(self) -> None:
        if self._drawing_thread is None:
            return
        self._stop_event.set()
        self._pause_event.set()
        # ??? INCOMPLETE ???
    
    def emergency_stop(self) -> None:
        """
        Immediate firmware-level emergency stop.

        Sends M112 directly to the printer,
        bypassing normal checked communication.
        """

        # stop internal execution state
        self._stop_event.set()

        # release pause state
        self._pause_event.set()

        try:

            if self.ser is not None:

                # firmware emergency stop
                self.ser.write(b"M112\n")

                # optional flush
                self.ser.flush()

            self.log("EMERGENCY STOP triggered")

        except Exception as e:

            self.log(f"Emergency stop failed: {e}")

        # update UI state immediately
        self.drawing_running_changed.emit(False)
        self.drawing_paused_changed.emit(False)
    
    def reset_after_emergency(self) -> bool:
        """
        Recover printer communication after an emergency stop.

        This function:
        1. Clears internal execution flags
        2. Sends firmware reset/recovery command (M999)
        3. Reinitializes machine state
        4. Restores controller/UI state

        Returns:
            True if recovery succeeded
            False otherwise
        """

        try:

            # printer must still be connected
            if self.ser is None:
                self.log("Cannot reset: printer not connected")
                return False

            # clear controller state
            self._stop_event.clear()
            self._pause_event.set()

            # clear serial buffers
            try:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
            except Exception:
                pass

            self.log("Attempting firmware recovery...")

            # ---------------- firmware reset ----------------

            # M999 = restart after M112 emergency stop
            self.ser.write(b"M999\n")
            self.ser.flush()

            # give firmware time to recover
            time.sleep(2.0)

            # ---------------- reinitialize machine ----------------

            self.log("Reinitializing printer state...")

            self._send_and_wait_ok("G90")
            self._send_and_wait_ok("M82")
            self._send_and_wait_ok("G92 E0")

            # optional re-home
            self.log("Rehoming printer...")
            self._send_and_wait_ok("G28", timeout_s=120.0)

            self.drawing_running_changed.emit(False)
            self.drawing_paused_changed.emit(False)

            self.log("Emergency recovery completed")

            return True

        except Exception as e:

            self.log(f"Recovery failed: {e}")

            # safest fallback:
            # fully disconnect serial
            try:
                self.disconnect()
            except Exception:
                pass

            return False
    
    # ---------- Safe area helpers ----------
    def _safe_center(self) -> tuple[float, float, float, float, float, float]:
        p = self.state.params
        x_min, x_max, y_min, y_max = p.safe_x_min, p.safe_x_max, p.safe_y_min, p.safe_y_max
        xc = (x_min + x_max) / 2.0
        yc = (y_min + y_max) / 2.0
        return x_min, x_max, y_min, y_max, xc, yc

    def _validate_rect(
        self,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
    ) -> tuple[float, float, float, float]:
        """
        Validate rectangle against configured safe bounds.
        Returns the same rectangle if valid.
        """

        x_min, x_max, y_min, y_max, _, _ = self._safe_center()

        if x0 < x_min or x1 > x_max or y0 < y_min or y1 > y_max:
            raise RuntimeError(
                f"Rectangle outside safe bounds. "
                f"Rect: X[{x0:.2f},{x1:.2f}] Y[{y0:.2f},{y1:.2f}] | "
                f"Safe: X[{x_min:.2f},{x_max:.2f}] Y[{y_min:.2f},{y_max:.2f}]"
            )

        return x0, x1, y0, y1


    def _compute_anchored_rect(
        self,
        length: float,
        width: float,
        start_x: float,
        start_y: float,
        axis: str,
    ) -> tuple[float, float, float, float]:
        """
        Compute a rectangle anchored at (start_x, start_y).

        axis:
            "horizontal" -> fibers run along X
            "vertical"   -> fibers run along Y

        Returns:
            (x0, x1, y0, y1)
        """

        # machine compensation
        start_y += 20

        if axis == "horizontal":

            # length along X
            # width along Y
            x0 = start_x
            x1 = start_x + length

            y0 = start_y
            y1 = start_y + width

        elif axis == "vertical":

            # width along X
            # length along Y
            x0 = start_x
            x1 = start_x + width

            y0 = start_y
            y1 = start_y + length

        else:
            raise RuntimeError(f"Invalid axis: {axis}")

        return self._validate_rect(x0, x1, y0, y1)


    def _get_active_rectangles(
        self,
    ) -> list[tuple[str, tuple[float, float, float, float]]]:
        """
        Returns all active drawing rectangles according
        to the selected orientation.

        Returns:
            [
                ("horizontal", (x0, x1, y0, y1)),
                ("vertical",   (x0, x1, y0, y1)),
            ]
        """

        p = self.state.params

        orientation = str(p.fiber_orientation)

        rectangles = []

        if orientation == "Horizontal":

            rect = self._compute_anchored_rect(
                length=float(p.fiber_length),
                width=float(p.fiber_width),
                start_x=float(p.start_x),
                start_y=float(p.start_y),
                axis="horizontal",
            )

            rectangles.append(("horizontal", rect))

        elif orientation == "Vertical":

            rect = self._compute_anchored_rect(
                length=float(p.fiber_length),
                width=float(p.fiber_width),
                start_x=float(p.start_x),
                start_y=float(p.start_y),
                axis="vertical",
            )

            rectangles.append(("vertical", rect))

        elif orientation == "Both":

            h_rect = self._compute_anchored_rect(
                length=float(p.fiber_length),
                width=float(p.fiber_width),
                start_x=float(p.start_x),
                start_y=float(p.start_y),
                axis="horizontal",
            )

            v_rect = self._compute_anchored_rect(
                length=float(p.fiber_length),
                width=float(p.fiber_width),
                start_x=float(p.start_x),
                start_y=float(p.start_y),
                axis="vertical",
            )

            rectangles.append(("horizontal", h_rect))
            rectangles.append(("vertical", v_rect))

        else:
            raise RuntimeError(f"Invalid orientation: {orientation}")

        return rectangles

    def draw_rectangles_are_valid(self) -> bool:
        try:
            _ = self._get_active_rectangles()
            return True
        except Exception:
            return False
    
    @staticmethod
    def _clamp(v: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, v))

    # ---------- Drawing loop ----------
    def _run_drawing_loop(self, status_signal: Signal) -> None:
        if self.ser is None:
            raise RuntimeError("No connection to the printer")
        self._run_custom_centered(status_signal)

    def _wait_pause_or_stop(self) -> None:
        # allows responsive stop while paused
        while not self._pause_event.is_set():
            if self._stop_event.is_set():
                raise RuntimeError("Stopped")
            time.sleep(0.05)
        if self._stop_event.is_set():
            raise RuntimeError("Stopped")

    def _send_checked(self, cmd: str) -> None:
        if self._stop_event.is_set():
            raise RuntimeError("Stopped")
        self._wait_pause_or_stop()
        self._send_and_wait_ok(cmd)

    def _line_length(self, x0, y0, x1, y1):
        return math.sqrt(pow((x1 - x0), 2) + pow((y1 - y0), 2))
    
    def _deposited_volume(self, d):
        # d = distance calculed with line_length
        # w = layer`s width default 0.45
        # h = layer`s height default 0.2
        # V = deposited volume
        V = d * 0.45 * 0.2
        return V
    
    def _filament_area(self):
        # considering diameter = 1.75mm
        r = 1.75 / 2 # 0.875mm
        A_f = math.pi * pow(r, 2)
        return A_f
    
    def _filament_length_to_extrude(self, x0, y0, x1, y1):
        d = self._line_length(x0, y0, x1, y1)

        V = self._deposited_volume(d)
        A_f = self._filament_area()

        E = V / A_f
        return E

    def _horizontal_fiber(
        self,
        i: int,
        x0: float,
        x1: float,
        y0: float,
        spacing: float,
    ) -> tuple[float, float, float, float]:
        """
        Generate one horizontal serpentine fiber.
        Returns:
            (xs, ys, xe, ye)
        """

        y = y0 + i * spacing

        # serpentine motion
        if (i % 2) == 0:
            xs, xe = x0, x1
        else:
            xs, xe = x1, x0

        return xs, y, xe, y


    def _vertical_fiber(
        self,
        i: int,
        x0: float,
        y0: float,
        y1: float,
        spacing: float,
    ) -> tuple[float, float, float, float]:
        """
        Generate one vertical serpentine fiber.
        Returns:
            (xs, ys, xe, ye)
        """

        x = x0 + i * spacing

        # serpentine motion
        if (i % 2) == 0:
            ys, ye = y0, y1
        else:
            ys, ye = y1, y0

        return x, ys, x, ye


    def _clean_motion(
        self,
        axis: str,
        xe: float,
        ye: float,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        speed: int,
    ) -> None:

        send = self._send_checked

        x_min, x_max, y_min, y_max, _, _ = self._safe_center()

        if axis == "horizontal":

            if xe >= (x0 + x1) / 2.0:
                x_a = self._clamp(xe + 5.0, x_min, x_max)
                x_b = self._clamp(xe + 10.0, x_min, x_max)
            else:
                x_a = self._clamp(xe - 5.0, x_min, x_max)
                x_b = self._clamp(xe - 10.0, x_min, x_max)

            send(f"G0 X{x_a:.3f} Z0 F{speed}")
            send(f"G0 X{x_b:.3f} F{speed}")
            send(f"G0 Z3 F{speed}")

        elif axis == "vertical":

            if ye >= (y0 + y1) / 2.0:
                y_a = self._clamp(ye + 5.0, y_min, y_max)
                y_b = self._clamp(ye + 10.0, y_min, y_max)
            else:
                y_a = self._clamp(ye - 5.0, y_min, y_max)
                y_b = self._clamp(ye - 10.0, y_min, y_max)

            send(f"G0 Y{y_a:.3f} Z0 F{speed}")
            send(f"G0 Y{y_b:.3f} F{speed}")
            send(f"G0 Z3 F{speed}")


    def _execute_fiber(
        self,
        xs: float,
        ys: float,
        xe: float,
        ye: float,
        speed: int,
        zoff: float,
        is_retracted: bool,
    ) -> bool:

        send = self._send_checked

        E = self._filament_length_to_extrude(
            xs,
            ys,
            xe,
            ye,
        )

        # move to start
        send(f"G0 X{xs:.3f} Y{ys:.3f} F{speed}")

        # go to print height
        send(f"G0 Z{zoff:.3f} F{speed}")

        # unretract if needed
        if is_retracted:
            send("G11")
            send("G1 E0.1 F300")

        # extrusion move
        send(
            f"G1 X{xe:.3f} "
            f"Y{ye:.3f} "
            f"E{E:.3f} "
            f"F{speed}"
        )

        # retract
        send("G10")

        send("M400")

        return True


    def _run_pass(
        self,
        axis: str,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        status_signal: Signal,
    ) -> None:

        send = self._send_checked

        is_retracted = False
        i = 0

        while True:

            pp = self.state.params

            spacing = float(pp.fiber_spacing)

            if spacing <= 0:
                raise RuntimeError("Fiber spacing must be > 0")

            speed = int(pp.speed)
            zoff = float(pp.z_offset)
            clean = bool(pp.clean)

            # ---------------- generate fiber ----------------

            if axis == "horizontal":

                xs, ys, xe, ye = self._horizontal_fiber(
                    i=i,
                    x0=x0,
                    x1=x1,
                    y0=y0,
                    spacing=spacing,
                )

                # stop condition
                if ys > y1 + 1e-6:
                    break

            elif axis == "vertical":

                xs, ys, xe, ye = self._vertical_fiber(
                    i=i,
                    x0=x0,
                    y0=y0,
                    y1=y1,
                    spacing=spacing,
                )

                # stop condition
                if xs > x1 + 1e-6:
                    break

            else:
                raise RuntimeError(f"Invalid axis: {axis}")

            # ---------------- execute fiber ----------------

            is_retracted = self._execute_fiber(
                xs=xs,
                ys=ys,
                xe=xe,
                ye=ye,
                speed=speed,
                zoff=zoff,
                is_retracted=is_retracted,
            )

            # ---------------- cleaning ----------------

            if clean:
                self._clean_motion(
                    axis=axis,
                    xe=xe,
                    ye=ye,
                    x0=x0,
                    x1=x1,
                    y0=y0,
                    y1=y1,
                    speed=speed,
                )

            status_signal.emit(
                f"{axis.capitalize()} fiber {i + 1} completed"
            )

            i += 1


    def _run_custom_centered(
        self,
        status_signal: Signal,
    ) -> None:

        send = self._send_checked

        # ---------------- header ----------------

        send("M220 S100")
        send("M221 S100")

        send("M207 S1.0 F1500")
        send("M208 F1500")

        send("G90")
        send("M83")

        send("G0 Z2 F1500")

        send("G92 E0")

        send(f"M109 S{float(self.state.params.temperature)}")

        # ---------------- active patterns ----------------

        rectangles = self._get_active_rectangles()

        for axis, rect in rectangles:

            x0, x1, y0, y1 = rect

            self._run_pass(
                axis=axis,
                x0=x0,
                x1=x1,
                y0=y0,
                y1=y1,
                status_signal=status_signal,
            )

        # ---------------- footer ----------------

        send("M300 S440 P200")
        send("G0 X10 Y190 Z30 F3000")

    # ---------- Misc ----------
    def movement_test(self) -> None:
        self.log("Movement test")

    def test_zoffset(self) -> None:
        self.log("Test Z-Offset")
        send = self._send_checked
        send(f"G1 Z{self.state.params.z_offset:.3f} F1000")