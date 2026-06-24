import numpy as np

def get_lane_types_from_adjacency(adj_matrix):
    """
    Extract lane types for each arm from an adjacency matrix of shape (4, 22, 66).
    Returns:
        lane_types: dict mapping arm_idx (0-3) to a list of lane types for its 22 slots.
        Slot lane types are represented as strings: 'no_lane', 'L', 'T', 'R', 'LT', 'TR', 'LR', 'LTR'.
    """
    lane_types = {}
    for arm_idx in range(4):
        arm_types = []
        for slot_idx in range(22):
            row = adj_matrix[arm_idx, slot_idx]
            
            # Left turns: columns 0-21
            has_left = np.any(row[0:22] > 0.5)
            # Through turns: columns 22-43
            has_through = np.any(row[22:44] > 0.5)
            # Right turns: columns 44-65
            has_right = np.any(row[44:66] > 0.5)
            
            if not (has_left or has_through or has_right):
                arm_types.append('no_lane')
            elif has_left and has_through and has_right:
                arm_types.append('LTR')
            elif has_left and has_through:
                arm_types.append('LT')
            elif has_through and has_right:
                arm_types.append('TR')
            elif has_left and has_right:
                arm_types.append('LR')
            elif has_left:
                arm_types.append('L')
            elif has_through:
                arm_types.append('T')
            elif has_right:
                arm_types.append('R')
                
        lane_types[arm_idx] = arm_types
    return lane_types

def get_slot_turn_categories(adj_matrix):
    """
    Get counts of Left, Through, Right turning lanes, and Approach lanes for each arm.
    """
    categories = {}
    for arm_idx in range(4):
        arm_cats = {
            'left': 0,
            'through': 0,
            'right': 0,
            'approach': 0
        }
        for slot_idx in range(22):
            row = adj_matrix[arm_idx, slot_idx]
            has_left = np.any(row[0:22] > 0.5)
            has_through = np.any(row[22:44] > 0.5)
            has_right = np.any(row[44:66] > 0.5)
            
            if has_left:
                arm_cats['left'] += 1
            if has_through:
                arm_cats['through'] += 1
            if has_right:
                arm_cats['right'] += 1
            if has_left or has_through or has_right:
                arm_cats['approach'] += 1
                
        categories[arm_idx] = arm_cats
    return categories

def compute_f1_from_counts(y_true_counts, y_pred_counts, classes):
    """
    Compute Precision, Recall, and F1 score from count vectors.
    y_true_counts: list of dicts/lists of true counts per class
    y_pred_counts: list of dicts/lists of predicted counts per class
    """
    metrics = {}
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    class_tps = {c: 0 for c in classes}
    class_fps = {c: 0 for c in classes}
    class_fns = {c: 0 for c in classes}
    
    for yt, yp in zip(y_true_counts, y_pred_counts):
        for c in classes:
            true_c = yt.get(c, 0)
            pred_c = yp.get(c, 0)
            
            tp = min(true_c, pred_c)
            fp = max(0, pred_c - true_c)
            fn = max(0, true_c - pred_c)
            
            class_tps[c] += tp
            class_fps[c] += fp
            class_fns[c] += fn
            
            total_tp += tp
            total_fp += fp
            total_fn += fn
            
    # Class-wise metrics
    for c in classes:
        tp = class_tps[c]
        fp = class_fps[c]
        fn = class_fns[c]
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2.0 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        
        metrics[c] = {
            'precision': prec,
            'recall': rec,
            'f1': f1,
            'support': tp + fn
        }
        
    # Overall micro metrics
    micro_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = 2.0 * micro_prec * micro_rec / (micro_prec + micro_rec) if (micro_prec + micro_rec) > 0 else 0.0
    
    metrics['mean'] = {
        'precision': micro_prec,
        'recall': micro_rec,
        'f1': micro_f1,
        'support': total_tp + total_fn
    }
    
    return metrics

