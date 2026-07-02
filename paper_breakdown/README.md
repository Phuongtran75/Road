# Paper Breakdown: Nilsson 2024 & 2026

Folder này chia nhỏ pipeline từ hai bài báo của Hugo Nilsson thành **8 phần** độc lập.
Mỗi phần có README giải thích lý thuyết và script Python reproduce được.

## Papers

- **Nilsson 2024** (Luận văn): *Inferring lane-level topology of signalised intersections from aerial imagery and OpenStreetMap using deep learning*
- **Nilsson & Oucheikh 2026** (ISPRS Journal): *Predicting the adjacency matrix to construct lane-level topology of signalised intersections with aerial imagery and deep learning*

## Pipeline tổng thể

```
Stage 1: Oriented Object Detector  →  32 classes  →  10 classes  →  220-dim projection
                                                                          ↓
Stage 2: Lane Detector (CNN + MLP)  ←  projection + bearing offsets  →  22×8 lane slots
                                                                          ↓
Stage 3: Turn Detector (CNN + MLP)  ←  stacked 4×22×8 + bearings   →  4×22×66 adjacency
                                                                          ↓
Stage 4: Post-Processing Heuristic  →  6 rules  →  binary adjacency matrix
```

## Cách sử dụng

```bash
# Từ gốc project
cd f:\Road\paper_breakdown

# Chạy từng phần
python part1_data_exploration\explore_data.py
python part2_intersection_processing\process_intersections.py
python part3_object_detection\build_projections.py
# ... tiếp tục
```

## Yêu cầu

- Python 3.8+
- `numpy`, `torch`, `torchvision`, `PIL`
- Dữ liệu Zenodo tại `f:\Road\main_task\data\`

## Danh sách phần

| # | Folder | Nội dung | Paper Section |
|---|--------|----------|---------------|
| 1 | `part1_data_exploration` | Khám phá dataset, thống kê | 3.1-3.3 |
| 2 | `part2_intersection_processing` | OSM → arms, bearings, 3-way→4-way | 3.4-3.5 |
| 3 | `part3_object_detection` | Object detection → projection vector | 3.6 |
| 4 | `part4_lane_detection` | Stage 2: Lane Detector | 3.7 |
| 5 | `part5_turn_detection` | Stage 3: Turn Detector + adjacency matrix | 3.8 |
| 6 | `part6_loss_functions` | Weighted BCE, Soft Dice, N/P ratios | 3.7-3.8 |
| 7 | `part7_augmentation` | Rotation + slot shift augmentation | 3.7 |
| 8 | `part8_postprocessing_eval` | PPH rules + evaluation metrics | 3.9-4.0 |
