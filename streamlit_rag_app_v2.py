# streamlit_rag_app_v2.py
import streamlit as st
from search_tfidf import TfidfSearcher
from rag_answer import Retriever, RAGAnswerer, DISCLAIMER
from datetime import datetime

st.set_page_config(page_title="선거법 RAG 안내 데모", page_icon="🗳️", layout="wide")

st.title("🗳️ 선거법 RAG 안내 (데모 v2)")
st.caption("※ 법률 자문이 아닌 참고 서비스입니다. 사례/판례/선관위 자료를 인용합니다.")

# Sidebar — 백엔드/옵션
with st.sidebar:
    st.header("옵션")
    backend = st.selectbox("답변 백엔드", ["none","openai"], index=0, help="'none'은 LLM 없이 템플릿 요약")
    model = st.text_input("OpenAI 모델명", value="gpt-4o-mini")
    topk = st.slider("참고 사례 수", 3, 15, 6)

@st.cache_resource(show_spinner=True)
def get_searcher():
    return TfidfSearcher(index_dir="./index")

searcher = get_searcher()
retriever = Retriever(searcher)

user_query = st.text_area("문안/행사 계획/질문", height=140, placeholder="예: 선거일 20일 전, 지역축제에서 현수막과 유인물을 배포하려 합니다. 허용 범위가 궁금합니다.")

col1, col2 = st.columns([1,1])
with col1:
    run = st.button("검색 + RAG 안내 생성")
with col2:
    clear = st.button("초기화")
    if clear:
        st.experimental_rerun()

if run and not user_query:
    st.warning("질문 또는 문안을 입력하세요.")

report_block = None
if run and user_query:
    with st.spinner("사례 검색 중…"):
        cases = retriever.retrieve(user_query, topk=topk)
    st.subheader("참고 사례")
    for i, c in enumerate(cases, start=1):
        with st.container(border=True):
            st.markdown(f"**{i}. {c.id}** · {c.law} {c.article} · {c.penalty} · score={c.score}")
            st.markdown(f"요지: {c.fact}…")
            if c.source_url:
                st.markdown(f"[출처]({c.source_url})")

    with st.spinner("RAG 안내 생성 중…"):
        answerer = RAGAnswerer(backend=backend, model=model)
        out = answerer.answer(user_query, cases)

    st.subheader("안내 결과")
    if out.get("mode") == "template":
        st.markdown("**요약**: " + out["summary"])
        st.markdown("**가이드**:\n" + out["guidance"])
        st.markdown("**인용/출처**:\n" + "\n".join(out["citations"]))
        st.info(DISCLAIMER)
        # Report payload
        report_block = {
            "query": user_query,
            "advice": out["guidance"],
            "citations": out["citations"],
            "cases": cases,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    else:
        st.markdown(out.get("answer","(응답 없음)"))
        st.info(DISCLAIMER)
        report_block = {
            "query": user_query,
            "llm_answer": out.get("answer",""),
            "cases": cases,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

# ===== Report (HTML download) =====
if report_block:
    import html
    def build_html(rep):
        def case_li(c):
            src = f'<a href="{html.escape(c.source_url)}" target="_blank">원문</a>' if c.source_url else ""
            return f"<li><b>{html.escape(c.id)}</b> — {html.escape(c.law)} {html.escape(c.article)} / {html.escape(c.penalty)} {src}</li>"
        cases_html = "\n".join(case_li(c) for c in rep["cases"])
        body = f"""
        <html><head><meta charset='utf-8'><style>
        body{{font-family:Pretendard,Arial,sans-serif;max-width:900px;margin:40px auto;line-height:1.6;}}
        h1{{color:#0a67b5;}}
        .box{{border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin:12px 0;}}
        .muted{{color:#64748b;font-size:12px}}
        </style></head><body>
        <h1>선거법 RAG 안내 (보고서)</h1>
        <p class='muted'>생성시각: {rep['generated_at']}</p>
        <div class='box'><b>입력</b><br>{html.escape(rep['query'])}</div>
        {('<div class="box"><b>LLM 답변</b><br>'+rep.get('llm_answer','').replace('\n','<br>')+'</div>') if rep.get('llm_answer') else ''}
        {('<div class="box"><b>가이드</b><br>'+rep.get('advice','').replace('\n','<br>')+'</div>') if rep.get('advice') else ''}
        <div class='box'><b>인용/출처</b><ul>{cases_html}</ul></div>
        <p class='muted'>※ 본 보고서는 법률 자문이 아니며, 사례/판례/선관위 자료 기반 참고 안내입니다.</p>
        </body></html>
        """
        return body

    html_blob = build_html(report_block)
    st.download_button(
        label="리포트 저장 (HTML)",
        data=html_blob.encode("utf-8"),
        file_name="electionlaw_rag_report.html",
        mime="text/html"
    )
    st.caption("※ HTML을 열어 브라우저 인쇄 → PDF 저장을 권장합니다.")

st.markdown("---")
st.caption("© 학습·연구용. 법률 자문 아님. 정치적 중립을 지키며 출처를 명확히 표기합니다.")
