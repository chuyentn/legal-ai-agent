# HỢP ĐỒNG ĐẠI LÝ

**Số:** {{contract_number}}

---

## THÔNG TIN CÁC BÊN

### Bên A: BÊN CHỦ (Principal)

- **Tên công ty:** {{principal_name}}
- **Mã số thuế:** {{principal_tax_code}}
- **Địa chỉ:** {{principal_address}}
- **Điện thoại:** {{principal_phone}}
- **Email:** {{principal_email}}
- **Người đại diện:** {{principal_representative}} - Chức vụ: {{principal_position}}

### Bên B: BÊN ĐẠI LÝ (Agent)

- **Tên công ty:** {{agent_name}}
- **Mã số thuế:** {{agent_tax_code}}
- **Địa chỉ:** {{agent_address}}
- **Điện thoại:** {{agent_phone}}
- **Email:** {{agent_email}}
- **Người đại diện:** {{agent_representative}} - Chức vụ: {{agent_position}}

---

## ĐIỀU 1: LOẠI ĐẠI LÝ

1.1. **Loại:** {{agency_type}}

<!-- Chọn một trong các loại sau:
- **Đại lý độc lập:** Đại lý thực hiện giao dịch nhân danh Bên B, Bên B chịu trách nhiệm trước bên thứ ba
- **Đại lý phụ thuộc:** Đại lý thực hiện giao dịch nhân danh Bên A, Bên A chịu trách nhiệm trước bên thứ ba
- **Đại lý độc quyền:** Chỉ Bên B được phép phân phối sản phẩm của Bên A trong khu vực nhất định
- **Đại lý không độc quyền:** Bên A có thể chỉ định nhiều đại lý hoặc tự bán hàng trong cùng khu vực
-->

1.2. **Quyền ký kết hợp đồng:**
- Bên B {{contract_authority}} quyền ký kết hợp đồng mua bán nhân danh Bên A
<!-- Có / Không có -->

1.3. **Giới hạn quyền hạn:**
- Bên B chỉ có quyền thực hiện giao dịch trong phạm vi {{transaction_limit}} VNĐ
- Giao dịch vượt giới hạn phải được Bên A phê duyệt bằng văn bản

---

## ĐIỀU 2: SẢN PHẨM VÀ DỊCH VỤ

2.1. **Sản phẩm/dịch vụ đại lý:**

| STT | Tên sản phẩm/dịch vụ | Mã SP | Đơn giá | Hoa hồng (%) | Ghi chú |
|-----|----------------------|-------|---------|--------------|---------|
| {{item_1_no}} | {{item_1_name}} | {{item_1_code}} | {{item_1_price}} | {{item_1_commission}} | {{item_1_note}} |
| {{item_2_no}} | {{item_2_name}} | {{item_2_code}} | {{item_2_price}} | {{item_2_commission}} | {{item_2_note}} |
| ... | ... | ... | ... | ... | ... |

2.2. **Bảng giá:** Bên A cung cấp bảng giá bán cho khách hàng và bảng giá đại lý riêng (nếu có). Bảng giá có thể thay đổi theo thông báo của Bên A.

2.3. **Sản phẩm mới:** Khi Bên A ra mắt sản phẩm mới, Bên B được ưu tiên phân phối (đối với đại lý độc quyền).

---

## ĐIỀU 3: KHU VỰC ĐẠI LÝ

3.1. **Phạm vi địa lý:** {{territory}}
<!-- Ví dụ: Toàn quốc / Miền Bắc / TP.HCM và các tỉnh phía Nam / Quốc tế (Đông Nam Á)... -->

3.2. **Độc quyền:** {{exclusivity_status}}
<!-- Độc quyền / Không độc quyền -->

3.3. **Nếu độc quyền:**
- Bên A không được chỉ định đại lý khác hoặc tự bán hàng trong khu vực này
- Bên B phải cam kết đạt doanh số tối thiểu: {{minimum_sales_target}} VNĐ/{{target_period}}
- Nếu không đạt doanh số 02 kỳ liên tiếp, Bên A có quyền hủy độc quyền

---

## ĐIỀU 4: HOA HỒNG VÀ THANH TOÁN