def get_baseline_counts(intersection_info):
    """
    Get the default rule-based baseline counts for each arm of an intersection.
    """
    arms = intersection_info['arms']
    is_3way = len(arms) == 3
    
    baseline_counts = {}
    
    # 7 lane types
    lane_types_list = ['L', 'LT', 'LTR', 'LR', 'T', 'TR', 'R']
    
    if not is_3way:
        # 4-way intersection baseline: each arm gets 1 LT and 1 TR lane
        for idx in range(4):
            baseline_counts[idx] = {c: 0 for c in lane_types_list}
            baseline_counts[idx]['LT'] = 1
            baseline_counts[idx]['TR'] = 1
    else:
        # 3-way intersection baseline
        # First sort by bearing to understand the clockwise ordering
        from .data_encoding import get_3way_transform_mapping
        new_arms, _ = get_3way_transform_mapping(arms)
        
        for idx in range(4):
            baseline_counts[idx] = {c: 0 for c in lane_types_list}
            arm = new_arms[idx]
            if arm.get('is_virtual'):
                # Virtual arm has no lanes
                continue
                
            # Determine which exit arms are physical relative to this arm
            left_virtual = new_arms[(idx + 1) % 4].get('is_virtual', False)
            through_virtual = new_arms[(idx + 2) % 4].get('is_virtual', False)
            right_virtual = new_arms[(idx + 3) % 4].get('is_virtual', False)
            
            if left_virtual:
                # Left is virtual, so Through and Right exist
                baseline_counts[idx]['T'] = 1
                baseline_counts[idx]['TR'] = 1
            elif through_virtual:
                # Through is virtual, so Left and Right exist (stem of T-junction)
                baseline_counts[idx]['L'] = 1
                baseline_counts[idx]['R'] = 1
            elif right_virtual:
                # Right is virtual, so Left and Through exist
                baseline_counts[idx]['T'] = 1
                baseline_counts[idx]['LT'] = 1
                
    return baseline_counts

def evaluate_predictions(y_true_matrices, y_pred_matrices, intersection_infos):
    """
    Evaluate predicted adjacency matrices against true matrices.
    Returns:
        results: dict containing turn-level, slot-level, and arm-level evaluation metrics.
    """
    # 1. Turn-level metrics (strict cell-by-cell matching)
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    for yt, yp in zip(y_true_matrices, y_pred_matrices):
        yt_bin = yt > 0.5
        yp_bin = yp > 0.5
        
        total_tp += np.sum(yt_bin & yp_bin)
        total_fp += np.sum((~yt_bin) & yp_bin)
        total_fn += np.sum(yt_bin & (~yp_bin))
        
    turn_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    turn_rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    turn_f1 = 2.0 * turn_prec * turn_rec / (turn_prec + turn_rec) if (turn_prec + turn_rec) > 0 else 0.0
    
    # 2. Slot turn-level metrics
    true_slot_cats = []
    pred_slot_cats = []
    
    for yt, yp in zip(y_true_matrices, y_pred_matrices):
        yt_cats = get_slot_turn_categories(yt)
        yp_cats = get_slot_turn_categories(yp)
        
        # We only evaluate for physical arms
        # If intersection is 3-way, get_baseline_counts will tell us which arm is virtual
        # or we can check which arms are virtual. But a simple check: if yt has no turns,
        # is it virtual? In the training data, a virtual arm has no approach lanes or exit lanes.
        for arm_idx in range(4):
            # Check if arm is virtual in ground truth: if it has no approach or exit slots
            # actually we can just include all arms since virtual arms should have 0 true and 0 pred,
            # which doesn't affect TP but might add to FP/FN if pred makes a mistake.
            true_slot_cats.append(yt_cats[arm_idx])
            pred_slot_cats.append(yp_cats[arm_idx])
            
    slot_classes = ['left', 'through', 'right', 'approach']
    slot_results = compute_f1_from_counts(true_slot_cats, pred_slot_cats, slot_classes)
    
    # 3. Arm-level lane type metrics
    true_lane_counts = []
    pred_lane_counts = []
    baseline_lane_counts = []
    
    lane_types_list = ['L', 'LT', 'LTR', 'LR', 'T', 'TR', 'R']
    
    for yt, yp, info in zip(y_true_matrices, y_pred_matrices, intersection_infos):
        yt_types = get_lane_types_from_adjacency(yt)
        yp_types = get_lane_types_from_adjacency(yp)
        yp_baseline = get_baseline_counts(info)
        
        for arm_idx in range(4):
            # Count occurrences of each type
            t_counts = {c: yt_types[arm_idx].count(c) for c in lane_types_list}
            p_counts = {c: yp_types[arm_idx].count(c) for c in lane_types_list}
            b_counts = yp_baseline[arm_idx]
            
            true_lane_counts.append(t_counts)
            pred_lane_counts.append(p_counts)
            baseline_lane_counts.append(b_counts)
            
    arm_results = compute_f1_from_counts(true_lane_counts, pred_lane_counts, lane_types_list)
    baseline_results = compute_f1_from_counts(true_lane_counts, baseline_lane_counts, lane_types_list)
    
    return {
        'turn_level': {
            'precision': turn_prec,
            'recall': turn_rec,
            'f1': turn_f1,
            'support': total_tp + total_fn
        },
        'slot_level': slot_results,
        'arm_level': arm_results,
        'baseline_level': baseline_results
    }
