# Part 3 — Object Detection & Projection Vector

## Mục tiêu

Hiểu Stage 1 của pipeline: oriented object detector phát hiện 32 loại lane objects, rồi gộp thành 10 classes và tạo 220-dim projection vector.

## Stage 1: Oriented Object Detection

Nilsson dùng oriented object detector (đã pre-trained) để phát hiện các đối tượng trên mặt đường từ ảnh arm đã xoay. Detector output là COCO-format bounding boxes cho **32 detailed classes**:

| ID | Class | Loại |
|----|-------|------|
| 0 | Arrow left | Mũi tên |
| 1 | Arrow right | Mũi tên |
| 5 | Arrow through | Mũi tên |
| 8-10 | Car backward/forward/other | Xe |
| 17 | Line vertical lane | Vạch đứt |
| 18 | Line vertical lane solid | Vạch liền |
| 30 | Stop line | Vạch dừng |
| ... | ... | ... |

## Aggregation: 32 → 10 classes

32 classes chi tiết được gộp thành 10 classes theo bảng:

| 10-class | Tên | Gộp từ |
|----------|-----|--------|
| 0 | Left arrow | Arrow left, Arrow right left, Arrow through left |
| 1 | Right arrow | Arrow right, Arrow right through |
| 2 | Through arrow | Arrow right through left, Arrow through |
| 3 | Cars forward | Car forward, Large vehicle forward |
| 4 | Cars backward | Car backward, Large vehicle backward |
| 5 | Cars other | Car other, Large vehicle other |
| 6 | Solid line | Line vertical lane solid, Median physical, ... |
| 7 | Dashed line | Line vertical lane, Line vertical parking |
| 8 | Stop line | Line vertical give way, Stop line |
| 9 | Other | Bus lane, Cycle lane, Pedestrian crossing, ... |

## 220-dim Projection Vector

Mỗi arm image có **22 lane slots × 10 classes = 220 dimensions**.

Cách tính:
1. Với mỗi detection, tính tâm bounding box (`cx`)
2. Map `cx` vào 1 trong 22 lane slots: `slot = int(cx / (image_width / 22))`
3. Cộng dồn confidence score vào vị trí `[slot × 10 + class_id]`

Kết quả: vector 220-dim biểu diễn spatial distribution của lane objects trên arm.

## Paper reference

- Nilsson 2024, Section 3.6: Lane object detection
- Code gốc: `replication/train.py`, lines 18-52 (mapping) và 194-215 (projection)

## Chạy

```bash
python build_projections.py
```
