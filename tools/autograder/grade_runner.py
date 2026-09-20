#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import json
import signal
import glob
import importlib.util
import shutil
import tempfile

# 1. Path Resolution
if os.path.exists("/autograder"):
    SUBMISSION_DIR = "/autograder/submission"
    RESULTS_FILE = "/autograder/results/results.json"
    SOURCE_DIR = "/autograder/source"
    VIDEO_PATH = "/autograder/results/run.mp4"
    TRAJECTORY_JSON = os.path.join(tempfile.gettempdir(), "trajectory.json")
else:
    # Local mock mode
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    SUBMISSION_DIR = os.path.join(base_dir, "python")  # mock submission is the local python dir
    RESULTS_FILE = os.path.join(base_dir, "tools", "autograder", "results.json")
    SOURCE_DIR = os.path.join(base_dir, "tools", "autograder")
    VIDEO_PATH = os.path.join(base_dir, "tools", "autograder", "run.mp4")
    TRAJECTORY_JSON = os.path.join(base_dir, "tools", "autograder", "trajectory.json")

def write_results(score, feedback, test_name="Autograder Evaluation"):
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    results = {
        "score": score,
        "max_score": 100.0,
        "output": feedback,
        "visibility": "visible",
        "tests": [
            {
                "name": test_name,
                "score": score,
                "max_score": 100.0,
                "output": feedback,
                "visibility": "visible"
            }
        ]
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[Grader] Results written to {RESULTS_FILE} with score {score}")

def generate_trajectory_svg(trajectory_file):
    try:
        if not trajectory_file or not os.path.exists(trajectory_file):
            return ""
        with open(trajectory_file, "r") as f:
            data = json.load(f)
        traj = data.get("trajectory", [])
        if not traj or len(traj) < 2:
            return ""
        
        # Bounding coordinates
        xs = [pt[0] for pt in traj] + [0.0, 1.0]
        ys = [pt[1] for pt in traj] + [0.0, 1.0]
        min_x, max_x = min(xs) - 0.15, max(xs) + 0.15
        min_y, max_y = min(ys) - 0.15, max(ys) + 0.15
        span_x = max(max_x - min_x, 0.5)
        span_y = max(max_y - min_y, 0.5)
        
        w, h = 450, 450
        def to_svg(x, y):
            sx = (x - min_x) / span_x * (w - 70) + 35
            sy = h - ((y - min_y) / span_y * (h - 70) + 35)
            return sx, sy
        
        pts = [to_svg(pt[0], pt[1]) for pt in traj]
        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        
        ideal = [to_svg(0,0), to_svg(1,0), to_svg(1,1), to_svg(0,1), to_svg(0,0)]
        ideal_poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in ideal)
        
        start_x, start_y = to_svg(traj[0][0], traj[0][1])
        end_x, end_y = to_svg(traj[-1][0], traj[-1][1])
        
        svg = f'''<div style="margin: 15px 0;">
  <h4 style="margin-bottom: 8px; color: #fff;">📊 Recorded Trajectory Map:</h4>
  <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="background:#181818; border:1px solid #444; border-radius:6px; max-width: 100%; height: auto;">
    <rect width="100%" height="100%" fill="#181818"/>
    <!-- Grid Marks -->
    <line x1="35" y1="15" x2="35" y2="{h-15}" stroke="#2a2a2a" stroke-width="1"/>
    <line x1="15" y1="{h-35}" x2="{w-15}" y2="{h-35}" stroke="#2a2a2a" stroke-width="1"/>
    <!-- Ideal Square Reference -->
    <polyline points="{ideal_poly}" fill="none" stroke="#666666" stroke-width="2" stroke-dasharray="5,5"/>
    <!-- Actual Mouse Trajectory -->
    <polyline points="{polyline}" fill="none" stroke="#00b4d8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- Start & End Markers -->
    <circle cx="{start_x:.1f}" cy="{start_y:.1f}" r="5" fill="#2ec4b6" stroke="#fff" stroke-width="1.5"/>
    <circle cx="{end_x:.1f}" cy="{end_y:.1f}" r="5" fill="#e71d36" stroke="#fff" stroke-width="1.5"/>
    <text x="{start_x+8:.1f}" y="{start_y+4:.1f}" fill="#2ec4b6" font-size="11" font-family="sans-serif" font-weight="bold">Start (0,0)</text>
    <text x="{end_x+8:.1f}" y="{end_y+4:.1f}" fill="#e71d36" font-size="11" font-family="sans-serif" font-weight="bold">End ({traj[-1][0]:.2f}, {traj[-1][1]:.2f})</text>
    <!-- Legend -->
    <text x="45" y="30" fill="#888888" font-size="10" font-family="sans-serif">--- Ideal Square (1m x 1m)</text>
    <text x="45" y="45" fill="#00b4d8" font-size="10" font-family="sans-serif">── Actual Trajectory</text>
  </svg>
</div>'''
        return svg
    except Exception:
        return ""

