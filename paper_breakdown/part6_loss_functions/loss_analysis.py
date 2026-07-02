"""
Part 6: Loss Functions
=======================
Compute N/P ratios, visualize class weights, demo LaneLoss and TurnLoss.

Reference: Nilsson 2024 Table 4-5, Section 3.7-3.8
"""
import os
import sys
import json
import io
import numpy as np
import torch

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, r"f:\Road")
from replication.data_encoding import DatasetEncoder
from replication.losses import LaneLoss, TurnLoss, SoftDiceLoss

DATA_DIR = r"f:\Road\main_task\data"


def compute_lane_np_ratios():
    """Compute N/P ratios cho lane attributes từ training data."""
    print("=" * 70)
    print("1. LANE CLASS N/P RATIOS")
    print("=" * 70)

    encoder = DatasetEncoder(DATA_DIR)

    split_path = os.path.join(DATA_DIR, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
    train_ids = splits["train"]

    # Collect all lane attributes
    attr_names = ["lane", "lane_type", "slip", "left", "through",
                  "right", "approach", "exit"]
    total_slots = 0
    positive_counts = {n: 0 for n in attr_names if n != "lane_type"}

    for inter_id in train_ids:
        info = encoder.get_intersection_info(inter_id)
        if not info:
            continue
        for arm in info["arms"]:
            attrs = encoder.encode_lane_attributes(arm["id"])  # (22, 8)
            total_slots += 22
            positive_counts["lane"] += int(np.sum(attrs[:, 0] > 0))
            positive_counts["slip"] += int(np.sum(attrs[:, 2] > 0))
            positive_counts["left"] += int(np.sum(attrs[:, 3] > 0))
            positive_counts["through"] += int(np.sum(attrs[:, 4] > 0))
            positive_counts["right"] += int(np.sum(attrs[:, 5] > 0))
            positive_counts["approach"] += int(np.sum(attrs[:, 6] > 0))
            positive_counts["exit"] += int(np.sum(attrs[:, 7] > 0))

    print(f"\nTotal lane slots analyzed: {total_slots}")
    print(f"\n{'Class':>12s}  {'Positive':>8s}  {'Negative':>8s}  "
          f"{'N/P Ratio':>10s}  {'Weight (cap=30)':>15s}")
    print(f"{'─'*12}  {'─'*8}  {'─'*8}  {'─'*10}  {'─'*15}")

    # Paper values for comparison
    paper_values = {
        "lane": 4.80, "approach": 10.07, "exit": 11.18,
        "through": 13.72, "left": 26.29, "right": 27.57, "slip": 2118.81
    }

    for name in ["lane", "approach", "exit", "through", "left", "right", "slip"]:
        p = positive_counts[name]
        n = total_slots - p
        ratio = n / p if p > 0 else float("inf")
        weight = min(ratio, 30.0)
        paper = paper_values.get(name, "?")
        print(f"{name:>12s}  {p:8d}  {n:8d}  {ratio:10.2f}  "
              f"{weight:15.2f}  (paper: {paper})")


def compute_turn_np_ratios():
    """Compute cell-wise N/P ratios cho turn adjacency matrix."""
    print("\n" + "=" * 70)
    print("2. TURN CELL-WISE N/P RATIOS")
    print("=" * 70)

    encoder = DatasetEncoder(DATA_DIR)

    split_path = os.path.join(DATA_DIR, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
    train_ids = splits["train"][:50]  # Subset for speed

    # Collect adjacency matrices
    matrices = []
    for inter_id in train_ids:
        matrices.append(encoder.encode_intersection_turns(inter_id))
    y_arr = np.stack(matrices)  # (N, 4, 22, 66)

    positives = np.sum(y_arr, axis=0)  # (4, 22, 66)
    N = len(train_ids)
    negatives = N - positives

    np_ratios = np.zeros_like(positives)
    for a in range(4):
        for s in range(22):
            for c in range(66):
                p = positives[a, s, c]
                np_ratios[a, s, c] = 1000.0 if p == 0 else negatives[a, s, c] / p

    print(f"\nAnalyzed {N} intersections")
    print(f"Adjacency matrix shape per intersection: (4, 22, 66)")
    print(f"Total cells: {4*22*66} = {4*22*66}")

    # Statistics
    total_positive_cells = int(np.sum(positives > 0))
    total_cells = 4 * 22 * 66
    almost_impossible = int(np.sum(np_ratios >= 1000))

    print(f"\nCell statistics:")
    print(f"  Cells with at least 1 positive: {total_positive_cells} "
          f"({total_positive_cells/total_cells*100:.1f}%)")
    print(f"  'Almost impossible' cells (N/P ≥ 1000): {almost_impossible} "
          f"({almost_impossible/total_cells*100:.1f}%)")
    print(f"  'Area of interest' cells (N/P < 1000): "
          f"{total_cells - almost_impossible}")

    # N/P ratio distribution
    valid_ratios = np_ratios[np_ratios < 1000]
    if len(valid_ratios) > 0:
        print(f"\nN/P ratio distribution (cells with positives):")
        print(f"  Min:    {valid_ratios.min():.2f}")
        print(f"  Median: {np.median(valid_ratios):.2f}")
        print(f"  Mean:   {valid_ratios.mean():.2f}")
        print(f"  Max:    {valid_ratios.max():.2f}")

    return np_ratios


def demo_lane_loss():
    """Demo LaneLoss forward pass."""
    print("\n" + "=" * 70)
    print("3. LANE LOSS DEMO")
    print("=" * 70)

    criterion = LaneLoss()
    print(f"\nLoss weights:")
    for k, v in criterion.loss_weights.items():
        print(f"  {k}: {v}")
    print(f"\nPositive weights:")
    for k, v in criterion.pos_weights.items():
        print(f"  {k}: {v}")

    # Dummy forward pass
    B = 4
    preds = {
        "lane": torch.randn(B, 22),
        "lane_type": torch.randn(B, 3, 22),
        "left": torch.randn(B, 22),
        "through": torch.randn(B, 22),
        "right": torch.randn(B, 22),
        "slip": torch.randn(B, 22),
    }
    targets = {
        "lane": torch.zeros(B, 22),
        "lane_type": torch.zeros(B, 22, dtype=torch.long),
        "left": torch.zeros(B, 22),
        "through": torch.zeros(B, 22),
        "right": torch.zeros(B, 22),
        "slip": torch.zeros(B, 22),
    }
    # Set some positives
    targets["lane"][:, 5:8] = 1.0
    targets["lane_type"][:, 5:7] = 1  # approach
    targets["lane_type"][:, 7] = 2    # exit
    targets["left"][:, 5] = 1.0
    targets["through"][:, 6] = 1.0
    targets["right"][:, 7] = 1.0  # use as approach-right since exit doesn't have turn

    loss = criterion(preds, targets)
    print(f"\nLoss value: {loss.item():.4f}")


def demo_turn_loss(np_ratios):
    """Demo TurnLoss forward pass."""
    print("\n" + "=" * 70)
    print("4. TURN LOSS DEMO")
    print("=" * 70)

    criterion = TurnLoss(np_ratios=np_ratios)

    print(f"\nTurnLoss parameters:")
    print(f"  CE weight (area of interest): {criterion.ce_weight_interest}")
    print(f"  CE weight (almost impossible): {criterion.ce_weight_impossible}")
    print(f"  Dice weight: {criterion.dice_weight}")
    print(f"  Weight cap: {criterion.weight_cap}")
    print(f"  N/P threshold: {criterion.np_threshold}")

    almost_impossible_count = int(criterion.almost_impossible_mask.sum())
    total = criterion.almost_impossible_mask.numel()
    print(f"\n  Almost impossible cells: {almost_impossible_count} / {total} "
          f"({almost_impossible_count/total*100:.1f}%)")

    # Dummy forward pass
    B = 2
    pred_logits = torch.randn(B, 4, 22, 66)
    targets = torch.zeros(B, 4, 22, 66)
    targets[:, 0, 5, 25] = 1.0  # approach arm 0, slot 6, through exit slot 4

    loss = criterion(pred_logits, targets)
    print(f"\nLoss value: {loss.item():.4f}")


def demo_soft_dice():
    """Demo Soft Dice Loss."""
    print("\n" + "=" * 70)
    print("5. SOFT DICE LOSS DEMO")
    print("=" * 70)

    dice = SoftDiceLoss()

    # Perfect prediction
    pred_perfect = torch.tensor([0.9, 0.9, 0.1, 0.1])
    target = torch.tensor([1.0, 1.0, 0.0, 0.0])
    loss_perfect = dice(pred_perfect, target)

    # Random prediction
    pred_random = torch.tensor([0.5, 0.5, 0.5, 0.5])
    loss_random = dice(pred_random, target)

    # Worst prediction
    pred_worst = torch.tensor([0.1, 0.1, 0.9, 0.9])
    loss_worst = dice(pred_worst, target)

    print(f"\nTarget: {target.tolist()}")
    print(f"  Perfect pred {pred_perfect.tolist()} → Dice loss = {loss_perfect:.4f}")
    print(f"  Random pred  {pred_random.tolist()} → Dice loss = {loss_random:.4f}")
    print(f"  Worst pred   {pred_worst.tolist()} → Dice loss = {loss_worst:.4f}")
    print(f"\n  Dice loss = 1 - (2 * intersection + ε) / (union + ε)")
    print(f"  Lower is better. 0 = perfect overlap.")


def main():
    print("PAPER BREAKDOWN — PART 6: LOSS FUNCTIONS")
    print("Nilsson 2024 & 2026")
    print()

    compute_lane_np_ratios()
    np_ratios = compute_turn_np_ratios()
    demo_lane_loss()
    demo_turn_loss(np_ratios)
    demo_soft_dice()

    print("\n" + "=" * 70)
    print("DONE. Kết luận:")
    print("  - LaneLoss: 8 thành phần (4 CE + 4 Dice)")
    print("  - TurnLoss: area-weighted BCE + Soft Dice")
    print("  - N/P ratios xử lý class imbalance, cap tại 30")
    print("  - 'Almost impossible' cells nhận weight thấp hơn")
    print("  - 2026 tối ưu các tham số này bằng Optuna")
    print("=" * 70)


if __name__ == "__main__":
    main()