4.1. **Hoa hồng:** {{commission_percentage}}% trên doanh thu thuần (sau thuế VAT)

4.2. **Phương thức tính hoa hồng:** {{commission_calculation}}
<!-- Tính trên doanh thu / Tính trên lợi nhuận / Hoa hồng cố định mỗi giao dịch -->

4.3. **Kỳ thanh toán hoa hồng:** {{commission_payment_schedule}}
<!-- Hàng tháng / Hàng quý / Sau mỗi giao dịch -->

4.4. **Thời hạn thanh toán:** Trong vòng {{commission_payment_period}} ngày kể từ cuối kỳ

4.5. **Báo cáo doanh số:**
- Bên B phải gửi báo cáo doanh số cho Bên A vào ngày {{reporting_date}} hàng {{reporting_frequency}}
- Báo cáo bao gồm: danh sách khách hàng, số lượng bán, doanh thu, hóa đơn

4.6. **Phương thức thanh toán:**
- Chuyển khoản vào tài khoản số {{agent_account}} tại {{agent_bank}}

4.7. **Thưởng doanh số (nếu có):** Nếu đạt doanh số vượt chỉ tiêu, Bên B được thưởng thêm {{bonus_structure}}

---

## ĐIỀU 5: THỜI HẠN HỢP ĐỒNG

5.1. **Thời hạn:** {{contract_duration}} tháng/năm

5.2. **Từ ngày:** {{start_date}} **đến ngày:** {{end_date}}

5.3. **Gia hạn tự động:** {{auto_renewal}}
<!-- Có / Không. Nếu có, gia hạn tự động mỗi X tháng/năm trừ khi một bên thông báo chấm dứt trước X ngày -->

---

## ĐIỀU 6: QUYỀN VÀ NGHĨA VỤ BÊN CHỦ

6.1. **Quyền:**
- Thu hồi quyền đại lý nếu Bên B vi phạm nghiêm trọng hợp đồng
- Kiểm tra hoạt động đại lý của Bên B
- Thay đổi bảng giá (phải thông báo trước {{price_change_notice}} ngày)
- Chấm dứt hợp đồng nếu Bên B không đạt doanh số tối thiểu (đối với đại lý độc quyền)

6.2. **Nghĩa vụ:**
- Cung cấp sản phẩm đủ số lượng, chất lượng cho Bên B
- Giao hàng đúng hạn (trong vòng {{delivery_time}} ngày kể từ khi nhận đơn hàng)
- Hỗ trợ marketing: {{marketing_support}}
<!-- Catalogue, brochure, banner, quảng cáo, đào tạo bán hàng... -->
- Bảo hành sản phẩm theo cam kết
- Thanh toán hoa hồng đúng hạn
- Giải quyết khiếu nại của khách hàng (nếu do lỗi sản phẩm)

---

## ĐIỀU 7: QUYỀN VÀ NGHĨA VỤ BÊN ĐẠI LÝ

7.1. **Quyền:**
- Nhận hoa hồng đúng hạn
- Được hỗ trợ marketing, đào tạo
- Được độc quyền trong khu vực (nếu là đại lý độc quyền)
- Yêu cầu Bên A giao hàng đúng hạn, đúng chất lượng

7.2. **Nghĩa vụ:**
- Tích cực quảng bá, bán hàng trong khu vực được phân công
- Đạt chỉ tiêu doanh số (nếu có)
- Tuân thủ chính sách giá bán, chính sách khuyến mại của Bên A
- Báo cáo doanh số định kỳ
- Không bán hàng giả, hàng nhái, hàng kém chất lượng
- Bảo vệ uy tín thương hiệu của Bên A
- Không kinh doanh sản phẩm cạnh tranh (nếu có thỏa thuận)
- Thu thập phản hồi khách hàng, báo cáo cho Bên A
- Chịu trách nhiệm về hoạt động kinh doanh của mình (thuế, giấy phép, nhân sự...)

---

## ĐIỀU 8: GIAO HÀNG VÀ THANH TOÁN

8.1. **Đơn đặt hàng:**
- Bên B gửi đơn đặt hàng cho Bên A qua email/hệ thống (ít nhất {{order_lead_time}} ngày trước khi cần hàng)
- Bên A xác nhận đơn hàng trong vòng {{order_confirmation_time}} ngày

