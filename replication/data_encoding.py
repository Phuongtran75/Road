import json
import os
import numpy as np

def normalize_bearing(bearing):
    """Normalize bearing to be in [0, 360)."""
    b = bearing % 360
    return b

def get_3way_transform_mapping(arms):
    """
    Given a list of 3 arms (dicts with 'bearing' and 'label'),
    returns the mapping to map them to 4 arms.
    Returns:
        new_arms_info: list of 4 dicts. Virtual arm will have is_virtual=True.
        arm_mapping: dict mapping old label (1, 2, 3) to new label (1, 2, 3, 4).
    """
    # Sort arms by bearing clockwise (increasing bearing)
    sorted_arms = sorted(arms, key=lambda x: normalize_bearing(x['bearing']))
    
    # Calculate consecutive bearing differences
    diffs = []
    n = len(sorted_arms)
    for i in range(n):
        b_current = normalize_bearing(sorted_arms[i]['bearing'])
        b_next = normalize_bearing(sorted_arms[(i + 1) % n]['bearing'])
        diff = (b_next - b_current) % 360
        diffs.append(diff)
        
    # Find the index of the largest difference
    max_diff_idx = np.argmax(diffs)
    
    # Insert virtual arm at index (max_diff_idx + 1) % 3
    # The bearing of the virtual arm is set to the bearing of the arm at max_diff_idx
    ref_arm = sorted_arms[max_diff_idx]
    virtual_bearing = normalize_bearing(ref_arm['bearing'])
    
    virtual_arm = {
        'id': -1,
        'label': -1,
        'bearing': virtual_bearing,
        'file_name': None,
        'is_virtual': True,
        'arm_segments': []
    }
    
    # Construct the new list of 4 arms
    new_arms = []
    insert_idx = (max_diff_idx + 1) % 3
    
    for i in range(3):
        if i == insert_idx:
            new_arms.append(virtual_arm)
        new_arms.append(sorted_arms[i])
        
    # If the virtual arm is the last one (insert_idx was 0 but we appended at end? No, if insert_idx is 0,
    # the condition i == 0 triggers, we append virtual, then sorted_arms[0]. That's correct.)
    if len(new_arms) < 4:
        # Fallback if list is not 4
        new_arms.append(virtual_arm)
        
    # Assign new labels 1, 2, 3, 4 in clockwise order
    arm_mapping = {}
    new_arms_info = []
    for idx, arm in enumerate(new_arms[:4]):
        new_label = idx + 1
        if arm.get('is_virtual'):
            new_arm_dict = arm.copy()
            new_arm_dict['label'] = new_label
            new_arms_info.append(new_arm_dict)
        else:
            arm_mapping[arm['label']] = new_label
            new_arm_dict = arm.copy()
            new_arm_dict['label'] = new_label
            new_arm_dict['is_virtual'] = False
            new_arms_info.append(new_arm_dict)
            
    return new_arms_info, arm_mapping

