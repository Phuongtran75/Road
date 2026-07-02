"""
Part 2: Intersection Processing
================================
Demo xử lý intersection: arms, bearings, 3-way → 4-way conversion.
Hiển thị clockwise ordering và bearing offsets.

Reference: Nilsson 2024 Section 3.4-3.5
"""
import os
import sys
import json
import io
import numpy as np

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = r"f:\Road\main_task\data"
sys.path.insert(0, r"f:\Road")
from replication.data_encoding import normalize_bearing, get_3way_transform_mapping


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_sample_intersections(intersections):
    """Tìm 1 sample 4-way và 1 sample 3-way."""
    sample_4way = None
    sample_3way = None
    for inter in intersections:
        n = len(inter["arms"])
        if n == 4 and sample_4way is None:
            sample_4way = inter
        elif n == 3 and sample_3way is None:
            sample_3way = inter
        if sample_4way and sample_3way:
            break
    return sample_4way, sample_3way


def demo_4way_processing(inter):
    """Demo xử lý intersection 4-way."""
    print("=" * 70)
    print(f"4-WAY INTERSECTION (id={inter['id']})")
    print("=" * 70)

    arms = inter["arms"]
    print(f"\nRaw arms ({len(arms)} arms):")
    for arm in arms:
        print(f"  label={arm['label']}, bearing={arm['bearing']:.1f}°")

    # Sort clockwise by bearing
    sorted_arms = sorted(arms, key=lambda x: normalize_bearing(x["bearing"]))
    print(f"\nSorted clockwise:")
    for idx, arm in enumerate(sorted_arms):
        print(f"  index={idx} (label {arm['label']}), "
              f"bearing={normalize_bearing(arm['bearing']):.1f}°")

    # Compute bearing offsets for arm 0
    ref_arm = sorted_arms[0]
    ref_bearing = ref_arm["bearing"]
    print(f"\nBearing offsets (từ arm index=0, bearing={ref_bearing:.1f}°):")
    for i in range(1, 4):
        other = sorted_arms[i]
        diff = (other["bearing"] - ref_bearing) % 360
        print(f"  → arm index={i} (label {other['label']}): "
              f"offset = {diff:.1f}° ({diff/360:.3f} normalized)")


def demo_3way_processing(inter):
    """Demo chuyển đổi 3-way → 4-way với virtual arm."""
    print("\n" + "=" * 70)
    print(f"3-WAY INTERSECTION (id={inter['id']})")
    print("=" * 70)

    arms = inter["arms"]
    print(f"\nRaw arms ({len(arms)} arms):")
    for arm in arms:
        print(f"  label={arm['label']}, bearing={arm['bearing']:.1f}°")

    # Sorted by bearing
    sorted_arms = sorted(arms, key=lambda x: normalize_bearing(x["bearing"]))
    print(f"\nSorted clockwise:")
    bearings = []
    for idx, arm in enumerate(sorted_arms):
        b = normalize_bearing(arm["bearing"])
        bearings.append(b)
        print(f"  index={idx}, bearing={b:.1f}°")

    # Calculate gaps
    print(f"\nBearing gaps:")
    n = len(sorted_arms)
    for i in range(n):
        b_curr = bearings[i]
        b_next = bearings[(i + 1) % n]
        gap = (b_next - b_curr) % 360
        print(f"  gap {i}→{(i+1)%n}: {gap:.1f}°")

    # Apply 3-way transform
    new_arms, arm_mapping = get_3way_transform_mapping(arms)
    print(f"\nSau chuyển đổi 3-way → 4-way:")
    print(f"  Arm mapping (old_label → new_label): {arm_mapping}")
    for idx, arm in enumerate(new_arms):
        is_virtual = arm.get("is_virtual", False)
        tag = " ← VIRTUAL" if is_virtual else ""
        print(f"  new_label={arm['label']}, "
              f"bearing={normalize_bearing(arm['bearing']):.1f}°, "
              f"virtual={is_virtual}{tag}")


def demo_relative_encoding():
    """Giải thích relative exit arm encoding."""
    print("\n" + "=" * 70)
    print("RELATIVE EXIT ARM ENCODING")
    print("=" * 70)

    print("""
Trong adjacency matrix (4, 22, 66), 66 cột chia thành 3 nhóm:
  - Columns 0-21:  Left exit arm   = (approach_arm + 1) % 4
  - Columns 22-43: Through exit arm = (approach_arm + 2) % 4
  - Columns 44-65: Right exit arm  = (approach_arm + 3) % 4

Ví dụ, nếu approach arm = 0 (Bắc):
  - Left exit  = arm 1 (Đông)   → columns 0-21
  - Through    = arm 2 (Nam)    → columns 22-43
  - Right exit = arm 3 (Tây)    → columns 44-65

Ưu điểm: encoding tương đối (relative) nên rotation augmentation
KHÔNG cần thay đổi cột — chỉ roll axis 0 (approach arm dimension).
""")

    # Demo cho từng approach arm
    for app in range(4):
        left = (app + 1) % 4
        through = (app + 2) % 4
        right = (app + 3) % 4
        print(f"  Approach arm {app}: Left→arm {left}, "
              f"Through→arm {through}, Right→arm {right}")


def main():
    print("PAPER BREAKDOWN — PART 2: INTERSECTION PROCESSING")
    print("Nilsson 2024 & 2026")
    print()

    intersections = load_json(
        os.path.join(DATA_DIR, "labels", "intersections.json"))
    sample_4way, sample_3way = find_sample_intersections(intersections)

    if sample_4way:
        demo_4way_processing(sample_4way)

    if sample_3way:
        demo_3way_processing(sample_3way)

    demo_relative_encoding()

    print("\n" + "=" * 70)
    print("DONE. Kết luận:")
    print("  - Arms sắp xếp clockwise theo bearing")
    print("  - 3-way → 4-way bằng virtual arm tại largest bearing gap")
    print("  - Adjacency matrix dùng relative exit arm encoding")
    print("=" * 70)


if __name__ == "__main__":
    main()
