# EEE3097/8/9S Micromouse 2026: GA3 Design Report Guide
## Common Pitfalls & How to Meet ECSA GA3 Requirements

---

### Executive Summary & Purpose

This guide outlines the critical findings, common failure modes, and best-practice exemplars identified during the audit of **Design Report 1**. 

The primary objective of these reports is to provide verifiable, defensible evidence of proficiency in the **ECSA Design Graduate Attribute (GA3)**. Meeting GA3 is a mandatory statutory requirement to pass the course. Use this guide to audit your draft before submitting **Design Report 2** (or subsequent remediation attempts).

---

### The ECSA GA3 Sub-Minimum Rule

To achieve an ECSA GA3 pass, a student must demonstrate competence across **all core design stages**:
* You must achieve **$\ge 50\%$ ($1.5 / 3.0\text{ pts}$)** on every individual technical section (Sections 3 to 7).
* Scoring high in one section (e.g., an exceptional Simulink diagram in Section 2) **cannot compensate** for leaving another section deficient (e.g., omitting the trade-off matrix in Section 5 or testing data in Section 7).

---

### Section-by-Section Pitfalls & Required Evidence

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 ECSA GA3 DESIGN PIPELINE                               │
│                                                                                        │
│  [Sec 3: Criteria] ──► [Sec 4: Assumptions] ──► [Sec 5: Trade-Offs]                    │
│   (Quantified)          (Physical Limits)        (Weighted Matrix)                     │
│                                                          │                             │
│                                                          ▼                             │
│  [Sec 2: Visuals]  ◄── [Sec 7: Evaluation]  ◄── [Sec 6: Modeling]                      │
│   (Explicitly Cited)    (Empirical Data)         (First-Principles Math)               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Section 2: Visual Aids (Page 4 of Template)

* **Weight:** $3.0\text{ pts}$ (Sub-minimum: $1.5\text{ pts}$)
* **Common Pitfalls:**
  
  * **The "Orphan Figure" Trap (51 students penalized):** Placing a diagram on Page 4 but **never mentioning or citing it in the body text**. A visual aid is only evidence if it is explicitly referenced (e.g., *"As shown in Figure 1..."* or *"See Page 4 block diagram for the feedback loop"*).
  * **Unreadable Low-Resolution Captures:** Pasting zoomed-out Simulink models or state machines where block names, mathematical expressions, or signal lines are illegible.
  * **Generic Internet / Stock Photos:** Pasting photos of a generic breadboard, motor, or stock Micromouse chassis instead of an actual technical design artifact.
  
* **What Meets the Standard:**
  
  * A clear, high-resolution **Simulink model**, **Stateflow transition chart**, **control block diagram**, or **circuit schematic**.
  * Complete signal labels, variable names, sample rates, and distinct subsystem boundaries.
  * Explicitly cited and explained within Section 6 or Section 7.

---

### Section 3: Design Criteria and Constraints

* **Weight:** $3.0\text{ pts}$ (Sub-minimum: $1.5\text{ pts}$)
* **Character Limit:** $700\text{ characters}$ (including spaces)
* **Common Pitfalls:**
  
  * **Qualitative Vagueness:** Using subjective words like *"the robot should turn quickly"*, *"must maintain a stable speed"*, or *"navigate accurately"*.
  * **Ignoring Computational & Physical Constraints:** Omitting system limits such as sampling loop frequencies, hardware timer resolutions, or bus communication limits.
  
* **What Meets the Standard:**
  
  * **Explicit Quantitative Performance Metrics:** State target numbers with physical units (e.g., steady-state error $e_{ss} \le 2.0\text{ mm}$, maximum overshoot $M_p < 5\%$, rise time $t_r \le 0.35\text{ s}$, heading drift $< 1.5^\circ/\text{m}$).
  * **Concrete Platform Constraints:** Specify exact hardware limits (e.g., MCU clock $80\text{ MHz}$, discrete loop period $T_s = 10\text{ ms}$ ($100\text{ Hz}$), $\text{I}^2\text{C}$ bus rate $400\text{ kHz}$, battery voltage range $3.6\text{ V} - 4.2\text{ V}$, motor deadband $\text{PWM} < 12\%$).

---

### Section 4: Main Design Assumptions with Justification

* **Weight:** $3.0\text{ pts}$ (Sub-minimum: $1.5\text{ pts}$)
* **Character Limit:** $700\text{ characters}$ (including spaces)
* **Common Pitfalls:**
  
  * **Stating Trivialities:** Listing textbook constants without engineering justification (e.g., *"Assume gravity is 9.81 m/s²"*).
  * **Unjustified "Ideal World" Assumptions:** Assuming zero wheel slip, zero sensor noise, or perfectly matched DC motors without stating why this assumption holds or where it breaks down.
  
* **What Meets the Standard:**
  
  * **Physically Grounded Assumptions with Boundaries:** State the assumption and justify its operational envelope mathematically or empirically:
    * *Traction / No-Slip:* *"Pure rolling is assumed because maximum acceleration $a_{max} = 0.8\text{ m/s}^2 \ll \mu g \approx 0.6 \times 9.81 = 5.88\text{ m/s}^2$."*
    * *Sensor Noise / Bias:* *"Gyro drift is assumed linear over a single maze corridor ($< 2\text{ s}$) and compensated by taking a 50-sample stationary bias calibration on boot."*
    * *Motor Dynamics:* *"Electrical time constant $\tau_e = L/R \approx 0.2\text{ ms}$ is neglected relative to mechanical time constant $\tau_m \approx 45\text{ ms}$."*

