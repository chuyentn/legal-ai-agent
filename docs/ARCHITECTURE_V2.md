# Legal AI Platform v2 — Full Legal Department Replacement

> **Tầm nhìn:** Thay thế hoàn toàn bộ phận pháp lý truyền thống trong doanh nghiệp.
> Không chỉ chatbot — mà là một **Legal Operating System**.

---

## 1. Product Vision

```
TRƯỚC (Truyền thống):                    SAU (Legal AI Platform):
                                         
Thuê luật sư ─── 15-50tr/tháng          ┌─────────────────────────┐
Thuê legal staff ── 10-20tr/tháng        │   LEGAL AI PLATFORM     │
                                         │                         │
Soạn HĐ ──── 2-3 ngày                   │   Soạn HĐ ── 5 phút    │
Review HĐ ── 1-2 ngày                   │   Review ─── 30 giây    │
Tra cứu luật ── vài giờ                 │   Tra cứu ── tức thì    │
Soạn nội quy ── 1 tuần                  │   Nội quy ── 10 phút    │
Tư vấn ───── đặt lịch, chờ             │   Tư vấn ─── 24/7       │
                                         │                         │
Chi phí: 30-70tr/tháng                   │   Chi phí: 3-8tr/tháng  │
                                         └─────────────────────────┘
```

---

## 2. Platform Modules

```
┌─────────────────────────────────────────────────────────────┐
│                    LEGAL AI PLATFORM                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  📄 DRAFT    │  │  🔍 REVIEW   │  │  💬 CONSULT      │   │
│  │  Soạn thảo   │  │  Rà soát     │  │  Tư vấn          │   │
│  │  văn bản     │  │  hợp đồng    │  │  pháp lý         │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  📚 LIBRARY  │  │  ✅ COMPLY   │  │  📊 MANAGE       │   │
│  │  Thư viện    │  │  Tuân thủ    │  │  Quản lý         │   │
│  │  mẫu & luật  │  │  pháp luật   │  │  văn bản DN      │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  🔄 BATCH    │  │  🔌 API      │                         │
│  │  Xử lý      │  │  Tích hợp    │                         │
│  │  hàng loạt   │  │  hệ thống    │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Module 1: DRAFT (Soạn thảo)
**Thay thế:** Luật sư soạn hợp đồng, admin soạn văn bản
```
Input:  Loại văn bản + thông tin cần thiết
Output: Văn bản hoàn chỉnh (Word/PDF), đúng pháp luật

Hỗ trợ:
├── Hợp đồng (lao động, dịch vụ, mua bán, thuê, hợp tác, đại lý)
├── Phụ lục (gia hạn, sửa đổi, bổ sung, thanh lý)
├── Văn bản nội bộ (nội quy, quy chế, quyết định, thông báo, biên bản)
├── Văn bản đối ngoại (công văn, giấy ủy quyền, đơn khiếu nại)
├── HR documents (HĐLĐ, quyết định lương, kỷ luật, sa thải, BHXH)
└── Báo cáo pháp lý (tuân thủ, rà soát, đánh giá rủi ro)
```

### Module 2: REVIEW (Rà soát)
**Thay thế:** Luật sư review hợp đồng
```
Input:  File hợp đồng (PDF/Word/ảnh)
Output: Báo cáo rủi ro + đề xuất sửa đổi

Chức năng:
├── Phát hiện điều khoản vi phạm pháp luật
├── Highlight điều khoản bất lợi
├── Kiểm tra thiếu sót (điều khoản bắt buộc)
├── So sánh với template chuẩn
├── Đề xuất sửa đổi cụ thể
├── Chấm điểm rủi ro (0-100)
└── Tạo redline version (markup thay đổi)
```

### Module 3: CONSULT (Tư vấn)
**Thay thế:** Luật sư tư vấn, hotline pháp lý
```
Input:  Câu hỏi pháp lý (text/voice)
Output: Câu trả lời + trích dẫn điều luật cụ thể

