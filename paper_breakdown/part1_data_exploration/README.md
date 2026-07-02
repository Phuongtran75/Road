# Part 1 — Data Exploration

## Mục tiêu

Khám phá dataset Zenodo của Nilsson, hiểu cấu trúc dữ liệu trước khi đi vào pipeline.

## Dữ liệu gồm gì?

Dataset công bố trên Zenodo chứa:

1. **Ảnh arm** (`a_*.png`): ảnh vệ tinh/hàng không đã cắt và xoay theo hướng bearing của từng nhánh đường (arm). Mỗi ảnh ~1000×1000 pixels.

2. **intersections.json**: thông tin về từng nút giao, bao gồm:
   - `id`: mã intersection
   - `arms`: danh sách các nhánh đường, mỗi arm có `id`, `label`, `bearing`, `file_name`
   - Intersection có thể là 3-way hoặc 4-way

3. **lane_labels.json**: nhãn lane cho từng arm, gồm 22 lane slot × 8 thuộc tính:
   - `lane_slot` (1-22), `approach`, `exit`, `left`, `through`, `right`, `slip`

4. **turn_labels.json**: nhãn turn (kết nối approach lane → exit lane), bao gồm:
   - `approach_arm_id`, `approach_lane_slot`, `exit_arm_id`, `exit_lane_slot`

5. **COCO detection results**: kết quả object detection cho 32 loại lane objects

## Paper reference

- Nilsson 2024, Section 3.1-3.3: Data collection and description
- Nilsson 2026, Section 3.1: Study area and data

## Chạy

```bash
python explore_data.py
```