8.2. **Giao hàng:**
- Địa điểm giao hàng: {{delivery_location}}
- Thời gian giao hàng: {{delivery_time}} ngày kể từ khi xác nhận đơn
- Chi phí vận chuyển: {{shipping_cost_responsibility}}
<!-- Bên A chịu / Bên B chịu / Chia đôi -->

8.3. **Thanh toán:**
- Hình thức: {{payment_terms}}
<!-- Trả trước 100% / Trả sau khi nhận hàng / Trả sau X ngày / Công nợ X ngày -->
- Nếu có công nợ: Hạn mức công nợ tối đa {{credit_limit}} VNĐ, thời hạn {{credit_period}} ngày

8.4. **Quyền sở hữu hàng hóa:**
- Đối với đại lý độc lập: Bên B mua hàng từ Bên A, sở hữu hàng hóa
- Đối với đại lý phụ thuộc: Hàng hóa vẫn thuộc sở hữu Bên A, Bên B chỉ giữ hộ và bán hộ

---

## ĐIỀU 9: BẢO HÀNH VÀ HẬU MÃI

9.1. **Bảo hành:** Sản phẩm được bảo hành {{warranty_period}} tháng theo chính sách bảo hành của Bên A

9.2. **Trách nhiệm bảo hành:**
- Bên A chịu trách nhiệm bảo hành (sửa chữa, thay thế) cho khách hàng
- Bên B có trách nhiệm tiếp nhận yêu cầu bảo hành và chuyển đến Bên A

9.3. **Hàng lỗi, trả hàng:**
- Hàng lỗi do nhà sản xuất: Bên A chịu trách nhiệm đổi hàng trong vòng {{return_period}} ngày
- Hàng không tiêu thụ được (quá hạn, ế ẩm): {{unsold_goods_policy}}
<!-- Không được trả lại / Trả lại với điều kiện X / Trả lại và được hoàn tiền X% -->

---

## ĐIỀU 10: SỞ HỮU TRÍ TUỆ VÀ THƯƠNG HIỆU

10.1. **Nhãn hiệu, thương hiệu:** Bên B được phép sử dụng nhãn hiệu, logo, thương hiệu của Bên A trong hoạt động đại lý (theo hướng dẫn sử dụng nhãn hiệu)

10.2. **Không sở hữu:** Bên B không có quyền sở hữu đối với nhãn hiệu, thương hiệu của Bên A

10.3. **Không đăng ký:** Bên B không được đăng ký nhãn hiệu, tên miền, tài khoản mạng xã hội trùng hoặc tương tự với thương hiệu của Bên A (trừ khi có sự đồng ý bằng văn bản)

10.4. **Khi chấm dứt hợp đồng:** Bên B phải ngừng sử dụng mọi nhãn hiệu, logo, thương hiệu của Bên A

---

## ĐIỀU 11: BẢO MẬT THÔNG TIN

11.1. **Thông tin bảo mật:**
- Bảng giá đại lý, chính sách hoa hồng
- Danh sách khách hàng, thông tin khách hàng
- Kế hoạch kinh doanh, chiến lược marketing
- Thông tin kỹ thuật, bí quyết sản xuất (nếu có tiếp cận)

11.2. **Nghĩa vụ bảo mật:**
- Không tiết lộ cho bên thứ ba
- Chỉ sử dụng cho mục đích thực hiện hợp đồng đại lý
- Bảo vệ dữ liệu khách hàng theo Nghị định 13/2023/NĐ-CP

11.3. **Thời hạn bảo mật:** {{confidentiality_period}} năm kể từ khi chấm dứt hợp đồng

11.4. **Vi phạm bảo mật:** Phạt {{confidentiality_penalty}}% giá trị hợp đồng + bồi thường thiệt hại

---

## ĐIỀU 12: CHẤM DỨT HỢP ĐỒNG

12.1. **Hợp đồng chấm dứt khi:**
- Hết thời hạn
- Hai bên thỏa thuận chấm dứt
- Một bên đơn phương chấm dứt hợp pháp

