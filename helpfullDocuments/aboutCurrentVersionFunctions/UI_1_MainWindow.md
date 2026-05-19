# CHANGING PAGES FLOW

The important thing is:

```python id="a7d2fu"
go()
```

Does NOT directly change the page. It changes the sidebar selection. tHEN the sidebar emits a signal automatically. THAT signal changes the stack page. So the relationship is INDIRECT.

## Let’s Start With The Connection

Earlier:

```python
self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
```

means:

```text
"When sidebar row changes,
call stack.setCurrentIndex(...)"
```

## Important Qt Concept

### Signals

A signal is:

```text
"an event notification"
```

### currentRowChanged

This signal belongs to:

```python
QListWidget
```

It automatically fires whenever:

* selected row changes

Example:

```text
User clicks "Draw"
```

or:

```python
setCurrentRow(1)
```

Both trigger:

* `currentRowChanged`

---

### The Signal Carries Data

Specifically:

```python
currentRowChanged
```

emits:

```python
(int row)
```

Example:

```python
currentRowChanged(1)
```


### Now The Slot

```python
self.stack.setCurrentIndex
```

is a Qt method.

It expects:

```python
(int index)
```

Example:

```python
setCurrentIndex(1)
```

which shows page 1.

---

# So This Connection Is Perfect

Because:

| Signal emits | Slot expects  |
| ------------ | ------------- |
| integer row  | integer index |

Qt automatically passes the value.

---

## NOW LET’S FOLLOW `go()`

Here is the function:

```python
def go(self, name: str) -> None:
    mapping = {
        "Welcome": 0,
        "Draw": 1,
        "Syringe": 2,
        "Summary": 3,
        "Connection": 4,
        "Log": 5
    }

    self.sidebar.setCurrentRow(mapping[name])
```

---

### Suppose You Call

```python
self.go("Draw")
```

---

#### Step 1

Mapping lookup:

```python
mapping["Draw"]
```

returns:

```python
1
```

#### Step 2

This executes:

```python
self.sidebar.setCurrentRow(1)
```

This changes the selected sidebar row.

Equivalent to user clicking:

```text
Draw
```

#### Step 3 — IMPORTANT

When the row changes,
Qt AUTOMATICALLY emits:

```python
currentRowChanged(1)
```

You do NOT manually call it.

Qt does internally.


#### Step 4

Because of this connection:

```python
self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
```

Qt now automatically calls:

```python
self.stack.setCurrentIndex(1)
```

#### Step 5

`QStackedWidget` switches visible page to:

```text
page index 1
```

which is:

* Draw page

### The Full Chain

Here is the entire flow:

```text
go("Draw")
    ↓
sidebar.setCurrentRow(1)
    ↓
QListWidget detects row changed
    ↓
currentRowChanged(1) signal emitted
    ↓
Qt sees connected slot
    ↓
stack.setCurrentIndex(1)
    ↓
Draw page becomes visible
```


## Why This Architecture Is GOOD

Because:

* navigation logic
* page switching logic

are decoupled.

`go()` only says:

```text
"select this navigation item"
```

NOT:

```text
"manually manipulate pages"
```

That makes the UI:

* cleaner
* more maintainable
* reactive

---

## Simple Analogy

Think of signals like electrical wiring.

```text
sidebar row changes
        ↓
(signal wire)
        ↓
stack changes page
```

The signal connection is literally:
the wire between components.

