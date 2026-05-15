# What is exactly a extruder stepper motor (E-axis) driving a lead screw?

In a typical Cartesian 3D printer, the **extruder stepper motor (E-axis)** is responsible for pushing material into the print head.

## What it is
- A **stepper motor** moves in precise, discrete steps → ideal for accuracy.
- The **E-axis (Extrusion axis)** controls material flow, not position.

### Axis comparison:
- **X-axis** → left/right movement  
- **Y-axis** → front/back  
- **Z-axis** → up/down  
- **E-axis** → material extrusion  

The E-axis does **not move the print head**, it controls how much material is fed.

## Modified Setup (Syringe Pump)

In this project, the E-axis is repurposed:

- The E-axis motor rotates a **lead screw**
- The lead screw pushes the **syringe plunger**
- Converts **rotational motion → linear force**

- **Result:** Controlled dispensing of **liquid/paste** instead of melted filament.

### Why use a stepper motor?

- High precision (important for flow rate)
- Repeatability
- Easy integration with G-code:
  - `E10` → extrude
  - `E-5` → retract
