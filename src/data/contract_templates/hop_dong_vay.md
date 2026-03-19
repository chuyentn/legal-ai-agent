# HỢP ĐỒNG VAY

**Số:** {{contract_number}}

---

## THÔNG TIN CÁC BÊN

### Bên A: BÊN CHO VAY

- **Tên công ty/cá nhân:** {{lender_name}}
- **CMND/CCCD:** {{lender_id}} - Ngày cấp: {{lender_id_issue_date}} - Nơi cấp: {{lender_id_issue_place}}
- **Địa chỉ:** {{lender_address}}
- **Điện thoại:** {{lender_phone}}
- **Email:** {{lender_email}}

### Bên B: BÊN VAY

- **Tên công ty/cá nhân:** {{borrower_name}}
- **CMND/CCCD:** {{borrower_id}} - Ngày cấp: {{borrower_id_issue_date}} - Nơi cấp: {{borrower_id_issue_place}}
- **Địa chỉ:** {{borrower_address}}
- **Điện thoại:** {{borrower_phone}}
- **Email:** {{borrower_email}}

---

## ĐIỀU 1: SỐ TIỀN VAY VÀ MỤC ĐÍCH

1.1. **Số tiền vay:** {{loan_amount}} VNĐ (Bằng chữ: {{loan_amount_in_words}})

1.2. **Mục đích vay:** {{loan_purpose}}
<!-- Ví dụ: Đầu tư kinh doanh, Mua nhà, Tiêu dùng cá nhân, Thanh toán nợ... -->

1.3. **Hình thức giao nhận:**
- Chuyển khoản vào tài khoản số {{borrower_account}} tại {{borrower_bank}}
- Hoặc giao tiền mặt (có biên nhận)

1.4. **Ngày giải ngân:** {{disbursement_date}}

---

## ĐIỀU 2: LÃI SUẤT

2.1. **Lãi suất:** {{interest_rate}}%/{{interest_period}}
<!-- %/năm hoặc %/tháng -->

<!-- Ghi chú: Lãi suất tối đa theo Điều 468 BLDS 2015:
- Cho vay giữa cá nhân: Tối đa 20%/năm
- Cho vay giữa tổ chức tín dụng và cá nhân/tổ chức: Theo quy định của Ngân hàng Nhà nước
-->

2.2. **Phương thức tính lãi:** {{interest_calculation_method}}
<!-- Lãi đơn / Lãi kép / Lãi suất cố định / Lãi suất thả nổi -->

2.3. **Kỳ tính lãi:** {{interest_accrual_period}}
<!-- Tính theo tháng / quý / năm -->

2.4. **Lãi suất quá hạn:** {{overdue_interest_rate}}%/{{overdue_period}}
<!-- Thường cao hơn lãi suất gốc 50% -->

---

## ĐIỀU 3: KỲ HẠN VAY

3.1. **Thời hạn vay:** {{loan_term}} tháng/năm

3.2. **Ngày bắt đầu:** {{start_date}}

3.3. **Ngày đáo hạn:** {{maturity_date}}

3.4. **Gia hạn:** {{extension_policy}}
<!-- Có thể gia hạn khi đến hạn nếu hai bên thỏa thuận / Không được gia hạn -->

---

## ĐIỀU 4: PHƯƠNG THỨC TRẢ NỢ

4.1. **Phương thức:** {{repayment_method}}
<!-- Trả gốc + lãi cuối kỳ / Trả gốc định kỳ, lãi cuối kỳ / Trả gốc lãi đều hàng tháng (annuity) -->

4.2. **Lịch trả nợ:**

| Kỳ | Ngày trả | Gốc (VNĐ) | Lãi (VNĐ) | Tổng (VNĐ) | Dư nợ (VNĐ) |
|----|----------|-----------|-----------|------------|-------------|
| {{period_1}} | {{date_1}} | {{principal_1}} | {{interest_1}} | {{total_1}} | {{balance_1}} |
| {{period_2}} | {{date_2}} | {{principal_2}} | {{interest_2}} | {{total_2}} | {{balance_2}} |
| ... | ... | ... | ... | ... | ... |

