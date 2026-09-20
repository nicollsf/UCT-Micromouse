import json
import math

# Milestone 2 / Submission 4 parameters: 4x6 maze with 2x2 target room
MAP = "random"
TIME_LIMIT = 90.0
IMBALANCE = 0.08
SLIP = 0.02
SEED = 42

# Maze Geometry: 4 rows (y: 0..4 * 0.2m = 0.8m) x 6 cols (x: 0..6 * 0.2m = 1.2m)
CELL_DIM = 0.20
MAZE_ROWS = 4
MAZE_COLS = 6

def evaluate_run(trajectory_file):
    try:
        with open(trajectory_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        return 0.0, f"Error reading trajectory file: {e}"

    start_x = data.get("start_x", 0.10)
    start_y = data.get("start_y", 0.10)
    final_x = data.get("final_x", start_x)
    final_y = data.get("final_y", start_y)
    sim_time = data.get("time", 0.0)
    crashed = data.get("crashed", False)
    trajectory = data.get("trajectory", []) # [(x, y, theta), ...]

    # Resolve target room center dynamically from simulator log or default 4x6 geometry
    if "target_room" in data and data["target_room"]:
        cx, cy = data["target_room"]
        target_center_x = cx * CELL_DIM
        target_center_y = cy * CELL_DIM
    else:
        # In 4x6 maze, target 2x2 room default (cx, cy) = (4, 2) -> (0.8m, 0.4m)
        target_center_x = 0.80
        target_center_y = 0.40
    target_radius = 0.28 # Within 2x2 room bounding circle

    # Check Stage 1: Target Discovery (Did trajectory enter target zone?)
    min_dist_to_target = 999.0
    entered_target = False
    target_entry_idx = -1

    for idx, pt in enumerate(trajectory):
        d = math.hypot(pt[0] - target_center_x, pt[1] - target_center_y)
        if d < min_dist_to_target:
            min_dist_to_target = d
        if d <= target_radius and not entered_target:
            entered_target = True
            target_entry_idx = idx

    # Check Stage 2: 360-degree Recognition Pirouette inside target zone
    pirouette_detected = False
    if entered_target and target_entry_idx >= 0:
        # Check yaw rotation in window after target entry
        yaw_accum = 0.0
        prev_theta = trajectory[target_entry_idx][2]
        for pt in trajectory[target_entry_idx:min(len(trajectory), target_entry_idx + 300)]:
            d_theta = pt[2] - prev_theta
            # Normalize angle wrap
            while d_theta > math.pi: d_theta -= 2 * math.pi
            while d_theta < -math.pi: d_theta += 2 * math.pi
            yaw_accum += abs(d_theta)
            prev_theta = pt[2]
            if yaw_accum >= 5.5: # ~315 deg to 360 deg
                pirouette_detected = True
                break

    # Check Stage 3: Return to Start (0,0) after visiting target
    returned_to_start = False
    if entered_target and target_entry_idx >= 0:
        for pt in trajectory[target_entry_idx:]:
            d_start = math.hypot(pt[0] - start_x, pt[1] - start_y)
            if d_start <= 0.15:
                returned_to_start = True
                break

    # Check Stage 4: High-Speed Sprint back to target
    sprint_completed = False
    if returned_to_start:
        final_dist_to_target = math.hypot(final_x - target_center_x, final_y - target_center_y)
        if final_dist_to_target <= target_radius:
            sprint_completed = True

    feedback = []
    feedback.append("=== Submission 4: Final Maze Solver Evaluation ===")
    feedback.append(f"Maze Grid           : {MAZE_ROWS}x{MAZE_COLS} (0.8m x 1.2m)")
    feedback.append(f"Start Position      : ({start_x:.3f}, {start_y:.3f})")
    feedback.append(f"Final Position      : ({final_x:.3f}, {final_y:.3f})")
    feedback.append(f"Min Dist to Target  : {min_dist_to_target:.3f} m")
    feedback.append(f"Simulation Time     : {sim_time:.2f} s")
    feedback.append(f"Collision / Crash   : {'YES' if crashed else 'NO'}")

    # Point allocation (100 pts total)
    # Stage 1: Target Discovery (30 pts)
    if entered_target:
        score_target = 30.0
        feedback.append("  [Phase 1] SUCCESS: 2x2 Target Room discovered and entered (30.0 / 30.0 pts)")
    else:
        progress = max(0.0, 1.0 - min_dist_to_target / 1.0)
        score_target = 30.0 * progress
        feedback.append(f"  [Phase 1] PARTIAL: Target room not reached ({score_target:.1f} / 30.0 pts)")

    # Stage 2: Pirouette (20 pts)
    score_pirouette = 20.0 if pirouette_detected else 0.0
    feedback.append(f"  [Phase 2] {'SUCCESS: 360° Target Recognition Pirouette verified' if pirouette_detected else 'FAILED: No 360° pirouette detected inside target room'} ({score_pirouette:.1f} / 20.0 pts)")

    # Stage 3: Return to Start (20 pts)
    score_return = 20.0 if returned_to_start else 0.0
    feedback.append(f"  [Phase 3] {'SUCCESS: Autonomous return to start (0,0) verified' if returned_to_start else 'FAILED: Did not return to start cell (0,0)'} ({score_return:.1f} / 20.0 pts)")

    # Stage 4: Sprint to Target (20 pts)
    score_sprint = 20.0 if sprint_completed else 0.0
    feedback.append(f"  [Phase 4] {'SUCCESS: High-speed sprint completed to target' if sprint_completed else 'FAILED: High-speed sprint to target not completed'} ({score_sprint:.1f} / 20.0 pts)")

    # Total Time Speed Bonus (10 pts)
    speed_bonus = 0.0
    if sprint_completed and not crashed:
        if sim_time <= 25.0:
            speed_bonus = 10.0
        elif sim_time <= 90.0:
            speed_bonus = 10.0 * (90.0 - sim_time) / (90.0 - 25.0)
    feedback.append(f"  [Bonus]   Speed & Efficiency Bonus: {speed_bonus:.1f} / 10.0 pts")

    subtotal = score_target + score_pirouette + score_return + score_sprint + speed_bonus
    timeout_penalty = 10.0 if sim_time >= TIME_LIMIT else 0.0
    if timeout_penalty > 0:
        feedback.append(f"  [Penalty] Timeout Penalty (> 90.0s): -{timeout_penalty:.1f} pts")

    final_grade = max(0.0, min(100.0, subtotal - timeout_penalty))
    final_grade_rounded = round(final_grade)

    feedback.append("\n=== Total Score Arithmetic ===")
    feedback.append(f"  Phase 1 (Target Discovery)  : {score_target:5.1f} / 30.0 pts")
    feedback.append(f"  Phase 2 (360° Pirouette)    : {score_pirouette:5.1f} / 20.0 pts")
    feedback.append(f"  Phase 3 (Return to Start)   : {score_return:5.1f} / 20.0 pts")
    feedback.append(f"  Phase 4 (High-Speed Sprint) : {score_sprint:5.1f} / 20.0 pts")
    feedback.append(f"  Speed Run Bonus             : {speed_bonus:5.1f} / 10.0 pts")
    feedback.append(f"  -------------------------------------------")
    feedback.append(f"  Final Calculated Grade      : {final_grade_rounded}%")

    return float(final_grade_rounded), "\n".join(feedback)
