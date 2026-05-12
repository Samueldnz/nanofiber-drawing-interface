# G0 and G1

## Main concepts

* add a linear  nomve to the queue
* straignt line from one point ot another
* the speed may change over time following an acceleration curve, according to the acceleration and jerk setting of the given axes

## Feedrate behavior

* `G1 F1000` sets the feedrate for all subsequent moves
* G0 non-extrusion movements,  G1 for moves that include extrusion

## Units

* coordinates are given in millimeters by default, units may be set to inches by G20

## Examples

```gcode"
G0 X12         ; Move to 12mm on the X axis
G0 F1500       ; Set the feedrate to 1500 mm/min
G1 X90.6 Y13.8 ; Move to 90.6mm on the X axis and 13.8mm on the Y axis
```

```gcode"
G1 F1500                    ; set the feedrate to 1500 mm/min
G92 E0                      ; redefines the current coordinate position
G1 X50 Y25.3 E22.4 F3000    ; Execute one synchronized multi-axis motion, the new default feedrate will be 3000 mm/min
```

---

# G4 - Dwell

## Main concepts

* pauses the command queue and waits for a period of time
* if both S and P are included, S takes precedence
* G4 without argumens is effectively the same as M400

## Example

```gcode"
G4 P500  ; Dwell for 500ms
```

---

# G10 and G11

## Main concepts

* G10 retract the filament according to settongs of M207
* G11 Unretract (i.e., recover, prime) the filament according to settings of M208.
* allows to tune retraction at the machine level and can significantly reduce the size of G-code files

## Retraction logic

So instead of using:

```gcode
G1 E-1 F1800
```

for example, it can simply use `G10`

And then `G11` to recover / unretract filament

Firmware maintains a logical state like:

```text
currently retracted? Yes or No
```

So if has a lot of G10 in sequence, only the first one will be execute, the other ones will be ignore to prevent double retraction

## Typical sequence

```gcode
G10      
(moves)   
G11
```

## Configuration with M207 and M208

what will define the settings of this movements are M207 and M208

```gcode
M207 S1.0 F2400 Z0.2
```

means:

* retract 1mm (`S1.0`)
* at 2400 mm/min (`F2400`)
* and make a Z-hop of 0.2mm (`Z0.2`)

its the same for M208, but te S value is used to extra filament recovery

---

# G12 - clean the nozzle

## Main concepts

* start the nozzle cleaning process, default patterns are straight strokes, but it also can be zigzags and circle. It requires a dedicated cleaning area

## Firmware behavior

* default behavior is defined by `NOZZLE_CLEAN_FEATURE` in `Configuration.h`

Website:

## [Marlin G12 Documentation](https://marlinfw.org/docs/gcode/G012.html?utm_source=chatgpt.com)

* with `NOZZLE_CLEAN_GOBACK` enabled, the nozzle automatically return to the XYZ position before G12, but its in firmware level

* The position of cleaning area is also possible to change, but it needs to change in the firmware level

---

# G28

## Main concepts

* it moves each axis towards one end of its track until il triggers a switch, commonly called an "endstop"

* is used to home one or more axes, the default behavior is to home all axes

* by default G28 disables bed leveling

## Specific axis homing

```gcode
G28 X Z
```

* it can also home an especific axel like X or Z

---

# G90 - absolute positioning

## Main concepts

* all coordinates given in G-code are interpreted as positions in the logical coordinate space, this includes the extruder position unless overridden by M83

* is the default

---

# G91 - Relative positioning

## Main concepts

* set relative position mode, all coordinates are interpreted as relative to the last position. This inlcudes the extruder posistion unless overridden by M82

---

# G92 - reset position

## Main concepts

* set the current posisition to the values specfieid

## Examples

```gcode
G92 X10 E90   ;  specify that the nozzles current X position is 10 and the current extruder position is 90

G92 X0 Y0 Z0  ; nozzels current position XYZ is now 0, 0, 0

G92 E0        ; current extruder position is now considerer as position 0, very usualful to absolute moves
```

---

# M82 - E absolute

## Main concepts

* this command is used to override G91 and put the E axis into absolute mode independente of the other axes

---

# M83 - E relative

## Main concepts

* this command is used to override G90 and put the E axis into relative mode independent of the other axes

---

# M104 - set hotend temperature

## Main concepts

* set a new target hot end temperature and continue without waiting. The firmware will continue to try to reach and hold temperature in the background

* use M109 to wait for the hotend to reach the target temperature

## Example

```gcode
M104 S185  ; set target temperature for the active hotend
```

---

# M105 - report temperatures

