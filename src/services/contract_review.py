"""
Contract Review AI Service (LLM-based)
Uses Claude to analyze contracts instead of regex pattern matching
"""

import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime
from anthropic import Anthropic

logger = logging.getLogger(__name__)


# System prompt for Claude contract review
REVIEW_SYSTEM_PROMPT = """Bạn là chuyên gia pháp lý Việt Nam với 20 năm kinh nghiệm rà soát hợp đồng.

Phân tích hợp đồng sau và trả về JSON với cấu trúc:

{
  "contract_title": "tên hợp đồng",
  "contract_type": "loại HĐ (lao_dong/thue/mua_ban/dich_vu/...)",
  "parties": ["Bên A", "Bên B"],
  "risk_score": 0-100 (0=an toàn, 100=rất rủi ro),
  "risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
  "summary": "tóm tắt 2-3 câu về hợp đồng và rủi ro chính",
  "clauses": [
    {
      "clause_number": "Điều X",
      "title": "tên điều khoản",
      "content": "trích dẫn nguyên văn phần rủi ro",
      "risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
      "risk_score": 0-100,
      "issue": "vấn đề gì",
      "law_reference": "Điều X Luật Y năm Z quy định...",
      "suggestion": "đề xuất sửa đổi cụ thể",
      "category": "penalty/liability/ip/dispute/termination/..."
    }
  ],
  "missing_clauses": [
    {
      "clause": "tên điều khoản thiếu",
      "importance": "HIGH/MEDIUM/LOW",
      "suggestion": "nên thêm điều khoản... theo Điều X Luật Y"
    }
  ],
  "compliance": {
    "bo_luat_dan_su_2015": {"status": "OK/PARTIAL/VIOLATION", "issues": []},
    "luat_thuong_mai_2005": {"status": "OK/PARTIAL/VIOLATION", "issues": []},
    "luat_lao_dong_2019": {"status": "OK/PARTIAL/VIOLATION/N_A", "issues": []},
    "luat_doanh_nghiep_2020": {"status": "OK/PARTIAL/VIOLATION/N_A", "issues": []}
  },
  "recommendations": [
    {
      "priority": 1,
      "action": "hành động cụ thể",
      "reason": "lý do, trích dẫn luật"
    }
  ]
}

Quy tắc phân tích:
1. Phạt vi phạm HĐ thương mại không được quá 8% giá trị phần nghĩa vụ bị vi phạm (Điều 301 Luật TM 2005)
2. Thời gian thử việc tối đa: 60 ngày (công việc cần CĐ/ĐH), 30 ngày (TC/CN), 6 ngày (khác) — Điều 25 BLLĐ 2019
3. Lương thử việc ≥ 85% lương chính thức — Điều 26 BLLĐ 2019
4. HĐ lao động phải có BHXH, BHYT, BHTN — Điều 168 BLLĐ 2019
5. Thời giờ làm việc ≤ 8h/ngày, 48h/tuần — Điều 105 BLLĐ 2019
6. Lãi suất vay không quá 20%/năm (dân sự) — Điều 468 BLDS 2015
7. Hợp đồng phải có điều khoản giải quyết tranh chấp
8. Nên có điều khoản bất khả kháng (force majeure) — Điều 156 BLDS 2015
9. Điều khoản bảo mật phải có thời hạn cụ thể
10. Quyền SHTT phải quy định rõ ràng

CHỈ trả về JSON, không giải thích thêm."""


class ContractReviewService:
    """
    Contract Review AI - Uses Claude LLM for intelligent contract analysis
    """
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    def review_contract(
        self,
        contract_text: str,
        contract_name: str = "",
        contract_type: Optional[str] = None,
        parties: Optional[list] = None
    ) -> Dict:
        """
        Main review function — uses Claude to analyze contract
        
        Args:
            contract_text: Full contract text
            contract_name: Name of contract
            contract_type: Type of contract (optional)
            parties: List of parties (optional)
        
        Returns:
            Dict with complete review results
        """
        if len(contract_text.strip()) < 50:
            return {
                "success": False,
                "error": "Nội dung hợp đồng quá ngắn để phân tích"
            }
        
        # Truncate if too long (Claude context limit)
        max_chars = 100000  # ~25K tokens
        if len(contract_text) > max_chars:
            contract_text = contract_text[:max_chars] + "\n\n[... nội dung bị cắt do quá dài ...]"
        
        # Build user message
        user_message = f"""Rà soát hợp đồng sau:

Tên: {contract_name or 'Không rõ'}
Loại: {contract_type or 'Tự xác định'}

---NỘI DUNG HỢP ĐỒNG---
{contract_text}
---HẾT NỘI DUNG---

Phân tích đầy đủ 10 danh mục rủi ro và trả về JSON."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=REVIEW_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text.strip()
            
            # Try to parse JSON (Claude might wrap in ```json blocks)
            if response_text.startswith("```"):
                # Remove markdown code block
                lines = response_text.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.startswith("```") and not in_block:
                        in_block = True
                        continue
                    elif line.startswith("```") and in_block:
                        break
                    elif in_block:
                        json_lines.append(line)
                response_text = "\n".join(json_lines)
            
            review_result = json.loads(response_text)
            review_result["success"] = True
            review_result["ai_model"] = self.model
            
            # Add metadata
            review_result["review_id"] = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            review_result["reviewed_at"] = datetime.now().isoformat()
            review_result["total_issues"] = len(review_result.get("clauses", []))
            
            # Ensure contract_title is set
            if not review_result.get("contract_title"):
                review_result["contract_title"] = contract_name or "Hợp đồng"
            
            return review_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            # Return the raw text as fallback
            return {
                "success": True,
                "raw_analysis": response_text,
                "parse_error": "AI trả về không đúng format JSON, hiển thị dạng text",
                "ai_model": self.model,
                "contract_title": contract_name or "Hợp đồng",
                "reviewed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Contract review failed: {e}")
            return {
                "success": False,
                "error": f"Lỗi phân tích: {str(e)}"
            }