Chức năng:
├── Q&A pháp luật 37+ lĩnh vực
├── Trích dẫn điều luật chính xác
├── Phân tích tình huống cụ thể
├── Gợi ý hành động tiếp theo
├── Lịch sử tư vấn (audit trail)
└── Multi-language (VN/EN/CN/KR/JP)
```

### Module 4: LIBRARY (Thư viện)
**Thay thế:** Tủ sách pháp luật, dịch vụ tra cứu
```
├── 600+ văn bản pháp luật VN (Luật, NĐ, TT)
├── Template library (50+ mẫu văn bản)
├── Smart search (semantic + keyword)
├── Cross-reference (luật liên quan)
├── Version tracking (luật sửa đổi)
├── Bookmark & highlight
└── Auto-update khi luật mới ban hành
```

### Module 5: COMPLY (Tuân thủ)
**Thay thế:** Kiểm toán pháp lý
```
Input:  Thông tin doanh nghiệp (ngành, quy mô, hoạt động)
Output: Checklist tuân thủ + cảnh báo vi phạm

Chức năng:
├── Compliance checklist theo ngành
├── Deadline nhắc nhở (báo cáo thuế, BHXH, PCCC)
├── Scanning nội quy vs luật hiện hành
├── Alert khi luật mới ảnh hưởng DN
└── Báo cáo tuân thủ định kỳ
```

### Module 6: MANAGE (Quản lý)
**Thay thế:** Tủ hồ sơ, Excel tracking
```
├── Kho văn bản DN (upload, phân loại, search)
├── Tracking hợp đồng (hết hạn, gia hạn)
├── Quản lý phiên bản (ai sửa, khi nào)
├── Workflow phê duyệt (draft → review → approve)
├── Nhắc nhở deadline (hợp đồng sắp hết, giấy phép hết hạn)
└── Báo cáo tổng hợp (bao nhiêu HĐ, trạng thái)
```

### Module 7: BATCH (Xử lý hàng loạt)
**Thay thế:** Admin/HR soạn hàng trăm HĐLĐ
```
Input:  Template + Excel data (tên, lương, vị trí...)
Output: Hàng loạt văn bản hoàn chỉnh