---

### Section 5: Design Process & Alternative Solutions

* **Weight:** $3.0\text{ pts}$ (Sub-minimum: $1.5\text{ pts}$)
* **Character Limit:** $700\text{ characters}$ (including spaces)
* **Primary Cause of GA3 Deficiencies across the Cohort.**
* **Common Pitfalls:**
  
  * **No Weighted Decision Matrix:** Describing two options purely in narrative prose without a structured comparison.
  * **Strawman / Trivial Alternatives:** Comparing your chosen solution against *"doing nothing"* or comparing two completely unrelated subsystems.
  
* **What Meets the Standard:**
  
  * Formulate at least **two viable, competing design alternatives** for the same subsystem (e.g., *Discrete P vs. PID with Anti-Windup*; *Direct Sensor Thresholding vs. Complementary Filter*; *Fixed PWM vs. Encoder-Based Velocity Feedback*).
  * Include a compact **Weighted Trade-Off Matrix** within your character budget:

| Option | Tracking Accuracy ($40\%$) | CPU/Memory Cost ($30\%$) | Noise Rejection ($30\%$) | Weighted Total |
| :--- | :---: | :---: | :---: | :---: |
| **A: Proportional Only** | $2.5 / 5$ | $5.0 / 5$ | $3.0 / 5$ | **`3.4 / 5.0`** |
| **B: Discrete PID + Filter** | $4.5 / 5$ | $3.5 / 5$ | $4.5 / 5$ | **`4.2 / 5.0` (Selected)** |

---

### Section 6: Design Implementation & First-Principles Modeling

* **Weight:** $3.0\text{ pts}$ (Sub-minimum: $1.5\text{ pts}$)
* **Character Limit:** $700\text{ characters}$ (including spaces)
* **Common Pitfalls:**
  
  * **Code Narrative instead of Mathematics:** Writing sentences like *"If sensor is less than 50 we call set_motors(30, 40)"*.
  * **Floating Equations:** Pasting standard equations without defining parameters, units, or linking them to the physical robot.
  
* **What Meets the Standard:**
  
  * **First-Principles Mathematical Formulation:** Define the governing differential equations, kinematic models, or discrete difference equations:
    * *Differential Kinematics:* $v = \frac{r(\omega_R + \omega_L)}{2}$, $\dot{\theta} = \frac{r(\omega_R - \omega_L)}{b}$ where track width $b = 85\text{ mm}$, wheel radius $r = 16\text{ mm}$.
    * *Discrete Controller:* $u[k] = u[k-1] + K_p(e[k] - e[k-1]) + K_i T_s e[k] + \frac{K_d}{T_s}(e[k] - 2e[k-1] + e[k-2])$.
    * *State Transition Equations:* Explicit conditional guarding logic ($[TOF_{left} < d_{thresh} \land |v| > 0] \rightarrow \text{ALIGN}$).

---

### Section 7: Design Evaluation, Testing & Discussion

* **Weight:** $3.0\text{ pts}$ (Sub-minimum: $1.5\text{ pts}$)
* **Character Limit:** $700\text{ characters}$ (including spaces)
* **Common Pitfalls:**
  
  * **"It Worked" Claims without Data:** Stating that the mouse completed the run successfully without showing numbers, plots, or metrics.
  * **Ignoring Discrepancies:** Failing to discuss the differences between the ideal theoretical model and the messy physical robot.
  
* **What Meets the Standard:**
  
  * **Quantitative Experimental Evidence:** Present measured test outcomes from your simulator or physical hardware telemetry (e.g., *"Measured settling time $t_s = 0.31\text{ s}$, steady-state error $e_{ss} = \pm 1.8\text{ mm}$, maximum heading overshoot $4.2\%$ across 10 trials"*).
  * **Critical Engineering Discussion of Discrepancies:** Explain deviations between model and hardware (e.g., *"Physical telemetry showed an unmodeled $15\text{ ms}$ latency in $\text{I}^2\text{C}$ sensor reads, requiring reduction of $K_d$ from $0.12$ to $0.08$ to prevent high-frequency chatter"*).

---

### Section 8: Quality, Synthesis & Template Compliance

* **Weight:** $2.0\text{ pts}$ (Sub-minimum: $1.0\text{ pt}$)
* **Rules to Follow:**
  
  * **Do Not Disable Form Protection:** Do not modify Word form boundaries, alter field names, or delete template tables.
  * **Strict Character Limits:** Ensure your text does not exceed the designated character caps. Truncated text cannot receive credit.
  * **Coherent Storyline:** Ensure the subsystem described in Section 1 matches the criteria in Section 3, the assumptions in Section 4, the options in Section 5, the equations in Section 6, and the data in Section 7.

---

### Summary Checklist for Submission 2

Before converting your Word document to PDF and submitting to Gradescope, check:

- [ ] Every technical section (Sections 3–7) contains specific numbers and physical units.
- [ ] Section 2 (Page 4 diagram) is explicitly cited and discussed in the body text (e.g., *"As shown in Figure 1..."*).
- [ ] Section 5 contains a structured decision / trade-off matrix comparing at least two options.
- [ ] Section 6 contains explicit first-principles governing mathematical formulas (differential kinematics, difference equations, or state transition guards).
- [ ] Section 7 contains quantitative test metrics comparing expected vs. measured performance.
- [ ] Form protection was maintained and no text exceeds character limits.
