"""
Part 5: Turn Detection & Adjacency Matrix (Stage 3)
====================================================
Demo Turn Detector, encode adjacency matrix, visualize connections.

Reference: Nilsson 2024 Section 3.8, Figure 16
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
from replication.models import TurnDetector
from replication.data_encoding import DatasetEncoder
from replication.post_processing import get_exit_arm_and_slot

DATA_DIR = r"f:\Road\main_task\data"


def show_architecture():
    """Khởi tạo và in kiến trúc TurnDetector."""
    print("=" * 70)
    print("1. TURN DETECTOR ARCHITECTURE")
    print("=" * 70)

    model = TurnDetector(num_arms=4, num_slots=22, num_attrs=8,
                         bearing_dim=4, frozen_resnet=True)

    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"\nModel summary:")
    print(f"  Total parameters:     {total:>10,d}")
    print(f"  Trainable parameters: {trainable:>10,d}")
    print(f"  Frozen (ResNet):      {total - trainable:>10,d}")

    print(f"\nComponents:")
    print(f"  1. Image backbone: ResNet-18 (frozen) → 512-dim")
    print(f"  2. Non-image MLP: (4×22×8 + 4 = 708) → 256 → 128")
    print(f"  3. Combined MLP: (512+128=640) → 512 → (4×22×66=5808)")

    print(f"\nInput shapes:")
    print(f"  img:             (B, 3, 224, 224)  — intersection image")
    print(f"  non_img_features: (B, 708)")

    print(f"\nOutput shape:")
    print(f"  logits: (B, 4, 22, 66) — adjacency matrix")

    return model


def demo_forward_pass(model):
    """Forward pass demo."""
    print("\n" + "=" * 70)
    print("2. FORWARD PASS DEMO")
    print("=" * 70)

    model.eval()
    B = 1

    img = torch.randn(B, 3, 224, 224)
    non_img = torch.randn(B, 708)

    with torch.no_grad():
        logits = model(img, non_img)

    probs = torch.sigmoid(logits)

    print(f"\nOutput shape: {logits.shape}")
    print(f"Probability stats:")
    print(f"  Min:  {probs.min():.4f}")
    print(f"  Max:  {probs.max():.4f}")
    print(f"  Mean: {probs.mean():.4f}")
    print(f"  Cells > 0.5: {(probs > 0.5).sum().item()} / {probs.numel()}")


def demo_adjacency_matrix():
    """Encode và visualize ground truth adjacency matrix."""
    print("\n" + "=" * 70)
    print("3. GROUND TRUTH ADJACENCY MATRIX")
    print("=" * 70)

    encoder = DatasetEncoder(DATA_DIR)

    # Find a 4-way intersection with turn labels
    split_path = os.path.join(DATA_DIR, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)

    sample_id = splits["train"][0]
    adj = encoder.encode_intersection_turns(sample_id)

    print(f"\nIntersection id: {sample_id}")
    print(f"Adjacency matrix shape: {adj.shape}")
    print(f"Total positive cells (connections): {int(np.sum(adj))}")

    # Decode connections
    print(f"\nAll connections:")
    print(f"  {'Approach':>8s}  {'Slot':>4s}  →  {'Exit':>4s}  {'Slot':>4s}  {'Type':>7s}")
    print(f"  {'─'*8}  {'─'*4}     {'─'*4}  {'─'*4}  {'─'*7}")

    type_names = {0: "Left", 1: "Through", 2: "Right"}

    for app_arm in range(4):
        for app_slot in range(22):
            for col in range(66):
                if adj[app_arm, app_slot, col] > 0.5:
                    exit_arm, exit_slot, turn_type = get_exit_arm_and_slot(
                        app_arm, col)
                    print(f"  Arm {app_arm:4d}  {app_slot+1:4d}  →  "
                          f"{exit_arm:4d}  {exit_slot+1:4d}  "
                          f"{type_names[turn_type]:>7s}")

    # Per-arm summary
    print(f"\nPer-arm summary:")
    for arm in range(4):
        arm_slice = adj[arm]
        n_approach = int(np.any(arm_slice > 0.5, axis=1).sum())
        n_left = int(np.any(arm_slice[:, 0:22] > 0.5, axis=1).sum())
        n_through = int(np.any(arm_slice[:, 22:44] > 0.5, axis=1).sum())
        n_right = int(np.any(arm_slice[:, 44:66] > 0.5, axis=1).sum())
        print(f"  Arm {arm}: {n_approach} approach lanes "
              f"(L={n_left}, T={n_through}, R={n_right})")

    return adj


def demo_matrix_visualization(adj):
    """Text-based visualization of adjacency matrix."""
    print("\n" + "=" * 70)
    print("4. ADJACENCY MATRIX VISUALIZATION (text)")
    print("=" * 70)

    for arm in range(4):
        arm_slice = adj[arm]
        has_data = np.any(arm_slice > 0.5, axis=1)

        if not np.any(has_data):
            continue

        print(f"\n  Approach Arm {arm}:")
        print(f"  {'':>6s}  |{'Left (arm+1)':^22s}|"
              f"{'Through (arm+2)':^22s}|{'Right (arm+3)':^22s}|")

        # Only show slots with data ± 1
        first = max(0, np.argmax(has_data) - 1)
        last = min(21, 21 - np.argmax(has_data[::-1]) + 1)

        for s in range(first, last + 1):
            row = arm_slice[s]
            left_str = ""
            for c in range(22):
                left_str += "█" if row[c] > 0.5 else "·"
            through_str = ""
            for c in range(22, 44):
                through_str += "█" if row[c] > 0.5 else "·"
            right_str = ""
            for c in range(44, 66):
                right_str += "█" if row[c] > 0.5 else "·"

            marker = "←" if has_data[s] else " "
            print(f"  s{s+1:2d} {marker} |{left_str}|{through_str}|{right_str}|")


def main():
    print("PAPER BREAKDOWN — PART 5: TURN DETECTION (STAGE 3)")
    print("Nilsson 2024 & 2026")
    print()

    model = show_architecture()
    demo_forward_pass(model)
    adj = demo_adjacency_matrix()
    demo_matrix_visualization(adj)

    print("\n" + "=" * 70)
    print("DONE. Kết luận:")
    print("  - TurnDetector: ResNet-18 + MLP → adjacency matrix (4,22,66)")
    print("  - 66 cột = 3 exit arms × 22 slots (relative encoding)")
    print("  - 2-phase training: GT first, then predicted lane attrs")
    print("  - Matrix cho biết: approach lane nào kết nối exit lane nào")
    print("=" * 70)


if __name__ == "__main__":
    main()
