# EEE3097/8/9S Micromouse 2026: Design Report Guidelines
## Graduate Attribute 3 (Design) Assessment Portfolio

---

### 1. Overview
As part of the course assessment, you must submit two formal engineering design reports documenting a structured design process conducted in relation to the Micromouse project. 

The main purpose of these submissions is to demonstrate proficiency in the **ECSA Design Graduate Attribute (GA3)**, which is a mandatory requirement to pass the course.

* **Design Report 1 (20%):** Submitted alongside the Milestone 1 assessment.
* **Design Report 2 (30%):** Submitted alongside the Milestone 2 assessment.

---

### 2. Format & Submission Rules

* **Design Report 1:** Submitted via the Microsoft Word form template and uploaded as a PDF.
* **Design Report 2:** Submitted directly via the **Gradescope Online Assignment** interface with real-time character counters, native LaTeX equation rendering, and direct graphic file uploads.
* **Recommended Workflow:** We strongly recommend drafting and refining your responses offline in your preferred markdown/text editor (e.g. VS Code, Word, Notion, Overleaf) to check character counts and format your equations, then copy-pasting your text directly into the respective Gradescope fields before submitting.

---

### 3. Open-Ended Design Task Selection
You can choose **any design task** from your Micromouse development for which you can confidently present evidence of design thinking. 

Without being prescriptive, some illustrative examples of design tasks you could document include:
1. **Dynamic Simulation Modeling:** Designing a more realistic and operationally useful Simulink model or Python physics representation of the Micromouse DC motor drive and friction system.
2. **Closed-Loop Speed Controller:** Designing, tuning, and discretizing a PID feedback controller to match wheel speeds.
3. **Robust Heading & Yaw Alignment:** Fusing gyroscope rates and encoders to steer the mouse and correct drift.
4. **Active Wall Centering:** Fusing front and side ToF sensor readings to steer down the corridor center.
5. **Algorithmic Path Exploration:** Designing Stateflow state machines, algorithmic flowcharts, or Python FSM classes to explore and map the maze cells.
6. **Pathfinding Optimizations:** Formulating Floodfill or BFS algorithms to calculate the shortest path.
7. **Educational Interfaces (Blockly):** Designing a child-friendly visual block programming library and Python code generator.
8. **Watchdog Safety Wrappers:** Designing software safety blocks or safety overrides to prevent collisions.

---

### 4. Required Report Sections & Strict Constraints
To encourage concise, high-density engineering communication and prevent AI-generated filler, strict character limits are enforced (including spaces). Your report must populate the template sections, detailing:
*   **Brief Description of Design Task (Max 350 chars):** Outline the subsystem task and the problem it solves.
*   **Visual Aids:** Insert a single graphic (e.g. block diagram, Stateflow transition chart, or telemetry plot) referenced in the text.
*   **Design Criteria & Constraints (Max 700 chars):** Define quantitative target metrics and physical/computational limits.
*   **Main Design Assumptions (Max 700 chars):** Outline and mathematically justify your engineering assumptions.
*   **Design Process Description (Max 700 chars):** Document your structured evaluation of at least two alternative solutions.
*   **Design Implementation (Max 700 chars):** Model your chosen design using first-principles dynamic equations or script flow charts.
*   **Design Evaluation & Testing (Max 700 chars):** Verify performance under physical perturbations (slip, motor asymmetry) and discuss model deviations.

---

### 5. Guidance & Common Pitfalls Reference
Before submitting, thoroughly consult the **[GA3 Common Pitfalls & How to Meet Requirements Guide](ga3_common_pitfalls_guide.md)** for section-by-section criteria, common failure modes, and concrete engineering exemplars.
