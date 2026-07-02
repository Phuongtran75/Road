# Part 5 — Turn Detection & Adjacency Matrix (Stage 3)

## Mục tiêu

Hiểu Stage 3: Turn Detector dự đoán adjacency matrix 4×22×66, biểu diễn kết nối approach lane → exit lane.

## Adjacency Matrix: 4 × 22 × 66

Đây là cấu trúc dữ liệu trung tâm của pipeline:

- **4**: 4 approach arms (sắp xếp clockwise)
- **22**: 22 lane slots trên mỗi approach arm
- **66**: 3 exit arms × 22 exit lane slots

### 66 cột chia thành 3 nhóm (relative encoding):

| Cột | Exit arm | Offset |
|-----|----------|--------|
| 0-21 | Left exit arm | (approach + 1) % 4 |
| 22-43 | Through exit arm | (approach + 2) % 4 |
| 44-65 | Right exit arm | (approach + 3) % 4 |

### Ví dụ đọc matrix

Nếu `adj_matrix[0, 3, 25] = 1`, có nghĩa:
- Approach arm 0, lane slot 4 (index 3)
- Exit arm = (0+2)%4 = arm 2 (Through), lane slot 4 (column 25 - 22 = 3)
- → Xe ở arm 0, làn 4 **được phép đi thẳng** sang arm 2, làn 4

## Kiến trúc Turn Detector

```
Input ảnh intersection (3, 224, 224)  →  ResNet-18 (frozen)  →  512-dim
                                                                    ↓
Input non-image (708-dim)             →  MLP (256→128)       →  128-dim
  ├── 704-dim: 4 arms × 22 slots × 8 attrs (stacked)              ↓
  └── 4-dim: absolute bearings (normalized)                   Concat → 640-dim
                                                                    ↓
                                                              MLP (512→5808)
                                                                    ↓
                                                              Reshape → (4, 22, 66)
```

## 2-Phase Transfer Learning

1. **Phase 1**: Train với ground-truth lane attributes → lưu best model
2. **Phase 2**: Load Phase 1 weights, fine-tune với predicted lane attributes (từ Stage 2), learning rate giảm 10×

Mục đích: model học cấu trúc topology từ GT trước, rồi thích ứng với noise trong predictions.

## Paper reference

- Nilsson 2024, Section 3.8, Figure 16, 31
- Code gốc: `replication/models.py` class `TurnDetector`, `replication/data_encoding.py` function `encode_intersection_turns()`

## Chạy

```bash
python turn_detector_demo.py
```