Use cases:
├── 500 HĐLĐ cho công nhân mới (HRVN!)
├── 200 phụ lục gia hạn
├── 100 quyết định tăng lương
├── 50 thông báo nghỉ việc
└── Batch export Word/PDF
```

### Module 8: API (Tích hợp)
```
REST API + WebSocket + SDK
├── Tích hợp vào ERP/HRM hiện có
├── Webhook events (HĐ hết hạn, luật mới)
├── Embeddable chat widget
├── Mobile SDK (iOS/Android)
└── Zapier / n8n integration
```

---

## 3. System Architecture v2

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │   Web    │ │  Chat    │ │  Mobile  │ │  API     │           │
│  │Dashboard │ │ Widget   │ │  App     │ │ Direct   │           │
│  │(Next.js) │ │(Embed)   │ │(Future)  │ │(REST)    │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
└───────┼─────────────┼────────────┼─────────────┼────────────────┘
        │             │            │             │
        └─────────────┴──────┬─────┴─────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                                 │
│                                                                 │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌────────────────┐   │
│  │   Auth    │ │   Rate    │ │  Billing  │ │   Request      │   │
│  │ (Supabase │ │  Limiter  │ │  Meter    │ │   Router       │   │
│  │  + API    │ │  (Redis)  │ │           │ │                │   │
│  │  Keys)    │ │           │ │           │ │                │   │
│  └───────────┘ └───────────┘ └───────────┘ └────────────────┘   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR LAYER                             │
│                   (FastAPI + LangGraph)                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │              INTENT ROUTER                               │     │
│  │  "Soạn hợp đồng lao động" → DRAFT agent                │     │
│  │  "Review file này" → REVIEW agent                       │     │
│  │  "Thai sản bao lâu?" → CONSULT agent                   │     │
│  │  "Tạo 500 HĐLĐ từ Excel" → BATCH agent                 │     │
│  │  "Công ty tôi cần tuân thủ gì?" → COMPLY agent         │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌────────────────── AGENT POOL ──────────────────────────┐     │
│  │                                                        │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │     │
│  │  │  DRAFT   │ │  REVIEW  │ │ CONSULT  │ │  COMPLY  │  │     │
│  │  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │  │     │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │     │
│  │                                                        │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐               │     │
│  │  │  BATCH   │ │ LIBRARY  │ │  MANAGE  │               │     │
│  │  │  Agent   │ │  Agent   │ │  Agent   │               │     │
│  │  └──────────┘ └──────────┘ └──────────┘               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌────────────────── SHARED SERVICES ────────────────────┐     │
│  │                                                        │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │     │
│  │  │Citation  │ │Halluc.   │ │ Template │ │ Document │  │     │
│  │  │Verifier  │ │Guard     │ │ Engine   │ │ Builder  │  │     │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │     │
│  │                                                        │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐               │     │
│  │  │ Context  │ │ Compliance│ │ Export   │               │     │
│  │  │ Manager  │ │ Checker  │ │ Service  │               │     │
│  │  └──────────┘ └──────────┘ └──────────┘               │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────────────────────┬────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   RAG ENGINE     │  │   LLM LAYER      │  │   TOOL LAYER     │
│                  │  │                  │  │                  │
│ Hybrid Search    │  │ Claude Sonnet    │  │ OCR (Surya)      │
│ (pgvector +      │  │ (primary)        │  │ PDF Parser       │
│  full-text)      │  │                  │  │ DOCX Generator   │
│                  │  │ Claude Haiku     │  │ PDF Generator    │
│ Reranker         │  │ (fast tasks)     │  │ Excel Reader     │
│                  │  │                  │  │ Template Render  │
│ Context Builder  │  │ Gemini Flash     │  │ E-Sign (future)  │
│                  │  │ (batch/cheap)    │  │ Web Search       │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SUPABASE LAYER                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL                              │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │   │
│  │  │  Tenants    │  │  Law DB      │  │  pgvector        │  │   │
│  │  │  (companies │  │  (636+ docs) │  │  (embeddings)    │  │   │
│  │  │  users,     │  │              │  │                  │  │   │
│  │  │  docs, HĐ)  │  │  Luật, NĐ,  │  │  law_chunks      │  │   │
│  │  │             │  │  TT, QĐ     │  │  company_chunks  │  │   │
│  │  │  RLS        │  │              │  │  template_chunks │  │   │
│  │  │  isolated   │  │  PUBLIC READ │  │                  │  │   │
│  │  └─────────────┘  └──────────────┘  └──────────────────┘  │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│  │  Auth    │  │ Storage  │  │ Realtime │  │  Edge        │     │
│  │ (Users + │  │ (Docs,   │  │ (Chat,   │  │  Functions   │     │
│  │ API Keys)│  │ exports) │  │ notify)  │  │  (webhooks)  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Document Generation Engine (Core Innovation)

```
┌─────────────────────────────────────────────────────────────────┐
│               DOCUMENT GENERATION ENGINE                         │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                 TEMPLATE SYSTEM                            │   │
│  │                                                           │   │
│  │  Templates are NOT static Word files.                     │   │
│  │  They are INTELLIGENT SCHEMAS:                            │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────┐          │   │
│  │  │  Template: "hop_dong_lao_dong"               │          │   │
│  │  │                                             │          │   │
│  │  │  Sections:                                  │          │   │
│  │  │  ├── header (company info, date, number)    │          │   │
│  │  │  ├── parties (employer + employee info)     │          │   │
│  │  │  ├── position (job title, department)       │          │   │
│  │  │  ├── term (duration, start date)            │          │   │
│  │  │  ├── salary (base, allowance, bonus)        │          │   │
│  │  │  ├── working_hours (schedule, overtime)     │          │   │
│  │  │  ├── insurance (BHXH, BHYT, BHTN)           │          │   │
│  │  │  ├── leave (annual, sick, maternity)        │          │   │
│  │  │  ├── obligations (employer + employee)      │          │   │
│  │  │  ├── termination (conditions, notice)       │          │   │
│  │  │  ├── dispute (resolution method)            │          │   │
│  │  │  └── signatures                             │          │   │
│  │  │                                             │          │   │
│  │  │  Required by law: [term, salary, insurance] │          │   │
│  │  │  Legal refs: [Điều 21-24 BLLĐ 2019]        │          │   │
│  │  │  Compliance rules: [max 36 months, ...]     │          │   │
│  │  └─────────────────────────────────────────────┘          │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                 GENERATION PIPELINE                        │   │
│  │                                                           │   │
│  │  ① Collect Variables                                      │   │
│  │  ┌─────────────────────────────────┐                      │   │
│  │  │ Interactive Q&A or API params:  │                      │   │
│  │  │ - company_name: "HRVN"          │                      │   │
│  │  │ - employee_name: "Nguyễn Văn A" │                      │   │
│  │  │ - position: "Công nhân sản xuất"│                      │   │
│  │  │ - salary: 6500000               │                      │   │
│  │  │ - term_months: 12               │                      │   │
│  │  └─────────────────────────────────┘                      │   │
│  │                    │                                      │   │
│  │                    ▼                                      │   │
│  │  ② Validate & Enrich                                     │   │
│  │  ┌─────────────────────────────────┐                      │   │
│  │  │ - Salary >= minimum wage? ✅     │                      │   │
│  │  │ - Term <= 36 months? ✅          │                      │   │
│  │  │ - Required fields present? ✅    │                      │   │
│  │  │ - Auto-calculate BHXH rates     │                      │   │
│  │  │ - Auto-add required clauses     │                      │   │
│  │  └─────────────────────────────────┘                      │   │
│  │                    │                                      │   │
│  │                    ▼                                      │   │
│  │  ③ Generate with LLM                                     │   │
│  │  ┌─────────────────────────────────┐                      │   │
│  │  │ Template schema + variables     │                      │   │
│  │  │ + relevant law articles         │                      │   │
│  │  │ + company custom rules          │                      │   │
│  │  │         │                       │                      │   │
│  │  │         ▼                       │                      │   │
│  │  │    Claude Sonnet                │                      │   │
│  │  │         │                       │                      │   │
│  │  │         ▼                       │                      │   │
│  │  │  Complete document (markdown)   │                      │   │
│  │  └─────────────────────────────────┘                      │   │
│  │                    │                                      │   │
│  │                    ▼                                      │   │
│  │  ④ Compliance Check                                      │   │
│  │  ┌─────────────────────────────────┐                      │   │
│  │  │ Verify generated doc against:   │                      │   │
│  │  │ - Relevant law articles         │                      │   │
│  │  │ - Template required sections    │                      │   │
│  │  │ - Company-specific rules        │                      │   │
│  │  │ - Common legal pitfalls         │                      │   │
│  │  └─────────────────────────────────┘                      │   │
│  │                    │                                      │   │
│  │                    ▼                                      │   │
│  │  ⑤ Export                                                │   │
│  │  ┌─────────────────────────────────┐                      │   │
│  │  │ Markdown → DOCX (python-docx)  │                      │   │
│  │  │ Markdown → PDF (weasyprint)    │                      │   │
│  │  │ With: company logo, formatting │                      │   │
│  │  │       page numbers, headers    │                      │   │
│  │  │       signature blocks         │                      │   │
│  │  └─────────────────────────────────┘                      │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Batch Processing Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                  BATCH PROCESSING ENGINE                         │
│          "Tạo 500 HĐLĐ trong 10 phút"                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Input: Excel/CSV + Template                              │   │
│  │                                                           │   │
│  │  Excel columns mapping:                                   │   │
│  │  ┌──────────────────────────────────────────────────┐     │   │
│  │  │ Họ tên    │ Ngày sinh │ CCCD        │ Vị trí    │     │   │
│  │  │ Nguyễn A  │ 01/01/90  │ 079190xxx  │ CN sản xuất│     │   │
│  │  │ Trần B    │ 15/03/95  │ 052195xxx  │ QC         │     │   │
│  │  │ ...       │ ...       │ ...        │ ...        │     │   │
│  │  │ (500 rows)│           │            │            │     │   │
│  │  └──────────────────────────────────────────────────┘     │   │
│  └───────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Processing Pipeline:                                     │   │
│  │                                                           │   │
│  │  Row 1 ──→ Validate ──→ Generate ──→ Check ──→ DOCX  ─┐  │   │
│  │  Row 2 ──→ Validate ──→ Generate ──→ Check ──→ DOCX  ─┤  │   │
│  │  Row 3 ──→ Validate ──→ Generate ──→ Check ──→ DOCX  ─┤  │   │
│  │  ...                                                  ─┤  │   │
│  │  Row N ──→ Validate ──→ Generate ──→ Check ──→ DOCX  ─┤  │   │
│  │                                                        │  │   │
│  │  Parallel processing: 10-20 concurrent (Celery workers) │  │   │
│  │  LLM: Use Gemini Flash for batch (cheaper, fast enough) │  │   │
│  └──────────────────────────────────────────────────────┬──┘   │
│                                                        │       │
│                                                        ▼       │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Output:                                                  │   │
│  │  ├── /batch_001/HDLD_NguyenVanA.docx                     │   │
│  │  ├── /batch_001/HDLD_TranVanB.docx                       │   │
│  │  ├── /batch_001/...                                       │   │
│  │  ├── /batch_001/SUMMARY.xlsx (tracking sheet)             │   │
│  │  └── /batch_001/ALL.zip (download all)                    │   │
│  │                                                           │   │
│  │  Summary: 500 created, 498 OK, 2 warnings                │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Template Library Architecture

