"""
Part 4: Lane Detection (Stage 2)
=================================
Demo kiến trúc LaneDetector, forward pass, và visualize predictions.

Reference: Nilsson 2024 Section 3.7, Figure 23
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
from replication.models import LaneDetector
from replication.data_encoding import DatasetEncoder

DATA_DIR = r"f:\Road\main_task\data"


def show_architecture():
    """Khởi tạo và in kiến trúc LaneDetector."""
    print("=" * 70)
    print("1. LANE DETECTOR ARCHITECTURE")
    print("=" * 70)

    model = LaneDetector(num_slots=22, num_attrs=8, proj_dim=220,
                         bearing_dim=3, frozen_resnet=True)

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters()
                          if p.requires_grad)
    frozen_params = total_params - trainable_params

    print(f"\nModel summary:")
    print(f"  Total parameters:     {total_params:>10,d}")
    print(f"  Trainable parameters: {trainable_params:>10,d}")
    print(f"  Frozen parameters:    {frozen_params:>10,d}")

    print(f"\nComponents:")
    print(f"  1. Image backbone: ResNet-18 (frozen) → 512-dim")
    print(f"  2. Non-image MLP: (220+3=223) → 128 → 64")
    print(f"  3. Combined MLP: (512+64=576) → 256 → (22×8=176)")

    print(f"\nInput shapes:")
    print(f"  img:             (B, 3, 224, 224)")
    print(f"  non_img_features: (B, 223)")

    print(f"\nOutput shapes:")
    print(f"  lane:      (B, 22)    — lane presence logits")
    print(f"  lane_type: (B, 3, 22) — lane type logits")
    print(f"  left:      (B, 22)    — left turn logits")
    print(f"  through:   (B, 22)    — through logits")
    print(f"  right:     (B, 22)    — right turn logits")
    print(f"  slip:      (B, 22)    — slip lane logits")

    return model


def demo_forward_pass(model):
    """Forward pass với dummy data."""
    print("\n" + "=" * 70)
    print("2. FORWARD PASS DEMO")
    print("=" * 70)

    model.eval()
    B = 2  # batch size

    # Dummy inputs
    img = torch.randn(B, 3, 224, 224)
    non_img = torch.randn(B, 223)

    with torch.no_grad():
        outputs = model(img, non_img)

    print(f"\nInput shapes:")
    print(f"  img: {img.shape}")
    print(f"  non_img: {non_img.shape}")

    print(f"\nOutput shapes:")
    for key, val in outputs.items():
        print(f"  {key:10s}: {val.shape}")

    # Show probabilities for first sample
    print(f"\nProbabilities (sample 0, first 5 slots):")
    lane_prob = torch.sigmoid(outputs["lane"][0])
    left_prob = torch.sigmoid(outputs["left"][0])
    through_prob = torch.sigmoid(outputs["through"][0])
    right_prob = torch.sigmoid(outputs["right"][0])
    type_prob = torch.softmax(outputs["lane_type"][0], dim=0)

    print(f"  {'Slot':>4s}  {'Lane':>6s}  {'NoLane':>6s}  {'Appr':>6s}  "
          f"{'Exit':>6s}  {'Left':>6s}  {'Thru':>6s}  {'Right':>6s}")
    print(f"  {'─'*4}  {'─'*6}  {'─'*6}  {'─'*6}  "
          f"{'─'*6}  {'─'*6}  {'─'*6}  {'─'*6}")
    for s in range(5):
        print(f"  {s+1:4d}  {lane_prob[s]:.4f}  "
              f"{type_prob[0, s]:.4f}  {type_prob[1, s]:.4f}  "
              f"{type_prob[2, s]:.4f}  "
              f"{left_prob[s]:.4f}  {through_prob[s]:.4f}  "
              f"{right_prob[s]:.4f}")


def demo_ground_truth():
    """Load ground truth lane attributes cho 1 arm."""
    print("\n" + "=" * 70)
    print("3. GROUND TRUTH LANE ATTRIBUTES")
    print("=" * 70)

    encoder = DatasetEncoder(DATA_DIR)
    intersections = encoder.intersections

    # Find a 4-way intersection with labels
    for inter in intersections:
        if len(inter["arms"]) == 4:
            arm = inter["arms"][0]
            arm_id = arm["id"]

            attrs = encoder.encode_lane_attributes(arm_id)
            if np.any(attrs != 0):
                print(f"\nIntersection {inter['id']}, Arm {arm_id} "
                      f"(bearing={arm['bearing']:.1f}°)")
                print(f"Lane attributes shape: {attrs.shape}")

                # Find slots with lanes
                print(f"\nSlots with lanes (attribute matrix [22, 8]):")
                print(f"  {'Slot':>4s}  {'Lane':>4s}  {'Type':>4s}  "
                      f"{'Slip':>4s}  {'Left':>4s}  {'Thru':>4s}  "
                      f"{'Right':>5s}  {'Appr':>4s}  {'Exit':>4s}")
                print(f"  {'─'*4}  {'─'*4}  {'─'*4}  "
                      f"{'─'*4}  {'─'*4}  {'─'*4}  "
                      f"{'─'*5}  {'─'*4}  {'─'*4}")

                type_names = {0: "none", 1: "appr", 2: "exit"}
                for s in range(22):
                    if attrs[s, 0] > 0 or np.any(attrs[s] != 0):
                        lt = int(attrs[s, 1])
                        print(f"  {s+1:4d}  "
                              f"{int(attrs[s, 0]):4d}  "
                              f"{type_names.get(lt, '?'):>4s}  "
                              f"{int(attrs[s, 2]):4d}  "
                              f"{int(attrs[s, 3]):4d}  "
                              f"{int(attrs[s, 4]):4d}  "
                              f"{int(attrs[s, 5]):5d}  "
                              f"{int(attrs[s, 6]):4d}  "
                              f"{int(attrs[s, 7]):4d}")

                n_approach = int(np.sum(attrs[:, 6]))
                n_exit = int(np.sum(attrs[:, 7]))
                print(f"\n  Total approach lanes: {n_approach}")
                print(f"  Total exit lanes: {n_exit}")
                return

    print("Không tìm thấy arm với lane labels.")


def main():
    print("PAPER BREAKDOWN — PART 4: LANE DETECTION (STAGE 2)")
    print("Nilsson 2024 & 2026")
    print()

    model = show_architecture()
    demo_forward_pass(model)
    demo_ground_truth()

    print("\n" + "=" * 70)
    print("DONE. Kết luận:")
    print("  - LaneDetector: ResNet-18 (frozen) + MLP")
    print("  - Input: ảnh arm 224×224 + 223-dim features")
    print("  - Output: 22 slots × 8 attributes")
    print("  - Mỗi slot cho biết: có lane?, loại lane, hướng rẽ cho phép")
    print("=" * 70)


if __name__ == "__main__":
    main()
