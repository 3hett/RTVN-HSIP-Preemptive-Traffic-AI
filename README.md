# RTVN & HSIP: Real-Time Violation Notification & High-Speed Interception System

**Preemptive AI-Based Traffic Policy Enforcement & Virtual Corridor Simulation Environment**  
*© 2026 Het Prajapati. All Rights Reserved. System Architecture & Engineering by Het Prajapati.*

---

## 1. System Overview
Existing traffic camera networks operate on a reactive enforcement model—issuing delayed post-violation digital challans days after an offense occurs, which fails to prevent imminent collisions in real time.

**RTVN & HSIP** introduces a **3-Node Preemptive Enforcement & Quick Law Enforcement Layer** designed to sit on top of highway and urban camera corridors:
1. **Camera Node 1 (0 m — Initial Detection & Real-Time Violator Alert):** Detects speeding and lane indiscipline and immediately pushes a **hands-free Voice Alert (English, Hindi, Gujarati)** and a **Detailed Written Violation Notice** directly to the violator's in-vehicle terminal/smartphone.
2. **Camera Node 2 (500 m Urban / 1,000 m Highway — Automated Rectification Verification):** Evaluates whether the driver complied within the corridor grace window:
   * **If Rectified:** Automatically dispatches a **Real-Time Rectification Confirmation** to the violator and closes the case with a **₹0 Fine**.
   * **If Unrectified:** Escalates and pauses the case at **Camera Node 3** for mandatory human review.
3. **Camera Node 3 (1,000 m Urban / 2,000 m Highway — Human Officer Confirmation Gate):** Enforces human-in-the-loop verification before executing higher-level penalties:
   * **Level 2 Confirmation:** Issues a ₹2,000 e-Challan + 3 Graded Demerit Points locked to vehicle insurance renewal.
   * **Level 3 HSIP Confirmation:** Preempts the Node 3 traffic signal to **RED** to create a controlled traffic buffer and dispatches an interception patrol unit.

---

## 2. Core Civil & Transportation Engineering Architecture
* **Corridor Node Spacing Geometry:** Configurable between **500 m** node spacing for Urban Arterial Roads and **1,000 m (1 km)** node spacing for High-Speed Highway Corridors.
* **IRC:35 Projective Homography:** Uses standard Indian Roads Congress (**IRC:35**) lane markings ($3.0\text{ m}$ paint dash + $4.5\text{ m}$ gap) as ground-plane reference coordinates to compute real-world velocity ($v = \Delta d / \Delta t$) and **Standard Deviation of Lateral Position ($SDLP$)** to identify erratic/DUI lane weaving.
* **IRC:73 Weather-Adaptive Stopping Sight Distance ($SSD$):** Solves $SSD = 0.278 \cdot v \cdot t_r + \frac{v^2}{254 \cdot f}$ in real time, automatically lowering enforced speed limits from $60\text{ km/h}$ on Dry Asphalt ($f = 0.35$) to $42\text{ km/h}$ on Monsoon Wet Pavement ($f = 0.18$).
* **Surrogate Safety Measures (SSMs):** Computes **Time-to-Collision ($TTC$)** and **Deceleration Rate to Avoid a Crash ($DRAC$)** to quantify pre-crash risk.
* **BSA 2023 Section 63 Cryptographic Evidence Ledger:** Hashes multi-node telemetry into an immutable **SHA-256** digest for tamper-proof evidentiary integrity.

---

## 3. Repository Structure
```text
├── index.html                              # Interactive 3-Node Virtual Corridor Simulation & Split-Screen Dashboard
├── rtvn_hsip_cv_engine.py                  # Core Python 3-Node Physics, Escalation & SHA-256 Telemetry Engine
├── sample_data/
│   └── corridor_telemetry_logs.json        # Verified 3-Node simulation telemetry & BSA 2023 SHA-256 logs
├── requirements.txt                        # Python package dependencies
├── LICENSE                                 # MIT License ((c) 2026 Het Prajapati)
├── .gitignore                              # Standard Git ignore rules
└── README.md                               # System documentation
```

---

## 4. How `index.html` and `rtvn_hsip_cv_engine.py` Work Together
* **`index.html` (Interactive Virtual Simulation Environment):** Runs directly in any browser (and via GitHub Pages) with zero installation so jury members can visually test the **3-Node Corridor**, switch between **500 m Urban** and **1 km Highway** geometry, hear the live **Split-Screen Violator Voice + Text Alerts**, and operate the **Node 3 Human Officer Confirmation Console**.
* **`rtvn_hsip_cv_engine.py` (Python Backend Engine):** Executes the identical 3-Node mathematical state machine in Python and generates the verified cryptographic telemetry log in `sample_data/corridor_telemetry_logs.json`.

### Quick Start
1. **Launch Web Simulation:** Open `index.html` in any modern web browser (Chrome / Edge) or visit the hosted GitHub Pages link.
2. **Run Python Simulation Suite:**
   ```bash
   pip install -r requirements.txt
   python rtvn_hsip_cv_engine.py
   ```

---
*© 2026 Het Prajapati. All Rights Reserved. System Architecture & Engineering by Het Prajapati.*
