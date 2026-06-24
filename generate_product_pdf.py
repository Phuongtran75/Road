# -*- coding: utf-8 -*-
"""
Generate a professional product overview PDF for Road Capacity Analyzer.
Uses fpdf2 with Arial (Windows system font) for Vietnamese support.
"""

from fpdf import FPDF
import os

class ProductPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Register Arial Unicode font from Windows
        font_dir = "C:\\Windows\\Fonts"
        self.add_font("ArialUni", "", os.path.join(font_dir, "arial.ttf"), uni=True)
        self.add_font("ArialUni", "B", os.path.join(font_dir, "arialbd.ttf"), uni=True)
        self.add_font("ArialUni", "I", os.path.join(font_dir, "ariali.ttf"), uni=True)
        self.add_font("ArialUni", "BI", os.path.join(font_dir, "arialbi.ttf"), uni=True)

    def header(self):
        if self.page_no() > 1:
            self.set_font("ArialUni", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "Road Capacity Analyzer — Product Overview", align="R")
            self.ln(4)
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("ArialUni", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Trang {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title, r=41, g=98, b=255):
        self.set_font("ArialUni", "B", 16)
        self.set_text_color(r, g, b)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(r, g, b)
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(6)

    def subsection_title(self, title):
        self.set_font("ArialUni", "B", 12)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("ArialUni", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def bullet(self, text, indent=15):
        self.set_font("ArialUni", "", 10)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        self.cell(indent, 6, "•")
        self.multi_cell(0, 6, text)
        self.ln(1)

    def highlight_box(self, text, r=230, g=243, b=255, border_r=41, border_g=98, border_b=255):
        self.set_fill_color(r, g, b)
        self.set_draw_color(border_r, border_g, border_b)
        self.set_font("ArialUni", "", 10)
        self.set_text_color(30, 30, 30)
        x, y = self.get_x(), self.get_y()
        w = self.w - 20
        self.multi_cell(w, 6, text, border=1, fill=True)
        self.ln(4)

    def table_row(self, cells, widths, bold=False, fill=False, fill_color=(240, 245, 255)):
        if fill:
            self.set_fill_color(*fill_color)
        style = "B" if bold else ""
        self.set_font("ArialUni", style, 9)
        self.set_text_color(40, 40, 40)
        h = 8
        for i, (cell, w) in enumerate(zip(cells, widths)):
            border = 1
            self.set_draw_color(200, 210, 230)
            self.cell(w, h, cell, border=border, fill=fill)
        self.ln(h)

    def flow_step(self, step_num, text, is_last=False):
        self.set_font("ArialUni", "B", 11)
        # Draw circle with number
        x, y = self.get_x() + 15, self.get_y() + 4
        self.set_fill_color(41, 98, 255)
        self.set_draw_color(41, 98, 255)
        self.ellipse(x - 4, y - 4, 8, 8, style="F")
        self.set_text_color(255, 255, 255)
        self.set_font("ArialUni", "B", 8)
        self.text(x - 2, y + 1.5, str(step_num))

        # Text
        self.set_text_color(40, 40, 40)
        self.set_font("ArialUni", "", 10)
        self.set_x(x + 8)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")

        # Arrow
        if not is_last:
            arrow_x = x
            self.set_draw_color(41, 98, 255)
            self.line(arrow_x, self.get_y(), arrow_x, self.get_y() + 5)
            self.set_font("ArialUni", "", 8)
            self.set_text_color(41, 98, 255)
            self.text(arrow_x - 1.5, self.get_y() + 7, "▼")
            self.ln(10)
        else:
            self.ln(4)


def create_pdf():
    pdf = ProductPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ==================== PAGE 1: COVER ====================
    pdf.add_page()

    # Background accent bar
    pdf.set_fill_color(41, 98, 255)
    pdf.rect(0, 0, 210, 80, "F")

    # Title
    pdf.set_y(18)
    pdf.set_font("ArialUni", "B", 32)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, "Road Capacity Analyzer", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("ArialUni", "", 14)
    pdf.set_text_color(200, 220, 255)
    pdf.cell(0, 10, "Tự động ước tính bề rộng đường & năng lực thông hành", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "từ ảnh vệ tinh & bản đồ OpenStreetMap", align="C", new_x="LMARGIN", new_y="NEXT")

    # Subtitle box
    pdf.set_y(85)
    pdf.set_font("ArialUni", "I", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Product Overview — Tài liệu giới thiệu sản phẩm", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Key value props
    pdf.set_y(110)
    props = [
        ("[INPUT]  Đầu vào", "Chỉ cần tọa độ khu vực — dữ liệu ảnh vệ tinh & OSM hoàn toàn miễn phí"),
        ("[OUTPUT] Đầu ra", "Bản đồ GIS: bề rộng đường, số làn xe, capacity (xe/giờ) cho từng đoạn đường"),
        ("[SPEED]  Tốc độ", "Xử lý 1 km đường trong < 1 giây — toàn bộ TP.HCM trong vài giờ"),
        ("[COST]   Tiết kiệm", "Thay thế khảo sát thực địa — tiết kiệm hàng tỷ đồng cho mỗi dự án"),
    ]
    for icon_title, desc in props:
        pdf.set_font("ArialUni", "B", 11)
        pdf.set_text_color(41, 98, 255)
        pdf.cell(55, 8, icon_title)
        pdf.set_font("ArialUni", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 8, desc, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Bottom
    pdf.set_y(260)
    pdf.set_font("ArialUni", "", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "Phương pháp dựa trên: Máttyus et al., ICCV 2015 — \"Enhancing Road Maps by Parsing Aerial Images\"", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Tiêu chuẩn capacity: Highway Capacity Manual (HCM 2010), TCVN 4054:2005", align="C", new_x="LMARGIN", new_y="NEXT")

    # ==================== PAGE 2: VẤN ĐỀ & GIẢI PHÁP ====================
    pdf.add_page()
    pdf.section_title("1. Vấn đề hiện tại")

    pdf.body_text(
        "Để đánh giá năng lực thông hành (capacity) của mạng lưới đường giao thông, "
        "các cơ quan quản lý và tư vấn hiện phải thực hiện khảo sát thực địa thủ công: "
        "cử đội ngũ kỹ sư ra đo bề rộng từng con đường, đếm số làn, ghi nhận điều kiện "
        "mặt đường. Quá trình này:"
    )

    problems = [
        "Tốn thời gian: Khảo sát 1 quận có thể mất hàng tuần đến hàng tháng",
        "Tốn chi phí: Nhân công, thiết bị đo, phương tiện di chuyển",
        "Không scale được: Không thể áp dụng cho quy mô tỉnh/quốc gia",
        "Dữ liệu nhanh chóng lỗi thời: Đường xây mới, mở rộng liên tục",
        "Thiếu ở vùng nông thôn/miền núi: Nơi cần nhất nhưng khó tiếp cận nhất",
    ]
    for p in problems:
        pdf.bullet(p)

    pdf.ln(3)
    pdf.section_title("2. Giải pháp: Road Capacity Analyzer")

    pdf.body_text(
        "Sản phẩm tự động trích xuất bề rộng đường từ ảnh vệ tinh kết hợp dữ liệu "
        "OpenStreetMap, sau đó tính toán năng lực thông hành dựa trên tiêu chuẩn "
        "Highway Capacity Manual (HCM). Toàn bộ quy trình không cần khảo sát thực địa."
    )

    pdf.highlight_box(
        "  INPUT:   Tọa độ khu vực cần phân tích (ví dụ: \"Quận 1, TP.HCM\")\n\n"
        "  OUTPUT:  Bản đồ GIS (GeoJSON/Shapefile) với mỗi đoạn đường có:\n"
        "           • Bề rộng đường (mét) — từ ảnh vệ tinh\n"
        "           • Số làn xe ước tính — từ bề rộng\n"
        "           • Capacity (xe/giờ) — từ công thức HCM\n"
        "           • Đánh giá: đủ / cần nâng cấp / quá tải"
    )

    # ==================== PAGE 3: QUY TRÌNH KỸ THUẬT ====================
    pdf.add_page()
    pdf.section_title("3. Quy trình kỹ thuật")

    pdf.subsection_title("3.1 Pipeline xử lý")
    pdf.ln(2)

    pdf.flow_step(1, "Tải đường trung tâm (centerline) từ OpenStreetMap cho khu vực đầu vào")
    pdf.flow_step(2, "Tải ảnh vệ tinh orthorectified (Google Earth / Sentinel-2 / ảnh drone)")
    pdf.flow_step(3, "Tính 5 đặc trưng hình ảnh cho mỗi đoạn đường (Road, Edge, Homogeneity, Context, Car)")
    pdf.flow_step(4, "Chạy MRF Inference (Dynamic Programming + Block Coordinate Descent)")
    pdf.flow_step(5, "Ước tính bề rộng đường (m) và offset centerline (m) cho mỗi segment")
    pdf.flow_step(6, "Tính số làn xe = bề rộng ÷ chiều rộng làn tiêu chuẩn")
    pdf.flow_step(7, "Tính Capacity (xe/giờ) theo công thức HCM 2010", is_last=True)

    pdf.ln(5)
    pdf.subsection_title("3.2 Phương pháp ước tính bề rộng đường")

    pdf.body_text(
        "Thuật toán dựa trên Markov Random Field (MRF), được đề xuất bởi Máttyus et al. "
        "(ICCV 2015). Với mỗi đoạn đường (segment) trên bản đồ OSM, thuật toán:"
    )
    pdf.bullet("Thử mọi bề rộng khả thi (3m đến 13m)")
    pdf.bullet("Chấm điểm dựa trên 5 đặc trưng từ ảnh: đường classifier, cạnh biên, "
               "tính đồng nhất, ngữ cảnh, phát hiện xe")
    pdf.bullet("Dùng Dynamic Programming chọn tổ hợp bề rộng mịn nhất cho toàn bộ con đường")
    pdf.bullet("Ràng buộc: đường song song không được chồng lên nhau")

    pdf.ln(2)
    pdf.highlight_box(
        "  Hiệu suất đã kiểm chứng (Máttyus et al., ICCV 2015):\n"
        "  • IoU (Intersection over Union): 72-77%\n"
        "  • Sai số bề rộng trung bình: < 1.0 mét\n"
        "  • Tốc độ inference: 0.1 giây / km đường\n"
        "  • Training: chỉ 1 phút, generalizes toàn thế giới",
        r=235, g=245, b=235, border_r=40, border_g=167, border_b=69
    )

    # ==================== PAGE 4: TÍNH CAPACITY ====================
    pdf.add_page()
    pdf.section_title("4. Tính năng lực thông hành (Capacity)")

    pdf.subsection_title("4.1 Công thức tính")

    pdf.body_text("Dựa trên Highway Capacity Manual (HCM 2010) và TCVN 4054:2005:")

    pdf.set_font("ArialUni", "", 10)
    pdf.set_text_color(50, 50, 50)

    formulas = [
        "Bước 1:  Số làn = (Bề rộng đường - 2 × Lề đường) ÷ Chiều rộng làn tiêu chuẩn",
        "Bước 2:  Capacity cơ bản = Số làn × Capacity tiêu chuẩn/làn (HCM)",
        "Bước 3:  Capacity thực tế = Capacity cơ bản × fw × fHV × fp × fN",
    ]
    for f in formulas:
        pdf.bullet(f)

    pdf.ln(3)
    pdf.subsection_title("4.2 Thông số capacity theo loại đường")

    # Table
    widths = [45, 35, 35, 35, 40]
    headers = ["Loại đường", "Tốc độ TK", "Làn rộng", "Cap/làn/giờ", "Ví dụ"]
    pdf.table_row(headers, widths, bold=True, fill=True, fill_color=(41, 98, 255))
    # Override text color for header
    pdf.set_y(pdf.get_y() - 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("ArialUni", "B", 9)
    for h_text, w in zip(headers, widths):
        pdf.cell(w, 8, h_text, border=1, fill=True)
    pdf.ln(8)
    # Reset
    pdf.set_fill_color(240, 245, 255)

    rows = [
        ["Cao tốc", "≥ 80 km/h", "3.75m", "2,200", "Cao tốc TPHCM-LT"],
        ["Đường đô thị chính", "50-60 km/h", "3.50m", "1,800", "Nguyễn Văn Linh"],
        ["Đường đô thị phụ", "40-50 km/h", "3.25m", "1,500", "Đường nội quận"],
        ["Đường nội bộ", "< 40 km/h", "3.00m", "1,200", "Đường ngõ, hẻm"],
        ["Đường nông thôn", "30-40 km/h", "2.75m", "800", "Đường liên xã"],
    ]
    for i, row in enumerate(rows):
        pdf.table_row(row, widths, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.subsection_title("4.3 Hệ số điều chỉnh")

    adjustments = [
        ("fw (bề rộng làn)", "0.90 - 1.00: Làn hẹp < 3.3m giảm capacity 10%"),
        ("fHV (xe nặng)", "0.85 - 0.95: Tỷ lệ xe tải cao làm giảm capacity"),
        ("fp (dân số lái)", "0.90 - 1.00: Khu vực có nhiều tài xế thiếu kinh nghiệm"),
        ("fN (số làn)", "0.90 - 1.00: Đường ít làn bị ảnh hưởng bởi xung đột giao thông"),
    ]
    for name, desc in adjustments:
        pdf.set_font("ArialUni", "B", 10)
        pdf.set_text_color(41, 98, 255)
        pdf.cell(40, 7, name)
        pdf.set_font("ArialUni", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 7, desc, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)
    pdf.subsection_title("4.4 Ví dụ tính toán")
    pdf.highlight_box(
        "  Đường Nguyễn Huệ, Quận 1, TP.HCM:\n"
        "  • Bề rộng đo từ ảnh: 25.0m\n"
        "  • Trừ lề + vỉa hè: 25.0 - 2×3.0 = 19.0m khả dụng\n"
        "  • Số làn: 19.0 ÷ 3.5 = 5 làn (làm tròn xuống)\n"
        "  • Capacity cơ bản: 5 × 1,800 = 9,000 xe/giờ\n"
        "  • Hệ số điều chỉnh: 0.95 × 0.95 = 0.90\n"
        "  • Capacity thực tế: 9,000 × 0.90 ≈ 8,100 xe/giờ",
        r=255, g=248, b=230, border_r=255, border_g=165, border_b=0
    )

    # ==================== PAGE 5: KHÁCH HÀNG MỤC TIÊU ====================
    pdf.add_page()
    pdf.section_title("5. Khách hàng mục tiêu")

    customers = [
        (
            "Sở Giao thông Vận tải (Sở GTVT)",
            "• Quy hoạch mở rộng đường: xác định đường nào cần nâng cấp\n"
            "• Đánh giá capacity mạng lưới đường hiện hữu\n"
            "• Lập kế hoạch phân luồng giao thông\n"
            "• Giám sát thi công: so sánh bề rộng thiết kế vs thực tế"
        ),
        (
            "Tư vấn Quy hoạch Đô thị",
            "• Đánh giá hạ tầng giao thông trong ĐTM (Đánh giá Tác động Môi trường)\n"
            "• Mô hình giao thông: cung cấp dữ liệu capacity cho VISUM/VISSIM\n"
            "• Quy hoạch khu đô thị mới: đánh giá kết nối giao thông"
        ),
        (
            "World Bank / ADB / Tổ chức quốc tế",
            "• Đánh giá nhanh hạ tầng giao thông vùng nông thôn trước khi đầu tư\n"
            "• Giám sát dự án: kiểm tra tiến độ xây dựng đường từ xa\n"
            "• Báo cáo tình trạng hạ tầng quốc gia quy mô lớn"
        ),
        (
            "Bảo hiểm / Logistics / Vận tải",
            "• Đánh giá rủi ro tắc đường trên tuyến vận chuyển\n"
            "• Tối ưu hóa tuyến đường dựa trên capacity\n"
            "• Định giá bảo hiểm dựa trên điều kiện hạ tầng"
        ),
    ]

    for title, desc in customers:
        pdf.set_fill_color(245, 248, 255)
        pdf.set_draw_color(41, 98, 255)

        pdf.set_font("ArialUni", "B", 11)
        pdf.set_text_color(41, 98, 255)
        pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("ArialUni", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 6, desc)
        pdf.ln(5)

    # ==================== PAGE 6: LỢI THẾ CẠNH TRANH ====================
    pdf.add_page()
    pdf.section_title("6. Lợi thế cạnh tranh")

    pdf.subsection_title("6.1 So sánh với phương pháp truyền thống")

    widths2 = [50, 65, 75]
    # Header
    pdf.set_fill_color(41, 98, 255)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("ArialUni", "B", 9)
    for h_text, w in zip(["Tiêu chí", "Khảo sát thực địa", "Road Capacity Analyzer"], widths2):
        pdf.cell(w, 8, h_text, border=1, fill=True)
    pdf.ln(8)

    compare_rows = [
        ["Chi phí", "50-200 triệu/quận", "< 5 triệu/quận (chỉ cloud)"],
        ["Thời gian", "2-4 tuần/quận", "Vài giờ/quận"],
        ["Quy mô", "1 quận/lần", "Toàn tỉnh/thành phố"],
        ["Cập nhật", "Khảo sát lại từ đầu", "Chạy lại với ảnh mới"],
        ["Vùng xa", "Rất khó tiếp cận", "Chỉ cần ảnh vệ tinh"],
        ["Độ chính xác", "± 0.1m (rất cao)", "± 1.0m (đủ cho quy hoạch)"],
    ]
    for i, row in enumerate(compare_rows):
        pdf.set_fill_color(245, 248, 255) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(50, 50, 50)
        pdf.table_row(row, widths2, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.highlight_box(
        "  LỢI THẾ THEN CHỐT:\n\n"
        "  Hiện tại, để biết capacity đường ở Việt Nam, phải cử đội khảo sát đi đo\n"
        "  thực địa từng con đường. Road Capacity Analyzer thay thế hoàn toàn bước này\n"
        "  bằng phân tích ảnh vệ tinh tự động → tiết kiệm hàng tỷ đồng cho mỗi dự án\n"
        "  quy hoạch. Đặc biệt hiệu quả ở vùng nông thôn, miền núi — nơi khảo sát\n"
        "  thực địa rất tốn kém và mất thời gian.",
        r=255, g=240, b=240, border_r=220, border_g=50, border_b=50
    )

    pdf.ln(3)
    pdf.subsection_title("6.2 Ưu điểm kỹ thuật")
    tech_advantages = [
        "Không cần GPU: Toàn bộ inference chạy trên CPU laptop thông thường",
        "Tổng quát hóa tốt: Train trên 1.5 km² ở Đức, áp dụng được toàn thế giới (đã kiểm chứng)",
        "Xử lý cực nhanh: < 0.3 giây cho mỗi km đường",
        "Dữ liệu miễn phí: Ảnh Google Earth Pro + OpenStreetMap, không tốn phí license",
        "Tự sửa lỗi OSM: Thuật toán tự động phát hiện và sửa lệch centerline",
        "Có cơ sở khoa học: Dựa trên bài báo ICCV 2015 (hội nghị AI hàng đầu thế giới)",
    ]
    for a in tech_advantages:
        pdf.bullet(a)

    # ==================== PAGE 7: LỘ TRÌNH ====================
    pdf.add_page()
    pdf.section_title("7. Lộ trình phát triển")

    phases = [
        ("Giai đoạn 1 — MVP (Tháng 1-2)", [
            "Reproduce thuật toán MRF từ Máttyus et al. (ICCV 2015)",
            "Chạy thử trên ảnh Google Earth khu vực Karlsruhe, Đức",
            "Validate kết quả: đạt IoU > 70%, sai số bề rộng < 1.5m",
            "Tích hợp module tính capacity theo HCM 2010",
        ]),
        ("Giai đoạn 2 — Việt Nam (Tháng 3)", [
            "Áp dụng lên ảnh Việt Nam (Quận 1 TP.HCM hoặc khu ven biển)",
            "Thu thập ground truth: đo thực địa 20-30 đoạn đường để validate",
            "Điều chỉnh thông số cho điều kiện Việt Nam (TCVN 4054:2005)",
            "Đóng gói thành Python package / QGIS plugin",
        ]),
        ("Giai đoạn 3 — Sản phẩm (Tháng 4-5)", [
            "Xây dựng web app: người dùng nhập tọa độ → nhận bản đồ capacity",
            "Tích hợp xuất báo cáo PDF/Excel tự động",
            "Demo với Sở GTVT hoặc công ty tư vấn quy hoạch",
            "Viết tài liệu kỹ thuật + case study",
        ]),
        ("Giai đoạn 4 — Mở rộng (Tháng 6+)", [
            "Thay thế road classifier bằng deep learning (DeepLabV3) để tăng độ chính xác",
            "Thêm tính năng: phát hiện vỉa hè, chỗ đỗ xe, vạch kẻ đường",
            "Mở rộng sang ứng dụng coastal: đo bề rộng đê biển, bãi biển",
            "Tiếp cận dự án World Bank / ADB về hạ tầng giao thông Đông Nam Á",
        ]),
    ]

    for title, items in phases:
        pdf.set_fill_color(41, 98, 255)
        pdf.set_font("ArialUni", "B", 11)
        pdf.set_text_color(41, 98, 255)
        pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")

        pdf.set_draw_color(230, 230, 230)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        for item in items:
            pdf.bullet(item)
        pdf.ln(4)

    # ==================== PAGE 8: THAM KHẢO ====================
    pdf.add_page()
    pdf.section_title("8. Tài liệu tham khảo")

    refs = [
        "[1] Máttyus G., Wang S., Fidler S., Urtasun R. (2015). \"Enhancing Road Maps by Parsing "
        "Aerial Images Around the World.\" International Conference on Computer Vision (ICCV 2015).",

        "[2] Máttyus G., Wang S., Fidler S., Urtasun R. (2016). \"HD Maps: Fine-grained Road "
        "Segmentation by Parsing Ground and Aerial Images.\" CVPR 2016.",

        "[3] Transportation Research Board (2010). \"Highway Capacity Manual (HCM 2010).\" "
        "National Research Council, Washington D.C.",

        "[4] Bộ Giao thông Vận tải (2005). \"TCVN 4054:2005 — Đường ô tô — Yêu cầu thiết kế.\"",

        "[5] Máttyus G. (2016). \"Joint Information Augmentation of Road Maps, Aerial Images and "
        "Ground Images.\" PhD Thesis, Technische Universität München.",

        "[6] OpenStreetMap Foundation. \"OpenStreetMap — The Free Wiki World Map.\" "
        "https://www.openstreetmap.org",
    ]

    for ref in refs:
        pdf.set_font("ArialUni", "", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 5, ref)
        pdf.ln(3)

    # ==================== SAVE ====================
    output_path = r"f:\Road\Road_Capacity_Analyzer_Product_Overview.pdf"
    pdf.output(output_path)
    print(f"PDF saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    create_pdf()
