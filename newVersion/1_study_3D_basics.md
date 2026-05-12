# 3D Printing Notes

## General Concepts

### What is 3D Printing?

3D printing creates three-dimensional parts by building up material layer by layer based on digital models created using computer-aided design (CAD).

The technology has existed since the 1980s, but recent advances in:

* machinery,
* materials,
* software,

have made it much more accessible to businesses and consumers.

---

### Main 3D Printing Technologies

There are many different 3D printing technologies and materials.

Different processes include:

* melting,
* powder fusion,
* resin curing.

Materials can include:

* plastic,
* concrete,
* metal,
* wood,
* and others.

Main technologies:

| Technology | Meaning                   |
| ---------- | ------------------------- |
| FDM        | Fused Deposition Modeling |
| SLA        | Stereolithography         |
| SLS        | Selective Laser Sintering |

---

#### FDM (Fused Deposition Modeling)

FDM is the most widely used 3D printing technology.

It works by:

* melting thermoplastic filament,
* extruding it through a nozzle,
* depositing it layer by layer.

The filament usually comes in a spool, similar to:

* wire,
* cable,
* thread.

The object is created by fusing deposited layers together.

---

#### SLA (Stereolithography)

SLA was the world’s first 3D printing technology and is usually more professional-oriented.

It uses liquid resin and works by using a laser to cure the resin into hardened plastic through a process called photopolymerization.

Advantages:

* very high resolution,
* high accuracy,
* smooth surfaces,
* excellent for detailed prototypes and molds.

Good for:

* molds,
* patterns,
* highly detailed parts,
* functional prototypes.

---

#### SLS (Selective Laser Sintering)

SLS uses a high-powered laser to fuse small particles of polymer powder.

The unfused powder supports the part during printing, eliminating the need for support structures.

Ideal for:

* complex geometries,
* internal structures,
* undercuts,
* thin walls,
* negative features.

Very common in industrial additive manufacturing.

---

### Benefits of 3D Printing

* Fast conversion from CAD model to physical part.
* Reduces tooling and setup costs.
* Allows unprecedented design freedom.
* Enables complex geometries.
* Makes customization easier because only the digital model needs to change.

---

## FDM vs Resin Printing

### FDM

FDM uses melted filament deposited layer by layer.

Advantages:

* cheaper materials,
* easier workflow,
* multi-color printing possible,
* easier maintenance.

Disadvantages:

* lower resolution compared to resin,
* visible layer lines,
* less smooth surfaces.

---

### Resin Printing

Resin printing is an umbrella term for multiple technologies that use UV-curable resin.

An LCD, laser, or projector cures each layer using UV light.

Advantages:

* very high detail,
* smooth surfaces,
* excellent precision.

Disadvantages:

* resin is usually toxic,
* requires cleaning and post-processing,
* harder workflow,
* usually cannot print multiple colors in a single print like FDM.

---

## Hot Bed

Most FDM printers use a heated bed. 

The bed temperature changes depending on the material being printed.

The heated bed helps:

* adhesion,
* reducing warping,
* improving print quality.

---

## Calibration Cube

There is a common cube design used to calibrate:

* bed leveling,
* extrusion,
* dimensional accuracy.

One example: **https://www.thingiverse.com/thing:214260**

---

## Extruder Basics

On most filament-based 3D printers, the filament is pushed into the hot nozzle by gears that grip the material and feed it forward.

There are two main variations.

---

### Single Gear Extruder

The simplest system:

* one driven gear,
* one freely rotating idler bearing.

The driven gear grips the filament and pushes it forward.

---

### Dual Drive Extruder

Dual-drive systems use gears on both sides of the filament.

Advantages:

* more grip,
* more pushing force,
* faster feeding,
* less chance of stripping the filament.

Because both sides push the filament, each side only needs about half the force.

---

## Extruder Pretension

To transmit force properly, the gears need to press against the filament.

---

### Too Much Pretension

* filament gets crushed or deformed,
* harder to feed,
* more friction,
* wastes motor energy,
* can damage the mechanism.

---

### Too Little Pretension

