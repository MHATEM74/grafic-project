# games/street_crosser/lanes.py
import random
from core.constants import SCREEN_W

def generate_level(level_idx):
    lanes = []
    safe_zones = []
    
    # Bottom safe zone (Start)
    safe_zones.append({"y": 700, "h": 68})
    
    # More difficult levels have faster cars and fewer safe zones
    num_blocks = 3 + level_idx
    y_pos = 660
    
    for i in range(num_blocks):
        num_lanes_in_block = random.randint(3, 5 + level_idx)
        
        for j in range(num_lanes_in_block):
            speed_base = 2 + level_idx * 0.5 + random.random() * 2
            dir_ = random.choice([-1, 1])
            types = ["Car", "Taxi"]
            if level_idx > 1: types += ["Bus", "Truck"]
            if level_idx > 3: types += ["Racecar", "Bike", "Ambulance"]
            
            lanes.append({
                "y": y_pos,
                "h": 40,
                "speed": speed_base,
                "dir": dir_,
                "types": random.sample(types, min(3, len(types))),
                "spawn_rate": random.randint(60, 120) - min(40, level_idx * 5)
            })
            y_pos -= 40
            
        # Add a safe zone after a block, except at the very top
        if i < num_blocks - 1:
            safe_zones.append({"y": y_pos, "h": 40})
            y_pos -= 40
            
    # Top safe zone (Goal)
    goal_y = y_pos
    safe_zones.append({"y": 0, "h": goal_y + 40})
    
    return lanes, safe_zones, goal_y
