"""
Part 3: Object Detection & Projection Vector
=============================================
Demo Stage 1: load COCO detection results, aggregate 32→10 classes,
compute 220-dim projection vector for sample arms.

Reference: Nilsson 2024 Section 3.6
"""
import os
import sys
import json
import io
import numpy as np

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = r"f:\Road\main_task\data"

# 32 detailed classes → 10 aggregated classes
# From replication/train.py
DETAILED_TO_10 = {
    0: 0,   # Arrow left → Left arrow
    1: 1,   # Arrow right → Right arrow
    2: 0,   # Arrow right left → Left arrow
    3: 1,   # Arrow right through → Right arrow
    4: 2,   # Arrow right through left → Through arrow
    5: 2,   # Arrow through → Through arrow
    6: 0,   # Arrow through left → Left arrow
    7: 9,   # Bus lane → Other
    8: 4,   # Car backward → Cars backward
    9: 3,   # Car forward → Cars forward
    10: 5,  # Car other → Cars other
    11: 9,  # Cycle lane → Other
    12: 4,  # Large vehicle backward → Cars backward
    13: 3,  # Large vehicle forward → Cars forward
    14: 5,  # Large vehicle other → Cars other
    15: 9,  # Line horizontal other → Other
    16: 8,  # Line vertical give way → Stop line
    17: 7,  # Line vertical lane → Dashed line
    18: 6,  # Line vertical lane solid → Solid line
    19: 6,  # Line vertical median → Solid line
    20: 9,  # Line vertical other → Other
    21: 7,  # Line vertical parking → Dashed line
    22: 6,  # Line vertical verge → Solid line
    23: 9,  # Median painted → Other
    24: 6,  # Median physical → Solid line
    25: 9,  # Other road marking → Other
    26: 9,  # Pedestrian crossing signalised → Other
    27: 9,  # Pedestrian crossing zebra → Other
    28: 9,  # Speed marking → Other
    29: 6,  # Split island → Solid line
    30: 8,  # Stop line → Stop line
    31: 9,  # Verge painted → Other
}

CLASS_10_NAMES = [
    "Left arrow", "Right arrow", "Through arrow",
    "Cars forward", "Cars backward", "Cars other",
    "Solid line", "Dashed line", "Stop line", "Other"
]