* gears barely grip the filament,
* little force is transmitted,
* gears slip,
* filament gets damaged by friction.

---

### Ideal Pretension

The filament should show some indentation from the gears:

* enough grip to transfer torque,
* not enough to crush the filament.

---

## Common Extruder Troubleshooting

Questions to check:

* Is the Bowden tube okay?
* Are the extruder gears clean and not worn down?
* Is the nozzle clogged?
* Is the hotend fan working correctly and preventing heat creep?
* Is the nozzle temperature high enough?
* Are you printing within the limits of the system?
* Did you load the correct filament?

---

## Filament Diameter

Most common filament diameter: `1.75 mm`

Roughly about the thickness of two credit cards.

---

## Stepper Motors

A stepper motor is different from a regular electric motor.

A stepper motor:

* can move in very precise increments,
* can hold its position accurately,
* stays in place until instructed to move again.

This precision is critical for 3D printers.

---

## Printing Startup Process

When the print starts:

1. The heated bed warms up.
2. The hotend heats up (often around 200–220°C).
3. The stepper motor pushes filament into the nozzle.
4. The printer purges filament to ensure proper flow.

This excess filament is commonly called: `purged filament` or informally, `printer poop`.

---

### Bed Leveling

Before printing, the printer usually performs bed leveling.

Purpose:

* ensure the bed is level relative to the nozzle,
* prevent print defects,
* improve first-layer adhesion.

Even small offsets can cause printing failures.

---

### Nozzle Wiping and Prime Lines

Before printing:

* the printer often draws lines at the front of the bed to verify flow,
* some printers use a nozzle wiper to clean the nozzle.

This helps ensure stable extrusion before the real print starts.

---

## Bowden vs Direct Drive Extruder

### Bowden System

The extruder motor is mounted away from the hotend.

A Bowden tube guides filament to the hotend.

Depending on the hotend type:

* the PTFE tube may stop at the top,
* or continue almost to the nozzle.

#### Advantages

* lighter hotend assembly,
* faster movement,
* easier upgrades and maintenance.

#### Disadvantages

* more difficult retraction tuning,
* flexible filaments are harder to print,
* more filament compression,
* slower response.

---

### Direct Drive System

The extruder is mounted directly on the hotend or X carriage.

Sometimes there is only a very short PTFE guide tube.

#### Advantages

* easier retraction,
* more responsive extrusion,
* much better for flexible filaments.

#### Disadvantages

* heavier moving assembly,
* potentially lower maximum movement speed.

---

## Extrusion and Pressure

Extrusion width determines how wide the deposited material line is.

Do not confuse:

* extrusion width,
* extrusion multiplier.

---

### Extrusion Width

Controls:

* width of deposited lines,
* spacing between extrusion paths.

Usually related to nozzle diameter.

Example: `0.4 mm nozzle`

---

### Extrusion Multiplier

Adjusts:

* material flow amount,
* without changing path spacing.

---

### Effects of High Extrusion Width

At high extrusion widths:

* layers squeeze into each other,
* surfaces may develop wrinkled textures,
* fine features may not print properly,
* extra material increases drag between nozzle and part,
* shear forces can deform the print.

---

### Pressure Inside the Nozzle

Extrusion is fundamentally a pressure system.

The extruder motor pushes filament into the hotend, generating pressure inside molten plastic.

The nozzle acts as a restriction:

* pressure builds,
* molten material flows out.

When movement stops:

* pressure still exists,
* material can continue leaking.

This causes:

* stringing,
* blobs,
* oozing.

---

## Retraction

Retraction pulls filament backwards slightly to relieve pressure inside the nozzle.

Purpose:

* reduce oozing,
* reduce stringing,
* improve print quality.

Bowden systems usually require larger retraction distances because the filament path is longer and more elastic.

---

## Important Observation

Extrusion is not simply: **motor moves → plastic instantly exits**

It behaves more like: **a pressurized fluid system**

The filament compresses slightly and pressure inside the hotend changes dynamically during printing.


## Questions

### Filament Path Summary

