#!/usr/bin/env python3
"""Quick test for diff utility"""

from src.services.diff_utils import generate_inline_diff

original = """Điều 1: Đối tượng hợp đồng
Bên A đồng ý cung cấp dịch vụ tư vấn pháp lý cho Bên B.

Điều 2: Thời hạn hợp đồng
Hợp đồng có hiệu lực trong 12 tháng.

Điều 3: Giá trị hợp đồng
Tổng giá trị: 100.000.000 VNĐ."""

edited = """Điều 1: Đối tượng hợp đồng
Bên A đồng ý cung cấp dịch vụ tư vấn pháp lý cho Bên B theo quy định tại Luật Doanh nghiệp 2020.

Điều 2: Thời hạn hợp đồng
Hợp đồng có hiệu lực trong 12 tháng, tự động gia hạn nếu không có thông báo chấm dứt.

Điều 3: Giá trị hợp đồng
Tổng giá trị: 100.000.000 VNĐ (bằng chữ: Một trăm triệu đồng).

Điều 4: Bảo mật thông tin
Các bên cam kết bảo mật thông tin theo quy định tại Điều 16 BLLĐ 2019."""

print("Testing diff generation...")
result = generate_inline_diff(original, edited)

print(f"\n✅ Changes count: {result['changes_count']}")
print(f"✅ Additions: {result['additions']}")
print(f"✅ Deletions: {result['deletions']}")
print(f"✅ Summary: {result['summary']}")
print(f"\n📄 Diff HTML (first 500 chars):")
print(result['diff_html'][:500] + "...")
print("\n✅ Test passed!")
