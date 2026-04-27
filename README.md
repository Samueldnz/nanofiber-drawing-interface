# Microfiber Drawing Interface (Refactored Version)

This repository contains a **refactored and adapted version** of the original Microfiber Tool, focused on improving code structure and extending its use to a **new 3D printing context**.

## Legacy Version (`GUI.py`)

The file `GUI.py` represents the **original legacy implementation** of the system.

* It was developed by **Drº Andrii Shykarenko**
* It uses a **Tkinter-based interface**
* It contains both **UI and control logic in a single file (monolithic design)**

### Running the legacy version

To execute the original system:

```bash
cd firstVersion
python GUI.py
```

⚠️ This version is **not used by the current application**, but is kept for:

* historical reference
* understanding original logic
* comparison during refactoring

---

### Current Version (`ui.py`, `backend.py`, `main.py`)

* This is the **active version of the project**
* Built using **PySide6** with a clearer separation between:

  * UI (`ui.py`)
  * Logic / Controller (`backend.py`)
  * Entry point (`main.py`)
* Designed for **maintainability, scalability, and hardware adaptation**
* Developed by **gabs911** and can be found here: https://github.com/gabs911/microfiber-tool/tree/main

---

## Project Goal

The main objective of this repository is to:

* Reuse a **proven microfiber fabrication system**
* Refactor its architecture into a **clean, modular design**
* Adapt it to a **new prototype 3D printer**
* Enable experimentation with **melted polymer-based nanofiber deposition**

In other words:

> This project is an **evolution of an existing syringe-based system into a new polymer-based fabrication platform**

---

## Current Project Credits

The current version was developed by:

**Developed by:** Gabriel Alvares de Sousa Guimaraes (gabs911)
**Supervised by:** Dr Andrii Shykarenko
**Institution:** Technical University of Liberec

---

## About This New Version

In this version, the focus is on:

* Code refactoring and cleanup
* Improved modularity
* Adaptation for a **new prototype nanofiber 3D printing system** based on **melted polymer extrusion**
* Maintaining compatibility with existing logic where possible

**Developed by:** Samuel Sampaio Diniz (Samueldnz)
**Supervised by:** Dr Andrii Shykarenko
**Institution:** Technical University of Liberec

---

## Final Notes

This project is an **ongoing refactor and adaptation effort** developed by Samuel Sampaio Diniz under the supervision of Andrii Shykarenko at the Technical University of Liberec in the year of 2026.
The intention is to preserve what already works while evolving the system to support **new experimental hardware and nanofiber production capabilities**.

