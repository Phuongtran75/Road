"""
Part 8: Post-Processing Heuristic & Evaluation
================================================
Demo PPH rules trên sample adjacency matrix, compute evaluation metrics.

Reference: Nilsson 2024 Section 3.9, Section 4
"""
import os
import sys
import json
import io
import numpy as np

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, r"f:\Road")
from replication.data_encoding import DatasetEncoder
from replication.post_processing import apply_pph, get_exit_arm_and_slot
from replication.evaluation import (
    evaluate_predictions,
    get_lane_types_from_adjacency,
    get_slot_turn_categories,
    get_baseline_counts,
)

DATA_DIR = r"f:\Road\main_task\data"


def demo_pph_rules():
    """Demo PPH rules trên ground truth + noise."""
    print("=" * 70)
    print("1. POST-PROCESSING HEURISTIC (PPH) DEMO")
    print("=" * 70)

    encoder = DatasetEncoder(DATA_DIR)

    split_path = os.path.join(DATA_DIR, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)

    sample_id = splits["test"][0]
    gt_adj = encoder.encode_intersection_turns(sample_id)

    print(f"\nIntersection: {sample_id}")
    gt_count = int(np.sum(gt_adj > 0.5))
    print(f"Ground truth connections: {gt_count}")

    # Create noisy prediction (GT + random noise)
    np.random.seed(42)
    noise = np.random.uniform(-0.3, 0.3, size=gt_adj.shape)
    noisy_probs = np.clip(gt_adj * 0.8 + noise * 0.3, 0, 1)

    # Also add some false positives
    for _ in range(10):
        a = np.random.randint(0, 4)
        s = np.random.randint(0, 22)
        c = np.random.randint(0, 66)
        noisy_probs[a, s, c] = np.random.uniform(0.4, 0.7)

    print(f"\nNoisy prediction:")
    print(f"  Cells > 0.5 (before PPH): "
          f"{int(np.sum(noisy_probs > 0.5))}")

    # Apply PPH
    binary = apply_pph(noisy_probs, threshold=0.5)
    pph_count = int(np.sum(binary > 0.5))

    print(f"  Cells > 0.5 (after PPH):  {pph_count}")
    print(f"  Removed by PPH: "
          f"{int(np.sum(noisy_probs > 0.5)) - pph_count}")

    # Compare with ground truth
    tp = int(np.sum((gt_adj > 0.5) & (binary > 0.5)))
    fp = int(np.sum((gt_adj <= 0.5) & (binary > 0.5)))
    fn = int(np.sum((gt_adj > 0.5) & (binary <= 0.5)))

    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0

    print(f"\n  vs Ground Truth:")
    print(f"    TP={tp}, FP={fp}, FN={fn}")
    print(f"    Precision: {prec:.4f}")
    print(f"    Recall:    {rec:.4f}")
    print(f"    F1:        {f1:.4f}")

    return gt_adj, binary, sample_id


def demo_pph_step_by_step():
    """Step-by-step trace of PPH on a small example."""
    print("\n" + "=" * 70)
    print("2. PPH STEP-BY-STEP TRACE")
    print("=" * 70)

    # Create a small hand-crafted example
    adj = np.zeros((4, 22, 66), dtype=np.float32)

    # Arm 0, slot 5: through (consistent)
    adj[0, 5, 25] = 0.95  # through exit arm, slot 4

    # Arm 0, slot 6: through (consistent)
    adj[0, 6, 26] = 0.90  # through exit arm, slot 5

    # Arm 0, slot 5: right (violates rule 3-5: left of slot 6 but right turn)
    adj[0, 5, 48] = 0.85  # right exit arm, slot 5

    # Arm 0, slot 4: left (consistent: left of through slots)
    adj[0, 4, 3] = 0.80   # left exit arm, slot 4

    # Arm 0, slot 7: right (consistent: right of through slots)
    adj[0, 7, 50] = 0.75  # right exit arm, slot 7

    # Duplicate exit: arm 0, slot 8 → same exit as slot 6 (violates rule 6)
    adj[0, 8, 26] = 0.70  # through exit arm, slot 5 (same as slot 6's exit)

    print(f"\nHand-crafted example (6 potential turns):")
    turns_desc = [
        (0, 5, 25, 0.95, "Through (slot 6 → through arm slot 4)"),
        (0, 6, 26, 0.90, "Through (slot 7 → through arm slot 5)"),
        (0, 5, 48, 0.85, "Right (slot 6 → right arm slot 5) — CONFLICT"),
        (0, 4, 3,  0.80, "Left (slot 5 → left arm slot 4)"),
        (0, 7, 50, 0.75, "Right (slot 8 → right arm slot 7)"),
        (0, 8, 26, 0.70, "Through (slot 9 → through arm slot 5) — DUPLICATE"),
    ]

    for a, s, c, p, desc in turns_desc:
        print(f"  prob={p:.2f}: Arm {a}, slot {s+1}, col {c} — {desc}")

    # Apply PPH
    binary = apply_pph(adj, threshold=0.5)
    accepted = int(np.sum(binary > 0.5))

    print(f"\nAfter PPH: {accepted} accepted (out of 6)")
    print(f"\nAccepted turns:")
    for a in range(4):
        for s in range(22):
            for c in range(66):
                if binary[a, s, c] > 0.5:
                    exit_arm, exit_slot, turn_type = get_exit_arm_and_slot(a, c)
                    type_name = {0: "Left", 1: "Through", 2: "Right"}[turn_type]
                    print(f"  Arm {a}, slot {s+1} → exit arm {exit_arm}, "
                          f"slot {exit_slot+1} ({type_name})")