```
Template Categories:
│
├── 📁 Hợp đồng (Contracts)
│   ├── hop_dong_lao_dong (HĐLĐ xác định/không xác định thời hạn)
│   ├── hop_dong_thu_viec (HĐ thử việc)
│   ├── hop_dong_dich_vu (HĐ dịch vụ)
│   ├── hop_dong_mua_ban (HĐ mua bán hàng hóa)
│   ├── hop_dong_thue (HĐ thuê mặt bằng/thiết bị)
│   ├── hop_dong_hop_tac (HĐ hợp tác kinh doanh)
│   ├── hop_dong_dai_ly (HĐ đại lý/phân phối)
│   ├── hop_dong_vay (HĐ vay vốn)
│   ├── hop_dong_gia_cong (HĐ gia công)
│   └── hop_dong_nhuong_quyen (HĐ nhượng quyền)
│
├── 📁 Phụ lục (Appendices)
│   ├── phu_luc_gia_han (Gia hạn HĐ)
│   ├── phu_luc_sua_doi (Sửa đổi điều khoản)
│   ├── phu_luc_bo_sung (Bổ sung điều khoản)
│   ├── phu_luc_thanh_ly (Thanh lý HĐ)
│   └── phu_luc_cham_dut (Chấm dứt HĐ)
│
├── 📁 Quyết định (Decisions)
│   ├── quyet_dinh_tuyen_dung (Tuyển dụng)
│   ├── quyet_dinh_bo_nhiem (Bổ nhiệm)
│   ├── quyet_dinh_tang_luong (Tăng lương)
│   ├── quyet_dinh_ky_luat (Kỷ luật)
│   ├── quyet_dinh_sa_thai (Sa thải)
│   ├── quyet_dinh_nghi_viec (Cho nghỉ việc)
│   ├── quyet_dinh_thuyen_chuyen (Thuyên chuyển)
│   └── quyet_dinh_cu_di_cong_tac (Cử đi công tác)
│
├── 📁 Nội quy & Quy chế (Policies)
│   ├── noi_quy_lao_dong (Nội quy lao động)
│   ├── quy_che_luong (Quy chế lương thưởng)
│   ├── quy_che_tai_chinh (Quy chế tài chính)
│   ├── quy_trinh_tuyen_dung (Quy trình tuyển dụng)
│   ├── quy_trinh_dao_tao (Quy trình đào tạo)
│   └── thoa_uoc_lao_dong (Thỏa ước LĐTT)
│
├── 📁 Công văn & Đơn từ (Correspondence)
│   ├── cong_van (Công văn)
│   ├── giay_uy_quyen (Giấy ủy quyền)
│   ├── don_xin_nghi (Đơn xin nghỉ phép)
│   ├── don_khieu_nai (Đơn khiếu nại)
│   ├── thu_moi (Thư mời)
│   └── thong_bao (Thông báo)
│
├── 📁 Biên bản (Minutes)
│   ├── bien_ban_hop (Biên bản họp)
│   ├── bien_ban_giao_nhan (Biên bản giao nhận)
│   ├── bien_ban_vi_pham (Biên bản vi phạm)
│   ├── bien_ban_kiem_tra (Biên bản kiểm tra)
│   └── nghi_quyet (Nghị quyết)
│
└── 📁 Báo cáo (Reports)
    ├── bao_cao_bhxh (Báo cáo BHXH)
    ├── bao_cao_thue_tncn (Báo cáo thuế TNCN)
    ├── bao_cao_lao_dong (Báo cáo lao động)
    └── bao_cao_pccc (Báo cáo PCCC)

Template Schema (JSON):
{
  "id": "hop_dong_lao_dong",
  "name": "Hợp đồng Lao động",
  "category": "contracts",
  "version": "2.0",
  "legal_basis": ["Điều 13-24, BLLĐ 2019", "NĐ 145/2020/NĐ-CP"],
  "variables": [
    {"key": "company_name", "label": "Tên công ty", "type": "text", "required": true},
    {"key": "company_address", "label": "Địa chỉ", "type": "text", "required": true},
    {"key": "company_tax_code", "label": "Mã số thuế", "type": "text", "required": true},
    {"key": "representative", "label": "Người đại diện", "type": "text", "required": true},
    {"key": "representative_title", "label": "Chức vụ", "type": "text", "required": true},
    {"key": "employee_name", "label": "Họ tên NLĐ", "type": "text", "required": true},
    {"key": "employee_dob", "label": "Ngày sinh", "type": "date", "required": true},
    {"key": "employee_cccd", "label": "Số CCCD", "type": "text", "required": true},
    {"key": "employee_address", "label": "Địa chỉ NLĐ", "type": "text", "required": true},
    {"key": "position", "label": "Vị trí", "type": "text", "required": true},
    {"key": "department", "label": "Bộ phận", "type": "text"},
    {"key": "work_location", "label": "Địa điểm làm việc", "type": "text", "required": true},
    {"key": "contract_type", "label": "Loại HĐ", "type": "enum", "options": ["definite", "indefinite", "seasonal"], "required": true},
    {"key": "term_months", "label": "Thời hạn (tháng)", "type": "number", "max": 36, "condition": "contract_type == 'definite'"},
    {"key": "start_date", "label": "Ngày bắt đầu", "type": "date", "required": true},
    {"key": "base_salary", "label": "Lương cơ bản", "type": "currency", "required": true, "min": "minimum_wage"},
    {"key": "allowances", "label": "Phụ cấp", "type": "json"},
    {"key": "working_hours", "label": "Giờ làm/tuần", "type": "number", "max": 48, "default": 48},
    {"key": "probation_days", "label": "Thử việc (ngày)", "type": "number", "max": 180}
  ],
  "sections": [...],
  "compliance_rules": [
    {"rule": "term_months <= 36", "message": "HĐLĐ xác định thời hạn tối đa 36 tháng (Điều 22)"},
    {"rule": "base_salary >= minimum_wage", "message": "Lương không được thấp hơn mức tối thiểu vùng"},
    {"rule": "working_hours <= 48", "message": "Không quá 48 giờ/tuần (Điều 105)"},
    {"rule": "probation_days <= 180", "message": "Thử việc tối đa 180 ngày cho vị trí quản lý (Điều 25)"}
  ]
}
```

