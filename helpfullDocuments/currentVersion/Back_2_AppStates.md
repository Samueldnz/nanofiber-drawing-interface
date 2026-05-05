# AppState System (backend.py)

AppState is a central data container that automatically notifies the rest of the app whenever something changes, using Qt’s signal system.

## Concept

The application has a **state** (parameters, settings, values).

Whenever something changes, you want:
- UI to update automatically
- Logs to be written
- State to be saved/loaded

Instead of manually wiring everything together, Qt gives you a system for this.

## What is `QObject`?

Base class of almost everything in Qt.
Think of it as a “super object with extra powers”, mainly:

It provides:
- Event system
- Memory management (parent/child)
- Signals and slots

So when you see:

```python
class AppState(QObject):
```
It means: `“This class can send signals and interact with Qt’s event system.”`

## What is a Qt signal?

A signal is basically:

`“Hey! Something happened!”`

It’s like an event emitter.

- changed = Signal() → `emits when something in the state changes`
- log = Signal(str) → `emits a message (string)`

## What is a slot?

A slot is just a function that reacts to a signal.

1. It stores your application data

Example:

```python
self.speed = 10
self.pressure = 5
```

2. It emits signals when something changes

Example:

```python
def set_speed(self, value):
    self.speed = value
    self.changed.emit()
```

So:
- UI updates automatically
- No manual refresh needed

3. It logs things

```python
self.log.emit("Speed changed to 10")
```

Something else (like a console or file logger) is listening waiting for this log emit.

4. It can SAVE and LOAD itself

This is the serialization part:

```python
to_project_dict
def to_project_dict(self):
    return {
        "speed": self.speed,
        "pressure": self.pressure
    }
```
- It converts state to dictionary (easy to save as JSON), building a simple database to load further

```python
apply_project_dict
def apply_project_dict(self, data):
    self.speed = data["speed"]
    self.pressure = data["pressure"]
    self.changed.emit()
```

- Loads state from saved data
- Emits signal so UI updates

## Why is this powerful?

Without this system, you'd have to do manually:
```python
set_speed()
update_ui()
write_log()
save_state()
```
But with Qt signals, you just need call `set_speed()`.

## Questions you might have

### You said everything happens automatically via connections once `set_speed()` is called, right? But I couldn’t see this in the function you showed me. Could you show the connection path?

You didn’t see the behavior in set_speed() because the actual reactions are defined externally via .connect(), not inside the function itself.

Actually, inside AppState, this only emits signals. It does not know who is listening.

1. Inside AppState
```python
class AppState(QObject):
    changed = Signal()
    log = Signal(str)

    def set_speed(self, value):
        self.speed = value
        self.changed.emit()
        self.log.emit(f"Speed changed to {value}")
```
2. Somewhere else: Connections are defined for example:
```python
app_state = AppState()

app_state.changed.connect(update_ui)
app_state.log.connect(write_log)
```
It runs when:

- app_state.set_speed(10)

Step-by-step:

- set_speed(10) is called
- self.changed.emit() fires
- Qt looks: “who is connected to changed?”

And finds for example:

- app_state.changed.connect(update_ui)

Then it calls: 

- update_ui()

Then: 

- self.log.emit(...) fires

Qt finds:

- write_log("Speed changed to 10")

It`s important to have this insight: signals don´t do anything by themselves, they only trigger function that were connected earlier.

### Where are these connections usually defined?

Typically in UI/ Controller layer

For example:
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_state = AppState()

        # 🔗 connections happen HERE
        self.app_state.changed.connect(self.update_ui)
        self.app_state.log.connect(self.append_log)

    def update_ui(self):
        print("UI updated")

    def append_log(self, msg):
        print("LOG:", msg)
```

The mental model for this is: you define your speed for example using `set_speed()`, so emit a changed signal to update_ui(), then emit a log signal to write a log

### What about saving? Is it just save after the UI updates?

What actually happens by default its when you call `set_speed()` as showed before, it only emits signals to UI updates and Logging if connected. Saving will only happens if you connect it.

If you want saving to happen automatically, you need somenthing like: 

```python
app_state.changed.connect(save_project)
```

Now the flow becomes:

set_speed()
   ↓
emit changed
   ├──▶ update_ui()
   ├──▶ save_project()
   └──▶ maybe other things...

The function `to_project_dict` just prepares data for saving, it does not save anything by itself. Usually it uses a function to save, for example:

```python
def save_project():
    data = app_state.to_project_dict()
    
    with open("project.json", "w") as f:
        json.dump(data, f)
```

that can be called when a user clicks "Save" in the interface. Or can be through auto-save.
