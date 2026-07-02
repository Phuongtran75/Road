"""
Part 1: Data Exploration
========================
Kham pha cau truc dataset Zenodo cua Nilsson.
Thong ke intersections, arms, lane labels, turn labels.
Hien thi sample arm image.

Reference: Nilsson 2024 Section 3.1-3.3
"""
import os
import sys
import json
import io
import numpy as np

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = r"f:\Road\main_task\data"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def explore_intersections():
    """Load intersections.json và in thống kê cơ bản."""
    print("=" * 70)
    print("1. INTERSECTIONS")
    print("=" * 70)

    intersections = load_json(os.path.join(DATA_DIR, "labels", "intersections.json"))
    print(f"Tổng số intersections: {len(intersections)}")

    # Đếm 3-way vs 4-way
    counts = {}
    for inter in intersections:
        n_arms = len(inter["arms"])
        counts[n_arms] = counts.get(n_arms, 0) + 1

    for k in sorted(counts.keys()):
        print(f"  {k}-way intersections: {counts[k]}")

    # Sample 1 intersection
    sample = intersections[0]
    print(f"\nSample intersection (id={sample['id']}):")
    print(f"  Số arms: {len(sample['arms'])}")
    for arm in sample["arms"]:
        print(f"  - Arm id={arm['id']}, label={arm['label']}, "
              f"bearing={arm['bearing']:.1f}°, file={arm.get('file_name', 'N/A')}")

    return intersections


def explore_lane_labels():
    """Load lane_labels.json và in thống kê."""
    print("\n" + "=" * 70)
    print("2. LANE LABELS")
    print("=" * 70)

    labels = load_json(os.path.join(DATA_DIR, "labels", "lanes", "lane_labels.json"))
    n_entries = len(labels["arm_id"])
    print(f"Tổng số lane label entries: {n_entries}")
    print(f"Các cột: {list(labels.keys())}")

    # Thống kê approach vs exit
    approach_count = sum(1 for v in labels["approach"].values() if v == 1)
    exit_count = sum(1 for v in labels["exit"].values() if v == 1)
    left_count = sum(1 for v in labels["left"].values() if v == 1)
    through_count = sum(1 for v in labels["through"].values() if v == 1)
    right_count = sum(1 for v in labels["right"].values() if v == 1)
    slip_count = sum(1 for v in labels["slip"].values() if v == 1)

    print(f"\nPhân bố thuộc tính:")
    print(f"  approach = 1: {approach_count} ({approach_count/n_entries*100:.1f}%)")
    print(f"  exit = 1:     {exit_count} ({exit_count/n_entries*100:.1f}%)")
    print(f"  left = 1:     {left_count} ({left_count/n_entries*100:.1f}%)")
    print(f"  through = 1:  {through_count} ({through_count/n_entries*100:.1f}%)")
    print(f"  right = 1:    {right_count} ({right_count/n_entries*100:.1f}%)")
    print(f"  slip = 1:     {slip_count} ({slip_count/n_entries*100:.1f}%)")

    # Phân bố lane_slot
    slot_counts = {}
    for v in labels["lane_slot"].values():
        slot_counts[v] = slot_counts.get(v, 0) + 1
    used_slots = sorted(slot_counts.keys())
    print(f"\n  Lane slots sử dụng: {min(used_slots)} đến {max(used_slots)}")
    print(f"  Số slots khác nhau: {len(used_slots)}")

    return labels


def explore_turn_labels():
    """Load turn_labels.json và in thống kê."""
    print("\n" + "=" * 70)
    print("3. TURN LABELS")
    print("=" * 70)

    labels = load_json(os.path.join(DATA_DIR, "labels", "turns", "turn_labels.json"))
    n_entries = len(labels["intersection_id"])
    print(f"Tổng số turn label entries: {n_entries}")
    print(f"Các cột: {list(labels.keys())}")

    # Số intersections có turn labels
    unique_inters = set(labels["intersection_id"].values())
    print(f"Số intersections có turn labels: {len(unique_inters)}")

    # Phân bố số turns per intersection
    turns_per_inter = {}
    for v in labels["intersection_id"].values():
        turns_per_inter[v] = turns_per_inter.get(v, 0) + 1

    counts = list(turns_per_inter.values())
    print(f"\nSố turns per intersection:")
    print(f"  Min: {min(counts)}, Max: {max(counts)}, "
          f"Mean: {np.mean(counts):.1f}, Median: {np.median(counts):.1f}")

    return labels


def explore_data_split():
    """Load data_split.json và in thống kê."""
    print("\n" + "=" * 70)
    print("4. DATA SPLIT")
    print("=" * 70)

    split = load_json(os.path.join(DATA_DIR, "labels", "turns", "data_split.json"))
    for key in split:
        print(f"  {key}: {len(split[key])} intersections")

    return split


def explore_sample_image(intersections):
    """Hiển thị thông tin về một sample arm image."""
    print("\n" + "=" * 70)
    print("5. SAMPLE ARM IMAGE")
    print("=" * 70)

    # Tìm arm đầu tiên có file tồn tại
    for inter in intersections:
        for arm in inter["arms"]:
            fname = arm.get("file_name")
            if fname:
                fpath = os.path.join(DATA_DIR, fname)
                if os.path.exists(fpath):
                    file_size = os.path.getsize(fpath) / 1024
                    print(f"File: {fname}")
                    print(f"Size: {file_size:.0f} KB")

                    try:
                        from PIL import Image
                        with Image.open(fpath) as img:
                            print(f"Dimensions: {img.size[0]} × {img.size[1]} pixels")
                            print(f"Mode: {img.mode}")
                    except ImportError:
                        print("(PIL không có sẵn, bỏ qua đọc image dimensions)")

                    print(f"Intersection id: {inter['id']}")
                    print(f"Arm id: {arm['id']}, bearing: {arm['bearing']:.1f}°")
                    return

    print("Không tìm thấy arm image nào.")


def main():
    print("PAPER BREAKDOWN — PART 1: DATA EXPLORATION")
    print("Nilsson 2024 & 2026")
    print()

    intersections = explore_intersections()
    explore_lane_labels()
    explore_turn_labels()
    explore_data_split()
    explore_sample_image(intersections)

    print("\n" + "=" * 70)
    print("DONE. Kết luận:")
    print("  - Dataset chứa intersections với 3 hoặc 4 arms")
    print("  - Mỗi arm có ảnh vệ tinh xoay theo bearing")
    print("  - Lane labels: 22 slots × 8 attributes per arm")
    print("  - Turn labels: approach lane → exit lane connections")
    print("=" * 70)


if __name__ == "__main__":
    main()