def get_video_html(video_path):
    if not video_path or not os.path.exists(video_path):
        return ""
    try:
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if size_mb > 25.0:  # Avoid excessive payload in Gradescope
            return ""
        import base64
        with open(video_path, "rb") as vf:
            b64_data = base64.b64encode(vf.read()).decode("utf-8")
        return f'''<div style="margin: 15px 0;">
  <h4 style="margin-bottom: 8px; color: #fff;">🎬 Simulation Run Playback Video:</h4>
  <video width="480" height="480" controls autoplay loop muted style="max-width: 100%; height: auto; border: 1px solid #444; border-radius: 6px; background: #000;">
    <source src="data:video/mp4;base64,{b64_data}" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</div>'''
    except Exception:
        return ""

def load_test_suite(assignment_name):
    suite_path = os.path.join(SOURCE_DIR, "assignments", assignment_name, "test_suite.py")
    if not os.path.exists(suite_path):
        # Local fallback if directory structured differently
        suite_path = os.path.join(os.path.dirname(__file__), "assignments", assignment_name, "test_suite.py")
        
    if not os.path.exists(suite_path):
        raise FileNotFoundError(f"Test suite not found at {suite_path}")
        
    spec = importlib.util.spec_from_file_location("test_suite", suite_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    print("=== UCT Micromouse Gradescope Autograder Runner ===")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    global SUBMISSION_DIR, RESULTS_FILE
    import argparse
    parser = argparse.ArgumentParser(description="Gradescope Autograder Runner")
    parser.add_argument("--submission", type=str, default=None, help="Submission directory")
    parser.add_argument("--results", type=str, default=None, help="Results output file path")
    args, _ = parser.parse_known_args()
    
    if args.submission:
        SUBMISSION_DIR = os.path.abspath(args.submission)
        print(f"[Grader] Overridden SUBMISSION_DIR: {SUBMISSION_DIR}")
    
    if args.results:
        RESULTS_FILE = os.path.abspath(args.results)
        print(f"[Grader] Overridden RESULTS_FILE: {RESULTS_FILE}")
    
    # 2. Find active assignment config
    active_assignment_file = os.path.join(SOURCE_DIR, "active_assignment.txt")
    if not os.path.exists(active_assignment_file):
        # Local fallback
        active_assignment_file = os.path.join(os.path.dirname(__file__), "active_assignment.txt")
        
    if os.path.exists(active_assignment_file):
        with open(active_assignment_file, "r") as f:
            assignment_name = f.read().strip()
    else:
        assignment_name = "milestone1" # default fallback
        
    print(f"[Grader] Active assignment: {assignment_name}")

    # Dynamically resolve default submission folder to workspace folders if not overridden
    if not args.submission:
        assignment_workspaces = {
            "milestone1_square": os.path.join(repo_root, "workspace", "task1_square"),
            "milestone2_maze": os.path.join(repo_root, "workspace", "task2_maze"),
            "final_demo": os.path.join(repo_root, "workspace", "final_task")
        }
        fallback_dir = assignment_workspaces.get(assignment_name)
        if fallback_dir and os.path.exists(fallback_dir):
            SUBMISSION_DIR = fallback_dir
            print(f"[Grader] Default SUBMISSION_DIR resolved to active workspace: {SUBMISSION_DIR}")
        else:
            print(f"[Grader] Default SUBMISSION_DIR resolved to: {SUBMISSION_DIR}")
    
    try:
        test_suite = load_test_suite(assignment_name)
    except Exception as e:
        write_results(0.0, f"System Error: Failed to load test suite for assignment '{assignment_name}': {e}")
        return

    # Early exit for Milestone 0 (log submission only, no simulator needed)
    if assignment_name == "milestone0_verification":
        print("[Grader] Milestone 0 log evaluation track detected.")
        try:
            log_path = os.path.join(SUBMISSION_DIR, "run_log.jsonl")
            if not os.path.exists(log_path):
                # Scan for any .jsonl file in the submission folder as fallback
                candidates = glob.glob(os.path.join(SUBMISSION_DIR, "*.jsonl"))
                if candidates:
                    log_path = candidates[0]
            score, feedback = test_suite.evaluate_log(log_path)
            write_results(score, feedback, "Milestone 0 Evaluation")
        except Exception as e:
            write_results(0.0, f"Grading Error: Failed to evaluate log submission: {e}", "Milestone 0 Evaluation")
        return

    # 3. Detect submission track (Simulink vs Python)
    print(f"[Grader] Scanning submission directory: {SUBMISSION_DIR}")
    
    # Clean up any student-submitted uct_mouse.py or micromouse.py files to prevent shadowing of the grader's corrected libraries
    for root, dirs, files in os.walk(SUBMISSION_DIR):
        for f in files:
            if f in ["uct_mouse.py", "micromouse.py"]:
                target_path = os.path.join(root, f)
                print(f"[Grader] Cleaning up student-submitted framework override: {target_path}")
                try:
                    os.remove(target_path)
                except Exception as e:
                    print(f"[Grader] Warning: Failed to remove {target_path}: {e}")

    # Check for Simulink track by looking for any folder ending in _ert_rtw
    ert_dirs = []
    for root, dirs, files in os.walk(SUBMISSION_DIR):
        for d in dirs:
            if d.endswith("_ert_rtw"):
                ert_dirs.append(os.path.join(root, d))
                
    track = None
    model_dir = None
    model_name = None
    main_file = None
    
    if ert_dirs:
        # Prefer UCT_KDeploy_ert_rtw if multiple
        target_dir = None
        for d in ert_dirs:
            if os.path.basename(d) == "UCT_KDeploy_ert_rtw":
                target_dir = d
                break
        if not target_dir:
            target_dir = ert_dirs[0]
            
        track = "simulink"
        model_dir = target_dir
        model_name = os.path.basename(target_dir)[:-8]  # Strip '_ert_rtw'
        print(f"[Grader] Track detected: Simulink")
        print(f"[Grader] Found code generation folder: {model_dir}")
        print(f"[Grader] Model name: {model_name}")
    else:
        # Check for Python track by looking for <assignment_name>.py or main.py
        main_candidates = []
        target_name = f"{assignment_name}.py"
        
        for root, dirs, files in os.walk(SUBMISSION_DIR):
            if target_name in files:
                main_candidates.append(os.path.join(root, target_name))
            if "main.py" in files:
                main_candidates.append(os.path.join(root, "main.py"))
                
        if main_candidates:
            target_main = None
            
            # 1. Prioritize files named exactly <assignment_name>.py
            for p in main_candidates:
                if os.path.basename(p) == target_name:
                    target_main = p
                    break
                    
            # 2. Prioritize files in a folder named after the active assignment (e.g., milestone1/)
            if not target_main:
                for p in main_candidates:
                    path_parts = p.split(os.sep)
                    if assignment_name in path_parts or any(assignment_name in part for part in path_parts):
                        target_main = p
                        break
                        
            # 3. Prioritize files under python/ directory
            if not target_main:
                for p in main_candidates:
                    if "/python/" in p or p.endswith("python/main.py"):
                        target_main = p
                        break
                        
            # 4. Fallback
            if not target_main:
                target_main = main_candidates[0]
                
            track = "python"
            main_file = target_main
            print(f"[Grader] Track detected: Python")
            print(f"[Grader] Found entry point: {main_file}")
        else:
            write_results(0.0, f"Submission Error: Neither a Simulink code generation folder (*_ert_rtw), a Python entry point ({target_name}), nor a standard 'main.py' was found in your submission.")
            return

    # 4. Compilation if Simulink track
    client_bin = os.path.join(tempfile.gettempdir(), "simulink_client")
    if track == "simulink":
        print("[Grader] Compiling Simulink deployment code...")
        
        # Locate wrapper files in SOURCE_DIR
        pc_main = os.path.join(SOURCE_DIR, "PC_client_main.c")
        sim_wrapper = os.path.join(SOURCE_DIR, "simulink_wrapper.c")
        sim_header = os.path.join(SOURCE_DIR, "simulink_wrapper.h")
        
        # Verify wrapper files exist (if not in SOURCE_DIR, fallback to repo paths)
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if not os.path.exists(pc_main):
            pc_main = os.path.join(repo_root, "matlab", "simulink", "PC_client_main.c")
        if not os.path.exists(sim_wrapper):
            sim_wrapper = os.path.join(repo_root, "firmware", "src", "kernel", "src", "simulink_wrapper.c")
        if not os.path.exists(sim_header):
            sim_header = os.path.join(repo_root, "firmware", "src", "kernel", "inc", "simulink_wrapper.h")
            
        if not os.path.exists(pc_main) or not os.path.exists(sim_wrapper):
            write_results(0.0, "System Error: Missing standalone main client or simulink wrappers in autograder package.")
            return
            
        # Find all generated sources in model directory (exclude ert_main.c)
        model_sources = glob.glob(os.path.join(model_dir, "*.c"))
        model_sources = [f for f in model_sources if os.path.basename(f) != "ert_main.c"]
        
        all_sources = [pc_main, sim_wrapper] + model_sources
        
        # Choose compiler
        compiler = shutil.which("gcc") or shutil.which("clang")
        if not compiler:
            write_results(0.0, "System Error: No suitable C compiler (gcc or clang) found in the autograder environment.")
            return
            
        # Build compile command
        cmd = [
            compiler,
            "-O2",
            f"-DMODEL_NAME={model_name}",
            f"-I{model_dir}",
            f"-I{os.path.dirname(sim_header)}", # wrapper header folder
            f"-I{SOURCE_DIR}" # also include source dir
        ]
        cmd.extend(all_sources)
        cmd.extend(["-o", client_bin, "-lm"])
        
        print(f"[Grader] Compiler command: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30.0)
            if res.returncode != 0:
                feedback = (
                    f"Compilation Error: Your Simulink generated C code failed to compile.\n\n"
                    f"--- Compiler Output (stdout) ---\n{res.stdout}\n\n"
                    f"--- Compiler Error (stderr) ---\n{res.stderr}"
                )
                write_results(0.0, feedback, "Compilation Check")
                return
            print("[Grader] Compilation succeeded.")
        except subprocess.TimeoutExpired:
            write_results(0.0, "Compilation Error: C compilation process timed out after 30 seconds.", "Compilation Check")
            return
        except Exception as e:
            write_results(0.0, f"Compilation Error: Failed to invoke compiler: {e}", "Compilation Check")
            return

    # 5. Execute Multi-Run Simulation Tests
    test_runs = getattr(test_suite, "TEST_RUNS", [("Standard Run", 1.0, 0.08, 0.08, False)])
    
    sim_script = os.path.join(SOURCE_DIR, "physics_sim.py")
    if not os.path.exists(sim_script):
        sim_script = os.path.join(repo_root, "tools", "physics_sim.py")
    if not os.path.exists(sim_script):
        sim_script = os.path.join(os.path.dirname(__file__), "..", "physics_sim.py")
    if not os.path.exists(sim_script):
        write_results(0.0, f"System Error: Simulator backend script 'physics_sim.py' not found (looked in {SOURCE_DIR}, {repo_root}/tools).")
        return
        
    # Check for student-submitted dynamic simulation config (sim_config.json)
    student_config = None
    for candidate in ["sim_config.json", "simulation_config.json"]:
        p = os.path.join(SUBMISSION_DIR, candidate)
        if os.path.exists(p):
            student_config = p
            print(f"[Grader] Discovered Student Identified Simulation Config: {student_config}")
            break

    total_score = 0.0
    gradescope_tests = []
    
    for idx, (run_name, weight, imb_val, slip_val, is_hidden) in enumerate(test_runs):
        print(f"\n[Grader] === Executing {run_name} (Weight: {weight*100:.0f}%, Imbalance: {imb_val}, Slip: {slip_val}) ===")
        
        sim_cmd = [
            sys.executable,
            "-u",
            sim_script,
            "--headless",
            "--map", getattr(test_suite, "MAP", "empty"),
            "--imbalance", str(imb_val),
            "--slip", str(slip_val),
            "--json-log", TRAJECTORY_JSON,
            "--video", VIDEO_PATH if idx == 0 else "", # only record video for first run
            "--max-time", str(getattr(test_suite, "TIME_LIMIT", 45.0)),
            "--seed", str(getattr(test_suite, "SEED", 42) + idx)
        ]
        if student_config:
            sim_cmd.extend(["--config", student_config])
        
        # Clean up old trajectory file
        if os.path.exists(TRAJECTORY_JSON):
            try:
                os.remove(TRAJECTORY_JSON)
            except Exception:
                pass
                
        sim_log_path = os.path.join(tempfile.gettempdir(), "simulator_backend.log")
        if os.path.exists(sim_log_path):
            try:
                os.remove(sim_log_path)
            except Exception:
                pass
                
        try:
            sim_log_file = open(sim_log_path, "w")
            sim_proc = subprocess.Popen(
                sim_cmd,
                stdout=sim_log_file,
                stderr=sim_log_file,
                text=True
            )
            sim_log_file.close()
        except Exception as e:
            write_results(0.0, f"System Error: Failed to start simulation backend: {e}")
            return
            
        # Wait for simulator readiness (increased timeout to 20s for slow/cold container boot)
        simulator_ready = False
        exited_early = False
        start_wait = time.time()
        while time.time() - start_wait < 20.0:
            poll_status = sim_proc.poll()
            if poll_status is not None:
                exited_early = True
                break
            if os.path.exists(sim_log_path):
                try:
                    with open(sim_log_path, "r") as f:
                        log_content = f.read()
                        if "Waiting for student script to connect" in log_content:
                            simulator_ready = True
                            break
                except Exception:
                    pass
            time.sleep(0.1)
            
        if not simulator_ready:
            sim_proc.terminate()
            try:
                sim_proc.wait(timeout=2.0)
            except Exception:
                sim_proc.kill()
                
            # Fetch backend log output to show student/convenor what failed
            log_tail = ""
            if os.path.exists(sim_log_path):
                try:
                    with open(sim_log_path, "r") as f:
                        lines = f.readlines()
                        log_tail = "".join(lines[-15:])  # Grab last 15 lines of simulator logs
                except Exception as log_err:
                    log_tail = f"Could not read log file: {log_err}"
            
            if exited_early:
                write_results(
                    0.0,
                    f"System Error: Simulator backend exited early with code {poll_status}.\n\n"
                    f"--- Simulator Backend Log (Last 15 lines) ---\n{log_tail}"
                )
            else:
                write_results(
                    0.0,
                    f"System Error: Simulator failed to start or bind to port 8000 within 20s timeout.\n\n"
                    f"--- Simulator Backend Log (Last 15 lines) ---\n{log_tail}"
                )
            return
            
        # Run Student Client
        client_env = os.environ.copy()
        client_env["GRADESCOPE_AUTOGRADER"] = "1"
        
        if track == "python":
            client_cmd = [sys.executable, main_file]
            python_paths = [SOURCE_DIR, os.path.dirname(main_file), os.path.join(repo_root, "python")]
            if "PYTHONPATH" in os.environ:
                python_paths.append(os.environ["PYTHONPATH"])
            client_env["PYTHONPATH"] = os.path.pathsep.join(python_paths)
            client_cwd = os.path.dirname(main_file)
        else:
            client_cmd = [client_bin]
            client_cwd = tempfile.gettempdir()
            
        try:
            client_proc = subprocess.Popen(
                client_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=client_env,
                cwd=client_cwd,
                text=True
            )
        except Exception as e:
            sim_proc.send_signal(signal.SIGINT)
            try: sim_proc.wait(timeout=2.0)
            except Exception: sim_proc.kill()
            write_results(0.0, f"Execution Error: Failed to start student script/binary: {e}")
            return
            
        # Monitor
        time_limit = getattr(test_suite, "TIME_LIMIT", 45.0)
        max_duration = time_limit + 10.0
        start_time = time.time()
        client_exited = False
        timed_out = False
        
        while time.time() - start_time < max_duration:
            if not client_exited and client_proc.poll() is not None:
                client_exited = True
                time.sleep(1.5)
            if sim_proc.poll() is not None:
                break
            time.sleep(0.5)
        else:
            timed_out = True
            
        # Cleanup
        if client_proc.poll() is None:
            client_proc.terminate()
            try: client_proc.wait(timeout=2.0)
            except Exception: client_proc.kill()
            
        if sim_proc.poll() is None:
            sim_proc.send_signal(signal.SIGINT)
            try: sim_proc.wait(timeout=3.0)
            except Exception: sim_proc.kill()
            
        client_stdout, client_stderr = client_proc.communicate()
        
        sim_stdout = ""
        if os.path.exists(sim_log_path):
            try:
                with open(sim_log_path, "r") as f:
                    sim_stdout = f.read()
            except Exception:
                pass
                
        # Evaluate
        run_score = 0.0
        run_feedback = ""
        
        if not os.path.exists(TRAJECTORY_JSON) or os.path.getsize(TRAJECTORY_JSON) == 0:
            run_feedback = (
                f"Execution Error: No simulation trajectory was recorded.\n"
                f"Your script or binary did not connect to the simulator on port 8000.\n\n"
                f"--- Console Output (stdout) ---\n{client_stdout}\n\n"
                f"--- Error Output (stderr) ---\n{client_stderr}\n"
            )
        else:
            try:
                raw_score, run_feedback = test_suite.evaluate_run(TRAJECTORY_JSON)
                run_score = raw_score
            except Exception as e:
                run_feedback = f"System Error: Failed to evaluate simulation results: {e}"
                
        weighted_score = run_score * weight
        total_score += weighted_score
        
        run_visibility = "after_due_date" if is_hidden else "visible"
        
        # Generate HTML visualizations
        svg_html = generate_trajectory_svg(TRAJECTORY_JSON)
        video_html = get_video_html(VIDEO_PATH) if (idx == 0 and os.path.exists(VIDEO_PATH)) else ""
        
        import html
        escaped_feedback = html.escape(run_feedback)
        escaped_stdout = html.escape(client_stdout) if client_stdout else ""
        escaped_stderr = html.escape(client_stderr) if client_stderr else ""
        escaped_simout = html.escape(sim_stdout) if sim_stdout else ""
        
        html_sections = []
        html_sections.append(f"<h3 style='margin-top:0;'>=== {run_name} ===</h3>")
        html_sections.append(f"<p><strong>Weight:</strong> {weight*100:.0f}% &nbsp;|&nbsp; <strong>Score:</strong> {run_score:.1f} / 100.0 pts &nbsp;|&nbsp; <strong>Contribution:</strong> {weighted_score:.1f} pts &nbsp;|&nbsp; <strong>Visibility:</strong> {run_visibility.replace('_', ' ').capitalize()}</p>")
        
        if svg_html:
            html_sections.append(svg_html)
        if video_html:
            html_sections.append(video_html)
            
        html_sections.append(f"<pre style='background:#1e1e1e; color:#d4d4d4; padding:12px; border-radius:6px; font-family:monospace; font-size:12px; line-height:1.4; overflow-x:auto;'>{escaped_feedback}</pre>")
        
        if escaped_stdout:
            html_sections.append(f"<details style='margin-top:10px;'><summary style='cursor:pointer; font-weight:bold;'>Student Console Output (stdout)</summary><pre style='background:#1e1e1e; color:#d4d4d4; padding:12px; border-radius:6px; font-family:monospace; font-size:12px; margin-top:6px;'>{escaped_stdout}</pre></details>")
        if escaped_stderr:
            html_sections.append(f"<details style='margin-top:10px;'><summary style='cursor:pointer; font-weight:bold; color:#ff6b6b;'>Student Error Output (stderr)</summary><pre style='background:#2a1818; color:#ff8080; padding:12px; border-radius:6px; font-family:monospace; font-size:12px; margin-top:6px;'>{escaped_stderr}</pre></details>")
        if escaped_simout:
            html_sections.append(f"<details style='margin-top:10px;'><summary style='cursor:pointer; font-weight:bold;'>Simulator Backend Output</summary><pre style='background:#1e1e1e; color:#888; padding:12px; border-radius:6px; font-family:monospace; font-size:12px; margin-top:6px;'>{escaped_simout}</pre></details>")
            
        joined_run_html = "".join(html_sections)
        
        test_status = "passed" if run_score > 0.0 else "failed"
        
        gradescope_tests.append({
            "name": run_name,
            "score": round(weighted_score, 2),
            "max_score": round(weight * 100.0, 2),
            "status": test_status,
            "output": joined_run_html,
            "output_format": "html",
            "visibility": run_visibility
        })
        
        print(f"[Grader] Completed {run_name}: Score {run_score}/100 (Weighted: {weighted_score})")

    # 6. Write Consolidated Results JSON File
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    final_score = round(total_score, 2)
    
    results = {
        "score": final_score,
        "max_score": 100.0,
        "output": f"<h3 style='margin-top:0;'>Combined Score: {final_score:.2f} / 100.0 pts</h3>",
        "output_format": "html",
        "visibility": "visible",
        "tests": gradescope_tests
    }
    
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

        
    print(f"\n[Grader] All test runs finished. Final combined score: {final_score}% written to {RESULTS_FILE}")

if __name__ == "__main__":
    main()
