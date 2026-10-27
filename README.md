<pre><code># RTVN &amp; HSIP: Preemptive AI-Based Urban Traffic Policy Enforcement &amp; Pre-Collision Kinematics Engine


[![VBYLD 2027](https://img.shields.io/badge/VBYLD_2027-Hack_for_Social_Cause-06b6d4?style=for-the-badge)](https://mybharat.gov.in/)
[![IRC Compliant](https://img.shields.io/badge/Civil_Engineering-IRC:35_%26_IRC:73_Compliant-10b981?style=for-the-badge)](#mathematical--transportation-engineering-formulation)
[![BSA 2023](https://img.shields.io/badge/Forensic_Ledger-BSA_2023_Sec_63_SHA256-f59e0b?style=for-the-badge)](#bharatiya-sakshya-adhiniyam-bsa-2023-section-63-cryptographic-hash)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)


&gt; **"In this modern world of quick e-commerce, we are serving quick law enforcement."**
&gt; Shifting Indian Smart Cities from reactive post-crash fine collection (`CAMERAS -&gt; CLOUD AI -&gt; ADMIN -&gt; FINE`) to real-time pre-collision kinematics, hands-free regional voice rectification (**RTVN**), and physical police signal-preemption interception (**HSIP**).


---


## 👨‍💻 Authorship, Ownership &amp; Credit Declaration


* **Het Ishwarbhai Prajapati** *(Enrollment No.: 2302030300002)* — **Team Lead, Chief System Architect &amp; Principal AI / Civil Engineering Developer**
  *Conceived and engineered the complete RTVN &amp; HSIP preemptive system architecture, the IRC:35 3x3 projective homography solver, the IRC:73 dynamic wet-pavement braking model, the Surrogate Safety Measures (TTC, DRAC, SDLP, Lateral Jerk) pre-collision engine, the 3-Level Multi-Node "If-Else" State Machine, and the full-stack Interactive Command Center (`index.html` &amp; `rtvn_hsip_cv_engine.py`).*
* **Dhruv Thumar** — **Research Co-Lead (Statistical &amp; Policy Research)**
  *Compiled the two-decade MoRTH macro-accident severity datasets (2005–2023), urban non-peak hazard profiles, and MoRTH Graded Demerit Point System policy integration.*
* **Institution:** Department of Civil Engineering, Aditya Silver Oak Institute of Technology (ASOIT), Silver Oak University, Ahmedabad, Gujarat, India.
* **Faculty Guide:** Dr. Abhijitsinh Parmar (Head of the Department, Civil Engineering).
* **AI Tool Disclosure (Per VBYLD 2027 Guidelines):** 80% Human-Authored Civil Engineering Architecture, Mathematical Formulation &amp; Research (led and architected by Het Ishwarbhai Prajapati, with statistical research by Dhruv Thumar); ~20% AI Assistance (Google Gemini used for UI layout scaffolding and code syntax structuring, alongside open-source pre-trained YOLOv8/OpenCV runtime libraries).


---


## 📊 Verified Problem Context (MoRTH &amp; Parivahan Datasets)


1. **Macro Road Lethality (MoRTH *Road Accidents in India 2023* Report):**
   * **4,80,583 road accidents** and **1,72,890 fatalities** annually (**1,317 crashes &amp; 474 deaths every single day**).
   * India ranks **#1 globally in road crash fatalities** (180% higher than #2 China: 1,68,491 vs. 60,676).
   * Crash **Severity Index** (deaths per 100 accidents) surged from **21.6 (2005)** to **36.0 (2023)**.
2. **The Urban "Other Roads" &amp; Nighttime Non-Peak Crisis:**
   * **"Other Roads"** (urban municipal &amp; local streets = **95% of India's 66 Lakh km road network**) suffered a **+10.91% annual surge in crashes** (rising from 2,02,633 in 2022 to 2,24,744 in 2023; **46.8%** of all crashes).
   * **Over-speeding** accounts for **68.4% of all crashes** (3,28,727) and **68.07% of all deaths** (1,17,682), while **wrong-side driving / lane indiscipline** surged by **+11.76%** (25,242 crashes).
3. **Empirical Proof of Reactive Smart City AI Failure (Parivahan Portal, Oct 2026):**
   * Across India, out of **49.15 Crore e-challans** issued worth **₹75,663.61 Crore**, over **30.37 Crore challans worth ₹49,636.64 Crore remain unpaid (65.6% uncollected nationally; 97.2% unpaid in Noida ITMS)**.


---


## 📐 Mathematical &amp; Transportation Engineering Formulation


1. **Radar-Free Perspective Homography Calibration (`IRC:35-2015`):**
   Uses standard Indian Roads Congress (**IRC:35**) highway lane markings (**3.0m painted white dash + 4.5m gap = 7.5m cycle**, **3.5m lane width**) to solve the 3x3 Projective Transformation Matrix **H** mapping 2D camera pixels `(u, v)` to ground-plane meters `(X, Y)`.
2. **Weather-Adaptive Stopping Sight Distance (`IRC:73-1980`):**
   `SSD = 0.278 * v * t_r + (v^2) / (254 * (f +/- 0.01 * S))`
   Dynamically adjusts enforced speed limits from **60 km/h on Dry Bituminous Concrete (`f = 0.35`, `SSD = 82.4m`)** to **42 km/h on Monsoon Wet Pavement (`f = 0.18`, `SSD = 67.8m`)**.
3. **Pre-Collision Surrogate Safety Measures (`TTC` &amp; `DRAC`):**
   * **Time-to-Collision:** `TTC = (Y_lead - Y_follow - L_veh) / (v_follow - v_lead)`
   * **Deceleration Rate to Avoid Crash:** `DRAC = (v_follow - v_lead)^2 / (2 * (Y_lead - Y_follow - L_veh))`
   Flags imminent pre-collision conflicts when `TTC &lt; 1.5s` or `DRAC &gt; 3.4 m/s^2`.
4. **DUI Sinusoidal Weaving (`SDLP`) &amp; Illegal Cut-In Lateral Jerk (`J_x`):**
   Flags intoxicated/fatigued weaving when `SDLP &gt;= 0.45m` and sudden illegal lane cuts when `J_x = |d^3X/dt^3| &gt;= 1.5 m/s^3`.
5. **HSIP Signal Preemption Timing (`t_preempt`):**
   `t_preempt = (d_corridor / v_veh) - t_clearance_buffer`
   Preempts the downstream Node 02 traffic signal at Iskcon Cross Road to RED to create a safe, controlled interception buffer ahead of the PCR patrol unit.


---


## 📂 Repository Structure
* `index.html` — Self-contained Interactive Pre-Collision Command Center, Mouse-Drive Tester &amp; Live Webcam Tracker.
* `rtvn_hsip_cv_engine.py` — Python OpenCV + YOLOv8 + IRC:35/73 Physics &amp; BSA-2023 SHA-256 Backend Engine.
* `requirements.txt` — Python dependencies.
* `sample_data/ahmedabad_sgh_corridor_telemetry.json` — Calibrated S.G. Highway corridor telemetry, MoRTH benchmarks &amp; test cases.
* `LICENSE` — Open-Source MIT License.
* `README.md` — System architecture &amp; mathematical documentation.


---


## 🚀 How to Run &amp; Test Immediately
1. **Interactive Web Command Center:** Open `index.html` in any browser (or via GitHub Pages). Click **`🕹️ Interactive Mouse Drive`** to manually drive and weave a vehicle across Node 01 and Node 02, click **`SSM: Cut-In / TTC`** to test pre-collision interception, or click **`🧪 Verify Math Suite`**.
2. **Python Engine:**
   ```bash
   pip install -r requirements.txt
   python rtvn_hsip_cv_engine.py --source sim
   python rtvn_hsip_cv_engine.py --source 0
   ```
</code></pre>
