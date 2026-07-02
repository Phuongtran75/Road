"""
Part 7: Data Augmentation
==========================
Demo rotation augmentation và slot shift augmentation.

Reference: Nilsson 2024 Section 3.7, Figure 20-22
"""
import os
import sys
import io
import numpy as np

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, r"f:\Road")
from replication.data_encoding import (
    DatasetEncoder,
    apply_rotation_augmentation,
    apply_slot_shift_augmentation,
)

DATA_DIR = r"f:\Road\main_task\data"


def create_sample_data():
    """Tạo sample lane_matrix và adj_matrix từ ground truth."""
    encoder = DatasetEncoder(DATA_DIR)

    import json
    split_path = os.path.join(DATA_DIR, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)

    sample_id = splits["train"][0]
    info = encoder.get_intersection_info(sample_id)

    arms = info["arms"]
    is_3way = len(arms) == 3
    if is_3way:
        from replication.data_encoding import get_3way_transform_mapping
        new_arms, _ = get_3way_transform_mapping(arms)
    else:
        new_arms = sorted(arms, key=lambda x: x["bearing"] % 360)

    lane_matrix = np.zeros((4, 22, 8), dtype=np.float32)
    for arm_i, arm in enumerate(new_arms):
        if not arm.get("is_virtual", False):
            lane_matrix[arm_i] = encoder.encode_lane_attributes(arm["id"])

    adj_matrix = encoder.encode_intersection_turns(sample_id)

    return lane_matrix, adj_matrix, sample_id


def print_lane_summary(lane_matrix, label=""):
    """In tóm tắt lane matrix."""
    if label:
        print(f"  {label}")
    for arm in range(4):
        n_lanes = int(np.sum(lane_matrix[arm, :, 0] > 0))
        n_appr = int(np.sum(lane_matrix[arm, :, 6] > 0))
        n_exit = int(np.sum(lane_matrix[arm, :, 7] > 0))
        if n_lanes > 0:
            # Find occupied slot range
            occupied = np.where(lane_matrix[arm, :, 0] > 0)[0]
            slot_range = f"slots {occupied[0]+1}-{occupied[-1]+1}"
            print(f"    Arm {arm}: {n_lanes} lanes ({n_appr} appr, "
                  f"{n_exit} exit) at {slot_range}")
        else:
            print(f"    Arm {arm}: no lanes (virtual?)")


def print_adj_summary(adj_matrix, label=""):
    """In tóm tắt adjacency matrix."""
    if label:
        print(f"  {label}")
    total = int(np.sum(adj_matrix > 0.5))
    print(f"    Total connections: {total}")
    for arm in range(4):
        n = int(np.sum(adj_matrix[arm] > 0.5))
        if n > 0:
            print(f"    Arm {arm}: {n} connections")


def demo_rotation():
    """Demo rotation augmentation."""
    print("=" * 70)
    print("1. ROTATION AUGMENTATION")
    print("=" * 70)

    lane_matrix, adj_matrix, sample_id = create_sample_data()

    print(f"\nIntersection: {sample_id}")
    print(f"\n--- Original ---")
    print_lane_summary(lane_matrix)
    print_adj_summary(adj_matrix)

    for k in range(1, 4):
        new_lane, new_adj, rotation = apply_rotation_augmentation(
            lane_matrix, adj_matrix, k=k)

        print(f"\n--- Rotated k={k} ({k*90}° clockwise) ---")
        print_lane_summary(new_lane)
        print_adj_summary(new_adj)

        # Verify total connections preserved
        orig_total = int(np.sum(adj_matrix > 0.5))
        new_total = int(np.sum(new_adj > 0.5))
        match = "✓" if orig_total == new_total else "✗ MISMATCH"
        print(f"    Connections preserved: {match} "
              f"({orig_total} → {new_total})")

    print(f"\n  Ý nghĩa: rotation chỉ roll axis 0 (approach arm index)")
    print(f"  Columns KHÔNG đổi vì dùng relative encoding")
    print(f"  → Model học được topology bất kể hướng tiếp cận")


