# Legal AI Vietnam — Nghiên cứu thị trường & Kỹ thuật

## 1. Đối thủ cạnh tranh

### 🏆 AI Luật (ailuat.luatvietnam.vn) — ĐỐI THỦ CHÍNH
- **Ai làm:** LuatVietnam.vn (công ty đã có 20+ năm trong ngành pháp luật)
- **Vận hành:** Cổng Pháp luật Quốc gia (ai.phapluat.gov.vn) — CHÍNH PHỦ dùng sản phẩm này
- **Phiên bản:** 1.0.1
- **Phạm vi:** 37 lĩnh vực pháp luật
- **Tính năng:** Giải đáp pháp lý, tra cứu văn bản, đa ngôn ngữ (Anh/Trung/Nhật/Hàn), giọng nói
- **Dữ liệu:** Hàng trăm nghìn văn bản pháp luật từ 1945 đến nay

#### Bảng giá AI Luật:
| Gói | Giá/tháng | Câu hỏi/tháng | Giá/câu |
|---|---|---|---|
| Cơ bản | 425.000đ | 50 | 8.500đ |
| Nâng cao | 2.490.000đ | 300 | 8.300đ |
| Doanh nghiệp | 8.000.000đ | 1.000 | 8.000đ |
| Theo lượt | 8.800đ/câu | Linh hoạt | 8.800đ |

#### Gói năm:
| Gói | Giá/năm | Câu hỏi/năm |
|---|---|---|
| Cơ bản | 5.100.000đ | 600 |
| Nâng cao | 29.880.000đ | 3.600 |
| Doanh nghiệp | 96.000.000đ | 12.000 |

**Nhận xét:**
- Lợi thế cực lớn: data 20+ năm, brand nhận diện, chính phủ dùng
- Yếu điểm: KHÔNG có Cloud API cho developer, KHÔNG có contract review, KHÔNG có multi-tenant
- Chỉ là chatbot Q&A, chưa phải platform cho doanh nghiệp tích hợp

### Đối thủ quốc tế (reference):
| Sản phẩm | Chức năng | Giá |
|---|---|---|
| **Harvey AI** | Legal AI assistant, contract review | Enterprise pricing |
| **LegalOn** | Contract review, 50+ playbooks | ~$199/user/month |
| **Ironclad (Jurist)** | CLM + AI contract review | Enterprise |
| **Spellbook** | Contract drafting in Word | ~$500/month |
| **Checkbox AI** | Legal chatbot for in-house | Custom |

---

## 2. Phân tích SWOT

### Strengths (Điểm mạnh)
- **API-first approach** — AI Luật chỉ có web chatbot, chưa ai cung cấp Cloud API
- **Contract review** — Thị trường VN chưa có sản phẩm review hợp đồng bằng AI
- **Multi-tenant architecture** — thiết kế cho enterprise từ đầu
- **Giá cạnh tranh** — AI Luật 8.000đ/câu, mình có thể thấp hơn với volume
- **Modern tech stack** — Claude (tốt hơn cho tiếng Việt), Supabase, pgvector

### Weaknesses (Điểm yếu)
- **Chưa có data** — AI Luật có 20+ năm xây dựng dữ liệu
- **Chưa có brand** — không ai biết
- **Chưa có legal expert** — cần luật sư validate chất lượng
- **1-person team** — bandwidth hạn chế

### Opportunities (Cơ hội)
- **Cloud API gap** — không ai cung cấp legal AI dạng API tại VN
- **Contract review** — nhu cầu lớn, chưa có solution
- **Luật AI mới** — VN vừa thông qua Luật Trí tuệ Nhân tạo (12/2025), tạo framework pháp lý
- **SME market** — DN nhỏ không đủ tiền thuê luật sư, cần AI assistant giá rẻ
- **HRVN = built-in customer** — beta test ngay với doanh nghiệp thật

