# RTVN & HSIP: Preemptive AI-Based Traffic Policy Enforcement System

**Real-Time Violation Notification (RTVN) & High-Speed Interception Protocol (HSIP)**  
*Developed for the Viksit Bharat Young Leaders Dialogue (VBYLD) 2027 — Hack for Social Cause*

* **System Architect & Lead Developer:** Het Ishwarbhai Prajapati
* **Research Co-Lead & Policy Integration:** Dhruv Thumar
* **Institution:** Department of Civil Engineering, Silver Oak University, Ahmedabad, Gujarat

---

## 1. Executive Summary & Problem Statement
India records **4,80,583 road accidents** and **1,72,890 fatalities** annually (averaging 474 deaths per day), ranking #1 globally in road crash fatalities. Over **95% of India's road network** consists of urban and local municipal streets ("Other Roads"), where over-speeding accounts for **68.4% of all crashes**.

Current Automated Traffic Management Systems (ITMS) operate on a **reactive pipeline**: cameras capture an infraction, process it in the cloud, and dispatch an SMS fine days later. Consequently, **65.6% of all issued e-challans (worth ₹49,636.64 Crore) remain unpaid nationally**, and delayed text messages fail to stop a speeding or intoxicated driver from causing a fatal collision seconds down the road.

**RTVN & HSIP** shifts smart-city enforcement from passive, post-crash fine collection to **active, real-time behavioral rectification and physical hazard interception** using existing municipal CCTV cameras with zero additional roadside Doppler radar hardware.

---

## 2. Core Engineering & Architectural Innovations

### A. The 3-Node Preemptive Escalation Pipeline
Our software acts as a real-time preemptive decision and notification layer across three sequential camera nodes (configurable for **500 m Urban Arterial Roads** or **1,000 m / 1 km High-Speed Highway Corridors**):

1. **Camera Node 1 (0 m — Initial Detection & Real-Time Audio Alert):**
   * Detects speeding, lane indiscipline, or erratic weaving in real time.
   * Immediately overrides the violator's in-car Bluetooth/navigation audio (via Android Auto, CarPlay, or companion web receiver) with a **hands-free Voice TTS Alert (English, Hindi, or Gujarati)** alongside a detailed written notice.
2. **Camera Node 2 (500 m / 1 km — Automated Rectification Verification):**
   * Evaluates the vehicle's velocity and lane discipline as it crosses the second node.
   * **Level 1 (Self-Rectified):** If the driver slows down below the enforced speed limit before reaching Node 2, the system automatically dispatches a compliance confirmation and closes the case with a **₹0 Fine** (collision prevented).
   * **Unrectified Escalation:** If the driver ignores the Node 1 warning and continues speeding, automation pauses and forwards the case to **Camera Node 3**.
3. **Camera Node 3 (1,000 m / 2 km — Human Officer Confirmation Gate & HSIP):**
   * Enforces a mandatory **Human-in-the-Loop Officer Confirmation Console** before executing severe penalties:
     * **Confirm Level 2 (Active Penalization):** Issues a ₹2,000 e-Challan + **3 MoRTH Graded Demerit Points** directly locked to IRDAI motor insurance renewal and FASTag access.
     * **Confirm Level 3 (HSIP Physical Interception):** Triggered for extreme speeders ($\ge 90\text{ km/h}$), DUI weaving, or ghost/tampered plates. Dynamically preempts the Node 3 traffic signal to **RED** (creating a safe traffic buffer) and dispatches the nearest GPS-tracked Police Control Room (PCR) interceptor van.
     * **Dismiss:** Allows the human officer to clear false positives (e.g., emergency vehicles yielding).

---

### B. Civil & Transportation Engineering Mathematics (Zero Radar CAPEX)
Instead of retrofitting ₹5 Lakh Doppler speed radars at every junction, our engine extracts exact ground-plane kinematics purely from 30-FPS CCTV feeds using Indian Roads Congress (IRC) standards:

* **IRC:35 Projective Homography Calibration:**
  Uses standard Indian road lane markings (**$3.0\text{ m}$ white paint dash + $4.5\text{ m}$ gap = $7.5\text{ m}$ cycle**) as ground-plane reference points to apply OpenCV Perspective Transformation (`cv2.getPerspectiveTransform`). Converts camera pixels into Bird's-Eye View real-world meters $(X, Y)$ to compute exact velocity:
  $$v = \frac{\Delta d}{\Delta t} \times 3.6 \text{ (km/h)}$$
