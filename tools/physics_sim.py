import os
import sys
import math
import time
import json
import socket
import argparse

# Silence Pygame's startup print in stdout
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

# Try importing dependencies, suppressing Objective-C duplicate class warnings on macOS
try:
    stderr_fd = sys.stderr.fileno()
    saved_stderr_fd = os.dup(stderr_fd)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull_fd, stderr_fd)
    try:
        import numpy as np
        import pygame
        import cv2
    finally:
        os.dup2(saved_stderr_fd, stderr_fd)
        os.close(devnull_fd)
        os.close(saved_stderr_fd)
except Exception:
    # Fallback to standard import if file descriptor redirection is not supported or fails
    try:
        import numpy as np
        import pygame
        import cv2
    except ImportError:
        print("=========================================================")
        print("ERROR: Missing required Python libraries for simulator.")
        print("Please install them by running:")
        print("  pip install -r python/requirements.txt")
        print("=========================================================")
        sys.exit(1)

# Helper: Line-segment intersection math for ToF ray-casting
def get_intersection(ray_start, ray_dir, line_start, line_end):
    # ray_start = (x, y), ray_dir = (dx, dy)
    # line_start = (x1, y1), line_end = (x2, y2)
    x1, y1 = line_start
    x2, y2 = line_end
    x3, y3 = ray_start
    dx, dy = ray_dir
    
    # Line equation: (1-t)*p1 + t*p2
    # Ray equation: p3 + u*dir
    # Solving for t and u:
    denom = (x1 - x2) * dy - (y1 - y2) * dx
    if abs(denom) < 1e-6:
        return None # Parallel
        
    t = ((x1 - x3) * dy - (y1 - y3) * dx) / denom
    u = ((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    if 0.0 <= t <= 1.0 and u >= 0.0:
        # Intersection point
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return (ix, iy, u)
    return None

def generate_random_maze(grid_rows=4, grid_cols=6, block_dim=0.20, seed=None, target_pos=None):
    """Generates a randomized DFS-based maze compliant with Micromouse rules.
    Default: 4 rows x 6 columns with a 2x2 open target room.
    """
    import random
    if seed is not None:
        random.seed(seed)
        
    visited = set()
    stack = []
    
    # Internal walls tracking
    v_walls = set((c, r) for c in range(1, grid_cols) for r in range(grid_rows))
    h_walls = set((c, r) for c in range(grid_cols) for r in range(1, grid_rows))
    
    # 2x2 Target room cells: default placed towards the opposite quadrant or center
    # For a 4x6 grid, default (cx, cy) = (4, 2) makes cells {(3,1), (3,2), (4,1), (4,2)} or (cols//2, rows//2)
    if target_pos:
        cx, cy = target_pos
    else:
        # Place 2x2 room in upper-right / center area, ensuring 1 <= cx <= grid_cols - 1 and 1 <= cy <= grid_rows - 1
        cx = max(1, min(grid_cols - 1, grid_cols - 2 if grid_cols >= 4 else grid_cols // 2))
        cy = max(1, min(grid_rows - 1, grid_rows // 2))
        
    tcs = {(cx - 1, cy - 1), (cx - 1, cy), (cx, cy - 1), (cx, cy)}
    
    def get_neighbors(cell):
        c, r = cell
        n = []
        if r < grid_rows - 1: n.append(('N', (c, r + 1)))
        if r > 0:             n.append(('S', (c, r - 1)))
        if c < grid_cols - 1: n.append(('E', (c + 1, r)))
        if c > 0:             n.append(('W', (c - 1, r)))
        return n
        
    curr = (0, 0)
    visited.add(curr)
    
    # Rule 1.3: Start cell (0, 0) has walls on three sides.
    # Exit is strictly to (1, 0) (East)
    # Remove the wall between (0, 0) and (1, 0) at the start
    if (1, 0) in v_walls:
        v_walls.remove((1, 0))
    visited.add((1, 0))
    curr = (1, 0)
    
    while len(visited) < grid_rows * grid_cols:
        # Get unvisited neighbors
        neighbors = [nb for nb in get_neighbors(curr) if nb[1] not in visited]
        if neighbors:
            dir_to, next_cell = random.choice(neighbors)
            c, r = curr
            
            # Remove the wall between curr and next_cell
            if dir_to == 'N':
                h_walls.discard((c, r + 1))
            elif dir_to == 'S':
                h_walls.discard((c, r))
            elif dir_to == 'E':
                v_walls.discard((c + 1, r))
            elif dir_to == 'W':
                v_walls.discard((c, r))
                
            if next_cell in tcs:
                # Mark all target cells as visited
                visited.update(tcs)
                # Remove all internal walls between the 4 center cells to make it a 2x2 open area
                v_walls.discard((cx, cy - 1))
                v_walls.discard((cx, cy))
                h_walls.discard((cx - 1, cy))
                h_walls.discard((cx, cy))
                
                # Do not advance current into target cells; back-track instead
            else:
                visited.add(next_cell)
                stack.append(curr)
                curr = next_cell
        elif stack:
            curr = stack.pop()
        else:
            # Fallback if stack is empty but some cells are not visited
            remaining = set((c, r) for c in range(grid_cols) for r in range(grid_rows)) - visited
            if remaining:
                curr = random.choice(list(remaining))
                visited.add(curr)
            else:
                break
                
    # Braid maze: randomly remove 7% of remaining walls (excluding boundary and center walls)
    center_boundary_v_walls = {(cx, cy - 1), (cx, cy), (cx - 1, cy - 1), (cx - 1, cy), (cx + 1, cy - 1), (cx + 1, cy)}
    center_boundary_h_walls = {(cx - 1, cy), (cx, cy), (cx - 1, cy - 1), (cx, cy - 1), (cx - 1, cy + 1), (cx, cy + 1)}
    
    v_list = [w for w in v_walls if w not in center_boundary_v_walls]
    random.shuffle(v_list)
    for w in v_list[:int(len(v_list) * 0.07)]:
        v_walls.remove(w)
        
    h_list = [w for w in h_walls if w not in center_boundary_h_walls]
    random.shuffle(h_list)
    for w in h_list[:int(len(h_list) * 0.07)]:
        h_walls.remove(w)
        
    segments = []
    for c, r in v_walls:
        segments.append(((c * block_dim, r * block_dim), (c * block_dim, (r + 1) * block_dim)))
    for c, r in h_walls:
        segments.append(((c * block_dim, r * block_dim), ((c + 1) * block_dim, r * block_dim)))
        
    return segments, (cx, cy)

class PhysicsSimulator:
    def __init__(self, maze_type="empty", imbalance=0.0, slip=0.0, headless=False, seed=None, config=None):
        self.maze_type = maze_type
        self.headless = headless
        self.seed = seed
        
        # Defaults (matching simstruct)
        self.L = 0.060  # axle half-length (m)
        self.R = 0.031  # wheel radius (m)
        self.collision_radius = 0.058
        self.ticks_per_rot = 8.0
        self.total_width = 0.143
        
        self.max_speed = 0.40
        self.tau = 0.088
        self.imbalance = imbalance
        self.slip_coeff = slip
        self.dead_band_l = 60.0  # Default dead-band left motor
        self.dead_band_r = 60.0  # Default dead-band right motor
        
        # Initialize default IMU variables
        self.gyro_bias = 0.0
        self.gyro_noise_std = 0.0
        self.accel_bias_x = 0.0
        self.accel_bias_y = 0.0
        self.accel_bias_z = 0.0
        self.accel_noise_std = 0.0
        
        self.sensor_offsets = [
            (0.045, 0.02, math.pi/2),   # Left ToF
            (0.055, 0.0, 0.0),          # Center ToF
            (0.045, -0.02, -math.pi/2)  # Right ToF
        ]
        
        self.grid_rows = 4
        self.grid_cols = 6
        self.block_dim = 0.20
        self.wall_thickness = 0.006
        self.target_room = None
        
        if config:
            if "robot" in config:
                rc = config["robot"]
                self.L = rc.get("axle_half_length", self.L)
                self.R = rc.get("wheel_radius", self.R)
                self.collision_radius = rc.get("collision_radius", self.collision_radius)
                self.ticks_per_rot = rc.get("ticks_per_rot", self.ticks_per_rot)
                self.total_width = rc.get("total_width", self.total_width)
            if "motor" in config:
                mc = config["motor"]
                self.max_speed = mc.get("max_speed", self.max_speed)
                self.tau = mc.get("tau", self.tau)
                # Load independent dead_bands if specified, falling back to a shared 'dead_band' value
                shared_db = mc.get("dead_band", 60.0)
                self.dead_band_l = mc.get("dead_band_l", shared_db)
                self.dead_band_r = mc.get("dead_band_r", shared_db)
                # If command line arguments were default, use config values
                if imbalance == 0.08:
                    self.imbalance = mc.get("imbalance", imbalance)
                if slip == 0.08:
                    self.slip_coeff = mc.get("slip", slip)
                
                # Apply seed-based Gaussian perturbations if a seed is active
                if seed is not None:
                    import random
                    rng = random.Random(seed)
                    
                    db_std = mc.get("perturb_dead_band_std", 0.0)
                    imb_std = mc.get("perturb_imbalance_std", 0.0)
                    slip_std = mc.get("perturb_slip_std", 0.0)
                    
                    if db_std > 0.0:
                        self.dead_band_l = max(0.0, self.dead_band_l + rng.gauss(0, db_std))
                        self.dead_band_r = max(0.0, self.dead_band_r + rng.gauss(0, db_std))
                    if imb_std > 0.0:
                        self.imbalance = max(-0.5, min(0.5, self.imbalance + rng.gauss(0, imb_std)))
                    if slip_std > 0.0:
                        self.slip_coeff = max(0.0, min(0.9, self.slip_coeff + rng.gauss(0, slip_std)))
            if "tof_sensors" in config:
                self.sensor_offsets = []
                for s in config["tof_sensors"]:
                    self.sensor_offsets.append((s["x"], s["y"], s["theta"]))
            if "maze" in config:
                mz = config["maze"]
                self.grid_rows = mz.get("grid_rows", mz.get("grid_size", self.grid_rows))
                self.grid_cols = mz.get("grid_cols", mz.get("grid_size", self.grid_cols))
                self.block_dim = mz.get("block_dim", self.block_dim)
                self.wall_thickness = mz.get("wall_thickness", self.wall_thickness)
            
            if "imu" in config:
                ic = config["imu"]
                self.gyro_noise_std = ic.get("gyro_noise_std", 0.0)
                self.accel_noise_std = ic.get("accel_noise_std", 0.0)
                
                # Apply seed-based static IMU bias errors
                if seed is not None:
                    import random
                    rng = random.Random(seed + 999) # unique offset to avoid correlation with motor seed
                    
                    g_bias_std = ic.get("gyro_bias_std", 0.0)
                    a_bias_std = ic.get("accel_bias_std", 0.0)
                    
                    if g_bias_std > 0.0:
                        self.gyro_bias = rng.gauss(0, g_bias_std)
                    if a_bias_std > 0.0:
                        self.accel_bias_x = rng.gauss(0, a_bias_std)
                        self.accel_bias_y = rng.gauss(0, a_bias_std)
                        self.accel_bias_z = rng.gauss(0, a_bias_std)

        # State: x, y, theta, actual wheel speeds, encoders
        self.reset_state()
        
        # Load Maze Walls
        self.walls = []
        self.build_maze()
        
    def reset_state(self):
        # Starting position: center of start cell (0,0) (or (0.1, 0.1) in world meters)
        self.x = self.block_dim / 2.0
        self.y = self.block_dim / 2.0
        self.theta = 0.0  # Facing East
        self.v_l = 0.0
        self.v_r = 0.0
        self.omega = 0.0  # angular velocity (rad/s)
        self.enc_l = 0.0
        self.enc_r = 0.0
        self.last_enc_l = 0.0  # tracks last-sent value to compute per-frame delta
        self.last_enc_r = 0.0
        self.time = 0.0
        self.trajectory = [(self.x, self.y, self.theta)]
        self.last_actuation = [0, 0]
        
        # Transient slip simulation state variables
        self.was_stationary = True
        self.start_slip_timer = 0.0
        self.start_slip_wheel = 0     # 0 = none, 1 = left, 2 = right
        self.start_slip_factor = 0.0
        self.is_turning = False
        
    def build_maze(self):
        self.maze_width = self.grid_cols * self.block_dim
        self.maze_height = self.grid_rows * self.block_dim
        
        # Outer border walls
        self.walls.append(((0, 0), (self.maze_width, 0))) # South
        self.walls.append(((0, self.maze_height), (self.maze_width, self.maze_height))) # North
        self.walls.append(((0, 0), (0, self.maze_height))) # West
        self.walls.append(((self.maze_width, 0), (self.maze_width, self.maze_height))) # East
        
        if self.maze_type == "spiral":
            # Generate a concentric spiral maze matching grid dimensions
            max_rings = min(self.grid_rows, self.grid_cols) // 2
            for k in range(1, max_rings):
                w_x = k * self.block_dim
                w_y = k * self.block_dim
                limit_x = self.maze_width - w_x
                limit_y = self.maze_height - w_y
                
                # Bottom wall: Y = w_y, X from w_x - block_dim to limit_x
                self.walls.append(((w_x - self.block_dim, w_y), (limit_x, w_y)))
                # Right wall: X = limit_x, Y from w_y to limit_y
                self.walls.append(((limit_x, w_y), (limit_x, limit_y)))
                # Top wall: Y = limit_y, X from w_x to limit_x
                self.walls.append(((w_x, limit_y), (limit_x, limit_y)))
                # Left wall: X = w_x, Y from w_y + block_dim to limit_y
                self.walls.append(((w_x, w_y + self.block_dim), (w_x, limit_y)))
        elif self.maze_type == "random":
            # Generate and add randomized DFS maze walls with 2x2 target room
            random_walls, self.target_room = generate_random_maze(self.grid_rows, self.grid_cols, self.block_dim, self.seed)
            self.walls.extend(random_walls)
                
    def step(self, pwm_l, pwm_r, dt):
        self.last_actuation = [pwm_l, pwm_r]
        
        # Calculate target velocities based on PWM, motor imbalance, and dead-band / static friction
        # Left motor:
        if abs(pwm_l) < self.dead_band_l:
            target_v_l = 0.0
        else:
            # Shift the command past the deadband to start the velocity ramp from zero (static friction model)
            sign_l = 1.0 if pwm_l >= 0 else -1.0
            active_pwm_l = (abs(pwm_l) - self.dead_band_l) / (100.0 - self.dead_band_l) * 100.0 * sign_l
            gain_l = 1.0 - max(0.0, self.imbalance)
            target_v_l = (active_pwm_l / 100.0) * self.max_speed * gain_l
            
        # Right motor:
        if abs(pwm_r) < self.dead_band_r:
            target_v_r = 0.0
        else:
            sign_r = 1.0 if pwm_r >= 0 else -1.0
            active_pwm_r = (abs(pwm_r) - self.dead_band_r) / (100.0 - self.dead_band_r) * 100.0 * sign_r
            gain_r = 1.0 - max(0.0, -self.imbalance)
            target_v_r = (active_pwm_r / 100.0) * self.max_speed * gain_r
            
        # Motor dynamics (lag)
        self.v_l += (target_v_l - self.v_l) / self.tau * dt
        self.v_r += (target_v_r - self.v_r) / self.tau * dt
        
        # 1. Starting Slip Simulation
        # If transitioning from a complete stop to forward drive, trigger a temporary starting slip
        is_stationary_now = (abs(self.v_l) < 1e-3 and abs(self.v_r) < 1e-3)
        if self.was_stationary and not is_stationary_now and (pwm_l > 0 and pwm_r > 0):
            # Select random wheel to slip (1 = left, 2 = right)
            self.start_slip_wheel = np.random.choice([1, 2])
            # Slip coefficient scales: reduces effective speed by 35% to 65% on starting
            self.start_slip_factor = np.random.uniform(0.35, 0.65)
            self.start_slip_timer = 0.200 # lasts for 200ms
            self.was_stationary = False
        elif is_stationary_now:
            self.was_stationary = True
            self.start_slip_timer = 0.0
            
        eff_v_l = self.v_l
        eff_v_r = self.v_r
        
        if self.start_slip_timer > 0.0:
            self.start_slip_timer -= dt
            if self.start_slip_wheel == 1:
                eff_v_l *= (1.0 - self.start_slip_factor)
            elif self.start_slip_wheel == 2:
                eff_v_r *= (1.0 - self.start_slip_factor)
                
        # 2. Turn Settle Slip Simulation
        # Detect if mouse was performing an in-place turn (left/right wheels running in opposite directions)
        is_turning_now = (pwm_l * pwm_r < 0)
        if is_turning_now:
            self.is_turning = True
        elif self.is_turning and (pwm_l == 0 and pwm_r == 0):
            # Just stopped turning! Inject a small settling slip offset to the theta angle (yaw slide)
            # Standard deviation of 1.0 degree around zero (approx +- 2.0 degrees max)
            settle_slip_yaw = math.radians(np.random.normal(0.0, 1.0))
            self.theta += settle_slip_yaw
            self.is_turning = False
            
        # Apply standard running baseline wheel slip
        if self.slip_coeff > 0:
            eff_v_l *= (1.0 - np.random.uniform(0.0, self.slip_coeff))
            eff_v_r *= (1.0 - np.random.uniform(0.0, self.slip_coeff))
            
        # Kinematics
        v = (eff_v_l + eff_v_r) / 2.0
        omega = (eff_v_r - eff_v_l) / (2.0 * self.L)
        self.omega = omega
        
        self.theta += omega * dt
        self.theta = (self.theta + math.pi) % (2.0 * math.pi) - math.pi # Wrap to [-pi, pi]
        
        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt
        
        # Log path
        if not self.trajectory or math.hypot(self.x - self.trajectory[-1][0], self.y - self.trajectory[-1][1]) > 0.01:
            self.trajectory.append((self.x, self.y, self.theta))
            
        # Integrate Encoders (measures physical rotations, before slip)
        self.enc_l += (self.v_l * dt) / (2.0 * math.pi * self.R) * self.ticks_per_rot
        self.enc_r += (self.v_r * dt) / (2.0 * math.pi * self.R) * self.ticks_per_rot
        
        self.time += dt
        
    def read_gyro(self):
        """Converts angular velocity to degrees/s and injects active sensor bias and white noise (dps)."""
        noise = np.random.normal(0.0, self.gyro_noise_std) if self.gyro_noise_std > 0.0 else 0.0
        gyro_dps = (self.omega * 180.0 / math.pi) + self.gyro_bias + noise
        return gyro_dps
        
    def read_accel(self):
        """Simulates accelerometer readings (ax, ay, az in m/s^2) with active biases and noise."""
        noise_std = self.accel_noise_std if self.accel_noise_std > 0.0 else 0.0
        
        # Calculate dynamic acceleration (simple numerical differentiation of velocity)
        # Note: on a physical flat surface, the accelerometer measures local body frame accelerations.
        # For simplicity in this kinematics model, we assume a small velocity step difference.
        if not hasattr(self, 'last_v'):
            self.last_v = 0.0
        v_current = (self.v_l + self.v_r) / 2.0
        a_forward = (v_current - self.last_v) / 0.05 # 50ms timestep
        self.last_v = v_current
        
        # Accelerometer measures (linear acceleration - gravity vector projection)
        # Assuming flat floor, gravity vector points straight down relative to the mouse frame:
        # ax (forward) = forward acceleration + noise + bias
        # ay (lateral) = centripetal acceleration (v * omega) + noise + bias
        # az (vertical) = gravity (9.81) + noise + bias
        ax = a_forward + self.accel_bias_x + np.random.normal(0.0, noise_std)
        ay = (v_current * self.omega) + self.accel_bias_y + np.random.normal(0.0, noise_std)
        az = 9.81 + self.accel_bias_z + np.random.normal(0.0, noise_std)
        
        return ax, ay, az
        
    def read_tofs(self):
        distances = []
        for ox, oy, otheta in self.sensor_offsets:
            # Position of the sensor in world frame
            s_theta = self.theta + otheta
            s_x = self.x + ox * math.cos(self.theta) - oy * math.sin(self.theta)
            s_y = self.y + ox * math.sin(self.theta) + oy * math.cos(self.theta)
            
            ray_dir = (math.cos(s_theta), math.sin(s_theta))
            min_dist = 2.0  # Max sensor range in meters
            
            for line_start, line_end in self.walls:
                res = get_intersection((s_x, s_y), ray_dir, line_start, line_end)
                if res:
                    min_dist = min(min_dist, res[2])
                    
            # Add minor sensor variance noise (0.01m)
            min_dist += np.random.normal(0, 0.005)
            min_dist = max(0.0, min_dist)
            
            # Convert to integer millimeters
            distances.append(int(min_dist * 1000))
        return distances

    def check_collision(self):
        # Collision check based on approximate mouse radius
        mouse_radius = self.collision_radius
        for line_start, line_end in self.walls:
            # Distance from point (x,y) to line segment
            px = line_end[0] - line_start[0]
            py = line_end[1] - line_start[1]
            something = px*px + py*py
            if something < 1e-9:
                continue
            u = ((self.x - line_start[0]) * px + (self.y - line_start[1]) * py) / float(something)
            u = max(0.0, min(1.0, u))
            ix = line_start[0] + u * px
            iy = line_start[1] + u * py
            dist = math.hypot(self.x - ix, self.y - iy)
            if dist < mouse_radius:
                return True
        return False

def main():
    parser = argparse.ArgumentParser(description="UCT Micromouse Python Physics & Graphics Simulator")
    parser.add_argument("--map", choices=["empty", "spiral", "random"], default="empty", help="Select maze layout")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for procedural maze generation")
    parser.add_argument("--imbalance", type=float, default=0.08, help="Motor asymmetry imbalance coefficient (-0.2 to 0.2)")
    parser.add_argument("--slip", type=float, default=0.08, help="Wheel traction slip coefficient (0.0 to 0.3)")
    parser.add_argument("--video", type=str, default="", help="Output path to record MP4 video file")
    parser.add_argument("--headless", action="store_true", help="Run in headless cloud mode (no window display)")
    parser.add_argument("--json-log", type=str, default="", help="Path to save simulation metrics summary as JSON")
    parser.add_argument("--telemetry-log", type=str, default="", help="Path to save C-Kernel matching hardware JSONL log")
    parser.add_argument("--trajectory-log", type=str, default="", help="Path to save detailed simulation trajectory state JSONL log")
    parser.add_argument("--max-time", type=float, default=None, help="Maximum simulation time limit in seconds")
    parser.add_argument("--config", type=str, default="", help="Path to simulation JSON config file")
    args = parser.parse_args()
    
    # Load config file if specified, or try default location
    config_data = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = args.config if args.config else os.path.join(script_dir, "simulation_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            print(f"[Simulator] Loaded configuration from: {config_path}")
        except Exception as e:
            print(f"[Simulator] Error loading config {config_path}: {e}")
            
    # Use the user-provided seed or generate a random one to enable default run-to-run parameter variations
    import random
    active_seed = args.seed if args.seed is not None else random.randint(1, 100000)
    print(f"[Simulator] Active Simulation Seed: {active_seed}")
            
    sim = PhysicsSimulator(maze_type=args.map, imbalance=args.imbalance, slip=args.slip, headless=args.headless, seed=active_seed, config=config_data)
    
    # Initialize Pygame in dummy mode if headless
    if args.headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        
    # Scale Pygame window to match maze aspect ratio (e.g. 600 wide x 400 high for 4x6)
    aspect_ratio = sim.maze_height / max(1e-3, sim.maze_width)
    width = 720
    height = int(width * aspect_ratio)
    if args.headless:
        # Headless rendering uses an offscreen surface
        screen = pygame.Surface((width, height))
    else:
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("UCT Micromouse Co-Simulation Testbed")
        
    clock = pygame.time.Clock()
    
    # Load mouse image if graphics enabled
    mouse_img = None
    if not args.headless:
        proj_root = os.path.dirname(script_dir)
        img_path = os.path.join(proj_root, "matlab", "simulator", "uctmm_image.png")
        if os.path.exists(img_path):
            try:
                mouse_img = pygame.image.load(img_path).convert_alpha()
                print(f"[Simulator] Loaded mouse image: {img_path}")
            except Exception as e:
                print(f"[Simulator] Failed to load mouse image {img_path}: {e}")
    
    # Initialize Video Writer if requested
    video_writer = None
    if args.video:
        # Try modern highly-compressed H.264 codecs first, fall back to standard mp4v for headless environments
        for codec in ['avc1', 'h264', 'mp4v']:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                video_writer = cv2.VideoWriter(args.video, fourcc, 20.0, (width, height))
                if video_writer.isOpened():
                    print(f"[Simulator] Video recording enabled using codec '{codec}'. Saving to: {args.video}")
                    break
                else:
                    video_writer.release()
            except Exception:
                pass
        else:
            print("[Simulator] Warning: Could not initialize any video writer codec.")
            video_writer = None
        
    # Start TCP Socket Server
    port = 8000
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", port))
    server_sock.listen(1)
    print(f"[Simulator] Server listening on localhost:{port}")
    print("[Simulator] Waiting for student script to connect...")
    
    try:
        conn, addr = server_sock.accept()
        print(f"[Simulator] Student connected from {addr[0]}:{addr[1]}")
        print("\n" + "=" * 50)
        print("=== ACTIVE SIMULATED MOUSE PARAMETERS ===")
        print(f"  Seed                  : {active_seed}")
        print(f"  Maze Geometry         : {sim.grid_rows} rows x {sim.grid_cols} cols ({sim.maze_height:.2f}m x {sim.maze_width:.2f}m)")
        print(f"  Dead Band (Left/Right): {sim.dead_band_l:.2f} / {sim.dead_band_r:.2f} PWM")
        print(f"  Motor Gain Imbalance  : {sim.imbalance * 100:+.2f}%")
        print(f"  Traction Slip Coeff   : {sim.slip_coeff * 100:.2f}%")
        print(f"  Gyroscope Bias Offset : {sim.gyro_bias:+.4f} dps")
        print(f"  Accelerometer Biases  : X={sim.accel_bias_x:+.2f}, Y={sim.accel_bias_y:+.2f}, Z={sim.accel_bias_z:+.2f} m/s^2")
        print("=" * 50 + "\n")
    except KeyboardInterrupt:
        server_sock.close()
        sys.exit(0)
        
    running = True
    crashed = False
    rate_hz = 20 # Default sync rate
    dt = 1.0 / rate_hz
    
    # 1-to-1 parallel telemetry and trajectory logger state
    telemetry_records = []
    trajectory_records = []
    logging_started = False
    
    # Track physical log shadow states for sparse comparison checks
    last_log_left_pwm = 0
    last_log_right_pwm = 0
    last_log_tof_l = 0
    last_log_tof_al = 0
    last_log_tof_c = 0
    last_log_tof_ar = 0
    last_log_tof_r = 0
    last_log_lenc = 0
    last_log_renc = 0
    last_log_gyro = 0.0
    
    # Main simulation tick loop
    try:
        while running:
            # Handle Pygame events to prevent window hang
            if not args.headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        
            # 1. Listen for Actuation target from student script
            try:
                conn.settimeout(0.5)
                rx_bytes = conn.recv(1024)
                if not rx_bytes:
                    break
                rx_str = rx_bytes.decode('utf-8').strip()
                
                # Split and parse lines
                for line in rx_str.split('\n'):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if "a" in data: # Actuation target
                            pwm_l, pwm_r = data["a"]
                            # Step simulation physics forward by dt
                            sim.step(pwm_l, pwm_r, dt)
                        elif "p" in data or "c" in data:
                            # Step simulation using last actuation targets to maintain lock-step velocity
                            sim.step(sim.last_actuation[0], sim.last_actuation[1], dt)
                        if "c" in data: # Configuration target
                            cfg = data["c"]
                            if "rate" in cfg:
                                rate_hz = cfg["rate"]
                                dt = 1.0 / rate_hz
                    except json.JSONDecodeError:
                        pass
            except socket.timeout:
                pass # timeout is fine, keeps rendering loop alive
                
            # 2. Collision checking
            if sim.check_collision():
                print("[Simulator] CRASH! Mouse hit a wall.")
                crashed = True
                running = False
                
            # Time limit checking
            if args.max_time and sim.time >= args.max_time:
                print(f"[Simulator] Time Limit Exceeded ({args.max_time}s).")
                running = False

            # Auto-exit if mouse has moved and then stopped for 3.0 seconds
            is_stationary = (abs(sim.v_l) < 1e-2 and abs(sim.v_r) < 1e-2 and sim.last_actuation == [0, 0])
            if is_stationary and sim.time > 1.0:
                if not hasattr(sim, "stationary_time"):
                    sim.stationary_time = 0.0
                sim.stationary_time += dt
                if sim.stationary_time >= 3.0:
                    start_x = sim.trajectory[0][0] if sim.trajectory else 0.0
                    start_y = sim.trajectory[0][1] if sim.trajectory else 0.0
                    max_disp = 0.0
                    for pt in sim.trajectory:
                        max_disp = max(max_disp, math.hypot(pt[0] - start_x, pt[1] - start_y))
                    if max_disp > 0.1:
                        print(f"[Simulator] Auto-completing run: Mouse stopped for 3.0s after moving.")
                        running = False
            else:
                sim.stationary_time = 0.0
                
            # 3. Draw Simulation Environment
            screen.fill((18, 18, 18)) # Dark theme background
            
            # Draw grid blocks
            scale = width / sim.maze_width
            for i in range(sim.grid_cols):
                for j in range(sim.grid_rows):
                    rect = pygame.Rect(i*sim.block_dim*scale, j*sim.block_dim*scale, sim.block_dim*scale, sim.block_dim*scale)
                    pygame.draw.rect(screen, (35, 35, 35), rect, 1)
                    
            # Draw trajectory path
            if len(sim.trajectory) > 1:
                pygame_pts = [(pt[0]*scale, (sim.maze_height - pt[1])*scale) for pt in sim.trajectory]
                pygame.draw.lines(screen, (0, 150, 255), False, pygame_pts, 2)
                
            # Draw ToF rays
            tofs = sim.read_tofs()
            for idx, (ox, oy, otheta) in enumerate(sim.sensor_offsets):
                s_theta = sim.theta + otheta
                s_x = sim.x + ox * math.cos(sim.theta) - oy * math.sin(sim.theta)
                s_y = sim.y + ox * math.sin(sim.theta) + oy * math.cos(sim.theta)
                
                # Compute projection length
                dist_m = tofs[idx] / 1000.0
                end_x = s_x + dist_m * math.cos(s_theta)
                end_y = s_y + dist_m * math.sin(s_theta)
                
                pygame.draw.line(screen, (220, 50, 50), 
                                 (s_x*scale, (sim.maze_height - s_y)*scale), 
                                 (end_x*scale, (sim.maze_height - end_y)*scale), 1)
                
            # Draw walls
            for line_start, line_end in sim.walls:
                pygame.draw.line(screen, (240, 240, 240), 
                                 (line_start[0]*scale, (sim.maze_height - line_start[1])*scale), 
                                 (line_end[0]*scale, (sim.maze_height - line_end[1])*scale), 4)
                
            # Draw mouse (rotated image or fallback circle)
            mouse_px = int(sim.x * scale)
            mouse_py = int((sim.maze_height - sim.y) * scale)
            
            if mouse_img:
                img_size_m = sim.total_width * (201.0 / 147.0)
                img_pixel_size = int(img_size_m * scale)
                
                # Resize and rotate
                scaled_img = pygame.transform.smoothscale(mouse_img, (img_pixel_size, img_pixel_size))
                rotated_img = pygame.transform.rotate(scaled_img, math.degrees(sim.theta))
                
                # Center and draw
                new_rect = rotated_img.get_rect(center=(mouse_px, mouse_py))
                screen.blit(rotated_img, new_rect.topleft)
            else:
                # Fallback to circle & arrow
                pygame.draw.circle(screen, (0, 200, 100), (mouse_px, mouse_py), int(sim.collision_radius * scale))
                head_x = int(mouse_px + sim.collision_radius * scale * math.cos(sim.theta))
                head_y = int(mouse_py - sim.collision_radius * scale * math.sin(sim.theta))
                pygame.draw.line(screen, (255, 255, 255), (mouse_px, mouse_py), (head_x, head_y), 3)
            
            # HUD metrics overlay
            font = pygame.font.Font(None, 24) if pygame.font.get_init() else None
            hud_y = 10
            metrics = [
                f"Time: {sim.time:.2f} s",
                f"Encoder L: {int(sim.enc_l)}",
                f"Encoder R: {int(sim.enc_r)}",
                f"ToF L: {tofs[0]} mm",
                f"ToF C: {tofs[1]} mm",
                f"ToF R: {tofs[2]} mm",
                f"PWM: L={sim.last_actuation[0]} | R={sim.last_actuation[1]}"
            ]
            
            for m_str in metrics:
                if font:
                    text_surface = font.render(m_str, True, (200, 200, 200))
                    screen.blit(text_surface, (10, hud_y))
                    hud_y += 20
                    
            if not args.headless:
                pygame.display.flip()
                clock.tick(20) # Match 20Hz stream rate
                
            # Write frame to video if recording
            if video_writer:
                frame_data = pygame.image.tostring(screen, 'RGB')
                frame = np.frombuffer(frame_data, dtype=np.uint8).reshape(height, width, 3)
                video_writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                
            # 4. Stream Telemetry back to student and Record Logs in Lock-step
            gyro_val = sim.read_gyro()
            ax_val, ay_val, az_val = sim.read_accel()
            # Send encoder as true per-frame DELTA (not cumulative total)
            delta_enc_l = int(sim.enc_l) - int(sim.last_enc_l)
            delta_enc_r = int(sim.enc_r) - int(sim.last_enc_r)
            sim.last_enc_l = sim.enc_l
            sim.last_enc_r = sim.enc_r
            tx_str = f'{{"tof_l":{tofs[0]}, "tof_c":{tofs[1]}, "tof_r":{tofs[2]}, "+lenc":{delta_enc_l}, "+renc":{delta_enc_r}, "gyro":{gyro_val:.4f}, "v_batt":6.0}}\r\n'
            
            # Logger triggers on first motor command
            if not logging_started:
                if sim.last_actuation[0] != 0 or sim.last_actuation[1] != 0:
                    logging_started = True
                    # Record log header as the first line of the telemetry log
                    header_rec = {"log_header": 1, "uid": "066AFF514885864967083830", "hash": 4017325881}
                    telemetry_records.append(header_rec)
                    
                    # Parallel trajectory log gets a detailed header detailing the active perturbed values
                    header_rec_traj = {
                        "log_header": 1,
                        "uid": "066AFF514885864967083830",
                        "hash": 4017325881,
                        "simulation_seed": active_seed,
                        "perturbed_dead_band_l": round(sim.dead_band_l, 2),
                        "perturbed_dead_band_r": round(sim.dead_band_r, 2),
                        "perturbed_imbalance": round(sim.imbalance, 4),
                        "perturbed_slip": round(sim.slip_coeff, 4),
                        "perturbed_gyro_bias": round(sim.gyro_bias, 4),
                        "perturbed_accel_bias_x": round(sim.accel_bias_x, 4),
                        "perturbed_accel_bias_y": round(sim.accel_bias_y, 4),
                        "perturbed_accel_bias_z": round(sim.accel_bias_z, 4)
                    }
                    trajectory_records.append(header_rec_traj)
                    
                    # Initialize last logged parameters
                    last_log_left_pwm = sim.last_actuation[0]
                    last_log_right_pwm = sim.last_actuation[1]
                    last_log_tof_l = tofs[0]
                    last_log_tof_c = tofs[1]
                    last_log_tof_r = tofs[2]
                    last_log_lenc = int(sim.enc_l)
                    last_log_renc = int(sim.enc_r)
                    last_log_gyro = gyro_val
                    last_log_ax = ax_val
                    last_log_ay = ay_val
                    last_log_az = az_val
            
            if logging_started:
                # Build hardware-matching sparse log entry
                sparse_entry = {}
                if sim.last_actuation[0] != last_log_left_pwm:
                    sparse_entry["l"] = sim.last_actuation[0]
                    last_log_left_pwm = sim.last_actuation[0]
                if sim.last_actuation[1] != last_log_right_pwm:
                    sparse_entry["r"] = sim.last_actuation[1]
                    last_log_right_pwm = sim.last_actuation[1]
                if tofs[0] != last_log_tof_l:
                    sparse_entry["tl"] = tofs[0]
                    last_log_tof_l = tofs[0]
                if tofs[1] != last_log_tof_c:
                    sparse_entry["tc"] = tofs[1]
                    last_log_tof_c = tofs[1]
                if tofs[2] != last_log_tof_r:
                    sparse_entry["tr"] = tofs[2]
                    last_log_tof_r = tofs[2]
                if int(sim.enc_l) != last_log_lenc:
                    sparse_entry["le"] = int(sim.enc_l)
                    last_log_lenc = int(sim.enc_l)
                if int(sim.enc_r) != last_log_renc:
                    sparse_entry["re"] = int(sim.enc_r)
                    last_log_renc = int(sim.enc_r)
                if abs(gyro_val - last_log_gyro) > 0.01:
                    sparse_entry["g"] = round(gyro_val, 2)
                    last_log_gyro = gyro_val
                if abs(ax_val - last_log_ax) > 0.1:
                    sparse_entry["ax"] = round(ax_val, 2)
                    last_log_ax = ax_val
                if abs(ay_val - last_log_ay) > 0.1:
                    sparse_entry["ay"] = round(ay_val, 2)
                    last_log_ay = ay_val
                if abs(az_val - last_log_az) > 0.1:
                    sparse_entry["az"] = round(az_val, 2)
                    last_log_az = az_val
                sparse_entry["v"] = 6.0 # v_batt constant
                
                # Write to telemetry log list
                telemetry_records.append(sparse_entry)
                
                # Write matching full pose entry to detailed trajectory log list
                # Line N of trajectory log maps exactly to Line N of telemetry log
                traj_entry = {
                    "time": round(sim.time, 4),
                    "x": round(sim.x, 6),
                    "y": round(sim.y, 6),
                    "theta": round(sim.theta, 6),
                    "v_l": round(sim.v_l, 4),
                    "v_r": round(sim.v_r, 4),
                    "enc_l": int(sim.enc_l),
                    "enc_r": int(sim.enc_r),
                    "pwm_l": sim.last_actuation[0],
                    "pwm_r": sim.last_actuation[1],
                    "ax": round(ax_val, 4),
                    "ay": round(ay_val, 4),
                    "az": round(az_val, 4)
                }
                trajectory_records.append(traj_entry)
            
            try:
                conn.sendall(tx_str.encode('utf-8'))
            except (BrokenPipeError, ConnectionResetError):
                break
                
    except Exception as e:
        print(f"[Simulator] Error encountered: {e}")
    finally:
        # Cleanup
        print("[Simulator] Cleaning up socket connection...")
        try:
            conn.close()
        except NameError:
            pass
        server_sock.close()
        
        if video_writer:
            print("[Simulator] Closing video writer...")
            video_writer.release()
            
        # If crashed and running interactively, show crash banner and wait
        if crashed and not args.headless:
            try:
                # Draw CRASHED text overlay
                if font:
                    crash_surface = font.render("CRASH! MOUSE HIT A WALL", True, (255, 0, 0))
                    # Draw a black rectangle with red border behind it for contrast
                    rect = pygame.Rect(width // 2 - 160, height // 2 - 25, 320, 50)
                    pygame.draw.rect(screen, (0, 0, 0), rect)
                    pygame.draw.rect(screen, (255, 0, 0), rect, 2)
                    screen.blit(crash_surface, (width // 2 - 140, height // 2 - 10))
                    pygame.display.flip()
                
                # Wait for 3 seconds or until window is closed
                waiting = True
                start_wait = time.time()
                while waiting and (time.time() - start_wait < 3.0):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting = False
                    pygame.time.wait(100)
            except Exception:
                pass
                
        pygame.quit()
        
        # Save JSON log if requested
        if args.json_log:
            try:
                # Calculate metrics
                start_x = sim.trajectory[0][0] if sim.trajectory else 0.0
                start_y = sim.trajectory[0][1] if sim.trajectory else 0.0
                final_x = sim.x
                final_y = sim.y
                
                # Max displacement
                max_displacement = 0.0
                for pt in sim.trajectory:
                    dist = math.hypot(pt[0] - start_x, pt[1] - start_y)
                    if dist > max_displacement:
                        max_displacement = dist
                
                log_data = {
                    "start_x": start_x,
                    "start_y": start_y,
                    "final_x": final_x,
                    "final_y": final_y,
                    "max_displacement": max_displacement,
                    "time": sim.time,
                    "crashed": crashed,
                    "grid_rows": sim.grid_rows,
                    "grid_cols": sim.grid_cols,
                    "target_room": sim.target_room,
                    "trajectory": sim.trajectory
                }
                with open(args.json_log, "w") as f:
                    json.dump(log_data, f, indent=2)
                print(f"[Simulator] Simulation metrics logged to: {args.json_log}")
            except Exception as ex:
                print(f"[Simulator] Failed to write JSON log: {ex}")
                
        # Save hardware-matching sparse telemetry log (.jsonl format)
        if args.telemetry_log and telemetry_records:
            try:
                with open(args.telemetry_log, "w") as f:
                    for rec in telemetry_records:
                        f.write(json.dumps(rec, separators=(',', ':')) + "\n")
                print(f"[Simulator] Telemetry JSONL log saved to: {args.telemetry_log}")
            except Exception as ex:
                print(f"[Simulator] Failed to write telemetry JSONL log: {ex}")
                
        # Save detailed simulation trajectory log (.jsonl format, 1-to-1 mapped lines)
        if args.trajectory_log and trajectory_records:
            try:
                with open(args.trajectory_log, "w") as f:
                    for rec in trajectory_records:
                        f.write(json.dumps(rec, separators=(',', ':')) + "\n")
                print(f"[Simulator] Trajectory state JSONL log saved to: {args.trajectory_log}")
            except Exception as ex:
                print(f"[Simulator] Failed to write trajectory JSONL log: {ex}")
                
        print("[Simulator] Closed successfully.")
        
        if crashed:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()
