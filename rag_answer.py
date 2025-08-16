# rag_answer.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import os

# ===== Safety notes =====
DISCLAIMER = (
    "본 안내는 법률 자문이 아니며, 사례/판례/선관위 자료 기반의 참고 정보입니다. "
    "최종 판단은 법률 전문가와 상의하세요."
)

SYSTEM_INSTRUCTION = (
    "당신은 '선거법 사례 안내 도우미'입니다. 법률 자문을 제공하지 않습니다.\n"
    "반드시 다음 원칙을 지키세요:\n"
    "1) 단정적인 법률 판단을 하지 말 것. '위반이다'/'합법'이라는 표현 금지.\n"
    "2) 과거 유사 사례와 조문을 '참고' 차원에서 제시.\n"
    "3) 모든 결론에는 항상 출처(사례ID/조문/URL)를 나열.\n"
    "4) 마지막 줄에 디스클레이머 명시.\n"
)

@dataclass
class RetrievedCase:
    id: str
    law: str
    article: str
    penalty: str
    fact: str
    source_url: str
    score: float

class Retriever:
    """TF-IDF 기반 상위 사례 조회. (v1의 search_tfidf와 동일 동작)"""
    def __init__(self, tfidf_searcher):
        self.searcher = tfidf_searcher

    def retrieve(self, query: str, topk: int = 5) -> List[RetrievedCase]:
        rows = self.searcher.query(query, topk=topk)
        out = []
        for r in rows:
            out.append(RetrievedCase(
                id=r.get("id",""), law=r.get("law",""), article=r.get("article",""),
                penalty=r.get("penalty",""), fact=r.get("fact",""),
                source_url=r.get("source_url",""), score=float(r.get("score",0.0))
            ))
        return out

class RAGAnswerer:
    def __init__(self, backend: str = "none", model: str = "", temperature: float = 0.2):
        self.backend = backend
        self.model = model
        self.temperature = temperature
        self.has_openai = False
        if backend == "openai":
            try:
                from openai import OpenAI  # type: ignore
                self._OpenAI = OpenAI
                self.has_openai = True
            except Exception:
                self.has_openai = False

    def _format_context(self, cases: List[RetrievedCase]) -> str:
        blocks = []
        for c in cases:
            block = (
                f"[사례ID] {c.id}\n"
                f"[조문] {c.law} {c.article}\n"
                f"[제재] {c.penalty}\n"
                f"[요지] {c.fact}\n"
                f"[출처] {c.source_url}\n"
            )
            blocks.append(block)
        return "\n---\n".join(blocks)

    def _build_prompt(self, user_query: str, cases: List[RetrievedCase]) -> str:
        ctx = self._format_context(cases)
        prompt = (
            f"사용자 입력: {user_query}\n\n"
            f"관련 사례(참고용):\n{ctx}\n\n"
            "요구사항:\n"
            "- 위 사례와 조문을 근거로, '위험신호/주의사항/대안 가이드'를 요약해 주세요.\n"
            "- 표현은 '참고 안내' 수준으로, 단정적인 법률 판단은 피하세요.\n"
            "- 반드시 마지막에 '인용/출처' 목록과 디스클레이머를 포함하세요.\n"
        )
        return prompt

    def answer(self, user_query: str, cases: List[RetrievedCase]) -> Dict[str, Any]:
        # 0) LLM 비사용 템플릿(기본)
        if self.backend == "none" or (self.backend == "openai" and not self.has_openai):
            bullets = []
            for c in cases:
                bullets.append(f"- {c.law} {c.article} / {c.id} — {c.penalty}")
            guidance = (
                "• 유사 사례를 참고할 때, 시기(선거일 전/후), 매체(온라인/오프라인), 대상(선거구민/지지자),\n"
                "  금품/물품 제공 여부를 반드시 구체화해 내부 검토를 진행하세요.\n"
                "• 문안은 사실관계 확인 후 표현을 완곡화하고, 공표/배포 시 금지기간 여부를 재확인하세요.\n"
            )
            return {
                "mode": "template",
                "summary": "유사 사례 기반 참고 안내입니다.",
                "guidance": guidance,
                "citations": bullets,
                "disclaimer": DISCLAIMER,
            }

        # 1) OpenAI 백엔드
        if self.backend == "openai" and self.has_openai:
            client = self._OpenAI()
            prompt = self._build_prompt(user_query, cases)
            msgs = [
                {"role":"system","content": SYSTEM_INSTRUCTION},
                {"role":"user","content": prompt}
            ]
            # gpt-4o-mini 등 경량 모델 권장
            model_name = self.model or "gpt-4o-mini"
            resp = client.chat.completions.create(model=model_name, messages=msgs, temperature=self.temperature)
            text = resp.choices[0].message.content.strip()
            return {
                "mode": "openai",
                "answer": text,
                "disclaimer": DISCLAIMER,
            }

        # 2) (확장) 로컬 LLM 백엔드 — 필요 시 추가 구현
        raise NotImplementedError("Backend not implemented: " + self.backend)
