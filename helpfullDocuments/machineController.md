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





