import numpy as np

def get_exit_arm_and_slot(approach_arm, col):
    """
    Get the exit arm index (0-3) and exit slot index (0-21)
    and turn type (0: Left, 1: Through, 2: Right) based on
    the approach arm index (0-3) and column index (0-65).
    """
    turn_type = col // 22  # 0: Left, 1: Through, 2: Right
    exit_slot = col % 22   # 0 to 21 (slot index)
    
    if turn_type == 0:     # Left exit arm: (approach_arm + 1) % 4
        exit_arm = (approach_arm + 1) % 4
    elif turn_type == 1:   # Through exit arm: (approach_arm + 2) % 4
        exit_arm = (approach_arm + 2) % 4
    else:                  # Right exit arm: (approach_arm + 3) % 4
        exit_arm = (approach_arm + 3) % 4
        
    return exit_arm, exit_slot, turn_type

def apply_pph(adj_matrix, threshold=0.5):
    """
    Apply Post-Processing Heuristic (PPH) rules to an adjacency matrix.
    
    Two-phase approach per the paper (Nilsson 2024, Section 3.9):
      Phase 1: Process ALL turns in descending probability order, classifying
               each as consistent or inconsistent based on heuristic rules.
      Phase 2: Apply the probability threshold only to the consistent turns
               to produce the final binary adjacency matrix.
    
    Parameters:
    -----------
    adj_matrix : np.ndarray
        Array of shape (4, 22, 66) containing connection probabilities.
    threshold : float
        Probability threshold for binarization of consistent turns.
        
    Returns:
    --------
    binary_matrix : np.ndarray
        Binary adjacency matrix of shape (4, 22, 66) with only consistent turns.
    """
    # 1. Flatten all potential turns with their probabilities and coordinates
    turns = []
    for app_arm in range(4):
        for app_slot in range(22):
            for col in range(66):
                prob = adj_matrix[app_arm, app_slot, col]
                exit_arm, exit_slot, turn_type = get_exit_arm_and_slot(app_arm, col)
                turns.append({
                    'prob': prob,
                    'app_arm': app_arm,
                    'app_slot': app_slot,
                    'exit_arm': exit_arm,
                    'exit_slot': exit_slot,
                    'turn_type': turn_type,
                    'col': col
                })
                
    # 2. Sort turns by probability in descending order
    turns.sort(key=lambda x: x['prob'], reverse=True)
    
    # Phase 1: Classify ALL turns as consistent or inconsistent
    # Process in descending probability order; only already-accepted (consistent)
    # turns constrain future turns.
    consistent_turns = []
    
    for turn in turns:
        app_arm = turn['app_arm']
        app_slot = turn['app_slot']
        exit_arm = turn['exit_arm']
        exit_slot = turn['exit_slot']
        turn_type = turn['turn_type']
        
        is_consistent = True
        
        # Rule 6: No turns from the same approach arm to the same exit arm and lane slot
        for act in consistent_turns:
            if act['app_arm'] == app_arm and act['exit_arm'] == exit_arm and act['exit_slot'] == exit_slot:
                is_consistent = False
                break
                
        if not is_consistent:
            continue
            
        # Rules 1 & 2: For any arm, approach slots must be to the left of exit slots.
        # Check app_arm: the new turn marks app_slot as approach.
        # app_slot must be strictly to the left of any exit_slots on app_arm.
        for act in consistent_turns:
            if act['exit_arm'] == app_arm:
                if app_slot >= act['exit_slot']:
                    is_consistent = False
                    break
        if not is_consistent:
            continue
            
        # Check exit_arm: the new turn marks exit_slot as exit.
        # exit_slot must be strictly to the right of any approach_slots on exit_arm.
        for act in consistent_turns:
            if act['app_arm'] == exit_arm:
                if exit_slot <= act['app_slot']:
                    is_consistent = False
                    break
        if not is_consistent:
            continue
            
        # Rules 3, 4, 5: Turn-type ordering on the same approach arm
        # Left (0) <= Through (1) <= Right (2) from left to right slots
        for act in consistent_turns:
            if act['app_arm'] == app_arm:
                if app_slot < act['app_slot'] and turn_type > act['turn_type']:
                    is_consistent = False
                    break
                if app_slot > act['app_slot'] and turn_type < act['turn_type']:
                    is_consistent = False
                    break
        if not is_consistent:
            continue
            
        # If all checks pass, mark as consistent
        consistent_turns.append(turn)
        
    # Phase 2: Apply threshold only to consistent turns to produce binary output
    binary_matrix = np.zeros_like(adj_matrix)
    for turn in consistent_turns:
        if turn['prob'] >= threshold:
            binary_matrix[turn['app_arm'], turn['app_slot'], turn['col']] = 1.0
        
    return binary_matrix
