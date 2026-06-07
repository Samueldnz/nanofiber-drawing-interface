from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

from PySide6.QtCore import QObject, Signal, QThread, Slot


import json
import time
import threading
import math
import re
import queue
from datetime import datetime
from reportlab.lib.pagesizes import A4

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
    z_hop: float = 10.0              # mm
    pause_ms: int = 0                # ms (G4 P...)
    z_offset: float = 0.4            # mm

    clean: bool = True

    # --- CustomCentered safe bounds (seu retângulo seguro) ---
    safe_x_min: float = 45     # ---- offset centralizador
    safe_x_max: float = 227

    safe_y_min: float = 33     # ----- offset centralizador
    safe_y_max: float = 180

    # --- Rectangle anchor (bottom-left corner of draw rectangle) ---
    start_x: float = 0
    start_y: float = 0
    # --- CustomCentered parameters ---
    fiber_orientation: str = "Horizontal"  # Horizontal | Vertical | Both
    fiber_length: float = 80.0            # L (mm)
    fiber_width: float = 40.0             # W (mm)
    fiber_spacing: float = 1.0            # S (mm) distância entre fibras

    current_temperature: float = 25.0
    target_temperature: float = 25.0
    temperature_status: str = "IDLE"
    temperature_reporting_enabled: bool = False

class SyringeEmptyError(Exception):
    pass

