# Part 2 — Intersection Processing

## Mục tiêu

Hiểu cách Nilsson xử lý dữ liệu OSM thành cấu trúc intersection → arms → bearings, và cách chuyển đổi 3-way thành 4-way bằng virtual arm.

## Các khái niệm chính

### Intersection và Arms

Mỗi nút giao (intersection) trong OSM có các nhánh đường (arms) giao nhau. Nilsson trích xuất:
- **Bearing**: góc hướng của arm tính từ tâm intersection ra ngoài (0°=Bắc, 90°=Đông, theo chiều kim đồng hồ)
- **Label**: thứ tự arm (1, 2, 3, 4) sắp xếp clockwise theo bearing

### Tại sao cần 4-way chuẩn hóa?

Pipeline yêu cầu mọi intersection đều có **đúng 4 arms** để adjacency matrix luôn có shape `(4, 22, 66)`. Khi gặp intersection 3-way:
1. Tính khoảng cách bearing giữa các arm liên tiếp
2. Tìm khoảng trống lớn nhất (largest gap)
3. Chèn **virtual arm** vào vị trí đó
4. Virtual arm: bearing = bearing của arm trước gap, tất cả attributes = 0

### Clockwise ordering

Arms được sắp xếp theo bearing tăng dần (clockwise từ Bắc). Thứ tự này quyết định:
- Index 0-3 trong adjacency matrix
- Relative exit arm encoding: Left=+1, Through=+2, Right=+3

## Paper reference

- Nilsson 2024, Section 3.4-3.5
- Code gốc: `replication/data_encoding.py`, function `get_3way_transform_mapping()`

## Chạy

```bash
python process_intersections.py
```
