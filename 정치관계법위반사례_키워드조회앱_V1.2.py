import streamlit as st
import pandas as pd
import re
from collections import Counter

# 페이지 설정
st.set_page_config(
    page_title="정치관계법 사례 조회 시스템",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS - 전문가급 디자인
st.markdown("""
<style>
    /* 메인 컨테이너 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 헤더 스타일링 */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* 검색 섹션 */
    .search-section {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    .search-title {
        color: #1e293b;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 카드 스타일 */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .violation-guide {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    .guide-title {
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .guide-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .guide-allowed {
        color: #059669;
        font-weight: 500;
    }
    
    .guide-violation {
        color: #dc2626;
        font-weight: 500;
    }
    
    /* 결과 통계 */
    .result-stats {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
    }
    
    /* 푸터 */
    .footer-section {
        background: #f1f5f9;
        padding: 2rem;
        border-radius: 12px;
        margin-top: 3rem;
        border: 1px solid #e2e8f0;
    }
    
    .footer-title {
        color: #1e293b;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .disclaimer {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #92400e;
    }
    
    .info-box {
        background: #dbeafe;
        border: 1px solid #3b82f6;
        padding: 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        color: #1e40af;
        line-height: 1.5;
    }
    
    /* Streamlit 컴포넌트 스타일 오버라이드 */
    .stSelectbox > div > div {
        border-radius: 6px;
        border: 1px solid #d1d5db;
    }
    
    .stTextInput > div > div {
        border-radius: 6px;
        border: 1px solid #d1d5db;
    }
    
    /* 데이터프레임 스타일링 */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# CSV 파일 불러오기
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("정치관계법_사례통합_요약테이블.csv")
        return df
    except FileNotFoundError:
        st.error("⚠️ CSV 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return pd.DataFrame()

df = load_data()

# 키워드 추출 함수
@st.cache_data
def extract_keywords(text_series, top_n=25):
    all_text = " ".join(text_series.dropna().astype(str)).lower()
    words = re.findall(r"[가-힣]{2,}", all_text)
    stop_words = {'이', '그', '저', '것', '수', '등', '및', '의', '을', '를', '이다', '있다', '하다'}
    words = [w for w in words if w not in stop_words]
    freq = Counter(words)
    return [word for word, _ in freq.most_common(top_n)]

# 키워드 준비
if not df.empty:
    if 'keywords' not in st.session_state:
        keywords = extract_keywords(
            df['대분류'].astype(str) + " " +
            df['소분류'].astype(str) + " " +
            df['사실관계'].astype(str) + " " +
            df['해설'].astype(str)
        )
        st.session_state.keywords = keywords
    else:
        keywords = st.session_state.keywords

    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <div class="main-title">⚖️ 정치관계법 위반·허용 사례 간편 조회 시스템</div>
        <div class="main-subtitle">제21대 대통령선거 정치관계법 사례예시집 기반</div>
        <div class="main-subtitle">Ver.250527 |  Data-Insight LAB by Carl</div>
    </div>
    
    """, unsafe_allow_html=True)

    # 위반 여부 가이드
    st.markdown("""
    <div class="violation-guide">
        <div class="guide-title">📋 위반 여부 판단 기준</div>
        <div class="guide-item">
            <span style="margin-right: 8px;">✅</span>
            <span class="guide-allowed">허용</span>
            <span style="margin-left: 8px; color: #64748b;">해당 사례는 선거법상 허용된 행위일 수 있습니다</span>
        </div>
        <div class="guide-item">
            <span style="margin-right: 8px;">❌</span>
            <span class="guide-violation">위반</span>
            <span style="margin-left: 8px; color: #64748b;">해당 사례는 선거법 위반으로 제재 대상일 수 있습니다</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 검색 섹션
    st.markdown("""
    <div class="search-section">
        <div class="search-title">🔍 사례 검색</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**📌 추천 키워드에서 선택**")
        selected = st.selectbox("키워드 선택", [""] + keywords, label_visibility="collapsed")

    with col2:
        st.markdown("**✏️ 직접 키워드 입력**")
        manual_input = st.text_input("키워드 입력", label_visibility="collapsed", placeholder="검색할 키워드를 입력하세요")

    search_term = selected if selected else manual_input

    if search_term:
        target_text = (
            df['대분류'].astype(str) + " " +
            df['소분류'].astype(str) + " " +
            df['사실관계'].astype(str) + " " +
            df['해설'].astype(str)
        )
        result = df[target_text.str.lower().str.contains(search_term.lower(), na=False)]

        if not result.empty:
            # 검색 결과 통계
            st.markdown(f"""
            <div class="result-stats">
                🎯 <strong>'{search_term}'</strong> 검색결과: 총 <strong>{len(result)}건</strong>의 사례가 검색되었습니다
            </div>
            """, unsafe_allow_html=True)

            display_df = result[['대분류', '소분류', '사실관계', '법조항', '위반여부', '해설']].reset_index(drop=True)

            def highlight_violation(val):
                if '위반' in str(val):
                    return 'background-color: #fef2f2; color: #dc2626; font-weight: 600; padding: 4px 8px; border-radius: 4px;'
                elif '허용' in str(val) or '가능' in str(val):
                    return 'background-color: #f0fdf4; color: #059669; font-weight: 600; padding: 4px 8px; border-radius: 4px;'
                return ''

            styled_df = display_df.style.applymap(highlight_violation, subset=['위반여부'])

            st.dataframe(
                styled_df, 
                use_container_width=True,
                height=400,
                column_config={
                    "대분류": st.column_config.TextColumn("대분류", width="medium"),
                    "소분류": st.column_config.TextColumn("소분류", width="medium"),
                    "사실관계": st.column_config.TextColumn("사실관계", width="large"),
                    "법조항": st.column_config.TextColumn("법조항", width="medium"),
                    "위반여부": st.column_config.TextColumn("위반여부", width="small"),
                    "해설": st.column_config.TextColumn("해설", width="large")
                }
            )

        else:
            st.markdown("""
            <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 1rem; border-radius: 6px; text-align: center; color: #dc2626;">
                🔍 '<strong>{}</strong>'에 대한 검색 결과가 없습니다.<br>
                다른 키워드로 다시 검색해보세요.
            </div>
            """.format(search_term), unsafe_allow_html=True)


 # 푸터
    st.markdown("---")
    
     
    st.warning("⚠️ **중요 안내:** 이 검색 결과는 참고용입니다.")
    
    st.info("""
📌 **정확한 위반 여부 판단은 선거관리위원회의 공식 유권해석을 받으시기 바랍니다.**

이 서비스는 정치관계법 사례 검색을 위한 참고 도구로, 실제 법적 판단의 근거로 사용하실 수 없습니다.
구체적인 사안에 대해서는 반드시 관련 기관에 문의하시기 바랍니다.
""")
     
    st.markdown("""
    <div class="footer-section">
        <div class="footer-title">🏛️ Data-Insight LAB by Carl</div>
    </div>
    """, unsafe_allow_html=True)
    
