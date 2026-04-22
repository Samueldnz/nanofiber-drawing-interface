# Microfiber Drawing Interface (Refactored Version)

This repository contains the construction of a **refactored and adapted version** of the original Microfiber Tool.

The **first functional version** of this project was developed by **gabs911** and can be found here:
👉 https://github.com/gabs911/microfiber-tool/tree/main

This project is based on that original implementation. The goal here is to **reuse, adapt, and refactor** the existing code to support a **different hardware context**.

---

## 🎯 Project Goal

The main objective of this repository is to:

* Take an already functional system (developed for a modified 3D printer)
* Adapt and refactor it for a **new prototype 3D printer**
* Enable the printing of **nanofibers from polymers**, extending the original microfiber capabilities

This is **not a project built from scratch**, but rather an **evolution and transformation** of a proven system into a new experimental platform.

---

## 📌 Original Project Credits

The original version was developed by:

* Gabriel Alvares de Sousa Guimaraes (gabs911)
* Under the supervision of Andrii Shykarenko
* At the Technical University of Liberec

This repository builds upon that work with a focus on **code restructuring, maintainability, and hardware adaptation**.

---

## 🧪 About This Version

In this version, the focus is on:

* Code refactoring and cleanup
* Improved modularity
* Adaptation for a **new prototype nanofiber 3D printing system**
* Maintaining compatibility with existing logic where possible

* Developed by: Samuel Sampaio Diniz (Samueldnz)
* Under the supervision of Andrii Shykarenko
* At the Technical University of Liberec

---

## 📦 Original Project Description

### Microfiber Drawing Interface

This repository contains a PySide6-based graphical user interface (GUI) designed to control a custom microfiber drawing tool. The hardware is built on top of a modified 3D printer chassis equipped with a custom syringe extruder.

---

## ✨ Features

* **Custom Extrusion Control:** Direct control over a syringe-based extruder for precise microfiber deposition.
* **Parametric Toolpath Generation:** Automatically generates G-code for horizontal or vertical fiber arrays based on geometric parameters.
* **Safe Area Boundaries:** Enforces physical hardware limits to prevent the toolhead from crashing.
* **Live Hardware Communication:** Real-time serial connection to Marlin/RepRap firmware with homing, pausing, and live parameter updates.
* **Project Management:** Save and load drawing configurations as JSON files, and export run summaries as PDFs.

---

## ⚙️ Installation

### Prerequisites

* Python 3.8 or higher

### Setup

Clone the original repository (if needed):

```
git clone https://github.com/gabs911/microfiber-tool.git
cd microfiber-controller
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the application:

```
python main.py
```

---

## ▶️ Usage

1. **Connect:** Navigate to the **Connection** tab. The software will automatically scan for available serial ports (at 115200 baud). Click **Connect**. The machine will automatically home its axes (G28) upon a successful connection.

2. **Setup Syringe:** Go to the **Syringe** tab to home the syringe plunger or prime it using the intake/ml controls.

3. **Configure Layout:** On the **Draw** tab, define the dimensions, spacing, and starting coordinates of your microfiber array. The UI will provide a live preview of the drawing rectangle relative to the safe bed area. Green indicates a valid placement; red indicates the toolpath exceeds the safe bounds.

4. **Set Deposition Parameters:** Adjust speed, Z-offset, and extrusion amounts in the "Drawing parameters" section.

5. **Run:** Once configured, navigate back to the **Connection** tab and click **Do Science!** to begin the drawing process. You can pause or stop the operation at any time.

---

## 📐 Parameter Glossary

### Layout Parameters

These parameters define the geometry of the fiber array you are printing.

* **Orientation:** The direction the fibers will be drawn - `Horizontal` or `Vertical`
* **Length (mm):** The length of the individual fibers.
* **Width (mm):** The total width of the array (perpendicular to the fiber length).
* **Spacing (mm):** The distance between each parallel fiber.
* **Starting X/Y (mm):** The bottom-left anchor coordinate of the rectangular array.

---

### Drawing Parameters

These control the physical motion and extrusion behavior of the machine.

* **Speed (mm/min):** The travel speed of the print head during deposition.

* **Droplet Amount (E units):** The volume of material extruded at the start of a fiber to anchor it.

* **Z-Offset (mm):** The absolute Z-height used while actively drawing a fiber. Use the `Test Z-Offset` button to verify this height safely.

* **Z-Hop (mm):** The clearance height the print head raises to when traveling between fiber lines.

* **Pause (ms):** A programmed delay (G4 command) after anchoring the droplet, allowing material to adhere before pulling the fiber.

* **Afterdrop:**  If enabled, the extruder will perform a secondary, smaller extrusion at the end of the fiber to detach/anchor the tail.

* **Clean:** If enabled, the print head will execute a wiping motion outside the array boundary after completing a fiber to break off trailing material.

---

### Syringe Parameters

* **Current Amount:** Tracks the theoretical position/volume of the syringe based on commanded moves.

* **Droplet Units:** The specific amount of material to draw into the syringe when using the intake function.

---

## 🔄 Final Notes

This project is an **ongoing refactor and adaptation effort** developed by Samuel Sampaio Diniz under the supervision of Andrii Shykarenko at the Technical University of Liberec in the year of 2026.
The intention is to preserve what already works while evolving the system to support **new experimental hardware and nanofiber production capabilities**.

