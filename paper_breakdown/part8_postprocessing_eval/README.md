# Part 8 — Post-Processing Heuristic & Evaluation

## Mục tiêu

Hiểu Stage 4: Post-Processing Heuristic (PPH) 6 rules, và 3 cấp độ evaluation metrics.

## Post-Processing Heuristic (PPH)

PPH là bước cuối pipeline, loại bỏ các dự đoán turn mâu thuẫn về mặt topology.

### 2-Phase approach

**Phase 1 — Classify:** Duyệt TẤT CẢ cells trong adjacency matrix theo thứ tự xác suất giảm dần. Mỗi cell được phân loại *consistent* hoặc *inconsistent* dựa trên 6 rules so với các cell đã accepted trước đó.

**Phase 2 — Threshold:** Chỉ giữ các cell *consistent* có probability ≥ threshold (mặc định 0.5) → binary matrix.

### 6 Rules

| Rule | Mô tả |
|------|-------|
| 1-2 | **Approach-Exit separation**: trên cùng arm, approach slots phải nằm bên trái exit slots. Nếu slot `s` là approach, không slot nào ≥ `s` được là exit trên arm đó. |
| 3-5 | **Turn type ordering**: trên cùng approach arm, từ trái sang phải phải tuân thủ Left ≤ Through ≤ Right. Slot rẽ trái phải nằm bên trái slot đi thẳng, slot đi thẳng bên trái slot rẽ phải. |
| 6 | **Exit uniqueness**: không có 2 approach lanes từ cùng arm kết nối đến cùng exit arm + cùng exit slot. |

### Ví dụ

Giả sử arm 0 có 3 approach lanes ở slot 5, 6, 7:
- Slot 5 rẽ trái (Left) ✓
- Slot 6 đi thẳng (Through) ✓
- Slot 7 rẽ phải (Right) ✓
- Slot 5 rẽ phải, Slot 7 rẽ trái → **vi phạm Rule 3-5** ✗

## Evaluation Metrics (3 cấp độ)

| Cấp độ | Đo gì | Metric |
|--------|-------|--------|
| **Turn-level** | Cell-by-cell match trong adjacency matrix | Precision, Recall, F1 |
| **Slot turn-level** | Đếm số lanes theo loại turn (L/T/R/approach) per arm | F1 per class |
| **Arm-level lane type** | Phân loại kiểu lane (L, LT, LTR, LR, T, TR, R) | F1 per type |

### Baseline

Rule-based baseline:
- 4-way: mỗi arm có 1 LT + 1 TR lane
- 3-way: tùy vị trí virtual arm (ví dụ: left virtual → 1 T + 1 TR)

## Paper reference

- Nilsson 2024, Section 3.9 (PPH), Section 4 (Evaluation)
- Code: `replication/post_processing.py`, `replication/evaluation.py`

## Chạy

```bash
python pph_eval_demo.py
```
