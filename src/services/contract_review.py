"""
Contract Review AI Service
Analyzes uploaded contracts, identifies risks, unfavorable clauses, and compares with Vietnamese law.
This is the killer feature for enterprise legal departments.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ContractReviewService:
    """
    Contract Review AI - Analyzes contracts for risks and legal compliance
    """
    
    # Vietnamese law references
    LAWS = {
        "civil_code_2015": {
            "name": "Bộ Luật Dân Sự 2015",
            "key_articles": {
                "156": "Bất khả kháng",
                "404": "Hợp đồng — Khái niệm",
                "420": "Điều kiện hiệu lực hợp đồng",
                "423": "Hợp đồng vô hiệu",
                "432": "Giải thích hợp đồng"
            }
        },
        "commercial_law_2005": {
            "name": "Luật Thương Mại 2005",
            "key_articles": {
                "301": "Phạt vi phạm — Tối đa 8%",
                "306": "Bồi thường thiệt hại"
            }
        },
        "enterprise_law_2020": {
            "name": "Luật Doanh Nghiệp 2020",
            "articles": ["4", "7", "11", "23"]
        },
        "labor_law_2019": {
            "name": "Bộ Luật Lao Động 2019",
            "key_articles": {
                "21": "Nội dung hợp đồng lao động",
                "25": "Thời gian thử việc",
                "35-36": "Đơn phương chấm dứt HĐLĐ",
                "90": "Lương tối thiểu",
                "105": "Thời giờ làm việc",
                "113": "Nghỉ phép năm"
            }
        }
    }
    
    # Risk categories
    RISK_CATEGORIES = {
        "unfavorable_terms": "Điều khoản bất lợi",
        "excessive_penalty": "Phạt vi phạm cao",
        "unreasonable_deadline": "Thời hạn bất hợp lý",
        "missing_protection": "Thiếu điều khoản bảo vệ",
        "law_conflict": "Mâu thuẫn với luật",
        "auto_renewal": "Điều khoản tự động gia hạn",
        "liability_limit": "Giới hạn trách nhiệm",
        "ip_confidentiality": "Bảo mật và SHTT",
        "dispute_resolution": "Giải quyết tranh chấp",
        "force_majeure": "Force majeure"
    }
    
    def __init__(self):
        self.risk_patterns = self._build_risk_patterns()
    
    def _build_risk_patterns(self) -> Dict:
        """Build regex patterns for risk detection"""
        return {
            "excessive_penalty": [
                r'phạt.*?(\d+)\s*%',
                r'chế tài.*?(\d+)\s*%',
                r'vi phạm.*?(\d+)\s*%.*?giá trị'
            ],
            "auto_renewal": [
                r'tự động.*?gia hạn',
                r'gia hạn.*?tự động',
                r'mặc định.*?kéo dài'
            ],
            "liability_limit": [
                r'giới hạn.*?trách nhiệm',
                r'không chịu.*?trách nhiệm',
                r'trách nhiệm.*?tối đa'
            ],
            "one_sided": [
                r'bên [AB].*?có quyền.*?đơn phương',
                r'bên [AB].*?quyết định.*?duy nhất'
            ]
        }
    
    def parse_contract(self, contract_text: str) -> Dict:
        """
        Extract contract structure: parties, terms, obligations, penalties, termination
        """
        sections = {
            "parties": self._extract_parties(contract_text),
            "terms": self._extract_terms(contract_text),
            "obligations": self._extract_obligations(contract_text),
            "penalties": self._extract_penalties(contract_text),
            "termination": self._extract_termination(contract_text),
            "payment": self._extract_payment(contract_text),
            "duration": self._extract_duration(contract_text)
        }
        
        return sections
    
    def _extract_parties(self, text: str) -> List[str]:
        """Extract contracting parties"""
        parties = []
        
        # Pattern: Bên A: ...
        pattern_a = r'bên\s+a[:\s]+([^\n]+)'
        pattern_b = r'bên\s+b[:\s]+([^\n]+)'
        
        match_a = re.search(pattern_a, text, re.IGNORECASE)
        match_b = re.search(pattern_b, text, re.IGNORECASE)
        
        if match_a:
            parties.append(f"Bên A: {match_a.group(1).strip()}")
        if match_b:
            parties.append(f"Bên B: {match_b.group(1).strip()}")
        
        # Fallback: look for company names (contains TNHH, cổ phần, etc.)
        company_pattern = r'(công ty[^,\n]{10,80})'
        companies = re.findall(company_pattern, text, re.IGNORECASE)
        if not parties and companies:
            parties = [c.strip() for c in companies[:2]]
        
        return parties
    
    def _extract_terms(self, text: str) -> List[Dict]:
        """Extract key contractual terms"""
        terms = []
        
        # Find all "Điều X" sections
        article_pattern = r'(điều\s+\d+[:\.]?.*?)(?=điều\s+\d+|$)'
        matches = re.finditer(article_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            article_text = match.group(1).strip()
            # Get first line as title
            lines = article_text.split('\n', 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else article_text
            
            terms.append({
                "clause": title,
                "content": content[:300]  # Limit for preview
            })
        
        return terms[:15]  # Return top 15 articles
    
    def _extract_obligations(self, text: str) -> List[str]:
        """Extract obligations/responsibilities"""
        obligations = []
        
        patterns = [
            r'nghĩa vụ[:\s]+([^\n]+)',
            r'trách nhiệm[:\s]+([^\n]+)',
            r'phải[:\s]+([^\n]+)',
            r'cam kết[:\s]+([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            obligations.extend([m.strip() for m in matches if len(m.strip()) > 10])
        
        return list(set(obligations))[:10]
    
    def _extract_penalties(self, text: str) -> List[Dict]:
        """Extract penalty clauses"""
        penalties = []
        
        # Pattern: phạt X%
        pattern = r'(phạt|vi phạm|chế tài).*?(\d+(?:[.,]\d+)?)\s*%.*?(?:giá trị|hợp đồng)?([^\n\.]{0,100})'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            percentage = float(match.group(2).replace(',', '.'))
            context = match.group(3).strip() if match.group(3) else ""
            
            penalties.append({
                "type": "percentage",
                "value": percentage,
                "context": context,
                "exceeds_legal_limit": percentage > 8  # Vietnam law limit
            })
        
        return penalties
    
    def _extract_termination(self, text: str) -> Dict:
        """Extract termination clauses"""
        termination = {
            "has_clause": False,
            "notice_period": None,
            "conditions": []
        }
        
        # Check for termination clause
        if re.search(r'chấm dứt|kết thúc|hủy bỏ', text, re.IGNORECASE):
            termination["has_clause"] = True
        
        # Extract notice period
        notice_pattern = r'thông báo.*?(\d+)\s*(ngày|tháng|tuần)'
        notice_match = re.search(notice_pattern, text, re.IGNORECASE)
        if notice_match:
            termination["notice_period"] = f"{notice_match.group(1)} {notice_match.group(2)}"
        
        return termination
    
    def _extract_payment(self, text: str) -> Dict:
        """Extract payment terms"""
        payment = {
            "amounts": [],
            "schedule": [],
            "method": None
        }
        
        # Extract amounts (VNĐ, USD, etc.)
        amount_pattern = r'(\d+(?:[.,]\d+)?)\s*(?:triệu|tỷ|nghìn|đồng|vnđ|vnd|usd)'
        amounts = re.findall(amount_pattern, text, re.IGNORECASE)
        payment["amounts"] = [a for a in amounts[:5]]
        
        # Payment method
        if re.search(r'chuyển khoản', text, re.IGNORECASE):
            payment["method"] = "Chuyển khoản"
        elif re.search(r'tiền mặt', text, re.IGNORECASE):
            payment["method"] = "Tiền mặt"
        
        return payment
    
    def _extract_duration(self, text: str) -> Dict:
        """Extract contract duration"""
        duration = {
            "start_date": None,
            "end_date": None,
            "term": None
        }
        
        # Date patterns
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        dates = re.findall(date_pattern, text)
        if len(dates) >= 2:
            duration["start_date"] = dates[0]
            duration["end_date"] = dates[1]
        
        # Term (months/years)
        term_pattern = r'thời hạn.*?(\d+)\s*(tháng|năm)'
        term_match = re.search(term_pattern, text, re.IGNORECASE)
        if term_match:
            duration["term"] = f"{term_match.group(1)} {term_match.group(2)}"
        
        return duration
    
    def analyze_risks(self, contract_text: str, contract_type: Optional[str] = None) -> List[Dict]:
        """
        Analyze contract for 10 risk categories
        Returns list of issues with severity, description, law reference, suggestion
        """
        issues = []
        text_lower = contract_text.lower()
        
        # 1. Excessive penalty clauses (>8% per Vietnamese law)
        penalties = self._extract_penalties(contract_text)
        for penalty in penalties:
            if penalty.get("exceeds_legal_limit"):
                issues.append({
                    "type": "excessive_penalty",
                    "category": "Phạt vi phạm cao",
                    "severity": "CRITICAL",
                    "clause": "Điều khoản phạt vi phạm",
                    "issue": f"Mức phạt {penalty['value']}% vượt quá quy định pháp luật",
                    "law_reference": "Điều 301 Luật Thương Mại 2005: mức phạt tối đa 8% giá trị phần nghĩa vụ bị vi phạm",
                    "suggestion": f"Giảm mức phạt xuống không quá 8% giá trị hợp đồng",
                    "risk_score": 95
                })
        
        # 2. Auto-renewal traps
        if any(re.search(pattern, text_lower) for pattern in self.risk_patterns["auto_renewal"]):
            issues.append({
                "type": "auto_renewal",
                "category": "Điều khoản tự động gia hạn",
                "severity": "HIGH",
                "clause": "Điều khoản gia hạn",
                "issue": "Hợp đồng tự động gia hạn mà không yêu cầu xác nhận",
                "law_reference": "Điều 420 BLDS 2015: hợp đồng cần được các bên thỏa thuận",
                "suggestion": "Thêm điều khoản yêu cầu xác nhận bằng văn bản trước khi gia hạn",
                "risk_score": 70
            })
        
        # 3. Missing force majeure
        if not re.search(r'bất khả kháng|force majeure', text_lower):
            issues.append({
                "type": "missing_clause",
                "category": "Force majeure",
                "severity": "MEDIUM",
                "clause": "Thiếu điều khoản bất khả kháng",
                "issue": "Không có điều khoản xử lý tình huống bất khả kháng",
                "law_reference": "Điều 156 BLDS 2015: sự kiện bất khả kháng",
                "suggestion": "Thêm Điều khoản bất khả kháng: 'Các bên không phải chịu trách nhiệm khi không thực hiện được nghĩa vụ do sự kiện bất khả kháng theo Điều 156 BLDS 2015'",
                "risk_score": 60
            })
        
        # 4. Missing dispute resolution
        if not re.search(r'tranh chấp|trọng tài|tòa án', text_lower):
            issues.append({
                "type": "missing_clause",
                "category": "Giải quyết tranh chấp",
                "severity": "HIGH",
                "clause": "Thiếu điều khoản giải quyết tranh chấp",
                "issue": "Không quy định cơ quan giải quyết tranh chấp",
                "law_reference": "Điều 404 BLDS 2015: cần xác định rõ quyền và nghĩa vụ",
                "suggestion": "Thêm điều khoản: 'Tranh chấp phát sinh sẽ được giải quyết tại Tòa án có thẩm quyền tại [địa điểm]'",
                "risk_score": 75
            })
        
        # 5. Missing confidentiality/IP
        if not re.search(r'bảo mật|confidential|bí mật|sở hữu trí tuệ', text_lower):
            issues.append({
                "type": "missing_clause",
                "category": "Bảo mật và SHTT",
                "severity": "MEDIUM",
                "clause": "Thiếu điều khoản bảo mật",
                "issue": "Không có điều khoản bảo mật thông tin",
                "law_reference": "Luật Sở hữu trí tuệ 2005 (sửa đổi 2009, 2019)",
                "suggestion": "Thêm điều khoản bảo mật: 'Các bên cam kết bảo mật thông tin liên quan đến hợp đồng trong suốt thời hạn và ít nhất 2 năm sau khi chấm dứt'",
                "risk_score": 55
            })
        
        # 6. Liability limitations — check if too restrictive
        liability_matches = [m for pattern in self.risk_patterns["liability_limit"] 
                            for m in re.finditer(pattern, text_lower)]
        if len(liability_matches) > 1:
            issues.append({
                "type": "liability_limit",
                "category": "Giới hạn trách nhiệm",
                "severity": "MEDIUM",
                "clause": "Điều khoản giới hạn trách nhiệm",
                "issue": "Nhiều điều khoản hạn chế trách nhiệm, có thể không công bằng",
                "law_reference": "Điều 420 BLDS 2015: hợp đồng cần đảm bảo cân bằng quyền lợi",
                "suggestion": "Rà soát lại các giới hạn trách nhiệm để đảm bảo công bằng cho cả hai bên",
                "risk_score": 50
            })
        
        # 7. One-sided terms
        one_sided_matches = [m for pattern in self.risk_patterns["one_sided"] 
                             for m in re.finditer(pattern, text_lower)]
        if one_sided_matches:
            issues.append({
                "type": "unfavorable_terms",
                "category": "Điều khoản bất lợi",
                "severity": "HIGH",
                "clause": "Điều khoản quyền đơn phương",
                "issue": "Một bên có quyền đơn phương mà không cần thỏa thuận",
                "law_reference": "Điều 420 BLDS 2015: nguyên tắc bình đẳng, tự do, thiện chí",
                "suggestion": "Sửa lại để các quyền quan trọng cần có sự thỏa thuận của cả hai bên",
                "risk_score": 80
            })
        
        # 8. Missing termination clause
        termination = self._extract_termination(contract_text)
        if not termination["has_clause"]:
            issues.append({
                "type": "missing_clause",
                "category": "Thiếu điều khoản bảo vệ",
                "severity": "HIGH",
                "clause": "Thiếu điều khoản chấm dứt hợp đồng",
                "issue": "Không quy định điều kiện và thủ tục chấm dứt hợp đồng",
                "law_reference": "Điều 423 BLDS 2015: hợp đồng chấm dứt trong các trường hợp quy định",
                "suggestion": "Thêm điều khoản chấm dứt: 'Hợp đồng chấm dứt khi: (a) hết thời hạn, (b) hoàn thành nghĩa vụ, (c) các bên thỏa thuận, (d) đơn phương chấm dứt với thông báo trước X ngày'",
                "risk_score": 75
            })
        
        # 9. Vague/unreasonable deadlines
        vague_terms = ['hợp lý', 'sớm nhất', 'kịp thời', 'nhanh chóng']
        if any(term in text_lower for term in vague_terms):
            issues.append({
                "type": "unreasonable_deadline",
                "category": "Thời hạn bất hợp lý",
                "severity": "LOW",
                "clause": "Điều khoản thời hạn mơ hồ",
                "issue": "Sử dụng thuật ngữ mơ hồ như 'hợp lý', 'sớm nhất', 'kịp thời' mà không quy định cụ thể",
                "law_reference": "Điều 432 BLDS 2015: điều khoản mơ hồ sẽ được giải thích có lợi cho bên bị thiệt",
                "suggestion": "Thay thế các thuật ngữ mơ hồ bằng thời hạn cụ thể (số ngày, tháng)",
                "risk_score": 40
            })
        
        # 10. Labor law specific (if contract type is employment)
        if contract_type and 'lao' in contract_type.lower():
            # Check BHXH
            if not re.search(r'bảo hiểm\s+xã\s+hội|bhxh', text_lower):
                issues.append({
                    "type": "law_conflict",
                    "category": "Mâu thuẫn với luật",
                    "severity": "CRITICAL",
                    "clause": "Thiếu quy định BHXH",
                    "issue": "Hợp đồng lao động không đề cập đến BHXH",
                    "law_reference": "Luật BHXH 2014: người sử dụng lao động phải tham gia BHXH bắt buộc",
                    "suggestion": "Thêm điều khoản: 'Người sử dụng lao động đóng BHXH, BHYT, BHTN theo quy định của pháp luật'",
                    "risk_score": 90
                })
            
            # Check working hours
            if not re.search(r'giờ làm việc|thời gian làm việc', text_lower):
                issues.append({
                    "type": "missing_clause",
                    "category": "Thiếu điều khoản bảo vệ",
                    "severity": "HIGH",
                    "clause": "Thiếu quy định giờ làm việc",
                    "issue": "Không quy định rõ thời gian làm việc",
                    "law_reference": "Điều 105 BLLĐ 2019: thời giờ làm việc bình thường không quá 8 giờ/ngày, 48 giờ/tuần",
                    "suggestion": "Thêm điều khoản quy định giờ làm việc theo Điều 105 BLLĐ 2019",
                    "risk_score": 70
                })
        
        return issues
    
    def check_compliance(self, contract_text: str, contract_type: Optional[str] = None) -> Dict:
        """
        Check compliance with Vietnamese laws:
        - Civil Code 2015
        - Commercial Law 2005
        - Enterprise Law 2020
        - Labor Law 2019 (for employment contracts)
        """
        text_lower = contract_text.lower()
        
        compliance = {
            "civil_code": {"status": "COMPLIANT", "issues": 0, "details": []},
            "commercial_law": {"status": "COMPLIANT", "issues": 0, "details": []},
            "labor_law": {"status": "N/A", "issues": 0, "details": []},
            "enterprise_law": {"status": "N/A", "issues": 0, "details": []}
        }
        
        # Civil Code checks
        # Article 420: validity requirements
        required_elements = ["bên a", "bên b", "nghĩa vụ", "quyền"]
        missing_elements = [e for e in required_elements if e not in text_lower]
        if missing_elements:
            compliance["civil_code"]["status"] = "PARTIAL"
            compliance["civil_code"]["issues"] += 1
            compliance["civil_code"]["details"].append(
                f"Thiếu yếu tố: {', '.join(missing_elements)} (Điều 420 BLDS 2015)"
            )
        
        # Commercial Law checks (if commercial contract)
        # Article 301: penalty limit 8%
        penalties = self._extract_penalties(contract_text)
        if any(p.get("exceeds_legal_limit") for p in penalties):
            compliance["commercial_law"]["status"] = "VIOLATION"
            compliance["commercial_law"]["issues"] += 1
            compliance["commercial_law"]["details"].append(
                "Mức phạt vi phạm vượt quá 8% (Điều 301 Luật TM 2005)"
            )
        
        # Labor Law checks (if labor contract)
        if contract_type and 'lao' in contract_type.lower():
            compliance["labor_law"]["status"] = "COMPLIANT"
            
            # Article 21: mandatory content
            mandatory_content = [
                ("công việc", "Công việc, chức danh"),
                ("thời hạn", "Thời hạn hợp đồng"),
                ("lương", "Tiền lương"),
                ("nơi làm việc", "Nơi làm việc")
            ]
            
            for keyword, description in mandatory_content:
                if keyword not in text_lower:
                    compliance["labor_law"]["status"] = "PARTIAL"
                    compliance["labor_law"]["issues"] += 1
                    compliance["labor_law"]["details"].append(
                        f"Thiếu: {description} (Điều 21 BLLĐ 2019)"
                    )
            
            # Check trial period (Article 25)
            trial_pattern = r'thử việc.*?(\d+)\s*(ngày|tháng)'
            trial_match = re.search(trial_pattern, text_lower)
            if trial_match:
                period = int(trial_match.group(1))
                unit = trial_match.group(2)
                if unit == "tháng" and period > 6:
                    compliance["labor_law"]["status"] = "VIOLATION"
                    compliance["labor_law"]["issues"] += 1
                    compliance["labor_law"]["details"].append(
                        "Thời gian thử việc vượt quá 6 tháng (Điều 25 BLLĐ 2019)"
                    )
                elif unit == "ngày" and period > 180:
                    compliance["labor_law"]["status"] = "VIOLATION"
                    compliance["labor_law"]["issues"] += 1
                    compliance["labor_law"]["details"].append(
                        "Thời gian thử việc vượt quá 180 ngày (Điều 25 BLLĐ 2019)"
                    )
        
        return compliance
    
    def calculate_risk_score(self, issues: List[Dict]) -> Tuple[int, str]:
        """
        Calculate overall risk score 0-100
        Returns (score, level)
        level: LOW / MEDIUM / HIGH / CRITICAL
        """
        if not issues:
            return 10, "LOW"  # Perfect contract = 10 points (minor adjustments)
        
        total_score = 0
        severity_weights = {
            "CRITICAL": 25,
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3
        }
        
        for issue in issues:
            severity = issue.get("severity", "LOW")
            weight = severity_weights.get(severity, 5)
            total_score += weight
        
        # Cap at 100
        total_score = min(total_score, 100)
        
        # Determine level
        if total_score >= 75:
            level = "CRITICAL"
        elif total_score >= 50:
            level = "HIGH"
        elif total_score >= 25:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        return total_score, level
    
    def generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """
        Generate actionable recommendations based on issues found
        """
        recommendations = []
        
        # Group by severity
        critical = [i for i in issues if i.get("severity") == "CRITICAL"]
        high = [i for i in issues if i.get("severity") == "HIGH"]
        
        if critical:
            recommendations.append(
                f"⚠️ KHẨN CẤP: Sửa ngay {len(critical)} vấn đề nghiêm trọng trước khi ký kết hợp đồng"
            )
            for issue in critical:
                recommendations.append(f"• {issue.get('suggestion', '')}")
        
        if high:
            recommendations.append(
                f"🔴 Ưu tiên sửa {len(high)} vấn đề quan trọng"
            )
        
        # General recommendations
        if any(i.get("type") == "missing_clause" for i in issues):
            recommendations.append(
                "📝 Bổ sung các điều khoản còn thiếu để bảo vệ quyền lợi đầy đủ"
            )
        
        if any(i.get("category") == "Mâu thuẫn với luật" for i in issues):
            recommendations.append(
                "⚖️ Tham vấn luật sư để đảm bảo tuân thủ pháp luật Việt Nam"
            )
        
        if not recommendations:
            recommendations.append(
                "✅ Hợp đồng tương đối tốt, chỉ cần điều chỉnh nhỏ"
            )
        
        return recommendations
    
    def review_contract(
        self,
        contract_text: str,
        contract_name: str = "Hợp đồng",
        contract_type: Optional[str] = None,
        parties: Optional[List[str]] = None
    ) -> Dict:
        """
        Main review function — returns complete review report
        """
        # Parse contract
        parsed = self.parse_contract(contract_text)
        
        # If parties not provided, use extracted ones
        if not parties:
            parties = parsed.get("parties", [])
        
        # Analyze risks
        issues = self.analyze_risks(contract_text, contract_type)
        
        # Check compliance
        compliance = self.check_compliance(contract_text, contract_type)
        
        # Calculate risk score
        risk_score, risk_level = self.calculate_risk_score(issues)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(issues)
        
        # Build summary
        summary = self._build_summary(
            contract_name, parties, risk_score, risk_level, 
            len(issues), compliance
        )
        
        # Group clauses by category
        clauses_by_category = {}
        for issue in issues:
            category = issue.get("category", "Khác")
            if category not in clauses_by_category:
                clauses_by_category[category] = []
            clauses_by_category[category].append({
                "clause_number": issue.get("clause", "N/A"),
                "title": issue.get("category", ""),
                "content": issue.get("issue", ""),
                "risk_level": issue.get("severity", "LOW"),
                "risk_score": issue.get("risk_score", 50),
                "issue": issue.get("issue", ""),
                "law_reference": issue.get("law_reference", ""),
                "suggestion": issue.get("suggestion", ""),
                "category": category
            })
        
        # Find missing clauses
        missing_clauses = [
            {
                "clause": issue.get("clause", ""),
                "importance": issue.get("severity", "MEDIUM"),
                "suggestion": issue.get("suggestion", "")
            }
            for issue in issues if issue.get("type") == "missing_clause"
        ]
        
        return {
            "review_id": f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "contract_title": contract_name,
            "contract_type": contract_type or "N/A",
            "parties": parties,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "summary": summary,
            "clauses": list(clauses_by_category.values())[0] if clauses_by_category else [],
            "missing_clauses": missing_clauses,
            "compliance": compliance,
            "recommendations": recommendations,
            "parsed_sections": parsed,
            "total_issues": len(issues),
            "reviewed_at": datetime.now().isoformat()
        }
    
    def _build_summary(
        self,
        contract_name: str,
        parties: List[str],
        risk_score: int,
        risk_level: str,
        num_issues: int,
        compliance: Dict
    ) -> str:
        """Build human-readable summary"""
        
        parties_str = ", ".join(parties) if parties else "Chưa xác định các bên"
        
        summary = f"""## Tóm tắt rà soát hợp đồng

