# EEE3097/8/9S Micromouse 2026: Submission 3
## GA3 Design Report 2 (30% of Course Mark)

---

### 1. Objective & Assessment Context
Submit a formal engineering design report documenting a structured design process conducted in relation to your **sensor filtering, maze mapping state flows, or routing pathfinder designs** from Milestone 2.

The primary purpose is to provide verifiable, defensible evidence of proficiency in the **ECSA Design Graduate Attribute (GA3)**. Meeting GA3 is a mandatory statutory requirement to pass the course.

---

### 2. Formative Calibration & Elevated Assessment Standards

> [!IMPORTANT]
> **Report 1 was a Formative Baseline — Report 2 Enforces Senior Engineering Rigor:**
> * **Formative Calibration:** In Design Report 1 (20%), markers gave students the benefit of the doubt on early conceptual designs and preliminary implementations to provide constructive diagnostic feedback.
> * **Senior Engineering Standards (30% Weighting):** Design Report 2 carries **1.5× the weight** of Report 1. Assessment will strictly reflect final-year engineering science standards.
> * **Calibrated Grading Expectations:** A standard, pedestrian submission that merely satisfies the basic template prompts with descriptive text, informal trade-off comparisons, or single-run test data will receive a solid baseline mark of **$2.0 / 3.0$ (66.7% / Lower Second band)**.
> * **Earning High Marks ($>75\%$ / First Class):** Scores in the **$2.5–3.0 / 3.0$** range are strictly reserved for submissions demonstrating deep technical rigor: formal first-principles equations ($u[k], T_s$, differential kinematics, $z$-domain models), analytical boundary proofs ($a_{\text{lat}} \le \mu g$), weighted decision matrices with numerical criteria, and multi-trial statistical telemetry ($\mu \pm \sigma$).
> * **GA3 Remediation:** For students who received $<1.5/3.0$ on any section in Report 1, Report 2 represents your primary statutory opportunity to remediate and clear all ECSA GA3 sub-minima.

---

### 3. Format & Submission Rules
To eliminate Word formatting issues and ensure seamless submission:
*   **Submission Platform:** Submit directly into the **Gradescope Online Assignment** titled `Submission 3: GA3 Design Report 2`.
*   **Character Limits:** Strict character limits (including spaces) are enforced during assessment for each question field. Check your character counts in your text editor before submitting.
*   **Visual Aids:** Upload your high-resolution diagram/model/schematic directly into the Question 2 file dropzone (`.png`, `.jpg`, or `.pdf`).
*   **LaTeX & MathJax Support:** Gradescope natively renders mathematical equations written in LaTeX format (e.g., inline math `$u[k] = K_p e[k]$` or block math `$$\dot{\theta} = \frac{r(\omega_R - \omega_L)}{b}$$`).
*   **Recommended Workflow (Draft Offline):** We strongly recommend drafting your responses offline in your favorite text/markdown editor (such as VS Code, Word, Notion, or Overleaf) where you can easily verify character counts and polish your equations, then copy-pasting your finalized text into the Gradescope Online Assignment fields before the deadline.

---

### 3. Open-Ended Design Subsystem Selection
You can choose any design subsystem from Milestone 2 for which you can confidently present evidence of design thinking. Illustrative examples include:

*   **Active Wall Centering:** Fusing side ToF measurements to steer down the corridor center.
*   **Algorithmic Path Exploration:** Designing Stateflow state machines, algorithmic flowcharts, or Python FSM classes to explore and map maze walls.
*   **Pathfinding Optimizations:** Formulating Floodfill, BFS, or Dijkstra algorithms to calculate the shortest path.
*   **Educational Interfaces:** Designing a visual block programming library and Python code generator.

---

### 4. Required Report Sections & Strict Constraints
Strict character constraints (including spaces) are enforced to ensure high-density communication:
1.  **Brief Description of Design Task (Max 350 chars):** Outline the subsystem task and the problem it solves.
2.  **Visual Aids:** Upload a single high-resolution graphic (e.g. block diagram, Stateflow transition chart, or telemetry plot) referenced in the text.
3.  **Design Criteria & Constraints (Max 700 chars):** Define quantitative target metrics and physical/computational limits.
4.  **Main Design Assumptions (Max 700 chars):** Outline and mathematically justify your engineering assumptions from first principles.
5.  **Design Process & Alternative Solutions (Max 900 chars):** Document your structured evaluation of at least two alternative design solutions (e.g., Floodfill vs. Dijkstra) including a compact decision matrix.
6.  **Design Implementation (Max 700 chars):** Model your chosen design using first-principles dynamic equations or script flow charts.
7.  **Design Evaluation & Testing (Max 700 chars):** Verify performance in simulation under physical perturbations (slip, motor asymmetry) and discuss model deviations.

---

### 5. Guidance & Common Pitfalls Reference
Review the **[GA3 Common Pitfalls & How to Meet Requirements Guide](ga3_common_pitfalls_guide.md)** for detailed section-by-section checklists, exemplars, and common traps identified during Design Report 1 audits.
