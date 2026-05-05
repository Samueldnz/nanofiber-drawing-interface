# DrawingWorker

## Overview

`DrawingWorker` is a worker class responsible for executing the drawing process in a background thread using Qt's threading model.

It is designed to run inside a `QThread`, ensuring that long-running drawing operations do not block the main UI thread.

The class communicates with other components (such as the controller and UI) through Qt signals, enabling safe cross-thread interaction.

## Class Definition

```python
class DrawingWorker(QObject):
```
---

## Purpose

* Execute the drawing process asynchronously
* Maintain UI responsiveness during long operations
* Provide real-time feedback through signals
* Handle errors safely without crashing the application

---

## Signals

### `finished`

```text
Signal()
```

Emitted when the drawing process completes, regardless of success or failure.

---

### `error`

```text
Signal(str)
```

Emitted when an exception occurs during execution.

* Payload: error message (string)

---

### `status`

```text
Signal(str)
```

Emitted to provide real-time updates during execution.

Typical uses:

* Logging
* UI feedback
* Progress tracking

---

## Initialization

### Arguments

* **controller** (`MachineController`)
  Reference to the main controller responsible for executing the drawing logic.

---

## Execution Entry Point

### `run()`

This method is the entry point when the worker is executed inside a `QThread`.

---

## Behavior

During execution, the worker:

1. Invokes the controller’s internal drawing loop
2. Relays status updates through the `status` signal
3. Monitors execution for errors
4. Ensures proper completion signaling

---

## Signal Emissions

### `status (str)`

* Emitted during execution
* Provides progress and log messages

---

### `error (str)`

* Emitted if an exception occurs
* Contains a descriptive error message

---

### `finished ()`

* Always emitted when execution ends
* Triggered whether execution succeeds or fails

---

## Threading Model

* Runs inside a `QThread`
* Does not interact directly with UI elements
* Communicates via signals (thread-safe)

---

## Notes

* The actual drawing logic is implemented in the controller
* This class acts as a bridge between threading and execution logic
* Ensures proper lifecycle management of long-running tasks

```