---

## 7. Compliance Engine

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLIANCE ENGINE                             │
│         "Công ty bạn đang tuân thủ pháp luật chưa?"             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Company Profile:                                         │   │
│  │  - Ngành: Sản xuất                                        │   │
│  │  - Quy mô: 500 NLĐ                                       │   │
│  │  - Địa bàn: Bình Dương                                    │   │
│  │  - Hoạt động: Gia công điện tử                            │   │
│  └──────────────────────┬────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Auto-Generate Compliance Checklist:                      │   │
│  │                                                           │   │
│  │  📋 Lao động                                             │   │
│  │  ├── ✅ HĐLĐ cho tất cả NLĐ                              │   │
│  │  ├── ✅ Nội quy lao động đăng ký Sở LĐTBXH               │   │
│  │  ├── ⚠️ Thỏa ước LĐTT (>10 NLĐ → bắt buộc)             │   │
│  │  ├── ✅ Báo cáo lao động 6 tháng/năm                     │   │
│  │  └── ❌ Quy chế dân chủ cơ sở                            │   │
│  │                                                           │   │
│  │  📋 BHXH/BHYT/BHTN                                       │   │
│  │  ├── ✅ Đóng BHXH cho NLĐ có HĐLĐ ≥ 1 tháng             │   │
│  │  ├── ⚠️ Khai báo tăng/giảm LĐ đúng hạn                  │   │
│  │  └── ✅ Báo cáo BHXH định kỳ                             │   │
│  │                                                           │   │
│  │  📋 An toàn lao động                                     │   │
│  │  ├── ✅ Huấn luyện ATVSLĐ                                │   │
│  │  ├── ❌ Khám sức khỏe định kỳ (Điều 21 Luật ATVSLĐ)      │   │
│  │  ├── ⚠️ Khai báo tai nạn LĐ                              │   │
│  │  └── ✅ Đánh giá nguy cơ rủi ro                           │   │
│  │                                                           │   │
│  │  📋 PCCC                                                 │   │
│  │  ├── ✅ Giấy chứng nhận PCCC                              │   │
│  │  ├── ⚠️ Kiểm tra hệ thống PCCC định kỳ                   │   │
│  │  └── ✅ Tập huấn PCCC hàng năm                            │   │
│  │                                                           │   │
│  │  📋 Thuế                                                 │   │
│  │  ├── ✅ Khai thuế GTGT hàng tháng/quý                    │   │
│  │  ├── ✅ Quyết toán thuế TNDN                             │   │
│  │  └── ✅ Quyết toán thuế TNCN cho NLĐ                     │   │
│  │                                                           │   │
│  │  📋 Môi trường                                           │   │
│  │  ├── ⚠️ Giấy phép xả thải (sản xuất)                    │   │
│  │  ├── ✅ Đánh giá tác động môi trường                      │   │
│  │  └── ❌ Báo cáo BVMT định kỳ                             │   │
│  │                                                           │   │
│  │  Score: 72/100 | Issues: 3 critical, 5 warnings           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Deadline Calendar:                                       │   │
│  │                                                           │   │
│  │  📅 15/03 — Nộp báo cáo BHXH tháng 2                     │   │
│  │  📅 20/03 — Khai thuế GTGT tháng 2                       │   │
│  │  📅 30/03 — Quyết toán thuế TNDN 2025                    │   │
│  │  📅 15/04 — Báo cáo lao động Q1                          │   │
│  │  📅 30/06 — Khám sức khỏe định kỳ                        │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Contract Lifecycle Management

