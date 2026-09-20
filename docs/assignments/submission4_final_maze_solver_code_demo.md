# EEE3097/8/9S Micromouse 2026: Submission 4
## Final Maze Solver Code & Demo (25% of Course Mark)

---

### 1. Objective
Design and implement the complete autonomous intelligence for your Micromouse. The robot must explore a **4x6 grid maze** ($0.8\text{ m} \times 1.2\text{ m}$) to discover its wall layout, identify the **2x2 open target room**, confirm target acquisition with a **$360^\circ$ victory pirouette**, calculate the optimal shortest path back to the starting cell `(0,0)`, and execute a high-speed "solving sprint" directly to the target.

#### **Specific Learning Objectives:**
* Interfacing with three VL53L0X Time-of-Flight (ToF) sensors and calibrating wall detection thresholds.
* Fusing high-resolution wheel encoders with the gyroscope yaw rate to track coordinate state $(x, y)$ and heading orientation.
* Implementing dynamic topological exploration state machines (e.g. Floodfill or Depth-First Search).
* Implementing online feature recognition to detect the 2x2 open target room (missing interior cross-walls).
* Implementing shortest-path planning solvers (e.g., A*, Dijkstra, or BFS) to calculate optimal routing.
* Tuning continuous velocity profiles (accelerations, corner deceleration limits) to merge consecutive straight segments during the speed sprint.

---

### 2. The 4-Stage Autonomous Mission: "Search, Celebrate & Sprint"

```text
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  Phase 1: Exploration   │ ──► │  Target Acknowledgment  │ ──► │   Phase 2: Return Run   │
│ (Explore from (0,0) and │     │ (Execute a 360° spin in │     │ (Compute shortest path  │
│  detect 2x2 target room)│     │  the 2x2 target plaza)  │     │  and navigate to (0,0)) │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
                                                                             │
                                                                             ▼
                                                                ┌─────────────────────────┐
                                                                │  Phase 3: Speed Sprint  │
                                                                │ (Pause 3s at start, then│
                                                                │  sprint fast to target) │
                                                                └─────────────────────────┘
```

#### **Phase 1: Autonomous Exploration & Mapping (Start at `(0,0)`)**
* Place your mouse in starting cell `(0,0)` facing North.
* The mouse must autonomously explore the 4x6 maze. As it enters each cell, it reads its ToF sensors, classifies wall presence, updates its internal map matrix, and applies active side-wall centering.
* **Target Feature Discovery:** The target is a **2x2 block of contiguous cells with all internal dividing walls removed**. The target location is not fixed and must be dynamically discovered through your wall map.

#### **Phase 2: Target Recognition Handshake ($360^\circ$ Pirouette)**
* Upon entering the 2x2 open target room, the mouse must **halt and execute an on-the-spot $360^\circ$ clockwise pirouette** using integrated gyro feedback. This provides clear, unambiguous confirmation to the autograder and tutors that the robot recognized the target zone.

#### **Phase 3: Autonomous Return-to-Start**
* Using its discovered topological map, the mouse calculates the shortest path from the target room back to starting cell `(0,0)`.
* It traverses back to `(0,0)`, turns to face North, and halts.

#### **Phase 4: High-Speed Solving Sprint**
* The mouse pauses at `(0,0)` for **3.0 seconds** to reset its state.
* It executes a high-speed sprint along the optimal path directly into the target zone, merging straight corridors into continuous acceleration-cruise-deceleration profiles.
* The mission completes when the mouse comes to a full stop inside the target room.

---

### 3. Final Week Micromouse Championship Competition

> [!IMPORTANT]
> **Final Week Live Championship Tournament:**
> In the final week of the course, we will host the live **2026 EEE3097S Micromouse Championship Competition**!
> * **The Challenge:** Robots will compete under the exact same 4-stage mission rules (*Search $\rightarrow 360^\circ$ Pirouette $\rightarrow$ Return $\rightarrow$ Sprint*), but on a **larger competition maze (e.g. 8x8 or 10x10)**!
> * **Design for Scalability:** Do **NOT** hardcode your code to 4x6 grid dimensions or fixed coordinates. Ensure your `MazeSolver` class dynamically parameterizes grid dimensions (`MAZE_ROWS`, `MAZE_COLS`) and relies strictly on dynamic topological wall discovery.

---

### 4. Deliverables (Gradescope Submission)
To package your final submission, run the following command from your repository root:
```bash
python tools/package_submission.py --task final_demo --src workspace/final_task/
```
This script will perform dynamic syntax and formatting checks and generate a single **`submission_final_demo.zip`** in your project root. Upload this ZIP AND your **`run_video.mp4`** separately to Gradescope (Gradescope allows you to drag-and-drop both files into the submission portal together).

The submission consists of:
1. **Your ZIP Package (`submission_final_demo.zip`):**
   * **Your Solving Code:** Automatically compiled and zipped from your workspace directory (includes `main.py` and any subfolders/libraries recursively).
   * **Physical Telemetry Log (`run_log.jsonl`):** Automatically detected by the packager tool from your project directory (no need to copy it manually).
2. **Your Physical Run Video (`run_video.mp4`):**
   * Uploaded as a **separate file** alongside your ZIP. The video must start with a **3-second close-up of your Student Card** followed by the uncut mapping and high-speed solving runs.

