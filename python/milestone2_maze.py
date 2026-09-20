# =========================================================================
# UCT Micromouse - Milestone 2 / Submission 4: 4x6 Maze Solver Template
# =========================================================================
# ASSIGNMENT MISSION: "Search, Celebrate & Sprint"
# 1. Phase 1 (Explore & Map): Autonomously explore the 4x6 maze from (0,0),
#    mapping wall presence using ToF sensors until discovering the 2x2 open
#    target room (4 contiguous cells with zero interior dividing walls).
# 2. Phase 2 (Target Recognition): Execute an on-the-spot 360° clockwise
#    pirouette inside the target room to signal goal acquisition.
# 3. Phase 3 (Return to Start): Compute the optimal shortest path back to (0,0),
#    navigate back, and stop at the starting cell.
# 4. Phase 4 (High-Speed Sprint): Pause 3.0s, then execute a high-speed sprint
#    along the optimal path directly into the target room.
#
# NOTE: In the final week competition, the maze will be larger (e.g. 8x8/10x10).
# Ensure your code parameterizes MAZE_ROWS and MAZE_COLS dynamically!
# =========================================================================

import uct_mouse
import math
import time

# Maze Dimensions (Default: 4 rows x 6 columns)
MAZE_ROWS = 4
MAZE_COLS = 6
CELL_LENGTH_M = 0.20

# Directions: 0: North (+y), 1: East (+x), 2: South (-y), 3: West (-x)
DX = [0, 1, 0, -1]
DY = [1, 0, -1, 0]

class MazeSolver:
    def __init__(self, rows=MAZE_ROWS, cols=MAZE_COLS):
        self.rows = rows
        self.cols = cols
        
        # 0 = unknown, 1 = wall, 2 = open
        self.walls = [[[0]*4 for _ in range(self.cols)] for _ in range(self.rows)]
        self.visited = [[False]*self.cols for _ in range(self.rows)]
        self.x = 0
        self.y = 0
        self.dir = 0  # 0: North
        
        # Target room coordinates (discovered dynamically)
        self.target_room = None  # e.g., (min_x, min_y) of 2x2 block
        
        # Initialize outer boundary walls
        for r in range(self.rows):
            self.walls[r][0][3] = 1            # West boundary
            self.walls[r][self.cols - 1][1] = 1 # East boundary
        for c in range(self.cols):
            self.walls[0][c][2] = 1            # South boundary
            self.walls[self.rows - 1][c][0] = 1 # North boundary

    def _read_sensors(self):
        """Helper to read all sensors (ToFs, encoders, gyro)."""
        tof_l, tof_c, tof_r = uct_mouse.get_tof()
        lenc, renc = uct_mouse.get_encoders()
        sensors = uct_mouse._mouse.get_sensors() if hasattr(uct_mouse, '_mouse') else {}
        gyro = sensors.get('gyro', 0.0)
        return tof_l, tof_c, tof_r, lenc, renc, gyro

    def _update_walls(self, tof_l, tof_c, tof_r):
        """
        TODO: Update self.walls for current cell (self.x, self.y) based on ToF readings.
        Remember to update symmetric wall entries in adjacent neighboring cells!
        """
        self.visited[self.y][self.x] = True
        # Student code here
        pass

    def check_for_target_room(self):
        """
        TODO: Scan self.walls to detect if a 2x2 block with NO internal cross-walls
        has been discovered anywhere in the explored map.
        Returns bottom-left (min_x, min_y) of the 2x2 room if found, else None.
        """
        # Student code here: check contiguous 2x2 cells for missing interior walls
        return None

    def turn_to(self, target_dir):
        """
        TODO: Turn in-place from self.dir to target_dir using closed-loop gyro feedback.
        Update self.dir upon completion.
        """
        if self.dir == target_dir:
            return
        # Student code here
        self.dir = target_dir

    def pirouette_360(self):
        """
        TODO: Execute an on-the-spot 360° clockwise spin using gyro feedback
        to signal target recognition.
        """
        print(">>> TARGET RECOGNIZED: Executing 360° victory pirouette! <<<")
        # Student code: spin until integrated gyro yaw accumulates 360 degrees
        pass

    def move_forward(self, speed_fast=False):
        """
        TODO: Drive forward exactly one cell (CELL_LENGTH_M) using closed-loop
        encoder + gyro control, with side-wall centering via ToFs.
        Update self.x and self.y upon arrival.
        """
        # Student code here
        self.x += DX[self.dir]
        self.y += DY[self.dir]

    def find_nearest_unvisited(self):
        """
        TODO: Use BFS / Floodfill to find the shortest path from (self.x, self.y)
        to the nearest unvisited cell.
        """
        # Student code here
        return None

    def find_shortest_path(self, start_pos, goal_pos):
        """
        TODO: Calculate optimal shortest path from start_pos to goal_pos using
        discovered wall matrix (e.g. Dijkstra, A*, or BFS).
        """
        # Student code here
        return []

    def solve(self):
        if not uct_mouse.init():
            return

        uct_mouse.set_polarity(1, 1)

        print("=== Starting 4-Stage Autonomous Micromouse Mission ===")
        
        # -----------------------------------------------------------------
        # Phase 1: Exploration & 2x2 Target Room Discovery
        # -----------------------------------------------------------------
        print("[Phase 1] Exploring maze and mapping walls...")
        while True:
            tof_l, tof_c, tof_r, _, _, _ = self._read_sensors()
            self._update_walls(tof_l, tof_c, tof_r)
            
            # Check if 2x2 target room has been discovered
            if not self.target_room:
                self.target_room = self.check_for_target_room()
                
            # If inside target room or all cells mapped, finish Phase 1
            if self.target_room and self.x >= self.target_room[0] and self.y >= self.target_room[1]:
                print("[Phase 1 Complete] Entered 2x2 Target Room!")
                break
                
            path = self.find_nearest_unvisited()
            if not path:
                print("[Phase 1 Complete] All reachable cells explored!")
                break
                
            # Move to next cell
            # Student code to turn_to and move_forward
            break # Scaffold placeholder

        # -----------------------------------------------------------------
        # Phase 2: Target Recognition Handshake (360° Pirouette)
        # -----------------------------------------------------------------
        print("[Phase 2] Executing Target Recognition Pirouette...")
        self.pirouette_360()

        # -----------------------------------------------------------------
        # Phase 3: Autonomous Return to Starting Cell (0,0)
        # -----------------------------------------------------------------
        print("[Phase 3] Navigating back to start (0,0)...")
        path_to_start = self.find_shortest_path((self.x, self.y), (0, 0))
        # Student code: traverse path_to_start back to (0,0) and face North
        print("[Phase 3 Complete] Returned safely to (0,0)!")

        # -----------------------------------------------------------------
        # Phase 4: High-Speed Solving Sprint
        # -----------------------------------------------------------------
        print("[Phase 4] Pausing 3.0s before High-Speed Sprint...")
        uct_mouse.delay_ms(3000)
        
        print("[Phase 4] Executing High-Speed Sprint to Target!")
        path_to_target = self.find_shortest_path((0, 0), self.target_room or (3, 5))
        # Student code: sprint along path_to_target with merged velocity profiling
        print("[Mission Complete] High-speed sprint finished inside target room!")

def main():
    solver = MazeSolver()
    solver.solve()

if __name__ == "__main__":
    main()