```
┌─────────────────────────────────────────────────────────────────┐
│              CONTRACT LIFECYCLE                                  │
│                                                                 │
│  ┌─────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌──────┐  │
│  │Draft│───▶│Review  │───▶│Approve │───▶│Active  │───▶│Expire│  │
│  │     │    │        │    │        │    │        │    │      │  │
│  └─────┘    └────────┘    └────────┘    └───┬────┘    └──────┘  │
│    AI          AI           Human          │                    │
│  generates   checks       approves         │                    │
│                                            │                    │
│                              ┌─────────────┤                    │
│                              │             │                    │
│                              ▼             ▼                    │
│                         ┌────────┐    ┌────────┐               │
│                         │Amend   │    │Renew   │               │
│                         │(Phụ lục)│    │(Gia hạn)│               │
│                         └────────┘    └────────┘               │
│                                                                 │
│  Tracking Dashboard:                                            │
│  ├── 245 Active contracts                                       │
│  ├── 12 Expiring in 30 days ⚠️                                  │
│  ├── 3 Pending review                                           │
│  ├── 1 Compliance issue 🔴                                      │
│  └── Last created: 2 hours ago                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Pricing Model (Updated)

### Pricing Philosophy: 
> **Rẻ hơn 90% so với thuê luật sư, nhưng đắt hơn chatbot thuần túy**
> Vì chúng ta **TẠO ra giá trị** (văn bản), không chỉ trả lời câu hỏi

| Plan | Giá/tháng | Bao gồm | Target |
|---|---|---|---|
| **Starter** | 2.000.000đ | 20 docs + 100 Q&A + 5 reviews | SME < 20 NLĐ |
| **Business** | 5.000.000đ | 100 docs + 500 Q&A + 20 reviews + compliance | SME 20-100 NLĐ |
| **Enterprise** | 15.000.000đ | Unlimited docs + Q&A + batch + API + SLA | DN 100+ NLĐ |
| **Custom** | Thỏa thuận | White-label, dedicated, training | Tập đoàn |

### Add-ons:
- Batch processing (500+ docs): 500.000đ/batch
- Custom template: 2.000.000đ/template
- Compliance audit: 3.000.000đ/lần
- API integration support: 5.000.000đ setup

### So sánh chi phí thực tế:
| Hạng mục | Truyền thống | Legal AI Platform |
|---|---|---|
| Soạn 1 HĐLĐ | 500K-2tr (luật sư) | ~10K (AI) |
| Review 1 HĐ | 2-5tr | ~50K |
| Nội quy LĐ | 5-15tr | ~200K |
| Thuê legal staff | 15-25tr/tháng | 5tr/tháng (Business plan) |
| Tư vấn 1 câu | 200-500K | ~10K |
| 500 HĐLĐ batch | 250tr+ (luật sư) | 500K |

---

## 10. Development Roadmap (Updated)

### Phase 1: Foundation (Week 1-4)
```
├── Supabase setup + full schema migration
├── FastAPI scaffold + auth + rate limiting
├── Law data pipeline (HuggingFace UTS_VLC → pgvector)
├── RAG engine (hybrid search + reranker)
├── Legal Q&A agent (CONSULT module)
└── Basic API endpoints
```

### Phase 2: Document Engine (Week 5-8)
```
├── Template schema system
├── Document generation pipeline
├── 10 core templates (HĐLĐ, QĐ, Nội quy...)
├── DOCX/PDF export (python-docx, weasyprint)
├── Contract review agent (REVIEW module)
├── DRAFT module API endpoints
└── HRVN beta test
```

### Phase 3: Batch + Management (Week 9-12)
```
├── Batch processing engine (Celery workers)
├── Excel import → batch document generation
├── Document management (upload, search, track)
├── Contract lifecycle tracking
├── Compliance engine (basic checklist)
├── Usage tracking + billing
└── Web dashboard (Next.js)
```

### Phase 4: Scale + Launch (Week 13-16)
```
├── Embeddable chat widget
├── Webhook events
├── Complete template library (50+ templates)
├── Advanced compliance (deadline calendar)
├── Mobile-responsive dashboard
├── Landing page + pricing page
├── Public launch
└── First paying customers
```
