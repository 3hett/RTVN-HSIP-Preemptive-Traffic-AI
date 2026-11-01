# RTVN & HSIP: Real-Time Violation Notification & High-Speed Interception System

**Preemptive AI-Based Urban Traffic Policy Enforcement & 3-Node Corridor Simulation Environment**  
*© 2026 Het Prajapati. All Rights Reserved. System Architecture, Civil Engineering Modeling & AI Engine by Het Prajapati.*

---

## 1. Executive Summary
Conventional Automated Traffic Enforcement Systems (ATES) operate on a post-hoc penalization model—issuing digital e-challans days after an offense occurs, which fails to prevent imminent high-speed collisions in real time.

**RTVN & HSIP** introduces a **3-Node Preemptive Enforcement Layer** over existing urban and highway CCTV corridors:
* **Camera Node 1 (0 m — Initial Detection & Real-Time Violator Alert):** Detects over-speeding and severe lateral weaving ($SDLP$) and immediately transmits a hands-free **Voice Alert (Web Speech TTS)** and **Written Violation Notice** to the driver.
* **Camera Node 2 (500 m Urban / 1,000 m Highway — Automated Rectification Verification):** Evaluates whether the driver decelerated within the corridor grace window:
  * **Level 1 (Self-Rectified):** Dispatches an immediate compliance confirmation and closes the case with a **₹0 Fine**.
  * **Unrectified:** Pauses automation and escalates the case to **Camera Node 3** for human-in-the-loop officer review.
* **Camera Node 3 (1,000 m Urban / 2,000 m Highway — Human Officer Confirmation Gate):**
  * **Level 2 Confirmation:** Issues a ₹2,000 e-Challan + 3 MoRTH Demerit Points.
  * **Level 3 HSIP Confirmation:** Preempts the Node 3 traffic signal to **RED** to create a controlled traffic buffer and dispatches an interception patrol unit.

---

## 2. Core Civil Engineering & Computer Vision Formulations
1. **IRC:35 Perspective Homography (`_calibrate_irc35_homography`):** Uses Indian Roads Congress (**IRC:35**) standard lane markings ($3.0\text{ m}$ dash + $4.5\text{ m}$ gap = $7.5\text{ m}$ cycle) to project 2D tire-asphalt contact pixels (`(cx, y_bottom)`) onto a flat metric plane ($7.0\text{ m} \times 30.0\text{ m}$), eliminating 3D bounding-box parallax error.
2. **IRC:73 Weather-Adaptive Stopping Sight Distance (`compute_irc73_ssd`):**
   $$SSD = 0.278 \cdot v \cdot t_r + \frac{v^2}{254 \cdot (f \pm 0.01 \cdot S)}$$
   Automatically adjusts enforced speed limits from **$60\text{ km/h}$** on Dry Asphalt ($f = 0.35$) to **$42\text{ km/h}$** on Monsoon Wet Pavement ($f = 0.18$).
3. **Surrogate Safety Measures (`compute_surrogate_safety` & `compute_sdlp`):** Continuously evaluates **Standard Deviation of Lateral Position ($SDLP \ge 0.45\text{ m}$)** for DUI weaving, **Time-to-Collision ($TTC$)**, and **Deceleration Rate to Avoid a Crash ($DRAC$)**.
4. **BSA 2023 Section 63 Evidence Hashing (`generate_bsa_section63_hash`):** Generates an immutable 64-character **SHA-256** digest of multi-node telemetry for electronic evidence admissibility under Section 63 of the Bharatiya Sakshya Adhiniyam (2023).

---

## 3. Repository Structure
```text
RTVN-HSIP-Preemptive-Traffic-AI/
├── index.html                                # Main Command Center & 3-Node Corridor Dashboard
├── notification-preview.html                 # Dedicated Violator-Side Real-Time Receiver View
├── styles.css                                # Dashboard layout & responsive styling
├── app.js                                    # Main frontend simulation & UI controller
├── config.js                                 # Corridor spacing (500m / 1km) & IRC:73 constants
├── state.js                                  # Centralized runtime state store
├── rules.js                                  # IRC:73 SSD, SDLP, TTC/DRAC & escalation rules
├── scenarios.js                              # Pre-configured multi-node verification scenarios
├── render.js                                 # DOM & telemetry rendering engine
├── notification-preview.js                   # Violator receiver sync & Web Speech TTS engine
├── backend-bridge.js                         # FastAPI WebSocket client & BSA Sec. 63 Tamper Auditor
├── rtvn_hsip_cv_engine.py                    # Python YOLOv8 + OpenCV Homography & FastAPI Engine
├── sample_data/
│   └── corridor_telemetry_logs.json          # Verified 3-Node telemetry & BSA 2023 SHA-256 logs
├── requirements.txt                          # Python dependencies
├── LICENSE                                   # MIT Open-Source License
└── README.md                                 # System documentation & setup guide
