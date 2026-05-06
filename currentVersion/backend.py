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

    # ---------- Safe area helpers ----------
    def _safe_center(self) -> tuple[float, float, float, float, float, float]:
        p = self.state.params
        x_min, x_max, y_min, y_max = p.safe_x_min, p.safe_x_max, p.safe_y_min, p.safe_y_max
        xc = (x_min + x_max) / 2.0
        yc = (y_min + y_max) / 2.0
        return x_min, x_max, y_min, y_max, xc, yc


    def _compute_anchored_rect(
        self,
        length: float,
        width: float,
        orient: str,
        start_x: float,
        start_y: float,
    ) -> tuple[float, float, float, float]:
        """
        Compute the drawing rectangle anchored at (start_x, start_y)
        and validate it against the configured safe bounds.

        Returns:
            (x0, x1, y0, y1)
        """
        # Get configured safe area limits
        x_min, x_max, y_min, y_max, _, _ = self._safe_center()

        # Apply Y-axis offset compensation
        start_y += 20

        # Compute rectangle dimensions based on fiber orientation
        if orient == "Horizontal":
            x0, x1 = start_x, start_x + length
            y0, y1 = start_y, start_y + width
        else:
            x0, x1 = start_x, start_x + width
            y0, y1 = start_y, start_y + length

        # Ensure the rectangle remains fully inside the safe area
        if x0 < x_min or x1 > x_max or y0 < y_min or y1 > y_max:
            raise RuntimeError(
                f"Rectangle outside safe bounds. "
                f"Rect: X[{x0:.2f},{x1:.2f}] Y[{y0:.2f},{y1:.2f}] | "
                f"Safe: X[{x_min:.2f},{x_max:.2f}] Y[{y_min:.2f},{y_max:.2f}]"
            )

        return x0, x1, y0, y1

    def get_draw_rectangle(self) -> tuple[float, float, float, float]:
        """Convenience for UI preview and validation (raises if invalid)."""
        p = self.state.params
        return self._compute_anchored_rect(
            float(p.fiber_length),
            float(p.fiber_width),
            str(p.fiber_orientation),
            float(p.start_x),
            float(p.start_y),
        )

    def draw_rectangle_is_valid(self) -> bool:
        try:
            _ = self.get_draw_rectangle()
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

    def _run_custom_centered(self, status_signal: Signal) -> None:
        """
        Custom mode:
        - user sets fiber_length (L), fiber_width (W), fiber_spacing (S)
        - rectangle is centered inside safe bounds
        - parameters are read live per-fiber
        """
        send = self._send_checked

        # header
        send("M220 S100") #Sets movement speed multiplier to 100%.
        send("M302 S0") #Allows extrusion at any temperature.
        send("M221 S100") #Sets extrusion flow multiplier to 100%.
        send("G90") #Use absolute positioning for X/Y/Z movement.
        send("M82") #Use absolute extrusion mode.
        send("G1 Z2 F1500") #Move Z axis to 2 mm at feedrate 1500.
        send("G92 E0") #Reset extruder position to zero.

        def extrusion() -> None:
            pp = self.state.params
            send("G91") #Switch to relative positioning.
            send(f"G1 E-{float(pp.droplet_amount)} F200") #move extruder by drolet amount in feedrate 200, negative way
            send("G4 P1000") #Pause for 1000 ms
            send("G90") 
            self.state.set_param(
                "syringe_current_amount",
                self.state.params.syringe_current_amount - float(pp.droplet_amount),
            )

        def afterdrop() -> None:
            pp = self.state.params
            send("G91")
            send(f"G1 E-{float(pp.droplet_amount)} F200")
            send("G4 P500")  #Pause for 500 ms
            send("G90")
            send(f"G1 F{int(pp.speed)}") #Reapplies configured movement feedrate.
            self.state.set_param(
                "syringe_current_amount",
                self.state.params.syringe_current_amount - float(pp.droplet_amount),
            )


        # run layers (anchored rectangle pattern; SAFE HARD)

        # we validate on every fiber because parameters can change live
        send("G90")
        send(f"G1 Z7 F{int(self.state.params.speed)}")

        i = 0
        while True:
            # allow live updates to apply to the NEXT fiber safely
            pp = self.state.params

            orient = str(pp.fiber_orientation)
            L = float(pp.fiber_length)
            W = float(pp.fiber_width)
            S = float(pp.fiber_spacing)

            if L <= 0 or W < 0:
                raise RuntimeError("Fiber length must be > 0 and width must be >= 0")
            if S <= 0:
                raise RuntimeError("Fiber spacing must be > 0")

            # SAFE HARD rectangle (raises if out of bounds)
            x0, x1, y0, y1 = self._compute_anchored_rect(
                L, W, orient, float(pp.start_x), float(pp.start_y)
            )

            speed = int(pp.speed)
            zoff = float(pp.z_offset)
            zhop = float(pp.z_hop)
            pause_ms = int(pp.pause_ms)
            after = bool(pp.afterdrop)
            clean = bool(pp.clean)

            if orient == "Horizontal":
                y = y0 + i * S
                if y > y1 + 1e-6:
                    break

                # Alternate fiber direction to create a continuous serpentine path
                # Even fibers: left → right
                # Odd fibers: right → left
                if (i % 2) == 0:
                    xs, xe = x0, x1
                else:
                    xs, xe = x1, x0

                # Move to fiber start position
                send(f"G1 X{xs:.3f} Y{y:.3f} F{speed}")

                # Lower nozzle/syringe to deposition height
                send(f"G1 Z{zoff:.3f} F{speed}")

                # Deposit initial droplet
                extrusion()

                # Raise nozzle slightly before movement
                send(f"G1 Z{zhop:.3f} F{speed}")

                # Optional stabilization delay after droplet deposition
                if pause_ms:
                    send(f"G4 P{pause_ms}")

                # Draw fiber from start point to end point
                send(f"G1 X{xe:.3f} Y{y:.3f} F{speed}")

                # Return to deposition height
                send(f"G1 Z{zoff:.3f} F{speed}")

                # Optional post-deposition extrusion/retraction step
                if after:
                    afterdrop()

                if clean:
                    x_min, x_max, y_min, y_max, _, _ = self._safe_center()
                    # move a bit further outside the end side (clamped to safe)
                    if xe >= (x0 + x1) / 2.0:
                        x_a = self._clamp(xe + 5.0, x_min, x_max)
                        x_b = self._clamp(xe + 10.0, x_min, x_max)
                    else:
                        x_a = self._clamp(xe - 5.0, x_min, x_max)
                        x_b = self._clamp(xe - 10.0, x_min, x_max)
                    send(f"G1 X{x_a:.3f} Z0 F{speed}")
                    send(f"G1 X{x_b:.3f} F{speed}")
                    send(f"G1 Z3 F{speed}")

                send("M400")

            else: 
                x = x0 + i * S
                if x > x1 + 1e-6:
                    break

                if (i % 2) == 0:
                    ys, ye = y0, y1
                else:
                    ys, ye = y1, y0

                send(f"G1 X{x:.3f} Y{ys:.3f} F{speed}")
                send(f"G1 Z{zoff:.3f} F{speed}")
                extrusion()
                send(f"G1 Z{zhop:.3f} F{speed}")
                if pause_ms:
                    send(f"G4 P{pause_ms}")

                send(f"G1 X{x:.3f} Y{ye:.3f} F{speed}")
                send(f"G1 Z{zoff:.3f} F{speed}")

                if after:
                    afterdrop()

                if clean:
                    x_min, x_max, y_min, y_max, _, _ = self._safe_center()
                    if ye >= (y0 + y1) / 2.0:
                        y_a = self._clamp(ye + 5.0, y_min, y_max)
                        y_b = self._clamp(ye + 10.0, y_min, y_max)
                    else:
                        y_a = self._clamp(ye - 5.0, y_min, y_max)
                        y_b = self._clamp(ye - 10.0, y_min, y_max)
                    send(f"G1 Y{y_a:.3f} Z0 F{speed}")
                    send(f"G1 Y{y_b:.3f} F{speed}")
                    send(f"G1 Z3 F{speed}")

                send("M400")

            i += 1

            # footer
            send("M300 S440 P200")
            send("G0 X10 Y190 Z30 F3000")

    # ---------- Legacy (ported from GUI.py logic, with live params) ----------
    
    # ---------- Syringe (ported) ----------
    _ML_TO_EPOS = {1: 20, 2: 53, 3: 86, 4: 119, 5: 152}

    def syringe_goto_ml(self, ml_mark: int) -> None:
        if self.ser is None:
            self.log("Error: No connection to the printer")
            return
        if ml_mark not in self._ML_TO_EPOS:
            self.log(f"Syringe: invalid mark {ml_mark}")
            return
        epos = float(self._ML_TO_EPOS[ml_mark])
        self.ser.write((f"M302 S0\nG1 E{int(epos)} F200\n").encode("utf-8"))
        self.state.set_param("syringe_current_amount", epos)
        self.log(f"Go to {ml_mark} ml")

    def syringe_intake_amount(self) -> None:
        if self.ser is None:
            self.log("Error: No connection to the printer")
            return
        p = self.state.params
        units = int(p.syringe_droplet_units)
        self.ser.write(("G91\n").encode("utf-8"))
        self.ser.write((f"M302 S0\nG1 E{units} F200 ;intake {units} units\n").encode("utf-8"))
        self.ser.write(("G90\n").encode("utf-8"))
        self.state.set_param("syringe_current_amount", float(p.syringe_current_amount + units))
        self.log(f"Intake {units} units")

    def syringe_home(self) -> None:
        if self.ser is None:
            self.log("Error: No connection to the printer")
            return

        def check_syringe() -> Optional[str]:
            self.ser.write(("M119\r\n").encode("utf-8"))
            t0 = time.time()
            while time.time() - t0 < 2.0:
                line = self.ser.readline()
                if line == b"filament: open\n":
                    return "empty"
                if line == b"filament: TRIGGERED\n":
                    return "full"
            return None

        try:
            self._send_and_wait_ok("M302 P1")
            self._send_and_wait_ok("M302")

            status = check_syringe()
            self._send_and_wait_ok("G91 E0")

            loops = 0
            while status == "full" and loops < 400:
                self._send_and_wait_ok("G1 E-0.5 F300")
                status = check_syringe()
                if status == "empty":
                    self._send_and_wait_ok("G92 E0")
                    self.state.set_param("syringe_current_amount", 0.0)
                loops += 1

            self._send_and_wait_ok("G92 E0")
            self._send_and_wait_ok("G90")
            self.log("Syringe homed")
        except Exception as e:
            self.log(f"Syringe home error: {e}")

    # ---------- Misc ----------
    def movement_test(self) -> None:
        self.log("Movement test")

    def test_zoffset(self) -> None:
        self.log("Test Z-Offset")
        send = self._send_checked
        send(f"G1 Z{self.state.params.z_offset:.3f} F1000")