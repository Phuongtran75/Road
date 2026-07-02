# Part 4 — Lane Detection (Stage 2)

## Mục tiêu

Hiểu kiến trúc và cách hoạt động của Lane Detector — Stage 2 trong pipeline.

## Kiến trúc

```
Input ảnh arm (3, 224, 224)  →  ResNet-18 (frozen)  →  512-dim
                                                          ↓
Input non-image (223-dim)    →  MLP (128→64)         →  64-dim
  ├── 220-dim projection vector                           ↓
  └── 3 bearing offsets                              Concat → 576-dim
                                                          ↓
                                                     MLP (256→176)
                                                          ↓
                                                     Reshape → (22, 8)
```

## Input chi tiết

1. **Ảnh arm** (3, 224, 224): ảnh vệ tinh xoay theo bearing, resize về 224×224, normalize bằng ImageNet mean/std

2. **Non-image features** (223-dim):
   - 220-dim: projection vector từ Stage 1
   - 3-dim: bearing offsets (khoảng cách góc tương đối đến 3 arms còn lại, normalized /360)

## Output chi tiết

22 lane slots × 8 thuộc tính:

| Index | Thuộc tính | Activation | Ý nghĩa |
|-------|-----------|------------|---------|
| 0 | lane | Sigmoid | Có lane hay không |
| 1-3 | lane_type | Softmax (3 class) | no_lane / approach / exit |
| 4 | left | Sigmoid | Được phép rẽ trái |
| 5 | through | Sigmoid | Được phép đi thẳng |
| 6 | right | Sigmoid | Được phép rẽ phải |
| 7 | slip | Sigmoid | Là slip lane |

## Paper reference

- Nilsson 2024, Section 3.7, Figure 23-25, Table 4-6
- Code gốc: `replication/models.py` class `LaneDetector`

## Chạy

```bash
python lane_detector_demo.py
```