* **DUI & Erratic Weaving Detection ($SDLP$):**
  Continuously tracks lateral displacement along the $X$-axis to compute the **Standard Deviation of Lateral Position ($SDLP$)**. When $SDLP \ge 0.45\text{ m}$, the vehicle is mathematically flagged for Driving Under the Influence (DUI) or severe drowsiness.
* **IRC:73 Weather-Adaptive Stopping Sight Distance ($SSD$) Physics:**
  Static speed limits fail during heavy monsoon rain when wet asphalt reduces tire-road skid friction. Our engine solves the **IRC:73 Stopping Sight Distance** equation in real time:
  $$SSD = 0.278 \cdot v \cdot t_r + \frac{v^2}{254 \cdot f}$$
  *(where reaction time $t_r = 2.5\text{ s}$ and longitudinal friction $f = 0.35$ for Dry Asphalt vs. $f = 0.18$ for Monsoon Wet Pavement)*. In Monsoon Mode, the software automatically lowers the enforced speed limit from **$60\text{ km/h}$ to $42\text{ km/h}$**.
* **Surrogate Safety Measures ($TTC$ & $DRAC$):**
  Computes **Time-to-Collision ($TTC < 1.5\text{ s}$)** and **Deceleration Rate to Avoid a Crash ($DRAC > 3.4\text{ m/s}^2$)** to identify micro-conflicts before physical impact occurs.
* **Bharatiya Sakshya Adhiniyam (BSA) 2023 Section 63 Evidence Hashing:**
  Every multi-node trajectory record is sealed with an immutable **SHA-256 cryptographic hash**, providing tamper-proof digital evidence for Lok Adalats and traffic courts.

---

## 3. Repository Structure
```text
RTVN-HSIP-Preemptive-Traffic-AI/
├── index.html                                # Interactive 3-Node Virtual Corridor & Split-Screen Web Dashboard
├── rtvn_hsip_cv_engine.py                    # Core Python 3-Node Physics, Escalation & OpenCV Engine
├── sample_data/
│   └── corridor_telemetry_logs.json          # Verified 3-Node simulation telemetry & BSA 2023 SHA-256 logs
├── requirements.txt                          # Python dependencies (numpy, opencv-python)
├── LICENSE                                   # MIT Open-Source License
├── .gitignore                                # Git ignore configuration
└── README.md                                 # Complete system documentation & setup guide
```

---

## 4. Software Setup & Installation Guide

Our system consists of two synchronized components that you can run independently:
1. **`index.html` (The Interactive Web Simulation & Split-Screen Dashboard):** Runs in any web browser with **zero installation** required.
2. **`rtvn_hsip_cv_engine.py` (The Local Python Computer Vision & Telemetry Engine):** Runs on your computer via Python/VS Code to execute the backend mathematical state machine, generate cryptographic JSON logs, or process live webcam/CCTV feeds.

### Prerequisites for Python Backend
* **Python 3.10 or higher** installed on Windows, macOS, or Linux.
* **Visual Studio Code (VS Code)** or any terminal emulator.

### Step 1: Clone or Download the Repository
Download this repository as a `.zip` file and extract it to your Desktop, or clone it via Git:
```bash
git clone https://github.com/<your-username>/RTVN-HSIP-Preemptive-Traffic-AI.git
cd RTVN-HSIP-Preemptive-Traffic-AI
```