#### **Testing the Autograder Offline (Locally)**
You are highly encouraged to test your algorithm against the grading suite locally on your laptop before uploading to Gradescope. To run the full multi-test evaluation suite locally, run this command from the repository root:
```bash
python tools/autograder/grade_runner.py
```

---

### 5. Hardware vs. Simulation Parity & System Identification

> [!IMPORTANT]
> **Why Open-Loop Timing Fails:**
> If you attempt to solve the maze using fixed time delays (e.g. `set_motors(70, 70); delay_ms(1200)` to travel 1 cell), your code will fail on both physical hardware and simulation.
> * **Physical Hardware:** Experiences battery voltage decay ($8.4\text{V} \rightarrow 7.0\text{V}$), caster stiction, motor cogging, and wheel slip.
> * **Simulation Engine:** Injects motor deadband thresholds ($58–62\text{ PWM}$), gain asymmetry ($\pm 8\%$), transient starting slip, and IMU noise.
> * **The Solution:** Use **closed-loop feedback control**! Your mouse must compute displacement from wheel encoders, integrate yaw heading from the gyroscope, and continuously regulate side-wall centering errors using ToF range measurements. A robust closed-loop controller performs identically on physical silicon and in simulation.

#### **Optional: Submitting Identified Chassis Dynamics (`sim_config.json`)**
As part of senior engineering design and system identification, you may optionally include a custom **`sim_config.json`** file in your workspace. When submitted, the Gradescope simulator will load your identified chassis parameters (e.g. measured wheel radius $R$, track width $L$, deadbands, and gear ticks-per-rev) to evaluate your simulation run:
```json
{
  "robot": {
    "axle_half_length": 0.054,
    "wheel_radius": 0.0325,
    "ticks_per_rot": 1170.0
  },
  "motor": {
    "dead_band_l": 58.0,
    "dead_band_r": 62.0
  }
}
```
*Note: The physical microcontroller ignores `sim_config.json` and runs your closed-loop feedback code directly.*

---

### 6. Video Requirements & Academic Honesty Declaration
To verify that your physical run is authentic, the video must strictly adhere to the following sequence:
1. **Student Card Close-up:** The video **MUST start with a clear, readable close-up of your physical Student Card** for at least 3 seconds (declaring this is your own work).
2. **Setup:** Show the mouse positioned at starting cell `(0,0)`.
3. **Traversals:** Capture the full uncut sequence: Phase 1 mapping, $360^\circ$ target pirouette, return to `(0,0)`, 3-second pause, and final high-speed sprint to the target room.

---

### 7. Code & Log Correlation Verification (Anti-Cheat Check)
* **Hardware ID Check:** The `"uid"` field represents your microcontroller's unique device ID. While this is not registered in advance, the course convenors check the submitted logs for duplicate UIDs. Submitting logs with identical UIDs under different student accounts indicates shared files/hardware runs and will trigger a plagiarism audit.
* **Code Match Check:** The autograder compiles and computes an FNV-1a checksum hash of your submitted code and matches it against the `"hash"` field in your telemetry header. **Mismatched hashes will result in an immediate submission rejection.**

---

### 8. Evaluation Criteria & Grading Rubric
Your Gradescope submission is evaluated across three parts:

* **Part A: Co-Simulation Speed & Accuracy (60% of Milestone Mark):**
  Your solver is tested in procedurally generated 4x6 virtual mazes under realistic physical perturbations ($8\%$ motor asymmetry, $2\%$ wheel slip). The simulation runs up to a **90-second limit**.
  
  The autograder score is calculated out of 100 points as follows:
  * **Target Room Discovery (30 points):** Awarded for navigating into the 2x2 target room during exploration.
  * **Recognition Pirouette (20 points):** Awarded for executing the $360^\circ$ clockwise spin inside the target room.
  * **Autonomous Return-to-Start (20 points):** Awarded for navigating back and stopping inside starting cell `(0,0)`.
  * **High-Speed Solving Sprint (20 points):** Awarded for sprinting from `(0,0)` directly back into the target room.
  * **Total Time Speed Bonus (10 points):** Scales continuously based on total elapsed mission time ($\le 25\text{s} = 10\text{ pts}$, $25\text{s} < t \le 90\text{s} = 10 \rightarrow 0\text{ pts}$).
  * **Applied Penalties:**
    * **Timeout Penalty ($-10$ points):** Subtracted if the mission exceeds the 90-second limit.
    * *Collision Note:* Contacting a wall halts the simulation immediately, capping the score at the milestones achieved prior to the crash.

* **Part B: Physical Run Verification (30% of Milestone Mark):**
  Tutors evaluate your submitted physical demonstration video (`run_video.mp4`) against the 4-stage mission: active wall-centering, mapping reliability, $360^\circ$ recognition pirouette, return-to-start navigation, and high-speed sprint.

* **Part C: Submission Compliance (10% of Milestone Mark):**
  * **All Files Included (5%):** Correct zipping of source code workspace and valid FNV-1a checksum matched physical telemetry log file (`run_log.jsonl`).
  * **Student Card Close-up (5%):** The physical demo video begins with a clear, readable 3-second close-up of your Student Card.

---

> [!NOTE]
> **Grading Adaptation Policy:** The grading thresholds, coefficients, and parameters detailed above serve as baseline targets. Course staff reserve the right to adjust or tailor specific parameters post-submission to ensure final grades are highly representative of actual design and hardware performance.