# 32 detailed class names (for reference)
DETAILED_NAMES = [
    "Arrow left", "Arrow right", "Arrow right left", "Arrow right through",
    "Arrow right through left", "Arrow through", "Arrow through left",
    "Bus lane", "Car backward", "Car forward", "Car other", "Cycle lane",
    "Large vehicle backward", "Large vehicle forward", "Large vehicle other",
    "Line horizontal other", "Line vertical give way", "Line vertical lane",
    "Line vertical lane solid", "Line vertical median", "Line vertical other",
    "Line vertical parking", "Line vertical verge", "Median painted",
    "Median physical", "Other road marking", "Pedestrian crossing signalised",
    "Pedestrian crossing zebra", "Speed marking", "Split island",
    "Stop line", "Verge painted"
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def show_class_mapping():
    """Hiển thị bảng mapping 32 → 10 classes."""
    print("=" * 70)
    print("1. CLASS MAPPING: 32 detailed → 10 aggregated")
    print("=" * 70)

    for det_id in range(32):
        agg_id = DETAILED_TO_10[det_id]
        print(f"  [{det_id:2d}] {DETAILED_NAMES[det_id]:40s} → "
              f"[{agg_id}] {CLASS_10_NAMES[agg_id]}")

    # Count per aggregated class
    print(f"\nSố detailed classes gộp vào mỗi aggregated class:")
    for agg_id in range(10):
        count = sum(1 for v in DETAILED_TO_10.values() if v == agg_id)
        print(f"  [{agg_id}] {CLASS_10_NAMES[agg_id]:15s}: {count} classes")


def load_detections():
    """Load COCO detection results."""
    print("\n" + "=" * 70)
    print("2. COCO DETECTION RESULTS")
    print("=" * 70)

    # Try multiple paths
    det_paths = [
        os.path.join(DATA_DIR, "labels", "2",
                     "coco_instances_results_detailed.json"),
        os.path.join(DATA_DIR, "predictions", "lane_objects",
                     "version_14", "coco_instances_results_detailed.json"),
    ]

    for det_path in det_paths:
        if os.path.exists(det_path):
            print(f"Loading: {det_path}")
            detections = load_json(det_path)
            print(f"Tổng số detections: {len(detections)}")

            # Sample detection
            if detections:
                d = detections[0]
                print(f"\nSample detection:")
                print(f"  image_id: {d['image_id']}")
                print(f"  category_id: {d['category_id']} "
                      f"({DETAILED_NAMES[d['category_id']] if d['category_id'] < 32 else '?'})")
                print(f"  bbox: {d['bbox']}")
                print(f"  score: {d['score']:.4f}")

            # Category distribution
            cat_counts = {}
            for d in detections:
                cid = d["category_id"]
                cat_counts[cid] = cat_counts.get(cid, 0) + 1

            print(f"\nTop 10 categories by count:")
            sorted_cats = sorted(cat_counts.items(), key=lambda x: -x[1])
            for cid, count in sorted_cats[:10]:
                name = DETAILED_NAMES[cid] if cid < 32 else f"unknown_{cid}"
                print(f"  [{cid:2d}] {name:40s}: {count:6d}")

            return detections

    print("Detection results không tìm thấy.")
    return []


def load_image_mapping():
    """Load COCO template to map image_id → filename."""
    tmpl_paths = [
        os.path.join(DATA_DIR, "labels", "2", "coco_template_detailed.json"),
        os.path.join(DATA_DIR, "coco_template_detailed.json"),
    ]

    for p in tmpl_paths:
        if os.path.exists(p):
            tmpl = load_json(p)
            mapping = {}
            for img in tmpl.get("images", []):
                mapping[img["id"]] = img
            return mapping

    return {}


def compute_projection(detections_for_image, img_width=1000.0):
    """
    Compute 220-dim projection vector cho 1 arm image.
    22 slots × 10 classes = 220.
    """
    proj = np.zeros(220, dtype=np.float32)

    for det in detections_for_image:
        cat_id = det["category_id"]
        if cat_id not in DETAILED_TO_10:
            continue
        cls_10 = DETAILED_TO_10[cat_id]

        bbox = det["bbox"]  # [x, y, w, h]
        cx = bbox[0] + bbox[2] / 2.0

        slot_idx = int(cx / (img_width / 22.0))
        slot_idx = max(0, min(21, slot_idx))

        proj[slot_idx * 10 + cls_10] += det["score"]

    return proj


def demo_projection(detections, image_mapping):
    """Demo tính projection vector cho 1 arm."""
    print("\n" + "=" * 70)
    print("3. PROJECTION VECTOR DEMO")
    print("=" * 70)

    if not detections:
        print("Không có detections, bỏ qua.")
        return

    # Group detections by image_id
    dets_by_image = {}
    for d in detections:
        img_id = d["image_id"]
        if img_id not in dets_by_image:
            dets_by_image[img_id] = []
        dets_by_image[img_id].append(d)

    # Pick first image with enough detections
    sample_img_id = None
    for img_id, dets in dets_by_image.items():
        if len(dets) >= 5:
            sample_img_id = img_id
            break

    if sample_img_id is None:
        sample_img_id = list(dets_by_image.keys())[0]

    sample_dets = dets_by_image[sample_img_id]
    img_info = image_mapping.get(sample_img_id, {})
    img_width = float(img_info.get("width", 1000))
    filename = img_info.get("file_name", "unknown")

    print(f"\nImage: {filename} (id={sample_img_id})")
    print(f"Image width: {img_width}px")
    print(f"Số detections: {len(sample_dets)}")

    # Compute projection
    proj = compute_projection(sample_dets, img_width)
    proj_2d = proj.reshape(22, 10)

    print(f"\nProjection vector shape: {proj.shape} (flat) → {proj_2d.shape} (2D)")
    print(f"Non-zero entries: {np.count_nonzero(proj_2d)}")
    print(f"Sum: {proj.sum():.2f}")

    # Print non-zero slots
    print(f"\nNon-zero slot × class entries:")
    print(f"  {'Slot':>4s}  {'Class':>15s}  {'Score':>8s}")
    print(f"  {'─'*4}  {'─'*15}  {'─'*8}")
    for slot in range(22):
        for cls in range(10):
            val = proj_2d[slot, cls]
            if val > 0:
                print(f"  {slot+1:4d}  {CLASS_10_NAMES[cls]:>15s}  {val:8.4f}")


def main():
    print("PAPER BREAKDOWN — PART 3: OBJECT DETECTION & PROJECTION")
    print("Nilsson 2024 & 2026")
    print()

    show_class_mapping()
    detections = load_detections()
    image_mapping = load_image_mapping()
    demo_projection(detections, image_mapping)

    print("\n" + "=" * 70)
    print("DONE. Kết luận:")
    print("  - Stage 1 phát hiện 32 loại lane objects trong ảnh arm")
    print("  - 32 classes được gộp thành 10 aggregated classes")
    print("  - Projection vector: 22 slots × 10 classes = 220 dim")
    print("  - Mỗi slot tích lũy confidence scores từ detections")
    print("=" * 70)


if __name__ == "__main__":
    main()