def demo_evaluation():
    """Demo evaluation metrics trên test set."""
    print("\n" + "=" * 70)
    print("3. EVALUATION METRICS")
    print("=" * 70)

    encoder = DatasetEncoder(DATA_DIR)

    split_path = os.path.join(DATA_DIR, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)

    test_ids = splits["test"][:10]  # Subset for speed

    y_true = []
    y_pred = []
    infos = []

    for inter_id in test_ids:
        gt = encoder.encode_intersection_turns(inter_id)
        info = encoder.get_intersection_info(inter_id)

        # Simulate prediction: GT with noise → PPH
        np.random.seed(inter_id % 1000)
        noise = np.random.uniform(-0.2, 0.2, size=gt.shape)
        pred_probs = np.clip(gt * 0.85 + noise * 0.2, 0, 1)
        pred_binary = apply_pph(pred_probs, threshold=0.5)

        y_true.append(gt)
        y_pred.append(pred_binary)
        infos.append(info)

    results = evaluate_predictions(y_true, y_pred, infos)

    # Turn-level
    tl = results["turn_level"]
    print(f"\n--- Turn-level metrics ---")
    print(f"  Precision: {tl['precision']:.4f}")
    print(f"  Recall:    {tl['recall']:.4f}")
    print(f"  F1:        {tl['f1']:.4f}")
    print(f"  Support:   {tl['support']}")

    # Slot-level
    print(f"\n--- Slot turn-level metrics ---")
    sl = results["slot_level"]
    print(f"  {'Class':>10s}  {'Prec':>6s}  {'Rec':>6s}  {'F1':>6s}  {'Support':>7s}")
    print(f"  {'─'*10}  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*7}")
    for cls in ["left", "through", "right", "approach", "mean"]:
        if cls in sl:
            m = sl[cls]
            print(f"  {cls:>10s}  {m['precision']:.4f}  {m['recall']:.4f}  "
                  f"{m['f1']:.4f}  {m['support']:>7d}")

    # Arm-level
    print(f"\n--- Arm-level lane type metrics ---")
    al = results["arm_level"]
    print(f"  {'Type':>6s}  {'Prec':>6s}  {'Rec':>6s}  {'F1':>6s}  {'Support':>7s}")
    print(f"  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*7}")
    for lt in ["L", "LT", "T", "TR", "R", "LTR", "LR", "mean"]:
        if lt in al:
            m = al[lt]
            if m["support"] > 0:
                print(f"  {lt:>6s}  {m['precision']:.4f}  {m['recall']:.4f}  "
                      f"{m['f1']:.4f}  {m['support']:>7d}")

    # Baseline comparison
    print(f"\n--- Baseline (rule-based) comparison ---")
    bl = results["baseline_level"]
    print(f"  {'Type':>6s}  {'Model F1':>8s}  {'Baseline F1':>11s}")
    print(f"  {'─'*6}  {'─'*8}  {'─'*11}")
    for lt in ["L", "LT", "T", "TR", "R", "mean"]:
        if lt in al and lt in bl:
            m_f1 = al[lt]["f1"]
            b_f1 = bl[lt]["f1"]
            better = "✓" if m_f1 > b_f1 else " "
            print(f"  {lt:>6s}  {m_f1:8.4f}  {b_f1:11.4f}  {better}")


def demo_lane_type_extraction():
    """Demo extracting lane types from adjacency matrix."""
    print("\n" + "=" * 70)
    print("4. LANE TYPE EXTRACTION")
    print("=" * 70)

    encoder = DatasetEncoder(DATA_DIR)

    split_path = os.path.join(DATA_DIR, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)

    sample_id = splits["test"][0]
    adj = encoder.encode_intersection_turns(sample_id)

    lane_types = get_lane_types_from_adjacency(adj)
    turn_cats = get_slot_turn_categories(adj)

    print(f"\nIntersection: {sample_id}")
    for arm in range(4):
        types = lane_types[arm]
        active = [t for t in types if t != "no_lane"]
        cats = turn_cats[arm]

        if active:
            print(f"\n  Arm {arm}:")
            print(f"    Lane types: {active}")
            print(f"    Counts: L={cats['left']}, T={cats['through']}, "
                  f"R={cats['right']}, approach={cats['approach']}")


def main():
    print("PAPER BREAKDOWN — PART 8: POST-PROCESSING & EVALUATION")
    print("Nilsson 2024 & 2026")
    print()

    demo_pph_rules()
    demo_pph_step_by_step()
    demo_evaluation()
    demo_lane_type_extraction()

    print("\n" + "=" * 70)
    print("DONE. Kết luận:")
    print("  - PPH: 2-phase (classify all → threshold consistent)")
    print("  - 6 rules đảm bảo: separation, ordering, uniqueness")
    print("  - Evaluation: 3 cấp (turn, slot, arm-level)")
    print("  - Baseline: rule-based (1 LT + 1 TR per arm cho 4-way)")
    print("=" * 70)


if __name__ == "__main__":
    main()