class DatasetEncoder:
    def __init__(self, data_dir=r"f:\Road\main_task\data"):
        self.data_dir = data_dir
        
        # Load label files
        with open(os.path.join(data_dir, "labels", "intersections.json"), "r", encoding="utf-8") as f:
            self.intersections = json.load(f)
            
        with open(os.path.join(data_dir, "labels", "lanes", "lane_labels.json"), "r", encoding="utf-8") as f:
            self.lane_labels_raw = json.load(f)
            
        with open(os.path.join(data_dir, "labels", "turns", "turn_labels.json"), "r", encoding="utf-8") as f:
            self.turn_labels_raw = json.load(f)
            
        # Index lane labels by arm_id and lane_slot
        self.lane_labels = {}
        # The keys of lane_labels_raw are: ['arm_id', 'lane_slot', 'slip', 'left', 'through', 'right', 'approach', 'exit']
        num_lane_labels = len(self.lane_labels_raw['arm_id'])
        for idx_str in self.lane_labels_raw['arm_id'].keys():
            arm_id = self.lane_labels_raw['arm_id'][idx_str]
            slot = self.lane_labels_raw['lane_slot'][idx_str]
            
            if arm_id not in self.lane_labels:
                self.lane_labels[arm_id] = {}
                
            self.lane_labels[arm_id][slot] = {
                'slip': self.lane_labels_raw['slip'][idx_str],
                'left': self.lane_labels_raw['left'][idx_str],
                'through': self.lane_labels_raw['through'][idx_str],
                'right': self.lane_labels_raw['right'][idx_str],
                'approach': self.lane_labels_raw['approach'][idx_str],
                'exit': self.lane_labels_raw['exit'][idx_str]
            }
            
        # Index turns by intersection_id
        self.turn_labels = {}
        num_turn_labels = len(self.turn_labels_raw['intersection_id'])
        for idx_str in self.turn_labels_raw['intersection_id'].keys():
            inter_id = self.turn_labels_raw['intersection_id'][idx_str]
            if inter_id not in self.turn_labels:
                self.turn_labels[inter_id] = []
                
            self.turn_labels[inter_id].append({
                'approach_arm_id': self.turn_labels_raw['approach_arm_id'][idx_str],
                'approach_arm_label': self.turn_labels_raw['approach_arm_label'][idx_str],
                'approach_lane_slot': self.turn_labels_raw['approach_lane_slot'][idx_str],
                'exit_arm_id': self.turn_labels_raw['exit_arm_id'][idx_str],
                'exit_arm_label': self.turn_labels_raw['exit_arm_label'][idx_str],
                'exit_lane_slot': self.turn_labels_raw['exit_lane_slot'][idx_str]
            })

    def get_intersection_info(self, intersection_id):
        """Get the intersection dict from intersections.json."""
        for item in self.intersections:
            if item['id'] == intersection_id:
                return item
        return None

    def encode_lane_attributes(self, arm_id):
        """
        Encode lane slot attributes for a given arm into a (22, 8) numpy array.
        Attributes: [lane, lane_type, slip, left, through, right, approach, exit]
        where lane_type: 0 (no_lane), 1 (approach), 2 (exit).
        """
        arr = np.zeros((22, 8), dtype=np.float32)
        
        # Default lane_type to 0 (no_lane)
        # Check if we have labels for this arm
        if arm_id not in self.lane_labels:
            # If no labels or virtual arm, return all zeros
            return arr
            
        arm_slots = self.lane_labels[arm_id]
        for slot in range(1, 23):
            row_idx = slot - 1
            if slot in arm_slots:
                s_data = arm_slots[slot]
                is_approach = s_data['approach']
                is_exit = s_data['exit']
                
                # lane_type: 0 if no lane, 1 if approach, 2 if exit
                l_type = 0
                if is_approach == 1:
                    l_type = 1
                elif is_exit == 1:
                    l_type = 2
                    
                has_lane = 1.0 if (is_approach == 1 or is_exit == 1) else 0.0
                
                arr[row_idx, 0] = has_lane
                arr[row_idx, 1] = l_type
                arr[row_idx, 2] = s_data['slip']
                arr[row_idx, 3] = s_data['left']
                arr[row_idx, 4] = s_data['through']
                arr[row_idx, 5] = s_data['right']
                arr[row_idx, 6] = is_approach
                arr[row_idx, 7] = is_exit
                
        return arr

    def encode_intersection_turns(self, intersection_id):
        """
        Encode turn labels for an intersection into a (4, 22, 66) adjacency matrix.
        Handles 3-way transformation automatically.
        """
        inter_info = self.get_intersection_info(intersection_id)
        if not inter_info:
            return np.zeros((4, 22, 66), dtype=np.float32)
            
        arms = inter_info['arms']
        is_3way = len(arms) == 3
        
        if is_3way:
            new_arms, arm_mapping = get_3way_transform_mapping(arms)
        else:
            new_arms = sorted(arms, key=lambda x: normalize_bearing(x['bearing']))
            arm_mapping = {arm['label']: idx + 1 for idx, arm in enumerate(new_arms)}
            
        adj_matrix = np.zeros((4, 22, 66), dtype=np.float32)
        
        # Get raw turn labels
        turns = self.turn_labels.get(intersection_id, [])
        
        for turn in turns:
            old_app_label = turn['approach_arm_label']
            old_exit_label = turn['exit_arm_label']
            
            # Map labels using the 3-way/4-way conversion mapping
            if old_app_label not in arm_mapping or old_exit_label not in arm_mapping:
                continue
                
            new_app_label = arm_mapping[old_app_label]
            new_exit_label = arm_mapping[old_exit_label]
            
            app_idx = new_app_label - 1   # 0 to 3
            exit_idx = new_exit_label - 1 # 0 to 3
            
            app_slot = turn['approach_lane_slot'] # 1 to 22
            exit_slot = turn['exit_lane_slot']     # 1 to 22
            
            app_row = app_slot - 1
            
            # Calculate exit arm offset clockwise
            d = (exit_idx - app_idx) % 4
            if d == 1:   # Left arm
                col = 0 + (exit_slot - 1)
            elif d == 2: # Through arm
                col = 22 + (exit_slot - 1)
            elif d == 3: # Right arm
                col = 44 + (exit_slot - 1)
            else:        # U-turn (not considered)
                continue
                
            adj_matrix[app_idx, app_row, col] = 1.0
            
        return adj_matrix