**Hợp đồng:** {contract_name}
**Các bên:** {parties_str}
**Điểm rủi ro:** {risk_score}/100 ({risk_level})
**Số vấn đề phát hiện:** {num_issues}

### Đánh giá tuân thủ pháp luật:
"""
        
        for law, details in compliance.items():
            status_emoji = {
                "COMPLIANT": "✅",
                "PARTIAL": "⚠️",
                "VIOLATION": "❌",
                "N/A": "➖"
            }.get(details["status"], "❓")
            
            law_name = {
                "civil_code": "Bộ Luật Dân Sự 2015",
                "commercial_law": "Luật Thương Mại 2005",
                "labor_law": "Bộ Luật Lao Động 2019",
                "enterprise_law": "Luật Doanh Nghiệp 2020"
            }.get(law, law)
            
            summary += f"- {status_emoji} **{law_name}**: {details['status']}"
            if details["issues"] > 0:
                summary += f" ({details['issues']} vấn đề)"
            summary += "\n"
        
        if risk_level == "CRITICAL":
            summary += "\n⚠️ **CẢNH BÁO:** Hợp đồng có nhiều rủi ro nghiêm trọng. Không nên ký kết trước khi sửa đổi.\n"
        elif risk_level == "HIGH":
            summary += "\n🔴 **LƯU Ý:** Hợp đồng có rủi ro cao. Cần sửa đổi trước khi ký.\n"
        elif risk_level == "MEDIUM":
            summary += "\n🟡 Hợp đồng có một số vấn đề cần điều chỉnh.\n"
        else:
            summary += "\n✅ Hợp đồng tương đối tốt, chỉ cần điều chỉnh nhỏ.\n"
        
        return summary
