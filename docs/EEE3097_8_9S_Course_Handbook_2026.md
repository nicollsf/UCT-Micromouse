# **EEE3097/8/9S Course Handbook & Project Specifications**

**Course:** EEE3097/8/9S (2026)  
**Project:** Autonomous Micromouse Robotic Maze Solver

> [!IMPORTANT]
> **Primary Course GitHub Repository:** [https://github.com/nicollsf/UCT-Micromouse](https://github.com/nicollsf/UCT-Micromouse)  
> Clone this repository recursively to establish your workspace, obtain updates, and access all templates and instructions.
> 
> *Note on Repository Updates:* Necessary updates and bug fixes will be pushed to the repository on the fly during the semester. It is your academic responsibility to configure **GitHub Notifications** (click the **"Watch"** button at the top-right of the repository page and select "All Activity") to automatically track changes. Check notifications and run `git pull --recurse-submodules` regularly to ensure all nested microcontroller submodules remain synchronized.
> 
> **Definitive Source of Truth (.md format):**  
> All files in the repository ending in `.md` (Markdown format) represent the single, definitive source of truth for course instructions, rubrics, and technical guides. Any PDF versions distributed on D2L (Amathuba) are compiled directly from these Markdown files. Always pull the latest repository updates to ensure your local documentation is accurate and up-to-date.
> 
> **How to Read Markdown (.md) Files:**  
> Markdown files are plain-text documents containing formatting markup. To read them with rich graphical styling (headers, bold text, links, and tables):
> *   **VS Code (Recommended):** Open the `.md` file and press **`Cmd+Shift+V`** (macOS) or **`Ctrl+Shift+V`** (Windows/Linux) to open the side-by-side graphical Preview panel.
> *   **Web Browser Extension:** Install the "Markdown Viewer" extension (Chrome/Firefox/Edge). Drag-and-drop local `.md` files into your browser window to render them as styled webpages.
> *   **GitHub Web Page:** Viewing the files directly on the GitHub web interface automatically renders them with rich formatting.
> 
> [!WARNING]
> **CRITICAL HARDWARE SAFETY WARNING:** 
> 1. **AVOID PLUGGING IN ANY MORE THAN ONE USB CABLE AT A TIME:** To protect your hardware (microcontroller, power board, and laptop/charger) from ground loop damage, do not simultaneously connect USB cables to the power board, the processor board, and the ST-Link debugger.
> 2. **DO NOT ROTATE THE MOUSE WHEELS EXTERNALLY/MANUALLY:** The wheels are connected to a high-ratio gearbox that is not back-drivable. Forcing the wheels to rotate by hand is highly likely to strip the gears and permanently destroy the motor assembly.
> 3. **DO NOT INITIALIZE THE BATTERY CONNECTION WHILE THE BOARD IS POWERED:** Under normal operation, the LiPo battery is plugged into the power board exactly once during assembly and remains connected. When initially plugging the battery connector into the board, **ensure all USB cables are disconnected and the board is completely unpowered**. Connecting the battery while the board is already powered (e.g., via USB) will cause the onboard charging/boost circuitry to fail catastrophically (with a high risk of the charging chip catching fire).

---

## **1. Introduction & Primary Course Task**

The UCT Micromouse project is a comprehensive engineering design challenge designed to evaluate and accredit your skills in embedded systems, control theory, and software design. 

### **The Primary Project Task:**
Your objective is to design, implement, and validate the code logic that enables a differential-drive robot to autonomously explore a maze, map the layout of its walls, plan the shortest path to a target cell, and execute a high-speed solving sprint. 

To pass the course and meet ECSA Graduate Attribute 3 (Design) requirements, you must prove that your mouse uses **active feedback control** to adapt to physical disturbances (such as motor asymmetries and wheel slip) rather than relying on faked or open-loop timed delays.

### **Project Reference Documentation:**
If you need assistance or technical reference details at any stage of the project, refer to the following developer and setup guides located in the `/docs/` directory:

*   **[Milestone 0: Hardware Verification Guide](assignments/submission0_milestone0_verification.md):** A step-by-step guide to confirm your physical build is functional, test sensors, and verify telemetry connections.
*   **[Python Track Quickstart](getting_started_python.md):** Walks you through setting up Python environment, flashing MicroPython, and writing scripts.
*   **[Simulink Track Quickstart](getting_started_simulink.md):** Walks you through MATLAB paths, visual co-simulation, and code generation.
*   **[Kernel & API Developer Guide](kernel_api_guide.md):** The primary reference for the high-level Python API (`uct_mouse` module) methods, OLED display configurations, and line sensor bindings.
*   **[Simulink Development & Autograding Guide](simulink_guide.md):** Covers Simulink template path setups, C-Coder compilation hooks, and automatic Pygame co-simulation socket mappings.
*   **[Hardware Setup & Calibration Guide](hardware_setup.md):** Contains DC motor wiring diagrams, battery switch details, sensor alternate-function pins, and processor clock-speed Sweeping diagnostics.

---

## **2. Development Tracks & Language Choices**

You may choose to implement your algorithms using either of the following two development options. The evaluation criteria are identical for both:

### **Option A: The Python Track**
* Write high-level control code in Python.
* Your scripts run natively on the physical mouse's internal interpreter or interact with the virtual maze simulator using the `uct_mouse` wrapper library.
* *Primary Entry Point:* `python/main.py`.

### **Option B: The Simulink Track**
* Model your algorithms visually using MATLAB, Simulink, and Stateflow.
* Use the Embedded Coder toolbox to compile your models into binary images that run natively on the STM32 processor.
* *Primary Model Template:* `matlab/simulink/StudentTemplate.slx`.

---

## **3. GA3 Design Project Reports**
For each of your two GA3 Design Reports, you must identify and document a structured engineering design process for a chosen subsystem of your choice related to the Micromouse. 

Consistent with the professional engineering standard, this selection is completely **open-ended and non-prescriptive**. You may choose any task for which you can confidently present evidence of design thinking.

Illustrative, non-prescriptive examples of design topics include:

* **Stream A (Control & Estimation):** Designing and tuning a discrete PID velocity controller; fusing gyroscope yaw and encoders; or modeling motor parameter identification dynamics.
* **Stream B (Interface & Systems Engineering):** Designing a visual Blockly block library and web-app generator; implementing high-level API safety wrappers; or coding automated hardware self-test calibrators.

---

## **4. Repository & Workspace Structure**

To facilitate updates to the core repository without overwriting your progress, the project workspace is partitioned:

* **Cloning the Workspace:** To clone this repository with all required microcontroller submodules, run this command in your terminal:
  ```bash
  git clone --depth=1 --recursive https://github.com/nicollsf/UCT-Micromouse.git
  ```
*(Note: Using a shallow clone with `--depth=1` is highly recommended to speed up download times and avoid fetching massive historical commit histories for submodules.)*

  If you have already cloned the repository without the submodules, initialize them using:
  ```bash
  git submodule update --init --recursive
  ```
* **Your Sandbox (`/workspace/`):** Put all your Python scripts, custom packages, libraries, and Simulink `.slx` files inside the `/workspace/` directory at the project root. This directory is ignored by Git, meaning your code remains safe and untracked when pulling repository updates.
* **The Deployer Tool (`tools/deploy.py`):** Use this script to copy your local Python files and custom package directories onto the physical mouse's internal drive:
  ```bash
  python tools/deploy.py --script workspace/my_task/main.py
  ```
* **The Simulator Testbed:** You can test your controller code locally on your laptop before deploying to the physical mouse. Run the visual simulation testbed to evaluate your algorithms against virtual mazes:
  ```bash
  python tools/physics_sim.py
  ```
* **Simulation Stress-Testing (Perturbations):** To verify that you are using active feedback control (speed matching and gyro heading alignment) rather than hardcoded open-loop delays, the autograder executes your code in co-simulation under randomized perturbations, including:
  * **Motor Asymmetry:** Left/right motor gain offsets (up to $\pm 10\%$).
  * **Wheel Slip / Traction Loss:** Simulated tire slippage to penalize pure time-based dead reckoning.

---

## **5. Chronological Submissions & Detailed Assessment Rubrics**

To satisfy the ECSA Graduate Attribute 3 (Design) accreditation portfolio, you must complete **four primary graded submissions** (and one initial build prerequisite) in chronological order:

### **Prerequisite: Milestone 0 Build Verification (0%)**
*   **Task:** Complete the physical assembly of your mouse, power on the board, and verify that the sensors, motors, encoders, and live telemetry are fully functioning.
*   **Verification:** Run the telemetry extraction utility (`python tools/dump_logs.py`) and confirm telemetry logs can be retrieved over the serial interface. Refer to the [Milestone 0: Hardware Verification Guide](assignments/submission0_milestone0_verification.md) for detailed instructions.

### **Submission 1: Milestone 1 Code & Demo (25%)**
*   **Task:** Drive a closed loop: drive 1.0m straight, turn 90° left (anticlockwise), and repeat this 4 times to form a 1.0m x 1.0m square, then stop autonomously.
*   **Assessment & Grading Metric:** The milestone mark is split as **60% Autograded Trajectory**, **30% Tutor Physical Run Evaluation**, and **10% Submission Compliance** (proper files and student card shown). 
    *   *Autograder Score (100 pts max):* Checked in co-simulation across multiple test cases (public baseline and hidden stress tests). Completes automatically when the mouse stops for 3.0s:
        *   **Leg Segments (30 pts max):** 7.5 pts per leg (East, North, West, South). Split equally between length accuracy ($\pm 5\text{ cm}$ tolerance) and straightness ($2\text{ cm}$ lateral deviation margin).
        *   **Corner Turn Angles (30 pts max):** 7.5 pts per corner. Evaluates orientation change accuracy relative to $90.0^\circ$ ($\pm 3^\circ$ tolerance).
        *   **Parking Accuracy (20 pts max):** Distance between final resting spot and start point. Full points if $\le 3\text{ cm}$, scaling to 0 at $\ge 25\text{ cm}$.
        *   **Run Speed Efficiency (10 pts max):** Full points if time $\le 20\text{s}$, scaling to 0 at $\ge 40\text{s}$.
        *   **Safety Bonus (10 pts):** Flat bonus if the run completes without colliding with virtual walls.
        *   *Completion Requirement:* The mouse must execute exactly **4 forward drives and 4 turns** to end on the starting tile facing the original heading, and then remain stopped for **at least 3.0s** to trigger autograding evaluation.
    *   *Physical Run (30%):* Tutor evaluation of video run performance, turning accuracy, and floor stability.
    *   *Compliance (10%):* Legible 3s student card close-up (5%) and code-telemetry log zip formatting (5%).

### **Submission 2: GA3 Design Report 1 (20%)**
*   **Task:** Submit a formal engineering design report (in PDF format) documenting your closed-loop feedback controller, velocity synchronization, or heading alignment designs from Milestone 1.
*   **Template:** Follow the formatting rules and character limits in [gareport_guidelines.md](assignments/gareport_guidelines.md) and the template in [EEE3097_8_9S_designreport.docx](assignments/EEE3097_8_9S_designreport.docx).
*   **Assessment & Passing Criteria:** Evaluated against the ECSA GA3 Design rubric. Must demonstrate a structured design brief (3.1), alternative evaluations (3.2), and first-principles modeling (3.3).

### **Submission 3: GA3 Design Report 2 (30%)**
*   **Task:** A second formal engineering design report (submitted directly via the **Gradescope Online Assignment** interface) documenting your sensor filters, mapping state flows, routing pathfinders, or visual programming interfaces from Milestone 2.
*   **Assessment & Passing Criteria:** Evaluated against the ECSA GA3 Design rubric. Must demonstrate implementation testing (3.4) and critical evaluation (3.5). One resubmission of this report is permitted if required to demonstrate Graduate Attribute competence.

### **Submission 4: Final Maze Solver Code & Demo (25%)**
*   **Task:** Navigate a virtual/physical mouse through the 4-stage autonomous mission (*Explore & Discover 2x2 Target Room $\rightarrow 360^\circ$ Recognition Pirouette $\rightarrow$ Return to Start `(0,0)` $\rightarrow$ High-Speed Solving Sprint*).
*   **Final Week Micromouse Championship:** In the final week of the course, we will host a live competition on a **larger competition maze (e.g. 8x8 or 10x10)** using the exact same 4-stage mission rules. Design your code to dynamically parameterize grid dimensions (`MAZE_ROWS`, `MAZE_COLS`) rather than hardcoding to 4x6!
*   **Assessment & Grading Metric:** The milestone mark is split as **60% Autograded Trajectory**, **30% Tutor Physical Run Evaluation**, and **10% Submission Compliance** (proper files and student card shown).
    *   *Autograder Score (100 pts max):* Checked in procedurally generated 4x6 virtual mazes under physical perturbations:
        *   **Target Room Discovery (30 pts):** Successfully navigating into the 2x2 target room during exploration.
        *   **Recognition Pirouette (20 pts):** Executing the $360^\circ$ clockwise spin inside the target room.
        *   **Return to Start (20 pts):** Navigating back and stopping at starting cell `(0,0)`.
        *   **High-Speed Sprint (20 pts):** Sprinting from `(0,0)` directly back into the target room.
        *   **Speed Run Bonus (10 pts):** Scales continuously based on total elapsed mission time ($\le 25\text{s} = 10\text{ pts}$, $25\text{s} < t \le 90\text{s} = 10 \rightarrow 0\text{ pts}$).
        *   *Penalties:* -10 pts for timeout (90s limit); Wall contact immediately halts the simulation.
    *   *Physical Run (30%):* Tutor evaluation of the 4-stage mission on the physical 4x6 board.
    *   *Compliance (10%):* Legible 3s student card close-up (5%) and code-telemetry log zip formatting (5%).

*   *Note on Grading Thresholds:* The grading thresholds, coefficients, and parameter metrics detailed in this handbook serve as baseline targets. Course staff reserve the right to tailor or adjust specific parameters post-submission to ensure final grades remain highly representative of actual design and hardware performance.


---

## **6. Telemetry Logs & Academic Honesty**

Your grades are verified through physical run telemetry logs and video evidence:

* **Single-Cable Connection & Safety:** Connect the USB cable ONLY to the **ST-Link debugger USB port** (the same port used for flashing code). You do not need to swap cables or connect to the processor OTG port. **WARNING: AVOID PLUGGING IN ANY MORE THAN ONE USB CABLE AT A TIME (e.g. power board, processor board, and ST-Link simultaneously) to protect your hardware from damage.**
* **Log Extraction:** Extract the log from your physical mouse by running:
  ```bash
  python tools/dump_logs.py
  ```
  This saves the output file as `run_log.jsonl` in your folder.
* **Authenticity Verification (Anti-Cheat):**
  * **Device UID:** The log records your microcontroller's unique Device UID. The course convenors check the submitted logs retrospectively. Logs containing identical UIDs under different student accounts are flagged for plagiarism review.
  * **Code FNV-1a Checksum:** The log contains an FNV-1a checksum hash computed in hardware representing the code loaded onto the board. The autograder compiles your submitted script/model locally and verifies that the resulting hash matches the log header. Mismatched hashes will result in an immediate submission rejection.
* **Student Card Video Declaration:** Every validation video must start with a **3-second close-up of your physical Student Card** to serve as your formal academic honesty declaration.

---

## **7. Project Licensing**

This handbook is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.
To view a copy of this license, visit [http://creativecommons.org/licenses/by/4.0/](http://creativecommons.org/licenses/by/4.0/).