### Threats (Rủi ro)
- **AI Luật mở rộng** — họ có thể thêm API bất cứ lúc nào
- **LegalTech quốc tế vào VN** — Harvey, LegalOn có thể localize
- **Hallucination risk** — sai luật = hậu quả nghiêm trọng
- **Pháp lý** — cần kiểm tra quy định về tư vấn pháp luật tự động

---

## 3. Nguồn dữ liệu pháp luật VN

### 🏆 HuggingFace Datasets (SẴN CÓ, FREE!)

#### Dataset 1: UTS_VLC (Vietnamese Legal Corpus)
- **URL:** https://huggingface.co/datasets/undertheseanlp/UTS_VLC
- **Tác giả:** Underthesea NLP
- **License:** MIT
- **Nội dung:** 636 văn bản pháp luật VN (Hiến pháp, Bộ luật, Luật)
- **Splits:** 2021 (110), 2023 (208), 2026 (318 docs)
- **Format:** Markdown, structured với số hiệu, ngày hiệu lực
- **Bao gồm:**
  - Bộ luật Lao động 2019 ✅
  - Bộ luật Dân sự 2015 ✅
  - Bộ luật Hình sự 2015 ✅
  - Luật Doanh nghiệp ✅
  - 300+ luật khác ✅
- **Kích thước:** Mỗi doc 2.5K - 559K chars
- **⭐ DÙNG ĐƯỢC NGAY** — đã structured, có metadata, MIT license

#### Dataset 2: VLSP2025-LegalSML/legal-pretrain
- **URL:** https://huggingface.co/datasets/VLSP2025-LegalSML/legal-pretrain
- **Nội dung:** Vietnamese legal documents (HTML format)
- **Metadata:** DocIdentity, DocName, IssueDate, OrganName
- **Yêu cầu:** Agree to terms trước khi truy cập
- **Dùng cho:** Pretrain/fine-tune legal language models

#### Dataset 3: vietnamese-legal-qa
- **URL:** https://huggingface.co/datasets/nqdhocai/vietnamese-legal-qa
- **Nội dung:** Vietnamese Law Multiple-Choice Questions
- **Dùng cho:** Evaluation, benchmark

### Nguồn crawl bổ sung:
| Nguồn | URL | Ghi chú |
|---|---|---|
| Thư viện Pháp luật | thuvienphapluat.vn | JS-heavy, cần Playwright/Selenium |
| LuatVietnam | luatvietnam.vn | Paywall cho full text |
| Cổng PLQG | vanban.chinhphu.vn | Government source, JS-rendered |
| Công báo | congbao.chinhphu.vn | PDF downloads |
| VBPL | vbpl.vn | Bộ Tư pháp |

**⚠️ Vấn đề crawling:** Hầu hết sites pháp luật VN dùng JavaScript rendering nặng → `webcrawl.py` (requests-based) không lấy được full text. Cần:
- Playwright/Selenium cho thuvienphapluat.vn
- Hoặc **dùng HuggingFace datasets** (đã có sẵn, sạch, structured) ← RECOMMENDED

### Chiến lược data:
1. **Phase 1:** Dùng UTS_VLC dataset (636 docs, sẵn có) → chunk → embed
2. **Phase 2:** Crawl nghị định/thông tư hướng dẫn (Playwright)
3. **Phase 3:** Crawl hỏi đáp pháp luật (thuvienphapluat Q&A section)
4. **Phase 4:** Partner với luật sư để validate + bổ sung case studies

---

## 4. Khác biệt hóa (Differentiation Strategy)

### Tại sao không chỉ clone AI Luật?

AI Luật = **Web chatbot cho cá nhân**
Chúng ta = **Cloud API platform cho doanh nghiệp**