### Step 2: Install Python Dependencies
Open your terminal (or press ``Ctrl + ` `` in VS Code) inside the project folder and install the required libraries:
```bash
pip install -r requirements.txt
```
*(Note: If you have multiple Python versions installed on Windows, run `python -m pip install numpy opencv-python` using your active Python interpreter path).*

---

## 5. How to Use the Software (Step-by-Step User Manual)

### Part A: Using the Interactive Web Dashboard (`index.html`)
1. **Launch the Interface:** Double-click `index.html` to open it in Google Chrome or Microsoft Edge (or visit the hosted **GitHub Pages** link). Make sure your system audio volume is turned up.
2. **Select Corridor Geometry & Weather Physics:**
   * Use the top navigation bar to toggle between **Urban Road Corridor (500 m node spacing)** and **High-Speed Highway Corridor (1 km node spacing)**.
   * Toggle between **Dry Asphalt ($f = 0.35$, Limit: $60\text{ km/h}$)** and **Monsoon Wet Pavement ($f = 0.18$, Limit: $42\text{ km/h}$)** to watch the IRC:73 Stopping Sight Distance ($SSD$) dynamically recalculate.
3. **Run the 3-Node Virtual Corridor Scenarios:**
   * **Scenario 1 (Level 1 — Self-Rectification):** Watch a speeding vehicle trigger an instant voice and written alert at **Node 1** on the right-hand **Violator Receiver Interface**. As the vehicle decelerates before **Node 2**, the system automatically issues a compliance confirmation and logs a **₹0 Fine**.
   * **Scenario 2 (Level 2 — Persistent Violator):** Watch a vehicle ignore the Node 1 warning and speed through Node 2. The system automatically pauses at **Node 3** and activates the **Node 3 Human Officer Confirmation Gate**. Click **"Confirm Level 2 (Challan)"** to issue the ₹2,000 fine + 3 demerit points and generate the BSA 2023 SHA-256 hash.
   * **Scenario 3 (Level 3 — HSIP Extreme Speed / DUI Weaving):** Simulates a high-speed weaving vehicle ($SDLP > 0.45\text{ m}$). When paused at Node 3, click **"Confirm Level 3 HSIP (Patrol)"** to preempt the Node 3 traffic signal to **RED** on the highway canvas and dispatch the interceptor unit.

---

### Part B: Running the Python Backend Engine (`rtvn_hsip_cv_engine.py`)
1. **Run the Automated 3-Node Diagnostic & Telemetry Suite:**
   In your terminal, execute:
   ```bash
   python rtvn_hsip_cv_engine.py
   ```
   **What happens:**
   * The script runs all three multi-node mathematical verification scenarios in the terminal (500 m Urban Self-Rectification, 500 m Urban Level 2 Escalation, and 1 km Highway Monsoon Level 3 HSIP).
   * It automatically computes $SDLP$, $TTC$, $DRAC$, IRC:73 $SSD$, and generates the immutable **BSA 2023 Section 63 SHA-256 hashes**.
   * It exports the verified telemetry records directly to `sample_data/corridor_telemetry_logs.json`.

2. **Run Live Hardware Webcam / CCTV Tracking (Optional Mode):**
   If using the local hardware script with a live webcam or pre-recorded traffic `.mp4` video:
   ```bash
   python local_hardware_cctv_enforcement_engine.py --mode live --source 0
   ```
   * Press **`W`** on your keyboard while the video feed is active to switch to **Monsoon Wet Mode** ($42\text{ km/h}$ limit).
   * Press **`D`** to return to **Dry Asphalt Mode** ($60\text{ km/h}$ limit).
   * Press **`Q`** to close the camera window.

---

## 6. Hosting Live on GitHub Pages (For Jury Inspection)
1. Upload all repository files (`index.html`, `rtvn_hsip_cv_engine.py`, `requirements.txt`, `README.md`, `LICENSE`, `.gitignore`, and `sample_data/corridor_telemetry_logs.json`) to your public GitHub repository.
2. Click **Settings** (top tab of your GitHub repository) $\rightarrow$ select **Pages** on the left sidebar.
3. Under **Build and deployment $\rightarrow$ Branch**, change `None` to **`main`** and click **Save**.
4. Wait 60 seconds and refresh the page. GitHub will provide a live URL (`https://<your-username>.github.io/<repo-name>/`) that opens your interactive 3-Node Simulation Dashboard on any laptop or smartphone.

---

## 7. AI Usage & Prior-Work Disclosure
* **80% Human-Authored Engineering & Research:** Core problem formulation, MoRTH statistical synthesis, the 3-Node RTVN/HSIP escalation state machine, and all IRC:35/IRC:73 civil engineering mathematical formulations were conceived, modeled, and verified by **Het Ishwarbhai Prajapati** and **Dhruv Thumar**.
* **20% AI Assistance:** Open-source computer vision libraries (OpenCV / YOLOv8) are utilized for runtime object tracking, and generative AI (Google Gemini) provided ~20% assistance strictly for frontend UI layout scaffolding, Python syntax optimization, and documentation formatting.

---

## 8. License & Copyright
Distributed under the **MIT License**. See `LICENSE` for full details.  
*© 2026 Het Prajapati. All Rights Reserved. System Architecture & Engineering by Het Prajapati.*
