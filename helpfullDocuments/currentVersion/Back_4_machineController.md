# Constructor

```python

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
```

- Line 8 hold the connection to the printer, ```none``` indicates that is not connect and ```serial.Serial``` that is connected. 

So why ```Option[...]```?
Means: This can be Serial object (a communication channel between your computer and your printer) Or None.

- Lines 11 and 12 are used for background execution, ```drawing_thread``` is the actual thread and the Qthread manages the thread, and the ```worker``` is the object that runs inside the thread, contains the logic.

- Line 14 creates a synchronization tool, like a traffic light to commucation between flags, so the line creates a flag initially OFF and then Line 15, set it ON - "NOT paused - keep running". So ```set()``` it means `Go` and ```clear()``` it means `Stop and wait`. In Line 16 is the same, but to finish.

Probably it will be used in some way like: 

```python
while not self._pause_event.is_set():  # is_set() = true if set(), loop continues/ is_set() = false if clear(), loop stops
    time.sleep(0.05)
```



---


# Serial Communication: _send_and_wait_ok

```python
def _send_and_wait_ok(self, command: str, timeout_s: float = 30.0) -> None:
```

## Purpose
Ensures reliable communication with the 3D printer by sending a single G-code command and waiting for confirmation before proceeding.

## Behavior
The function:
1. Sends a G-code command over serial.
2. Continuously reads firmware responses.
3. Blocks execution until one of the following occurs:
   - "ok" → command completed successfully
   - "error" → raises RuntimeError
   - timeout → raises TimeoutError

## Accepted Responses
- "ok"
- "ok <additional info>"
- "busy: processing" → ignored (wait continues)

## Error Handling
- Raises RuntimeError if firmware reports an error
- Raises TimeoutError if no valid response is received within the timeout

## Why This Is Important
3D printer firmware processes commands sequentially. Sending commands without waiting:
- Overflows the buffer
- Causes unpredictable motion
- Breaks synchronization

This function guarantees:
- Command execution order
- Safe communication
- Deterministic behavior

## Typical Usage

```python
_send_and_wait_ok("G28") # Home axes
_send_and_wait_ok("G1 X10") # Move to position
```

## Notes
- Assumes Marlin-like firmware behavior
- Uses blocking I/O (intended for controlled command flow)
- Should not be used for high-frequency streaming without modification


---

# Drawing Workflow: start_drawing

```python
def start_drawing(self) -> None:
```

## Purpose
Initializes and starts the drawing process in a separate thread to keep the UI responsive.

## Architecture
The drawing system is divided into two parts:

- **start_drawing()** → sets up threading and execution
- **DrawingWorker.run()** → executes the actual drawing logic

## Execution Flow

1. User triggers drawing (e.g., "Do Science!")
2. start_drawing() performs validation and setup
3. A QThread is created
4. A DrawingWorker is created and moved to that thread
5. Thread starts → worker.run() is executed
6. Worker sends commands to the printer (via serial)
7. When finished:
   - Worker emits `finished`
   - Thread stops
   - Resources are cleaned up

## Threading Model

- Main thread → UI (non-blocking)
- Worker thread → drawing execution (blocking allowed)

This prevents UI freezing during long operations.

## Signals Used

- `started` → triggers worker.run()
- `finished` → stops thread and cleans resources
- `status` → sends logs to UI
- `error` → reports runtime errors
- `drawing_running_changed` → updates UI state
- `drawing_paused_changed` → updates pause state

## Control Flags

- `_stop_event` → signals drawing to stop
- `_pause_event` → controls pause/resume behavior

## Safety Checks

- Prevents execution without serial connection
- Prevents multiple concurrent drawing threads

## Notes

- Drawing parameters (speed, Z offset, etc.) are read dynamically during execution
- Thread cleanup is essential to avoid memory leaks
- This design follows Qt best practices for long-running tasks




# Safe Area and Rectangle Validation

The function `_compute_anchored_rect()` is responsible for computing the drawing rectangle based on the selected dimensions, orientation, and starting position. Using the provided parameters, it generates the rectangle coordinates `(x0, x1, y0, y1)`, which represent the working area where the fibers will be deposited.

In addition to calculating the rectangle geometry, the function also validates whether the requested drawing area remains fully inside the configured safe bounds of the machine. These bounds are defined by the safe area parameters (`safe_x_min`, `safe_x_max`, `safe_y_min`, and `safe_y_max`) and act as a software safety mechanism to prevent out-of-range movements or invalid positioning during operation.

The rectangle behavior depends on the selected orientation. For horizontal fibers, the length is applied along the X axis and the width along the Y axis. For vertical fibers, the dimensions are inverted so that the length is applied along the Y axis. If any side of the rectangle exceeds the safe area, the function raises a `RuntimeError` and prevents the drawing process from starting.

An important observation is the presence of the line:

```python
start_y += 20
```

which applies an additional Y-axis offset before computing the rectangle. This offset does not appear explicitly in the legacy implementation (`GUI.py`), where positioning was handled through hardcoded coordinates and implicit margins. The same offset is also present in the UI preview logic (`ui.py`), suggesting that it was introduced during the refactoring process as a positional compensation or calibration adjustment. Since the offset currently exists in both the backend geometry logic and the visualization layer, it may lead to inconsistencies or duplicated positioning behavior if not carefully managed.


# Potential issue on `_run_custom_centered`

A potential issue exists in the extrusion control logic regarding the use of coordinate modes. The initialization sequence configures the printer with `M82`, which enables absolute extrusion mode, while the droplet deposition functions later switch to `G91` and perform relative extrusion movements using commands such as `G1 E-...`. Depending on the firmware implementation, `G91` may affect only the XYZ axes and not the extruder axis (E).

This behavior should be experimentally verified on the target firmware. If extrusion is expected to behave relatively, the use of `M83` (relative extrusion mode) may be more appropriate and predictable than relying on `G91` alone.

To validate the current implementation, a controlled extrusion test is recommended. The test should execute sequential extrusion commands after enabling `G91` and observe whether the extrusion axis behaves relatively (`-1 mm` followed by another `-1 mm`) or absolutely (second command produces no additional movement). A comparison using `M83` (relative extrusion mode) is also recommended to determine whether it provides more predictable behavior for the extrusion system.

---

## Proposed Test

```
M82        ; absolute extrusion mode
G92 E0     ; reset extruder position

G91        ; relative positioning
G1 E-1 F100

G1 E-1 F100
```

### Expected Behaviors

#### Case 1 — Extrusion behaves RELATIVELY

The syringe/extruder should move:

```
-1 mm
then
another -1 mm
```

This means:

* `G91` is affecting the E axis
* current implementation is valid

---

#### Case 2 — Extrusion behaves ABSOLUTELY

The first command moves to:

```
E = -1
```

The second command attempts:

```
E = -1 again
```

Result:

* second movement does not occur
* or movement is inconsistent

This means:

* `M82` still controls E independently
* `G91` only affected XYZ axes

You probably will find the results on `nanofiber-drawing-interface\currentVerion\documents\testReport.md`.