def apply_slot_shift_augmentation(lane_matrix, adj_matrix=None, max_shift=1):
    """
    Randomly shift the lane slot attributes horizontally by up to max_shift slots
    independently for each arm. Shifts the turn adjacency matrix correspondingly.
    
    Per Nilsson 2024 (p.40): "The maximum threshold was further constrained
    such that no positive turn labels were omitted." Shifts are clamped so no
    positive label is pushed off the edge.
    
    lane_matrix: shape (4, 22, 8)
    adj_matrix: shape (4, 22, 66), optional
    """
    new_lane_matrix = lane_matrix.copy()
    new_adj_matrix = adj_matrix.copy() if adj_matrix is not None else None
    
    # Generate random shifts for each of the 4 arms, then clamp to preserve positives
    shifts = np.random.randint(-max_shift, max_shift + 1, size=4)
    
    for arm_idx in range(4):
        # Clamp shift to preserve positive labels in lane_matrix
        # Find first and last slots with any positive attribute
        arm_feats = lane_matrix[arm_idx]  # (22, 8)
        positive_mask = np.any(arm_feats != 0, axis=1)  # (22,)
        
        if adj_matrix is not None:
            # Also check adjacency matrix rows for this approach arm
            adj_row_mask = np.any(adj_matrix[arm_idx] != 0, axis=1)  # (22,)
            positive_mask = positive_mask | adj_row_mask
            
        if np.any(positive_mask):
            positive_indices = np.where(positive_mask)[0]
            first_pos = positive_indices[0]
            last_pos = positive_indices[-1]
            # Positive shift moves data right: first_pos + shift >= 0 => shift >= -first_pos
            # Negative shift moves data left: last_pos + shift <= 21 => shift <= 21 - last_pos
            min_allowed = -first_pos
            max_allowed = 21 - last_pos
            shifts[arm_idx] = np.clip(shifts[arm_idx], min_allowed, max_allowed)
        
        shift = shifts[arm_idx]
        if shift == 0:
            continue
            
        # Shift lane slot attributes of the arm
        # Features are shape (22, 8)
        shifted_feats = np.zeros_like(arm_feats)
        
        if shift > 0:
            shifted_feats[shift:] = arm_feats[:-shift]
        else:
            shifted_feats[:shift] = arm_feats[-shift:]
            
        new_lane_matrix[arm_idx] = shifted_feats
        
        if adj_matrix is not None:
            # Shift the turn matrix rows for this approach arm by `shift`
            # adj_matrix[arm_idx] is of shape (22, 66)
            arm_turns = adj_matrix[arm_idx]
            shifted_turns = np.zeros_like(arm_turns)
            if shift > 0:
                shifted_turns[shift:] = arm_turns[:-shift]
            else:
                shifted_turns[:shift] = arm_turns[-shift:]
            new_adj_matrix[arm_idx] = shifted_turns
            
    if adj_matrix is not None:
        # Also need to shift the columns corresponding to exit slots!
        # For a given approach arm, the columns 0-21 (Left), 22-43 (Through), 44-65 (Right)
        # correspond to the exit slots of exit arms:
        # Left exit arm: (approach_arm + 1) % 4
        # Through exit arm: (approach_arm + 2) % 4
        # Right exit arm: (approach_arm + 3) % 4
        # Since the exit arm slots are shifted, we must shift the corresponding columns!
        final_adj_matrix = new_adj_matrix.copy()
        
        for app_idx in range(4):
            # Left exit arm index and its shift
            left_exit_idx = (app_idx + 1) % 4
            left_shift = shifts[left_exit_idx]
            if left_shift != 0:
                col_slice = new_adj_matrix[app_idx, :, 0:22]
                shifted_slice = np.zeros_like(col_slice)
                if left_shift > 0:
                    shifted_slice[:, left_shift:] = col_slice[:, :-left_shift]
                else:
                    shifted_slice[:, :left_shift] = col_slice[:, -left_shift:]
                final_adj_matrix[app_idx, :, 0:22] = shifted_slice
                
            # Through exit arm index and its shift
            through_exit_idx = (app_idx + 2) % 4
            through_shift = shifts[through_exit_idx]
            if through_shift != 0:
                col_slice = new_adj_matrix[app_idx, :, 22:44]
                shifted_slice = np.zeros_like(col_slice)
                if through_shift > 0:
                    shifted_slice[:, through_shift:] = col_slice[:, :-through_shift]
                else:
                    shifted_slice[:, :through_shift] = col_slice[:, -through_shift:]
                final_adj_matrix[app_idx, :, 22:44] = shifted_slice
                
            # Right exit arm index and its shift
            right_exit_idx = (app_idx + 3) % 4
            right_shift = shifts[right_exit_idx]
            if right_shift != 0:
                col_slice = new_adj_matrix[app_idx, :, 44:66]
                shifted_slice = np.zeros_like(col_slice)
                if right_shift > 0:
                    shifted_slice[:, right_shift:] = col_slice[:, :-right_shift]
                else:
                    shifted_slice[:, :right_shift] = col_slice[:, -right_shift:]
                final_adj_matrix[app_idx, :, 44:66] = shifted_slice
                
        return new_lane_matrix, final_adj_matrix
        
    return new_lane_matrix

