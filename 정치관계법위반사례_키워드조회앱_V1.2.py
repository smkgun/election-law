import streamlit as st
import pandas as pd
import re
from collections import Counter

# 페이지 설정
st.set_page_config(
    page_title="정치관계법 사례 조회",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# 키워드 추출 함수 (Python 기반, konlpy 제거)
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

    st.title("⚖️ 정치관계법 사례 조회 시스템")
    st.caption("출처: 제21대 대통령선거 정치관계법 사례예시집")

    st.markdown("""
    ### 🧾 위반 여부 표시 기준
    - ✅ **허용**: 해당 사례는 선거법상 허용된 행위입니다.  
    - ❌ **위반**: 해당 사례는 선거법 위반으로 간주되며 제재 대상입니다.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        selected = st.selectbox("📌 추천 키워드", [""] + keywords)

    with col2:
        manual_input = st.text_input("✏️ 키워드를 직접 입력")

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
            st.success(f"🔎 총 {len(result)}건의 사례가 검색되었습니다.")

            display_df = result[['대분류', '소분류', '사실관계', '법조항', '위반여부', '해설']].reset_index(drop=True)

            def highlight_violation(val):
                if '위반' in str(val):
                    return 'background-color: #ffebee; color: #c62828; font-weight: bold;'
                elif '허용' in str(val) or '가능' in str(val):
                    return 'background-color: #e8f5e8; color: #2e7d32; font-weight: bold;'
                return ''

            styled_df = display_df.style.applymap(highlight_violation, subset=['위반여부'])

            st.dataframe(styled_df, use_container_width=True)

        else:
            st.warning("검색된 사례가 없습니다. 다른 키워드로 시도해보세요.")

# 푸터
st.markdown("---")
st.markdown("#### 🏛️ Data-Insight LAB by Carl", unsafe_allow_html=True)
st.warning("⚠️ 이 검색 결과는 참고용입니다.")
st.info("""
정확한 위반 여부 판단은 선거관리위원회의 공식 유권해석을 받으시기 바랍니다.
이 서비스는 정치관계법 사례 검색을 위한 참고 도구입니다.
""")