In an FDM 3D printer, the filament starts on a spool and is pulled into the extruder system by a stepper motor connected to one or more drive gears. These gears grip the filament and push it forward through either a Bowden tube or directly into the hotend, depending on the printer design. Inside the hotend, the filament passes through the heat sink and heat break before reaching the heater block, where it melts due to the high temperature generated by the heater cartridge. The molten material is then forced through the nozzle, which controls the final extrusion width and deposited line size. While the printer moves along the X and Y axes, the extruder continuously pushes filament, creating deposited layers that fuse together to form the final object.

---

### Hotend, Nozzle and Extruder Components

The extrusion system of an FDM printer is divided into two major sections: the extruder and the hotend.

The extruder is responsible for gripping and pushing the filament. Its main components are:

* stepper motor,
* drive gear or hobbed gear,
* idler gear/bearing,
* tensioning mechanism,
* filament guide.

The stepper motor provides precise rotational movement. The drive gear bites into the filament and pushes it forward. The idler mechanism presses the filament against the drive gear so enough force can be transmitted without slipping.

The hotend is responsible for heating and melting the filament before deposition. Its main components are:

* heat sink,
* heat break,
* heater block,
* heater cartridge,
* thermistor,
* nozzle.

The heat sink keeps the upper region cool to prevent premature filament softening. The heat break creates a thermal transition between the cold and hot zones. The heater cartridge generates heat, while the thermistor measures temperature so the firmware can regulate it. Finally, the nozzle acts as the output restriction that shapes the deposited material line.

The nozzle diameter strongly influences print quality, speed and extrusion behavior. Smaller nozzles provide higher detail but require more pressure, while larger nozzles allow faster material flow.

---

### Bowden vs Direct Drive Extruder

In a Bowden system, the extruder motor is mounted away from the hotend and the filament travels through a PTFE Bowden tube before reaching the nozzle. The biggest advantage of this system is the reduced weight on the moving print head, allowing faster and smoother movement with less inertia. Bowden systems are also usually easier to upgrade and maintain because the extruder assembly is separated from the hotend. However, because the filament travels through a long tube, the system becomes more elastic and less responsive. This makes retraction tuning harder and flexible filaments more difficult to print.

In a direct drive system, the extruder is mounted directly on the hotend or very close to it. This creates a much shorter filament path, resulting in faster extrusion response and simpler retraction behavior. Direct drive systems are significantly better for flexible materials because the filament has less room to bend or compress before reaching the nozzle. The main disadvantage is the increased weight on the print head, which may reduce maximum movement speed and increase mechanical inertia.

Bowden systems generally make more sense when the goal is lightweight motion and higher printing speed with standard materials such as PLA. Direct drive systems are usually preferred when printing flexible materials, when more precise extrusion control is required, or when retraction performance is important.

---

### What “E” Means Mechanically

In G-code, the `E` axis represents extrusion movement. Mechanically, `E` corresponds to how much raw filament the extruder motor pushes into the hotend. For example:

```gcode"
G1 E5
```

usually means that the extruder should push 5 mm of filament forward.

The firmware converts this command into stepper motor rotation using the printer’s calibrated “steps per millimeter” value. If the extruder is calibrated at 93 steps/mm, then an `E5` command causes the motor to perform approximately 465 microsteps to move the filament by 5 mm.

Importantly, `E` does not directly represent deposited line length or deposited volume. Instead, it represents the length of raw filament entering the hotend. The actual deposited volume depends on the filament diameter, nozzle size, layer height, temperature, pressure inside the nozzle, and material behavior.

Most printers use 1.75 mm diameter filament. Because the filament has a physical cross-sectional area, pushing 5 mm of filament into the hotend corresponds to a certain volume of molten plastic. The slicer calculates this relationship mathematically so that the deposited material matches the geometry being printed.

During real printing, extrusion is usually synchronized with movement commands. For example:

```gcode"
G1 X100 Y100 E3
```

means the printer moves while simultaneously pushing filament. This creates continuous material flow and forms the printed line. Mechanically, the process is not instantaneous because the system behaves like a pressurized molten-fluid system. The motor pushes filament, pressure builds inside the hotend, and molten plastic exits through the nozzle continuously during motion.