## Main concepts

* request a temperature report to be sent to the host as soon as possible

---

# M106 - set fan speed

## Main concepts

* turn on oe of the fans and set its speed . If no fan index is given, the print cooling fan is selected.

* M106 with no speed sets the fan to full speed

* turn off fans with M107

* usually uses 8-bit values from 0 to 255

## Example

```gcode
M106 S200      ; turn on th fan at 200 of a total 255 DC, 255 is full speed
```

---

# M109 Wait for hotend temperature

## Main concepts

* this command optionally sets a new target hot end temperature and waits for the target temperature to be reached before proceeding.

* if the temperature is set with S, waits only when heating

* if is set with R, waits also for the temperature to go down

## Examples

```gcode 
M109 S180   ; set target temperature and wait (if heating up)
M109 R120   ; set target temperature, waait even if cooling
```

---

# M114 - get current position

## Main concepts

* get the current position of the active tool. Stepper values are included

* Normally M114 reports the “projected position” which is the last position Marlin was instructed to move to.

* With the M114_REALTIME option you can send R to get the “real” current position at the moment that the request was processed. This position comes directly from the steppers in the midst of motion, so when the printer is moving you can consider this the “recent position.”

* For debugging it can be useful to enable M114_DETAIL which adds D and E parameters to get extra details.

* hosts should respondo to the outuput of M114 by updating ther current position

## Example

```text
> M114
X:0.00 Y:127.00 Z:145.00 E:0.00 Count X: 0 Y:10160 Z:116000
ok
```

---

# M118 - serial print

## Main concepts

* send a message to the connected host for siplay in the host console or to perform a host action

* the E, A  and P parameters must precede the message

* A denote a comment or action command

* E some hosts will display echo messages

* P0 messasge to all ports, P1 to mai host serial port

## Example

```gcode
M118 E1 P0 Hello Word!    ; echo Hellow word! to all ports
```

---

# M119 - endstop states

## Main concepts

* use this command to get the current state of all endstops, usegul for setip and troubleshooting. Reporte as either "open" or "TRIGGERED"

## Example

```text
> M119
Reporting endstop status
x_min: open
y_min: open
z_min: TRIGGERED
z_probe: open
filament: open
```

---

# M140 - set bed temperature

## Main concepts

* set a new target temperature for the heated bed and continue without waiting.

## Example

```gcode
M140 S80   ; set target temperature in 80, no waiting
```

---

# M149 - set temperature units

## Main concepts

* use this command to set the current temperature units to Celsius Fahrenheit or Kelvin, Celsiu is the default (`M149 C/F/K`)

* send with no parameters to get the current temperature units

---

# M155 - temperature auto-report

## Main concepts

* it can be useful for host software to track temperatures, display and grpah them over time.

* requires AUTO_REPORT_TEMPERATURES

* also enable EXTENDED_CAPABILITIES_REPORT to notify hosts about this capability

## Examples

```gcode
M155 S4   ; report temperatures every 4 seconds
M155 S0   ; stop reporting temperatures
```

---

# M190 - wait for bed temperature

## Main concepts

* this command optionally sets a new target temperature for the heated bed and waits for the target temperature to be reached before proceeding.

* if is set with S then it waits only when heating

## Examples

```gcode
M190 S80    ; set target bed temperature (80) and wait (if heating)
M190 R40    ; set target bed temperature and wait even if cooling

M190 R70 T600 ; slowly cool downt to 70ºC over a 10minute period
```

---

# M220 - set feedrate percentage

## Main concepts

* set speed percentage factor, aka "feed rate" which applies to all g-code moves in all XYZE axes

* report the current speed percentage factor if no parameter is specfied

## Example

```gcode
M220 S80   ; set feedrate to 80%
```

---

# M221 - set flow percentage

## Main concepts

* set the flow percentage, which applies to all E moves added to the planner

## Example

```gcode 
M221 S150   ; set the flow rate to 150%
```

---

# M400 - finish moves

## Main concepts

* this command causes G-code processing to pause and wait in a loopuntil all moves in the planner are completed

## Examples

```gcode
M400 
M300 S440 P100      ; wait for moves to finish before playing a beep
```

---

# Safe abort sequence

```gcode
M400          ; wait moves finish
G91           ; relative mode
G1 Z10 F1200  ; lift nozzle
G90           ; absolute mode
G1 X0 Y220 F3000 ; park head
M104 S0       ; nozzle heater off
M140 S0       ; bed heater off
M107          ; fan off
M84           ; disable motors
```

---

# Questions

* what is the firmware of this printer? Do it match with official Marlin?
