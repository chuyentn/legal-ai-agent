"""Legal Q&A Agent — answers legal questions using RAG over Vietnamese law."""

import os
from typing import Optional

import anthropic

from src.rag.search import hybrid_search, SearchResult
from src.rag.embedder import get_embedder
from src.models.schemas import (
    LegalQuestionRequest,
    LegalAnswerResponse,
    Citation,
    LegalDomain,
)

SYSTEM_PROMPT = """Bạn là Trợ lý Pháp lý AI chuyên nghiệp về luật Việt Nam.

NĂNG LỰC:
1. TRẢ LỜI câu hỏi pháp lý — giải thích luật, tra cứu điều khoản
2. SOẠN THẢO văn bản — hợp đồng, đơn từ, biên bản, quyết định, nội quy
3. TƯ VẤN — phân tích rủi ro pháp lý, đề xuất giải pháp
4. RÀ SOÁT — kiểm tra tính hợp pháp của văn bản

Khi trả lời câu hỏi:
- Trích dẫn điều luật cụ thể (số hiệu, điều, khoản, điểm)
- Ngôn ngữ rõ ràng, dễ hiểu cho người không chuyên
- Ưu tiên văn bản pháp luật còn hiệu lực

Khi soạn thảo văn bản:
- Soạn HOÀN CHỈNH, chuyên nghiệp, đúng chuẩn pháp lý VN
- Đánh dấu chỗ cần điền: [THÔNG TIN CẦN ĐIỀN]
- Bao gồm đầy đủ điều khoản bắt buộc theo luật
- Format rõ ràng: tiêu đề, điều khoản đánh số, phần chữ ký

Quy tắc:
- Sử dụng nguồn luật được cung cấp làm tham chiếu chính
- Kết hợp kiến thức pháp luật VN để trả lời toàn diện
- KHÔNG bịa số hiệu văn bản hoặc điều luật cụ thể
- Nếu nguồn không đủ, vẫn hỗ trợ nhưng ghi chú rõ
- Luôn kèm disclaimer: tư vấn tham khảo, cần luật sư cho trường hợp cụ thể

Trả lời bằng tiếng Việt."""

DISCLAIMER = "Nội dung tư vấn mang tính tham khảo. Vui lòng tham khảo ý kiến luật sư cho trường hợp cụ thể."


class LegalQAAgent:
    """Agent that answers legal questions using RAG."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.embedder = get_embedder()
        self.model = "claude-sonnet-4-20250514"
    
    async def answer(self, request: LegalQuestionRequest) -> LegalAnswerResponse:
        """Process a legal question and return an answer with citations."""
        
        # Step 1: Embed the question
        query_embedding = await self.embedder.embed(request.question)
        
        # Step 2: Search for relevant law chunks
        domains = [d.value for d in request.domains] if request.domains else None
        search_results = await hybrid_search(
            query_embedding=query_embedding,
            query_text=request.question,
            domains=domains,
            limit=8,
        )
        
        # Step 3: Build context from search results
        context = self._build_context(search_results)
        
        # Step 4: Generate answer with Claude
        answer_text, citations = await self._generate_answer(
            question=request.question,
            context=context,
            search_results=search_results,
        )
        
        # Step 5: Extract related topics
        related = self._extract_related_topics(search_results)
        
        # Step 6: Calculate confidence
        confidence = self._calculate_confidence(search_results)
        
        return LegalAnswerResponse(
            answer=answer_text,
            confidence=confidence,
            citations=citations,
            related_topics=related,
            disclaimer=DISCLAIMER,
            usage={},  # TODO: track tokens
        )
    
    def _build_context(self, results: list[SearchResult]) -> str:
        """Build context string from search results."""
        parts = []
        for i, r in enumerate(results, 1):
            ref = f"[{i}] {r.law_title} ({r.law_number})"
            if r.article:
                ref += f" - {r.article}"
            if r.clause:
                ref += f", {r.clause}"
            ref += f" [Status: {r.law_status}]"
            
            parts.append(f"{ref}\n{r.content}")
        
        return "\n\n---\n\n".join(parts)
    
    async def _generate_answer(
        self,
        question: str,
        context: str,
        search_results: list[SearchResult],
    ) -> tuple[str, list[Citation]]:
        """Generate answer using Claude with retrieved context."""
        
        user_prompt = f"""Dựa trên các nguồn luật sau đây, hãy trả lời câu hỏi.

## Nguồn luật:

{context}

## Câu hỏi:

{question}

## Yêu cầu:
- Trả lời rõ ràng, có cấu trúc
- Trích dẫn cụ thể điều, khoản từ nguồn
- Ghi chú nếu luật đã hết hiệu lực hoặc sửa đổi
- Đề xuất các vấn đề liên quan nếu cần thiết"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        
        answer_text = response.content[0].text
        
        # Extract citations from search results used
        citations = []
        for r in search_results[:5]:  # Top 5 most relevant
            citations.append(Citation(
                law_title=r.law_title,
                law_number=r.law_number,
                article=r.article,
                clause=r.clause,
                text=r.content[:200] + "..." if len(r.content) > 200 else r.content,
                status=r.law_status,
            ))
        
        return answer_text, citations
    
    def _extract_related_topics(self, results: list[SearchResult]) -> list[str]:
        """Extract related topic suggestions from search results."""
        # TODO: Use LLM to suggest related topics
        topics = set()
        for r in results:
            if r.article:
                topics.add(f"{r.law_title} - {r.article}")
        return list(topics)[:5]
    
    def _calculate_confidence(self, results: list[SearchResult]) -> float:
        """Calculate confidence score based on search quality."""
        if not results:
            return 0.0
        
        # Based on top result relevance
        top_score = results[0].combined_score
        
        # Adjust based on number of relevant results
        relevant_count = sum(1 for r in results if r.combined_score > 0.5)
        coverage_bonus = min(relevant_count * 0.05, 0.2)
        
        confidence = min(top_score + coverage_bonus, 1.0)
        return round(confidence, 2)