class AppState(QObject):
    changed = Signal()
    log = Signal(str)
    temperature_changed = Signal(float)

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
            "Z-Hop": float(p.z_hop),
            "Pause (ms)": int(p.pause_ms),
            "Z-Offset": float(p.z_offset),

            "Clean": bool(p.clean),

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

            # =====================================================
            # TEMPERATURE
            # =====================================================

            "Current Temperature": float(
                p.current_temperature
            ),

            "Target Temperature": float(
                p.target_temperature
            ),

            "Temperature Status": str(
                p.temperature_status
            ),

            "Temperature Reporting Enabled": bool(
                p.temperature_reporting_enabled
            ),
        }

    def apply_project_dict(self, data: Dict[str, Any]) -> None:
        p = self.params

        p.speed = int(data.get("Speed", p.speed))
        p.z_hop = float(data.get("Z-Hop", p.z_hop))
        p.pause_ms = int(data.get("Pause (ms)", p.pause_ms))
        p.z_offset = float(data.get("Z-Offset", p.z_offset))

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

        # =====================================================
        # TEMPERATURE
        # =====================================================

        p.current_temperature = float(
            data.get(
                "Current Temperature",
                p.current_temperature
            )
        )

        p.target_temperature = float(
            data.get(
                "Target Temperature",
                p.target_temperature
            )
        )

        p.temperature_status = str(
            data.get(
                "Temperature Status",
                p.temperature_status
            )
        )

        p.temperature_reporting_enabled = str(
            data.get(
                "Temperature Reporting Enabled",
                p.temperature_reporting_enabled
            )
        ).lower() == "true"

        self.changed.emit()

    # =========================================================
    # TEMPERATURE
    # =========================================================

    def set_current_temperature(
        self,
        value: float
    ):

        self.params.current_temperature = float(value)

        self.temperature_changed.emit(
            float(value)
        )
        self.changed.emit()

    def set_target_temperature(
        self,
        value: float
    ):
        self.params.target_temperature = float(value)
        self.changed.emit()

    def set_temperature_status(
        self,
        status: str
    ):
        self.params.temperature_status = str(status)
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

        self._is_retracted = False
        self._emergency_stopped = False
        self._cooling_fan_enabled = False

        # drawing infra
        self._drawing_thread: Optional[QThread] = None
        self._worker: Optional[DrawingWorker] = None

        self._pause_event = threading.Event()
        self._pause_event.set()  # not paused
        self._stop_event = threading.Event()
        self._graceful_stop_requested = threading.Event()
        self._pause_requested = threading.Event()

        # =========================================================
        # SERIAL LISTENER
        # =========================================================

        self._serial_listener_thread = None
        self._serial_listener_running = False

        # =========================================================
        # SERIAL SYNCHRONIZATION
        # =========================================================
        # protects ALL serial writes
        self._serial_lock = threading.Lock()

        # queue for synchronous command responses
        self._response_queue = queue.Queue()

    def log(self, msg: str) -> None:
        self.state.log.emit(msg)

    # =========================================================
    # TEMPERATURE REPORTING
    # =========================================================

    def enable_temperature_reporting(
        self,
        interval_seconds: int = 2
    ):

        if not self.is_connected():
            return

        self.send_gcode(
            f"M155 S{interval_seconds}"
        )

        self.state.params.temperature_reporting_enabled = True

        self.log(
            f"Temperature auto-report enabled ({interval_seconds}s)"
        )

    def is_connected(self) -> bool:

        return (
            self.ser is not None
            and self.ser.is_open
        )
    
    def disable_temperature_reporting(self):

        if not self.is_connected():
            return

        self.send_gcode("M155 S0")

        self.state.params.temperature_reporting_enabled = False

        self.log(
            "Temperature auto-report disabled"
        )

    def update_cooling_fan(
        self,
        current_temp: float
    ):

        self.apply_fan_state_from_temperature()

    def apply_fan_state_from_temperature(self):

        current_temp = float(
            self.state.params.current_temperature
        )

        if (
            current_temp > 80
            and not self._cooling_fan_enabled
        ):

            self.send_gcode(
                "M106 S255"
            )

            self._cooling_fan_enabled = True

            self.log(
                f"Cooling fan enabled ({current_temp:.1f} °C)"
            )

        elif (
            current_temp <= 80
            and self._cooling_fan_enabled
        ):

            self.send_gcode(
                "M106 S0"
            )

            self._cooling_fan_enabled = False

            self.log(
                f"Cooling fan disabled ({current_temp:.1f} °C)"
            )

    # =========================================================
    # SET TEMPERATURE
    # =========================================================

    def set_temperature(
        self,
        target: float
    ):
        if self.ser is None or not self.ser.is_open:

            self.log(
                "Error: No connection to the printer"
            )

            raise RuntimeError(
                "Printer is not connected"
            )

        target = max(
            25.0,
            min(300.0, float(target))
        )

        self.send_gcode(
            f"M104 S{target:.1f}"
        )

        self.state.set_target_temperature(
            target
        )

        self.log(
            f"Target temperature set to {target:.1f} °C"
        )

    # =========================================================
    # TEMPERATURE PARSER
    # =========================================================

    def _parse_temperature(
        self,
        line: str
    ):
        """
        Example:

        ok T:31.4 /40.0 B:25.0 /0.0
        """
        current_match = re.search(
            r"T\d*:\s*([0-9]+(?:\.[0-9]+)?)",
            line
        )
        if not current_match:
            return

        try:
            current_temp = float(
                current_match.group(1)
            )

        except Exception:
            return

        self.state.set_current_temperature(
            current_temp
        )

        self.update_cooling_fan(
            current_temp
        )

        target = float(
            self.state.params.target_temperature
        )


        if target <= 0:
            status = "IDLE"

        elif abs(current_temp - target) < 1.0:
            status = "STABLE"

        elif current_temp < target:
            status = "HEATING"
        
        else:
            status = "COOLING"

        self.state.set_temperature_status(
            status
        )

    # ---------- Project I/O ----------
    def save_project(self, path: str) -> bool:

        try:

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.state.to_project_dict(),
                    f,
                    indent=2,
                    sort_keys=False
                )

            self.log(
                f"Project saved: {path}"
            )

            return True

        except Exception as e:

            self.log(
                f"Failed to save project: {e}"
            )

            return False

    def load_project(self, path: str) -> bool:

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            self.state.apply_project_dict(data)

            self.log(
                f"Loaded project: {path}"
            )

            return True

        except Exception as e:

            self.log(
                f"Failed to load project: {e}"
            )

            return False

    # ---------- PDF ----------
    def save_pdf(self, path: str) -> bool:
        p = self.state.params
        x_min, x_max, y_min, y_max, xc, yc = self._safe_center()

        sections = {

            "DRAW SETTINGS": {

                "Orientation":
                    p.fiber_orientation,

                "Speed":
                    f"{p.speed} mm/min",

                "Z-Offset":
                    f"{p.z_offset} mm",

                "Z-Hop":
                    f"{p.z_hop} mm",

                "Pause":
                    f"{p.pause_ms} ms",

                "Clean":
                    "on" if p.clean else "off",
            },

            "SAFE AREA": {

                "Safe Area X":
                    f"[{x_min}, {x_max}]",

                "Safe Area Y":
                    f"[{y_min}, {y_max}]",

                "Safe Center":
                    f"({xc:.2f}, {yc:.2f})",
            },

            "FIBER CONFIGURATION": {

                "Fiber Length":
                    f"{p.fiber_length} mm",

                "Fiber Width":
                    f"{p.fiber_width} mm",

                "Fiber Spacing":
                    f"{p.fiber_spacing} mm",
            },

            "TEMPERATURE": {

                "Current Temperature":
                    f"{p.current_temperature:.1f} °C",

                "Target Temperature":
                    f"{p.target_temperature:.1f} °C",

                "Temperature Status":
                    str(p.temperature_status),
            }
        }

        try:

            c = canvas.Canvas(
                    path,
                    pagesize=A4
                ) # create PDF file

            c.setFont("Helvetica-Bold", 24)  # set title font
            c.drawString(40, 810, "Project Summary") # draw title at top
            c.setFont("Helvetica", 11)

            c.drawString(
                40,
                790,
                datetime.now().strftime(
                    "Generated on %Y-%m-%d %H:%M:%S"
                )
            )

            c.setFont("Helvetica", 14)  # set font for content

            y = 750 # starting vertical position (below title)

            for section_name, items in sections.items():

                c.setFont(
                    "Helvetica-Bold",
                    16
                )

                c.drawString(
                    40,
                    y,
                    section_name
                )

                y -= 28

                c.setFont(
                    "Helvetica",
                    13
                )

                for k, v in items.items():

                    c.drawString(
                        56,
                        y,
                        f"{k:<24} {v}"
                    )

                    y -= 22

                    if y < 60:

                        c.showPage()

                        c.setFont(
                            "Helvetica-Bold",
                            20
                        )

                        c.drawString(
                            40,
                            810,
                            "Project Summary"
                        )

                        c.setFont(
                            "Helvetica",
                            11
                        )

                        c.drawString(
                            40,
                            790,
                            datetime.now().strftime(
                                "Generated on %Y-%m-%d %H:%M:%S"
                            )
                        )

                        c.setFont(
                            "Helvetica-Bold",
                            16
                        )

                        c.drawString(
                            40,
                            740,
                            section_name
                        )

                        c.setFont(
                            "Helvetica",
                            13
                        )

                        y = 720

                y -= 14

            c.save()

            self.log(
                f"PDF saved: {path}"
            )

            return True
        
        except Exception as e:

            self.log(
                f"Failed to save PDF: {e}"
            )

            return False

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
    
    # =========================================================
    # SERIAL LISTENER
    # =========================================================

    def _start_serial_listener(self):

        if self._serial_listener_running:
            return

        self._serial_listener_running = True

        self._serial_listener_thread = threading.Thread(
            target=self._serial_listener_loop,
            daemon=True
        )

        self._serial_listener_thread.start()

        self.log(
            "Serial listener started"
        )


    def _stop_serial_listener(self):

        self._serial_listener_running = False

        if self._serial_listener_thread is not None:

            self._serial_listener_thread.join(timeout=1.0)

            self._serial_listener_thread = None

        self.log(
            "Serial listener stopped"
        )


    def _serial_listener_loop(self):

        while self._serial_listener_running:

            try:

                if self.ser is None:
                    time.sleep(0.1)
                    continue

                raw = self.ser.readline()

                if not raw:
                    continue

                line = raw.decode(
                    errors="ignore"
                ).strip()

                if not line:
                    continue

                low = line.lower()

                if low.startswith("start"):
                    continue

                # =================================================
                # OK RESPONSES
                # =================================================

                if low == "ok" or low.startswith("ok"):

                    self._response_queue.put(line)

                    self._parse_temperature(line)

                    continue

                # =================================================
                # BUSY
                # =================================================

                if "busy" in low:

                    continue

                # =================================================
                # ERRORS
                # =================================================

                if "error" in low:

                    self._response_queue.put(
                        RuntimeError(line)
                    )

                    continue

                # =================================================
                # TEMPERATURE
                # =================================================

                self._parse_temperature(line)

            except Exception as e:

                self.log(
                    f"Serial listener error: {e}"
                )

                time.sleep(0.2)
    
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
            self._start_serial_listener()

            self.log("Homing printer...")

            self._send_and_wait_ok("G28", timeout_s=120.0)

            self.log("Homing done")

            self.send_gcode(
                "M106 S0"
            )

            self._cooling_fan_enabled = False

            # enable live temperature telemetry
            self.enable_temperature_reporting(2)

            self.log(
                "Cooling fan forced OFF at startup"
            )

            self.set_temperature(
                self.state.params.target_temperature
            )

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
            self._stop_serial_listener()

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
        
    def _send_and_wait_ok(
        self,
        command: str,
        timeout_s: float = 30.0
    ) -> None:

        if self.ser is None:
            raise RuntimeError(
                "No connection to the printer"
            )

        # clear old responses
        while not self._response_queue.empty():

            try:
                self._response_queue.get_nowait()

            except Exception:
                break

        # protected write
        with self._serial_lock:
            # to avoid disyncronezed "ok" answer in the queue
            while not self._response_queue.empty():
                try:
                    self._response_queue.get_nowait()
                except Exception:
                    break

            self.ser.write(
                (command + "\n").encode("utf-8")
            )

            self.ser.flush()

        deadline = time.time() + timeout_s

        while time.time() < deadline:

            remaining = max(
                0.1,
                deadline - time.time()
            )

            try:

                response = self._response_queue.get(
                    timeout=remaining
                )

            except queue.Empty:
                continue

            if isinstance(response, RuntimeError):

                raise response

            return

        raise TimeoutError(
            f"Timeout waiting for ok after: {command}"
        )
    
    # =========================================================
    # RAW GCODE SEND
    # =========================================================

    def send_gcode(
        self,
        command: str
    ) -> None:

        """
        Non-blocking raw G-code sender.

        Used for:
        - M104
        - M155
        - telemetry
        - non-critical commands
        """

        if self.ser is None:
            raise RuntimeError(
                "No connection to the printer"
            )

        with self._serial_lock:
            self.ser.write(
                (command + "\n").encode("utf-8")
            )

            self.ser.flush()

        self.log(f"> {command}")
    
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
        self._graceful_stop_requested.clear()
        self._pause_requested.clear()
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
        """
        Graceful pause request.

        Behavior:
        - finishes current fiber
        - retracts filament
        - pauses workflow safely
        - waits for resume
        """

        if self._drawing_thread is None:
            return

        self.log(
            "Pause requested..."
        )

        self._pause_requested.set()

    def resume_drawing(self) -> None:

        if self._drawing_thread is None:
            return

        self._pause_requested.clear() # without this line can be paused forever 
        self._pause_event.set()

    def toggle_pause(self) -> None:
        if self._drawing_thread is None:
            return
        if self._pause_event.is_set():
            self.pause_drawing()
        else:
            self.resume_drawing()

    def stop_drawing(self) -> None:
        """
        Graceful drawing stop.

        Behavior:
        - finishes current movement/fiber
        - stops generation after current fiber
        - retracts filament
        - parks toolhead safely
        - disables heater
        - keeps cooling fan active
        """

        if self._drawing_thread is None:
            return

        self.log(
            "Graceful stop requested..."
        )

        # =====================================================
        # REQUEST STOP AFTER CURRENT FIBER
        # =====================================================

        self._graceful_stop_requested.set()

        # =====================================================
        # ENSURE EXECUTION IS NOT PAUSED
        # =====================================================

        self._pause_event.set()

        # =====================================================
        # WAIT FOR THREAD TO FINISH CURRENT FIBER
        # =====================================================

        try:

            if self._drawing_thread is not None:

                finished = self._drawing_thread.wait(
                    30000
                )

                if not finished:

                    raise RuntimeError(
                        "Drawing thread timeout during stop"
                    )

        except Exception as e:

            self.log(
                f"Thread wait failed: {e}"
            )

        # =====================================================
        # SAFE SHUTDOWN SEQUENCE
        # =====================================================

        try:

            if self.ser is not None:

                # -------------------------------------------------
                # RETRACT FILAMENT
                # -------------------------------------------------

                if not self._is_retracted:
                    self.send_gcode(
                        "G10"
                    )
                    self._is_retracted = True

                # -------------------------------------------------
                # SAFE PARK
                # -------------------------------------------------

                self.send_gcode(
                    "G0 Z10 F1500"
                )

                self.send_gcode(
                    "G0 X10 Y190 F3000"
                )

                # -------------------------------------------------
                # DISABLE HEATER
                # -------------------------------------------------

                self.send_gcode(
                    "M104 S0"
                )

                # -------------------------------------------------
                # APPLY FAN POLICY
                # -------------------------------------------------

                self.apply_fan_state_from_temperature()

            self.log(
                "Drawing stopped safely"
            )

        except Exception as e:

            self.log(
                f"Stop sequence failed: {e}"
            )
    
    def emergency_stop(self) -> None:
        """
        Immediate motion interruption using M410.

        - Stops all buffered motion instantly
        - Stops current drawing workflow
        - Disables heater
        - Keeps cooling fan active
        - Preserves firmware/serial connection
        """
        if self.ser is None:
            self.log("Error: No connection to the printer")
            return

        # =====================================================
        # INTERNAL EXECUTION STATE
        # =====================================================

        self._stop_event.set()
        self._emergency_stopped = True
        self._pause_event.set()

        # =====================================================
        # CLEAR RESPONSE QUEUE
        # =====================================================

        while not self._response_queue.empty():

            try:
                self._response_queue.get_nowait()

            except Exception:
                break

        try:

            if self.ser is not None:

                self.apply_fan_state_from_temperature()

                with self._serial_lock:    

                    # -------------------------------------------------
                    # DISABLE HOTEND HEATER
                    # -------------------------------------------------

                    self.ser.write(
                        b"M104 S0\n"
                    )

                    # -------------------------------------------------
                    # RETRACT FILAMENT
                    # -------------------------------------------------
                    if not self._is_retracted:
                        self.ser.write(
                            b"G10\n"
                        )
                        self._is_retracted = True


                    self.ser.flush()

            self.log(
                "Emergency stop triggered"
            )

        except Exception as e:

            self.log(
                f"Emergency stop failed: {e}"
            )

        # =====================================================
        # FORCE UI STATE RESET
        # =====================================================

        self.drawing_running_changed.emit(
            False
        )

        self.drawing_paused_changed.emit(
            False
        )

        # =====================================================
        # DESTROY ACTIVE THREAD REFERENCES
        # =====================================================

        if self._drawing_thread is not None:

            try:    
                self._stop_event.set()
                self._drawing_thread.quit()
                self._drawing_thread.wait(2000)

            except Exception as e:

                self.log(
                    f"Thread shutdown failed: {e}"
                )

        self._drawing_thread = None
        self._worker = None
    
    def recover_from_emergency_stop(self) -> bool:
        """
        Restore machine to a clean READY state after emergency stop.

        Final state:
        - firmware synchronized
        - planner cleared
        - machine homed
        - heater OFF
        - telemetry ON
        - UI reset
        - ready for manual operation
        """

        self.log(
            "Starting recovery procedure..."
        )

        # =====================================================
        # VALIDATE CONNECTION
        # =====================================================

        if self.ser is None or not self.ser.is_open:

            self.log(
                "Recovery failed: printer disconnected"
            )

            return False

        try:

            # =================================================
            # RESET INTERNAL STATE
            # =================================================

            self.log(
                "Resetting controller state..."
            )

            self._stop_event.clear()

            self._pause_event.set()

            self._pause_requested.clear()

            self._graceful_stop_requested.clear()

            self._is_retracted = False

            # =================================================
            # CLEAR RESPONSE QUEUE
            # =================================================

            while not self._response_queue.empty():

                try:
                    self._response_queue.get_nowait()

                except Exception:
                    break

            # =================================================
            # RESET THREAD REFERENCES
            # =================================================

            if self._drawing_thread is not None:

                try:
                    self._drawing_thread.quit()
                    self._drawing_thread.wait(3000)

                except Exception as e:
                    self.log(f"Recovery thread cleanup failed: {e}")

            self._drawing_thread = None
            self._worker = None

            # =================================================
            # CLEAR FIRMWARE PLANNER
            # =================================================

            self.log(
                "Synchronizing firmware..."
            )

            self._send_and_wait_ok(
                "M400"
            )

            # =================================================
            # DISABLE HEATER
            # =================================================

            self.log(
                "Disabling heater..."
            )

            self._send_and_wait_ok(
                "M104 S0"
            )

            # =================================================
            # KEEP COOLING FAN ACTIVE
            # =================================================

            self.apply_fan_state_from_temperature()

            # =================================================
            # RESTORE DEFAULT MOTION MODES
            # =================================================

            self.log(
                "Restoring motion modes..."
            )

            self._send_and_wait_ok(
                "G90"
            )  # absolute XY

            self._send_and_wait_ok(
                "M83"
            )  # relative extrusion

            self._send_and_wait_ok(
                "G92 E0"
            )

            # =================================================
            # HOME MACHINE
            # =================================================

            self.log(
                "Homing machine..."
            )

            # relative mode
            self._send_and_wait_ok("G91")

            # lift safely
            self._send_and_wait_ok("G0 Z10 F1500")

            # back to absolute
            self._send_and_wait_ok("G90")

            self._send_and_wait_ok(
                "G28",
                timeout_s=120.0
            )

            # =================================================
            # SAFE PARK POSITION
            # =================================================

            self.log(
                "Parking toolhead..."
            )

            self._send_and_wait_ok(
                "G0 X10 Y190 Z10 F3000"
            )

            # =================================================
            # RESET TEMPERATURE STATE
            # =================================================

            self.state.set_target_temperature(25.0)

            self.state.set_temperature_status(
                "IDLE"
            )

            # =================================================
            # RESTORE TEMPERATURE TELEMETRY
            # =================================================

            self.enable_temperature_reporting(2)

            # =================================================
            # RESET UI STATE
            # =================================================

            self.drawing_running_changed.emit(
                False
            )

            self.drawing_paused_changed.emit(
                False
            )

            self.log(
                "Recovery completed successfully"
            )

            self.log(
                "Machine ready"
            )
            self._emergency_stopped = False
            return True

        except Exception as e:

            self.log(
                f"Recovery failed: {e}"
            )

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
        x_min, x_max, y_min, y_max, _, _ = self._safe_center()

        machine_x = x_min + start_x
        machine_y = y_min + start_y

        if axis == "horizontal":

            # length along X
            # width along Y
            x0 = machine_x
            x1 = machine_x + length

            y0 = machine_y
            y1 = machine_y + width

        elif axis == "vertical":

            # width along X
            # length along Y
            x0 = machine_x
            x1 = machine_x + width

            y0 = machine_y
            y1 = machine_y + length

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

        if self._stop_event.is_set():

            raise RuntimeError(
                "Stopped"
            )

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
    ) -> None:

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
        if self._is_retracted:
            send("G11")
            send("G1 E0.1 F300")
            self._is_retracted = False

        # extrusion move
        send(
            f"G1 X{xe:.3f} "
            f"Y{ye:.3f} "
            f"E{E:.3f} "
            f"F{speed}"
        )

        if not self._is_retracted:
            send("G10")
            self._is_retracted = True

        send("M400")
        send("G92 E0") # reset the extrusor



    def _run_pass(
        self,
        axis: str,
        x0: float,
        x1: float,
        y0: float,
        y1: float,
        status_signal: Signal,
    ) -> None:

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

            self._execute_fiber(
                xs=xs,
                ys=ys,
                xe=xe,
                ye=ye,
                speed=speed,
                zoff=zoff,
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

            # =====================================================
            # GRACEFUL PAUSE
            # =====================================================

            if self._pause_requested.is_set():

                try:

                    # ---------------------------------------------
                    # RETRACT FILAMENT
                    # ---------------------------------------------
                    if not self._is_retracted:
                        self.send_gcode(
                            "G10"
                        )
                        self._is_retracted = True

                except Exception as e:

                    self.log(
                        f"Pause retract failed: {e}"
                    )

                self._pause_event.clear()

                self.drawing_paused_changed.emit(
                    True
                )

                self.log(
                    "Paused"
                )

                # ---------------------------------------------
                # WAIT FOR RESUME
                # ---------------------------------------------

                while not self._pause_event.is_set():

                    if self._stop_event.is_set():

                        raise RuntimeError(
                            "Stopped"
                        )

                    if self._graceful_stop_requested.is_set():

                        self.log(
                            "Graceful stop during pause"
                        )

                        return

                    time.sleep(0.05)

                try:

                    # ---------------------------------------------
                    # UNRETRACT FILAMENT
                    # ---------------------------------------------
                    if self._is_retracted:
                        self.send_gcode(
                            "G11"
                        )
                        self._is_retracted = False

                except Exception as e:

                    self.log(
                        f"Resume unretract failed: {e}"
                    )

                self._pause_requested.clear()

                self.drawing_paused_changed.emit(
                    False
                )

                self.log(
                    "Resumed"
                )

            # =====================================================
            # GRACEFUL STOP
            # =====================================================

            if self._graceful_stop_requested.is_set():

                self.log(
                    "Graceful stop completed"
                )

                return

            i += 1

    def _prime_extruder(self) -> None:

        send = self._send_checked
        p = self.state.params

        # =====================================================
        # PURGE POSITION (SAFE AREA BORDER)
        # =====================================================

        purge_x = float(p.safe_x_min) + 2.0
        purge_y = float(p.safe_y_min) + 2.0

        purge_line_length = 15.0

        # =====================================================
        # ENSURE EXTRUDER IS NOT RETRACTED
        # =====================================================

        if self._is_retracted:

            send("G11")

            self._is_retracted = False

        # =====================================================
        # DISCOVER FIRST FIBER START POSITION
        # =====================================================

        rectangles = self._get_active_rectangles()

        axis, rect = rectangles[0]

        x0, x1, y0, y1 = rect

        if axis == "horizontal":

            first_x = x0
            first_y = y0

        elif axis == "vertical":

            first_x = x0
            first_y = y0

        else:

            raise RuntimeError(
                f"Invalid axis: {axis}"
            )

        # =====================================================
        # RESET EXTRUDER
        # =====================================================

        send("G92 E0")

        # =====================================================
        # MOVE TO PURGE LOCATION
        # =====================================================

        send(
            f"G0 X{purge_x:.3f} "
            f"Y{purge_y:.3f} "
            f"F3000"
        )

        send(
            f"G0 Z{p.z_offset:.3f} "
            f"F1500"
        )

        # =====================================================
        # STATIONARY PRIME (~2 SECONDS)
        # =====================================================

        send(
            "G1 E2.0 F60"
        )

        # =====================================================
        # PURGE LINE
        # =====================================================

        purge_end_x = purge_x + purge_line_length

        e_line = self._filament_length_to_extrude(
            purge_x,
            purge_y,
            purge_end_x,
            purge_y
        )

        send(
            f"G1 X{purge_end_x:.3f} "
            f"Y{purge_y:.3f} "
            f"E{e_line:.3f} "
            f"F300"
        )

        # =====================================================
        # RETRACT
        # =====================================================

        send("G10")

        self._is_retracted = True

        send("G92 E0")

        # =====================================================
        # LIFT NOZZLE
        # =====================================================

        send(
            f"G0 Z{p.z_offset + 2.0:.3f} "
            f"F1500"
        )

        # =====================================================
        # GO TO FIRST FIBER
        # =====================================================

        send(
            f"G0 X{first_x:.3f} "
            f"Y{first_y:.3f} "
            f"F3000"
        )

        send("M400")


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

        self._send_and_wait_ok(
            f"M109 S{float(self.state.params.target_temperature)}",
            timeout_s=300.0
        )

        # ---------------- purge line ----------------

        self._prime_extruder()


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
        # Ensure printer is connected
        if self.ser is None:
            self.log("Error: No connection to the printer")
            
            raise RuntimeError(
                "Printer is not connected"
            )
        
        self.log("Test Z-Offset")
        send = self._send_checked
        send(f"G1 Z{self.state.params.z_offset:.3f} F1000")