| Feature | AI Luật | Chúng ta |
|---|---|---|
| Q&A pháp luật | ✅ | ✅ |
| Cloud API | ❌ | ✅ |
| Contract Review | ❌ | ✅ |
| Multi-tenant | ❌ | ✅ |
| Custom training | ❌ | ✅ (company docs) |
| Compliance audit | ❌ | ✅ |
| Realtime chat (WS) | ❌ | ✅ |
| Embeddable widget | ❌ | ✅ |
| Developer SDK | ❌ | ✅ |
| Usage analytics | ❌ | ✅ |

### Positioning:
> **"AI Luật cho chatbot cá nhân. Chúng tôi cho doanh nghiệp tích hợp."**

### Target customers:
1. **HR companies** (như HRVN) — tư vấn luật lao động
2. **Công ty luật** — hỗ trợ luật sư review hợp đồng nhanh hơn
3. **Startups / SMEs** — không đủ budget thuê legal team
4. **Kế toán / Tax firms** — tra cứu luật thuế
5. **Bất động sản** — review hợp đồng mua bán, thuê

---

## 5. Rủi ro pháp lý

### Vấn đề cần xác minh:
1. **Tư vấn pháp luật có cần giấy phép?** → Kiểm tra Luật Luật sư, Luật Trợ giúp pháp lý
2. **AI tư vấn pháp lý có hợp pháp?** → Luật AI mới (12/2025) cho phép nhưng cần tuân thủ
3. **Disclaimer bắt buộc?** → Cần ghi rõ "tham khảo, không thay thế luật sư"
4. **Data privacy (CCCD, hợp đồng)?** → Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân
5. **Crawl data pháp luật có hợp pháp?** → Văn bản pháp luật là public domain, nhưng database compilation có thể có bản quyền

### Giải pháp:
- ✅ Luôn disclaimer
- ✅ Không tư vấn hình sự
- ✅ Dùng dataset MIT license (UTS_VLC)
- ✅ Encrypt company data
- ✅ Comply Nghị định 13 về data privacy

---

## 6. Revenue Projection

### Scenario: First Year

| Tháng | Khách hàng | MRR (VND) | Notes |
|---|---|---|---|
| 1-3 | 0 (beta) | 0 | HRVN beta test |
| 4 | 3 | 9.000.000 | First paying customers |
| 5 | 5 | 15.000.000 | |
| 6 | 10 | 35.000.000 | Mix starter + pro |
| 7-8 | 15 | 52.000.000 | |
| 9-10 | 25 | 87.000.000 | |
| 11-12 | 40 | 140.000.000 | |

### Year 1 total: ~500 triệu - 1 tỷ VND
### Cost: ~100-200 triệu (infra + API)
### Profit: 300-800 triệu

### Break-even: Tháng 4-5 (chỉ cần 3-4 khách hàng starter)

---

## 7. MVP Priority

### Phải có (Must):
1. Legal Q&A with RAG + citations
2. API key auth + rate limiting
3. Bộ luật Lao động + Doanh nghiệp data
4. Basic dashboard

### Nên có (Should):
5. Contract review (PDF upload)
6. Usage tracking + billing
7. Embeddable chat widget

### Có thể sau (Could):
8. Compliance audit
9. Document drafter
10. Mobile SDK
11. Fine-tuned legal model

---

## 8. Kết luận

### Khả thi? ✅ CÓ
- Data sẵn có (HuggingFace MIT license)
- Tech stack rõ ràng (FastAPI + Supabase + Claude)
- Market gap rõ (API platform, contract review)
- Chi phí thấp (~$130/tháng)
- Break-even nhanh (3-4 khách)

### Rủi ro lớn nhất?
1. **Chất lượng AI** — sai luật = mất khách, mất uy tín
2. **AI Luật mở API** — họ có data advantage 20 năm
3. **Acquisition cost** — tìm khách hàng enterprise cần sales

### Recommendation:
**GO** — build MVP trong 8-10 tuần, beta test với HRVN, target HR/labor law companies trước (mảng mình hiểu rõ nhất).