4.3. **Phương thức thanh toán:**
- Chuyển khoản vào tài khoản số {{lender_account}} tại {{lender_bank}}
- Hoặc nộp tiền mặt (có biên nhận)

4.4. **Thời hạn thanh toán:** Trước hoặc vào ngày đáo hạn. Nếu ngày đáo hạn trùng ngày nghỉ, thanh toán vào ngày làm việc tiếp theo.

---

## ĐIỀU 5: TRẢ NỢ TRƯỚC HẠN

5.1. Bên B có quyền trả nợ trước hạn (một phần hoặc toàn bộ) {{prepayment_policy}}
<!-- Bất cứ lúc nào / Phải báo trước X ngày / Không được trả trước hạn -->

5.2. **Phí trả nợ trước hạn:** {{prepayment_fee}}
<!-- Không phí / X% số tiền trả trước hạn / X% lãi còn lại -->

5.3. Khi trả nợ trước hạn, lãi chỉ tính đến ngày trả thực tế.

---

## ĐIỀU 6: TÀI SẢN ĐẢM BẢO (Nếu có)

6.1. **Loại tài sản:** {{collateral_type}}
<!-- Nhà đất / Ô tô / Máy móc / Cổ phiếu / Vàng / Tài sản khác -->

6.2. **Mô tả tài sản:**
- Địa chỉ/vị trí: {{collateral_location}}
- Diện tích/số lượng: {{collateral_quantity}}
- Giá trị ước tính: {{collateral_value}} VNĐ
- Giấy tờ pháp lý: {{collateral_documents}}
<!-- Sổ đỏ / Giấy đăng ký xe / Chứng từ sở hữu -->

6.3. **Hình thức đảm bảo:** {{security_type}}
<!-- Thế chấp / Cầm cố / Bảo lãnh / Ký cược ký quỹ -->

6.4. **Đăng ký giao dịch bảo đảm:**
- Tài sản thế chấp phải được đăng ký tại {{registration_authority}} (theo NĐ 102/2017/NĐ-CP)
- Chi phí đăng ký do {{registration_fee_payer}} chịu

6.5. **Quyền xử lý tài sản:**
- Nếu Bên B không trả nợ đúng hạn, Bên A có quyền xử lý tài sản đảm bảo (bán đấu giá, thỏa thuận, định đoạt...)
- Thu hồi nợ gốc, lãi, phí, lệ phí. Số tiền thừa (nếu có) trả lại Bên B.

---

## ĐIỀU 7: QUYỀN VÀ NGHĨA VỤ BÊN CHO VAY

7.1. **Quyền:**
- Nhận đủ gốc, lãi đúng hạn
- Kiểm tra việc sử dụng vốn vay (nếu cho vay có mục đích)
- Yêu cầu Bên B trả nợ trước hạn nếu vi phạm nghiêm trọng hợp đồng
- Xử lý tài sản đảm bảo khi Bên B không trả nợ

7.2. **Nghĩa vụ:**
- Giao tiền vay đủ, đúng hạn
- Không yêu cầu lãi suất vượt mức quy định pháp luật
- Cung cấp chứng từ thanh toán (hóa đơn, biên nhận, sao kê)

---

## ĐIỀU 8: QUYỀN VÀ NGHĨA VỤ BÊN VAY

8.1. **Quyền:**
- Nhận đủ tiền vay đúng hạn
- Trả nợ trước hạn (theo thỏa thuận)
- Nhận lại tài sản đảm bảo khi trả hết nợ

8.2. **Nghĩa vụ:**
- Sử dụng tiền vay đúng mục đích (nếu cho vay có mục đích)
- Trả gốc, lãi đầy đủ, đúng hạn
- Bảo quản tài sản đảm bảo
- Thông báo ngay cho Bên A nếu tài sản đảm bảo bị mất, hư hỏng, giảm giá trị
- Chịu mọi rủi ro liên quan đến việc vay vốn

---

## ĐIỀU 9: PHẠT TRẢ CHẬM VÀ XỬ LÝ VI PHẠM

