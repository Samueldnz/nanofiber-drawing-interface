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