def apply_rotation_augmentation(lane_matrix, adj_matrix, img=None, k=None):
    """
    Rotate the intersection configuration clockwise by k * 90 degrees.
    k is a random integer in [0, 3].
    
    If img is provided, it will also rotate the image correspondingly:
    rotated_img = np.rot90(img, -k, axes=(1, 2))  # for PyTorch image tensor shape (C, H, W)
    """
    if k is None:
        k = np.random.randint(0, 4)
        
    if k == 0:
        if img is not None:
            return lane_matrix, adj_matrix, img, 0
        return lane_matrix, adj_matrix, 0
        
    # Rotate lane_matrix (shape 4, 22, 8) along the arm dimension (axis 0)
    # Stacking clockwise order, so rotating by k shifts the arms by k
    new_lane_matrix = np.roll(lane_matrix, k, axis=0)
    
    # Rotate turn adjacency matrix (shape 4, 22, 66)
    # The approach arm dimension (axis 0) is rolled by k.
    new_adj_matrix = np.roll(adj_matrix, k, axis=0)
    
    # Also, the columns of the adjacency matrix represent exit arms relative to approach arms
    # Wait, do the exit arm columns change their meaning after rolling?
    # Let's think:
    # "The exit arms are ordered in terms of offset order from the approach arm... proceeding left, through, and right."
    # Since the columns are *relative* to the approach arm, their relative positions (Left, Through, Right)
    # do NOT change when we rotate the whole intersection!
    # For example, if we rotate the intersection, the arm to the left of the new arm 1 is still the new arm 2.
    # So the relative offsets remain exactly the same!
    # This is the beauty of relative encoding: the adjacency columns do NOT need to be rolled when we rotate!
    # Let's verify this:
    # Yes! Because columns are relative (Left = +1, Through = +2, Right = +3).
    # Since they are relative, they are invariant to absolute rotations of the intersection!
    # This is a major mathematical benefit of relative encoding!
    
    if img is not None:
        # Rotate image clockwise: np.rot90 rotates counter-clockwise by default,
        # so for clockwise we pass -k
        # If img is a PyTorch tensor, we can use torch.rot90:
        # torch.rot90(img, -k, [1, 2])
        # If it's a numpy array of shape (C, H, W)
        import torch
        if isinstance(img, torch.Tensor):
            rotated_img = torch.rot90(img, -k, [1, 2])
        else:
            rotated_img = np.rot90(img, -k, axes=(1, 2))
        return new_lane_matrix, new_adj_matrix, rotated_img, k
        
    return new_lane_matrix, new_adj_matrix, k
