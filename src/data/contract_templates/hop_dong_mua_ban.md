# HỢP ĐỒNG MUA BÁN HÀNG HÓA

**Số:** {{contract_number}}

---

## THÔNG TIN CÁC BÊN

### Bên A: BÊN BÁN

- **Tên công ty/cá nhân:** {{seller_name}}
- **Mã số thuế:** {{seller_tax_code}}
- **Địa chỉ:** {{seller_address}}
- **Điện thoại:** {{seller_phone}}
- **Email:** {{seller_email}}
- **Người đại diện:** {{seller_representative}} - Chức vụ: {{seller_position}}

### Bên B: BÊN MUA

- **Tên công ty/cá nhân:** {{buyer_name}}
- **Mã số thuế:** {{buyer_tax_code}}
- **Địa chỉ:** {{buyer_address}}
- **Điện thoại:** {{buyer_phone}}
- **Email:** {{buyer_email}}
- **Người đại diện:** {{buyer_representative}} - Chức vụ: {{buyer_position}}

---

## ĐIỀU 1: HÀNG HÓA

1.1. **Danh mục hàng hóa:**

| STT | Tên hàng | Mã hàng | ĐVT | Số lượng | Đơn giá | Thành tiền |
|-----|----------|---------|-----|----------|---------|------------|
| {{item_1_no}} | {{item_1_name}} | {{item_1_code}} | {{item_1_unit}} | {{item_1_quantity}} | {{item_1_price}} | {{item_1_total}} |
| {{item_2_no}} | {{item_2_name}} | {{item_2_code}} | {{item_2_unit}} | {{item_2_quantity}} | {{item_2_price}} | {{item_2_total}} |
| ... | ... | ... | ... | ... | ... | ... |

**Tổng cộng:** {{total_amount}} VNĐ (Bằng chữ: {{total_amount_in_words}})

1.2. **Chất lượng hàng hóa:** {{quality_standard}}
<!-- Ví dụ: Theo tiêu chuẩn Việt Nam TCVN..., ISO..., hoặc mẫu đã thỏa thuận -->

1.3. **Xuất xứ:** {{origin}}

1.4. **Thương hiệu:** {{brand}}

1.5. **Bao bì đóng gói:** {{packaging}}

---

## ĐIỀU 2: GIÁ CẢ VÀ THANH TOÁN

2.1. **Tổng giá trị hợp đồng:** {{total_contract_value}} VNĐ (Bằng chữ: {{total_value_in_words}})

2.2. **Thuế VAT:** {{vat_rate}}% ({{vat_included_or_excluded}})

2.3. **Phương thức thanh toán:** {{payment_method}}
<!-- Tiền mặt / Chuyển khoản / Séc / L/C -->

2.4. **Tiến độ thanh toán:**
- Tạm ứng: {{deposit_percentage}}% khi ký hợp đồng
- Thanh toán lần 2: {{second_payment_percentage}}% khi {{second_payment_milestone}}
- Thanh toán cuối: {{final_payment_percentage}}% khi {{final_payment_milestone}}

2.5. **Thông tin tài khoản:**
- Ngân hàng: {{seller_bank}}
- Số tài khoản: {{seller_account}}
- Chủ tài khoản: {{seller_account_holder}}

---

## ĐIỀU 3: GIAO HÀNG VÀ VẬN CHUYỂN

3.1. **Địa điểm giao hàng:** {{delivery_location}}

3.2. **Thời hạn giao hàng:** Trong vòng {{delivery_period}} ngày kể từ ngày {{delivery_start_milestone}}

3.3. **Phương thức giao hàng:** {{delivery_method}}
<!-- Giao tận nơi / Giao kho / FOB / CIF... -->

3.4. **Chi phí vận chuyển:** {{shipping_cost_responsibility}}
<!-- Bên A chịu / Bên B chịu / Chia đôi -->

3.5. **Rủi ro:** Rủi ro chuyển giao cho Bên B khi {{risk_transfer_point}}

3.6. **Nghiệm thu:**
- Bên B có quyền kiểm tra hàng hóa trong vòng {{inspection_period}} ngày kể từ ngày nhận hàng
- Nếu không có ý kiến trong thời hạn trên, coi như Bên B chấp nhận hàng hóa

---

## ĐIỀU 4: BẢO HÀNH

4.1. **Thời hạn bảo hành:** {{warranty_period}} tháng kể từ ngày nghiệm thu

4.2. **Phạm vi bảo hành:** {{warranty_scope}}
<!-- Sửa chữa miễn phí / Thay thế / Hoàn tiền -->

4.3. **Điều kiện bảo hành:**
- Lỗi do nhà sản xuất
- Hàng hóa được sử dụng đúng mục đích, đúng hướng dẫn
- Tem bảo hành còn nguyên vẹn

4.4. **Không bảo hành:**
- Hư hỏng do sử dụng sai, va đập, thiên tai
- Tem bảo hành bị rách, mờ, không rõ ràng
- Đã hết thời hạn bảo hành

---