def demo_slot_shift():
    """Demo slot shift augmentation."""
    print("\n" + "=" * 70)
    print("2. SLOT SHIFT AUGMENTATION")
    print("=" * 70)

    lane_matrix, adj_matrix, sample_id = create_sample_data()

    print(f"\nIntersection: {sample_id}")
    print(f"\n--- Original ---")
    print_lane_summary(lane_matrix)

    # Show original slot positions for arm 0
    arm0 = lane_matrix[0]
    occupied = np.where(arm0[:, 0] > 0)[0]
    if len(occupied) > 0:
        print(f"\n  Arm 0 occupied slots: {[s+1 for s in occupied]}")

    # Apply shift multiple times to show variety
    print(f"\n--- Shifted samples (max_shift=1) ---")
    for trial in range(5):
        np.random.seed(trial)
        new_lane, new_adj = apply_slot_shift_augmentation(
            lane_matrix, adj_matrix, max_shift=1)

        # Show shifts applied
        for arm in range(4):
            orig_occupied = np.where(lane_matrix[arm, :, 0] > 0)[0]
            new_occupied = np.where(new_lane[arm, :, 0] > 0)[0]
            if len(orig_occupied) > 0:
                orig_slots = [s+1 for s in orig_occupied]
                new_slots = [s+1 for s in new_occupied]
                if orig_slots != new_slots:
                    shift = new_occupied[0] - orig_occupied[0]
                    print(f"  Trial {trial}, Arm {arm}: "
                          f"slots {orig_slots} → {new_slots} (shift={shift:+d})")

        # Verify no positive labels lost
        orig_pos = int(np.sum(adj_matrix > 0.5))
        new_pos = int(np.sum(new_adj > 0.5))
        if orig_pos != new_pos:
            print(f"  ⚠ Connections changed: {orig_pos} → {new_pos}")

    print(f"\n  Clamping logic: shift bị giới hạn nếu sẽ mất positive labels")
    print(f"  → Đảm bảo no information loss")


def demo_combined():
    """Demo kết hợp cả hai augmentation."""
    print("\n" + "=" * 70)
    print("3. COMBINED AUGMENTATION EFFECT")
    print("=" * 70)

    lane_matrix, adj_matrix, _ = create_sample_data()

    original_connections = int(np.sum(adj_matrix > 0.5))
    all_preserved = True

    for k in range(4):
        for trial in range(3):
            np.random.seed(k * 10 + trial)
            rot_lane, rot_adj, _ = apply_rotation_augmentation(
                lane_matrix, adj_matrix, k=k)
            shift_lane, shift_adj = apply_slot_shift_augmentation(
                rot_lane, rot_adj, max_shift=1)

            new_connections = int(np.sum(shift_adj > 0.5))
            if new_connections != original_connections:
                all_preserved = False

    augmentation_factor = 4 * 3  # 4 rotations × 3 shifts (-1, 0, +1)
    print(f"\n  Rotation: 4 orientations (0°, 90°, 180°, 270°)")
    print(f"  Slot shift: ±1 → 3 shifts per arm")
    print(f"  Effective augmentation factor: ~{augmentation_factor}×")
    print(f"  Connections preserved in all variants: "
          f"{'✓ Yes' if all_preserved else '✗ No (some shifted out)'}")


def main():
    print("PAPER BREAKDOWN — PART 7: DATA AUGMENTATION")
    print("Nilsson 2024 & 2026")
    print()

    demo_rotation()
    demo_slot_shift()
    demo_combined()

    print("\n" + "=" * 70)
    print("DONE. Kết luận:")
    print("  - Rotation: xoay k×90° chỉ roll arm axis, columns bất biến")
    print("  - Slot shift: dịch ±1 slot, clamped để giữ positive labels")
    print("  - Kết hợp: ~12× augmentation factor")
    print("  - Tăng training data từ ~2390 lên ~28,680 samples")
    print("=" * 70)


if __name__ == "__main__":
    main()
