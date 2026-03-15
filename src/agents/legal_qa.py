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

SYSTEM_PROMPT = """Bạn là một trợ lý pháp lý AI chuyên về luật Việt Nam. Vai trò của bạn là:

1. Trả lời câu hỏi pháp lý dựa trên các nguồn luật được cung cấp
2. LUÔN trích dẫn điều luật cụ thể (số hiệu văn bản, điều, khoản, điểm)
3. Sử dụng ngôn ngữ rõ ràng, dễ hiểu cho người không chuyên
4. Nếu thông tin không đủ hoặc không chắc chắn, PHẢI nói rõ
5. KHÔNG bao giờ bịa đặt điều luật hoặc trích dẫn không có trong nguồn

Quy tắc quan trọng:
- Chỉ trả lời dựa trên nguồn luật được cung cấp trong context
- Nếu câu hỏi nằm ngoài phạm vi nguồn, nói rõ giới hạn
- Luôn kèm disclaimer rằng đây là tư vấn tham khảo
- Ưu tiên văn bản pháp luật còn hiệu lực (status: active)
- Nếu luật đã sửa đổi, ghi chú rõ ràng

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
