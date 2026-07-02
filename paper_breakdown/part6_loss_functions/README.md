# Part 6 — Loss Functions

## Mục tiêu

Hiểu thiết kế loss function cho cả Lane Detector và Turn Detector, bao gồm xử lý class imbalance.

## LaneLoss (Stage 2)

Kết hợp **Weighted BCE** + **Soft Dice** cho 4 nhóm thuộc tính:

| Nhóm | Loss CE | Loss Dice | Weight CE | Weight Dice |
|------|---------|-----------|-----------|-------------|
| Lane presence | Binary CE | Soft Dice | 0.20 | 0.20 |
| Lane type | Multi-class CE | Multi-class Dice | 0.15 | 0.15 |
| Turn direction (L+T+R) | 3× Binary CE | 3× Soft Dice | 0.10 | 0.10 |
| Slip lane | Binary CE | Soft Dice | 0.05 | 0.05 |

### Class imbalance → Positive weights

| Class | N/P ratio | Weight used |
|-------|-----------|-------------|
| Lane | 4.80 | 4.80 |
| Approach | 10.07 | 10.07 |
| Exit | 11.18 | 11.18 |
| Through | 13.72 | 13.72 |
| Left | 26.29 | 26.29 |
| Right | 27.57 | 27.57 |
| Slip | 2118.81 | **30.0** (capped) |

Weight cap = 30: giá trị N/P ratio > 30 bị giới hạn ở 30 để tránh gradient explosion.

## TurnLoss (Stage 3)

3 thành phần:
1. **Weighted BCE (area of interest)**: weight 0.40 — cho cells có N/P < threshold
2. **Weighted BCE (almost impossible)**: weight 0.20 — cho cells có N/P ≥ threshold
3. **Soft Dice**: weight 0.40

### "Almost impossible" area

Trong adjacency matrix 4×22×66, phần lớn cells không bao giờ có positive label (ví dụ lane slot 20 của arm 0 kết nối với lane slot 1 của arm 2). Đó là "almost impossible" area.

- **Nilsson 2024**: N/P threshold cố định = 1000
- **Nilsson 2026**: threshold là tunable hyperparameter (tối ưu bằng Optuna)

## Paper reference

- Nilsson 2024, Table 4-5, Section 3.7-3.8
- Nilsson 2026, Section 3.7
- Code: `replication/losses.py`

## Chạy

```bash
python loss_analysis.py
```