12.2. **Đơn phương chấm dứt:**
- Phải báo trước {{termination_notice}} ngày bằng văn bản
- Bên A có quyền chấm dứt ngay nếu Bên B:
  - Vi phạm nghiêm trọng hợp đồng (bán hàng giả, làm tổn hại uy tín...)
  - Không đạt doanh số tối thiểu 02 kỳ liên tiếp (đại lý độc quyền)
  - Vi phạm bảo mật
- Bên B có quyền chấm dứt nếu Bên A không thanh toán hoa hồng quá {{payment_delay_threshold}} ngày

12.3. **Thanh lý khi chấm dứt:**
- Thanh toán hết công nợ, hoa hồng
- Trả lại tài liệu, tài sản của Bên A (nếu có)
- Ngừng sử dụng nhãn hiệu, thương hiệu
- Hàng hóa tồn kho: {{termination_inventory_policy}}
<!-- Bên A mua lại / Bên B tự xử lý / Chia sẻ tổn thất -->

---

## ĐIỀU 13: PHẠT VI PHẠM

13.1. **Không đạt doanh số:** Phạt {{underperformance_penalty}} VNĐ/kỳ (nếu là đại lý độc quyền)

13.2. **Bán hàng ngoài khu vực (vi phạm độc quyền):** Phạt {{territory_violation_penalty}}% doanh thu giao dịch vi phạm

13.3. **Thanh toán chậm:** Phạt {{late_payment_penalty}}%/ngày trên số tiền chậm

13.4. **Vi phạm giá bán, chính sách:** Phạt {{price_violation_penalty}} VNĐ/lần

13.5. **Hủy hợp đồng trái pháp luật:** Phạt {{contract_breach_penalty}}% giá trị hoa hồng 12 tháng gần nhất

13.6. **Mức phạt tối đa:** Không vượt quá 8% giá trị phần nghĩa vụ vi phạm (theo Điều 418 BLDS 2015)

---

## ĐIỀU 14: BẤT KHẢ KHÁNG

14.1. Bất khả kháng: thiên tai, chiến tranh, dịch bệnh, thay đổi chính sách...

14.2. Bên gặp bất khả kháng phải thông báo trong {{force_majeure_notice}} ngày

14.3. Nghĩa vụ thực hiện hợp đồng được tạm hoãn tương ứng

14.4. Nếu kéo dài quá {{force_majeure_duration}} ngày, các bên có quyền chấm dứt hợp đồng

---

## ĐIỀU 15: GIẢI QUYẾT TRANH CHẤP

15.1. Tranh chấp được giải quyết bằng thương lượng

15.2. Nếu không thương lượng được trong {{dispute_period}} ngày, tranh chấp sẽ được đưa ra Tòa án nhân dân {{court_jurisdiction}}

15.3. **Luật áp dụng:** Pháp luật Việt Nam

---

## ĐIỀU 16: ĐIỀU KHOẢN CHUNG

16.1. Hợp đồng có hiệu lực kể từ ngày ký

16.2. Mọi sửa đổi, bổ sung phải lập thành văn bản có chữ ký của cả hai bên

16.3. Hợp đồng lập thành 02 bản, mỗi bên giữ 01 bản có giá trị pháp lý như nhau

16.4. **Phụ lục:** Bảng giá sản phẩm, Danh mục sản phẩm, Hướng dẫn sử dụng nhãn hiệu (nếu có) là bộ phận không tách rời của hợp đồng

---

**Ngày ký:** {{signing_date}}

| **BÊN CHỦ (A)** | **BÊN ĐẠI LÝ (B)** |
|-----------------|---------------------|
| (Ký, ghi rõ họ tên, đóng dấu) | (Ký, ghi rõ họ tên, đóng dấu) |
| {{principal_signature}} | {{agent_signature}} |

---

<!--
Căn cứ pháp lý:
- Luật Thương mại 2005 - Điều 116-131 về Hợp đồng đại lý
- Bộ luật Dân sự 2015 - Điều 554-562 về Hợp đồng ủy quyền
- Điều 418 BLDS 2015 về phạt vi phạm hợp đồng
- Luật Sở hữu trí tuệ 2005 (sửa đổi 2009, 2019) về nhãn hiệu
- Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân
-->
