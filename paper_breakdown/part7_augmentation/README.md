# Part 7 — Data Augmentation

## Mục tiêu

Hiểu hai kỹ thuật augmentation: rotation augmentation và slot shift augmentation.

## Rotation Augmentation

Xoay toàn bộ intersection k×90° (k ∈ {0, 1, 2, 3}):
- **Lane matrix** (4, 22, 8): roll axis 0 by k
- **Adjacency matrix** (4, 22, 66): roll axis 0 by k
- **Image** (C, H, W): rotate −k×90° (counter-clockwise)
- **Bearings** (4,): roll by k

Columns KHÔNG cần thay đổi vì dùng **relative encoding** (Left=+1, Through=+2, Right=+3). Khi xoay intersection, arm bên trái của arm mới vẫn nằm ở offset +1.

## Slot Shift Augmentation

Dịch lane slot attributes sang trái/phải tối đa ±1 slot:
- **Projections** (220-dim): reshape thành (22, 10), shift rows
- **Lane targets** (22, 8): shift rows
- **Adjacency matrix**: shift cả rows (approach slots) VÀ columns (exit slots)

### Clamping logic

Nilsson 2024 (p.40): *"The maximum threshold was further constrained such that no positive turn labels were omitted."*

Nếu shift sẽ đẩy positive label ra ngoài biên (slot 0 hoặc slot 21), shift bị giới hạn để giữ lại tất cả labels.

### Tác dụng

| Augmentation | Factor | Ý nghĩa |
|---|---|---|
| Rotation | ×4 | Model invariant với hướng tiếp cận |
| Slot shift ±1 | ×3 | Model robust với lỗi spatial alignment nhỏ |
| Kết hợp | ×12 | Từ 2390 arm samples → ~28,680 augmented samples |

## Paper reference

- Nilsson 2024, Section 3.7, Figure 20-22
- Code: `replication/data_encoding.py` functions `apply_rotation_augmentation()`, `apply_slot_shift_augmentation()`

## Chạy

```bash
python augmentation_demo.py
```
