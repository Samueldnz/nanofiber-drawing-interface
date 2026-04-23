# Difference between G90 and G91

In the project, we use use absolute positioning (G90) for motion and relative positioning (G91) for extrusion(E)

- Easy to reason about position
- No cumulative errors
- You always know where the head is
- Extrusion (E) → temporarily Relative (G91)

## What´s the problem with extrusion in absolute mode?

If you used absolute E all the time, you'd get:

```
G90
G1 E1
G1 E2
G1 E3
G1 E4
```
You must keep track of the total extrusion value forever causing some problems as:

- Numbers grow indefinitely
- Harder to manage resets
- Risk of bugs if you lose track

So instead, the script will do something like this:

```
G91        ; switch to relative
G1 E1      ; extrude 1 unit
G1 E0.5    ; extrude 0.5 more
G1 E-0.2   ; retract slightly
G90        ; go back to absolute
```

What the script is doing step-by-step is:

Move head precisely → (G90, absolute)
↓
Switch mode → G91
↓
Extrude small controlled amount (relative)
↓
Maybe do "afterdrop" (extra push or retract)
↓
Switch back → G90
↓
Continue precise movement

## What is “afterdrop”?

Its a material that keeps flowing after pressure. So we may need a small extra push or a retraction. For example:

```
G91
G1 E0.2   ; push a bit more (afterdrop)
G1 E-0.1  ; slight retract
G90
```

## Why mixing modes is smart?

We can mixe modes to make more predictable positioning using absolute mode to motion and a easier path planning. And for E, we use relative positioning for simple extrusion control without global tracking and a easier tuning (especially for syringe sustems)

### Important detail
Even though you switch to G91, it affects all axes, not just E. So your script must ensure: during G91, you only move E, not X/Y/Z