## ĐIỀU 5: QUYỀN VÀ NGHĨA VỤ BÊN BÁN

5.1. **Quyền:**
- Nhận đủ tiền thanh toán đúng hạn
- Yêu cầu Bên B thanh lý hợp đồng nếu vi phạm
- Giữ lại hàng hóa nếu Bên B chưa thanh toán đủ

5.2. **Nghĩa vụ:**
- Giao hàng đúng chất lượng, số lượng, thời hạn
- Cung cấp chứng từ hợp lệ (hóa đơn, chứng từ xuất xứ, CO...)
- Chịu trách nhiệm nếu hàng hóa không đúng cam kết
- Bảo hành theo cam kết

---

## ĐIỀU 6: QUYỀN VÀ NGHĨA VỤ BÊN MUA

6.1. **Quyền:**
- Nhận hàng đúng chất lượng, số lượng
- Kiểm tra, nghiệm thu hàng hóa
- Yêu cầu đổi, trả hàng nếu không đúng cam kết
- Được bảo hành theo cam kết

6.2. **Nghĩa vụ:**
- Thanh toán đủ, đúng hạn
- Nhận hàng đúng thời hạn
- Bảo quản hàng hóa sau khi nhận
- Thông báo ngay cho Bên A nếu phát hiện lỗi

---

## ĐIỀU 7: PHẠT VI PHẠM VÀ BỒI THƯỜNG

7.1. **Giao hàng chậm:** Bên A phạt {{late_delivery_penalty}}%/ngày trên giá trị lô hàng giao chậm (tối đa {{max_late_delivery_penalty}}%)
<!-- Tối đa 8% theo Điều 300 Luật TM 2005 -->

7.2. **Thanh toán chậm:** Bên B phạt {{late_payment_penalty}}%/ngày trên số tiền chậm (tối đa {{max_late_payment_penalty}}%)

7.3. **Hàng hóa không đúng chất lượng:**
- Bên A phải đổi hàng trong vòng {{replacement_period}} ngày
- Nếu không đổi được, Bên B có quyền hủy hợp đồng và yêu cầu hoàn tiền + bồi thường thiệt hại

7.4. **Hủy hợp đồng trái pháp luật:** Bên vi phạm phạt {{contract_breach_penalty}}% giá trị hợp đồng

7.5. **Mức phạt tối đa:** Không vượt quá 8% giá trị phần nghĩa vụ vi phạm (theo Điều 300 Luật TM 2005)

---

## ĐIỀU 8: BẤT KHẢ KHÁNG

8.1. Bất khả kháng là sự kiện xảy ra khách quan, không thể lường trước và không thể khắc phục (thiên tai, hỏa hoạn, chiến tranh, dịch bệnh, chính sách cấm vận...)

8.2. Bên gặp bất khả kháng phải thông báo cho bên kia trong vòng {{force_majeure_notice}} ngày và cung cấp chứng từ chứng minh

8.3. Nghĩa vụ thực hiện hợp đồng được tạm hoãn trong thời gian bất khả kháng

8.4. Nếu bất khả kháng kéo dài quá {{force_majeure_duration}} ngày, các bên có quyền chấm dứt hợp đồng

---

## ĐIỀU 9: GIẢI QUYẾT TRANH CHẤP

9.1. Mọi tranh chấp phát sinh được giải quyết trước hết bằng thương lượng

9.2. Nếu không thương lượng được trong vòng {{dispute_resolution_period}} ngày, tranh chấp sẽ được đưa ra:
- Trọng tài kinh tế {{arbitration_center}}
- Hoặc Tòa án nhân dân {{court_jurisdiction}}

9.3. **Luật áp dụng:** Pháp luật Việt Nam

---

## ĐIỀU 10: ĐIỀU KHOẢN CHUNG

10.1. Hợp đồng có hiệu lực kể từ ngày ký

10.2. Thời hạn hợp đồng: Từ ngày {{contract_start_date}} đến khi hoàn thành nghĩa vụ

10.3. Mọi sửa đổi, bổ sung phải lập thành văn bản có chữ ký của cả hai bên

10.4. Hợp đồng lập thành 02 bản, mỗi bên giữ 01 bản có giá trị pháp lý như nhau

10.5. **Phụ lục:** Danh mục hàng hóa chi tiết (nếu có) là bộ phận không tách rời của hợp đồng

---

**Ngày ký:** {{signing_date}}

| **BÊN BÁN (A)** | **BÊN MUA (B)** |
|-----------------|-----------------|
| (Ký, ghi rõ họ tên, đóng dấu) | (Ký, ghi rõ họ tên, đóng dấu) |
| {{seller_signature}} | {{buyer_signature}} |

---

<!--
Căn cứ pháp lý:
- Luật Thương mại 2005 (Chương IV - Hợp đồng mua bán hàng hóa)
- Điều 284-308 Luật TM 2005
- Điều 418 BLDS 2015 về phạt vi phạm hợp đồng
- Luật Bảo vệ quyền lợi người tiêu dùng 2010
-->