9.1. **Phạt trả chậm:**
- Nếu Bên B trả chậm, phải chịu phạt {{late_payment_penalty}}%/ngày trên số tiền chậm trả (tối đa {{max_late_penalty}}%)
- Lãi tiếp tục tính trên số tiền chậm với lãi suất quá hạn (Điều 2.4)

9.2. **Vi phạm nghiêm trọng:** Bên A có quyền yêu cầu trả nợ ngay lập tức (không cần chờ đáo hạn) nếu Bên B:
- Chậm trả nợ quá {{default_grace_period}} ngày
- Sử dụng tiền vay sai mục đích (đối với khoản vay có mục đích)
- Cố ý làm giảm giá trị tài sản đảm bảo
- Chuyển nhượng, tẩu tán tài sản để trốn nợ
- Bị phá sản, giải thể

9.3. **Xử lý tài sản đảm bảo:**
- Nếu Bên B không trả nợ trong vòng {{foreclosure_notice}} ngày kể từ ngày đáo hạn, Bên A có quyền xử lý tài sản đảm bảo
- Thứ tự ưu tiên thanh toán: (1) Phí, lệ phí xử lý tài sản, (2) Lãi quá hạn, (3) Lãi đúng hạn, (4) Gốc, (5) Phạt vi phạm

---

## ĐIỀU 10: BẤT KHẢ KHÁNG

10.1. Bất khả kháng: thiên tai, hỏa hoạn, chiến tranh, dịch bệnh không thể lường trước và không thể khắc phục

10.2. Bên gặp bất khả kháng phải thông báo cho bên kia trong vòng {{force_majeure_notice}} ngày

10.3. Thời hạn trả nợ được gia hạn tương ứng với thời gian bất khả kháng (nếu hai bên thỏa thuận)

10.4. Nếu bất khả kháng kéo dài quá {{force_majeure_duration}} ngày, các bên có quyền chấm dứt hợp đồng

---

## ĐIỀU 11: GIẢI QUYẾT TRANH CHẤP

11.1. Tranh chấp được giải quyết bằng thương lượng

11.2. Nếu không thương lượng được trong {{dispute_period}} ngày, tranh chấp sẽ được đưa ra Tòa án nhân dân {{court_jurisdiction}}

11.3. **Luật áp dụng:** Pháp luật Việt Nam

---

## ĐIỀU 12: ĐIỀU KHOẢN CHUNG

12.1. Hợp đồng có hiệu lực kể từ ngày ký

12.2. Mọi sửa đổi, bổ sung phải lập thành văn bản có chữ ký của cả hai bên

12.3. Hợp đồng lập thành 02 bản, mỗi bên giữ 01 bản có giá trị pháp lý như nhau

12.4. **Phụ lục:** Lịch trả nợ chi tiết, Biên bản thế chấp (nếu có) là bộ phận không tách rời của hợp đồng

---

**Ngày ký:** {{signing_date}}

| **BÊN CHO VAY (A)** | **BÊN VAY (B)** |
|---------------------|-----------------|
| (Ký, ghi rõ họ tên) | (Ký, ghi rõ họ tên) |
| {{lender_signature}} | {{borrower_signature}} |

---

## PHỤ LỤC: XÁC NHẬN NHẬN TIỀN

Tôi là **{{borrower_name}}**, CMND/CCCD: {{borrower_id}}, xác nhận đã nhận đủ số tiền **{{loan_amount}} VNĐ** (Bằng chữ: {{loan_amount_in_words}}) từ {{lender_name}} vào ngày {{disbursement_date}}.

**Người nhận tiền**  
(Ký, ghi rõ họ tên)

{{borrower_signature}}

---

<!--
Căn cứ pháp lý:
- Bộ luật Dân sự 2015 - Điều 466-482 về Hợp đồng vay
- Điều 468 BLDS 2015: Lãi suất tối đa 20%/năm (đối với cá nhân)
- Nghị định 102/2017/NĐ-CP về đăng ký giao dịch bảo đảm
- Điều 295-318 BLDS 2015 về Thế chấp tài sản
- Điều 319-326 BLDS 2015 về Cầm cố tài sản
- Điều 418 BLDS 2015 về phạt vi phạm hợp đồng
-->
