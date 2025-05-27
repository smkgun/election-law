import streamlit as st
import pandas as pd
from konlpy.tag import Okt

# 페이지 설정
st.set_page_config(
    page_title="정치관계법 사례 조회",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS 스타일
st.markdown("""
<style>
    /* 메인 컨테이너 스타일링 */
    .main > div {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 헤더 스타일링 */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    /* 안내 박스 스타일링 */
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .info-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-content {
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* 검색 섹션 스타일링 */
    .search-container {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .search-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
        color: #2c3e50;
    }
    
    /* 결과 섹션 스타일링 */
    .result-container {
        background: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid #e0e6ed;
    }
    
    /* 데이터프레임 스타일링 */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* 모바일 반응형 */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        
        .search-container, .result-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .info-box {
            padding: 1.2rem;
        }
    }
    
    /* 스크롤바 스타일링 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# CSV 파일 불러오기
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(r"C:\Users\NOTE2\조원C&I\선거여론조사법령\정치관계법_사례통합_요약테이블.csv")
        return df
    except FileNotFoundError:
        st.error("⚠️ CSV 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 헤더 섹션
    st.markdown("""
    <div class="header-container">
        <div class="header-title">⚖️ 정치관계법 사례 조회 시스템</div>
        <div class="header-subtitle">제21대 대통령선거 정치관계법 사례예시집 기반 검색 서비스</div>
    </div>
    """, unsafe_allow_html=True)

    # 안내 정보 섹션
    st.markdown("""
    <div class="info-box">
        <div class="info-title">
            📋 위반 여부 표시 기준
        </div>
        <div class="info-content">
            <strong>✅ 허용</strong>: 해당 사례는 선거법상 허용된 행위입니다.<br>
            <strong>❌ 위반</strong>: 해당 사례는 선거법 위반으로 간주되며 제재 대상입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 키워드 추출 함수
    @st.cache_data
    def extract_keywords(text_series, top_n=25):
        """텍스트에서 키워드를 추출하는 함수"""
        okt = Okt()
        words = []
        
        with st.spinner('🔍 키워드를 분석하고 있습니다...'):
            for text in text_series.dropna():
                try:
                    words += okt.nouns(str(text))
                except:
                    continue
        
        # 불용어 제거 및 길이 필터링
        stop_words = {'이', '그', '저', '것', '수', '등', '및', '의', '을', '를', '이다', '있다', '하다'}
        words = [word for word in words if len(word) > 1 and word not in stop_words]
        
        freq = pd.Series(words).value_counts()
        return freq.head(top_n).index.tolist()

    # 키워드 자동 추출
    if 'keywords' not in st.session_state:
        with st.spinner('📊 데이터를 분석하여 키워드를 추출하고 있습니다...'):
            keywords = extract_keywords(
                df['대분류'].astype(str) + " " +
                df['소분류'].astype(str) + " " +
                df['사실관계'].astype(str) + " " +
                df['해설'].astype(str)
            )
            st.session_state.keywords = keywords
    else:
        keywords = st.session_state.keywords

    # 검색 섹션
    st.markdown("""
    <div class="search-container">
        <div class="search-title">🔍 사례 검색하기</div>
    </div>
    """, unsafe_allow_html=True)

    # 검색 UI (모바일 친화적 레이아웃)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**📌 추천 키워드에서 선택**")
        selected = st.selectbox(
            "",
            options=["키워드를 선택하세요..."] + keywords,
            key="keyword_select"
        )

    with col2:
        st.markdown("**✏️ 직접 입력**")
        manual_input = st.text_input(
            "",
            placeholder="예: 선거운동, 기부행위, SNS 등",
            key="manual_input"
        )

    # 검색어 결정
    search_term = ""
    if selected and selected != "키워드를 선택하세요...":
        search_term = selected
    elif manual_input:
        search_term = manual_input

    # 검색 결과 표시
    if search_term:
        st.markdown(f"""
        <div class="result-container">
            <h3 style="color: #2c3e50; margin-bottom: 1rem;">
                🎯 "<strong>{search_term}</strong>" 검색 결과
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # 검색 실행
        target_text = (
            df['대분류'].astype(str) + " " +
            df['소분류'].astype(str) + " " +
            df['사실관계'].astype(str) + " " +
            df['해설'].astype(str)
        )
        result = df[target_text.str.lower().str.contains(search_term.lower(), na=False)]

        if not result.empty:
            # 검색 결과 통계
            total_cases = len(result)
            violation_cases = len(result[result['위반여부'].str.contains('위반', na=False)])
            allowed_cases = total_cases - violation_cases

            # 통계 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 총 사례 수", total_cases)
            with col2:
                st.metric("❌ 위반 사례", violation_cases)
            with col3:
                st.metric("✅ 허용 사례", allowed_cases)

            st.markdown("---")

            # 결과 데이터프레임 표시
            display_df = result[['대분류', '소분류', '사실관계', '법조항', '위반여부', '해설']].reset_index(drop=True)
            
            # 위반여부 컬럼 스타일링을 위한 함수
            def highlight_violation(val):
                if '위반' in str(val):
                    return 'background-color: #ffebee; color: #c62828; font-weight: bold;'
                elif '허용' in str(val) or '가능' in str(val):
                    return 'background-color: #e8f5e8; color: #2e7d32; font-weight: bold;'
                return ''

            styled_df = display_df.style.applymap(highlight_violation, subset=['위반여부'])
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=400
            )

        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: #fff3cd; border-radius: 10px; margin: 2rem 0;">
                <h3 style="color: #856404;">🔍 검색 결과가 없습니다</h3>
                <p style="color: #856404; margin-bottom: 0;">
                    다른 키워드로 검색해보시거나, 키워드를 더 간단하게 입력해보세요.
                </p>
            </div>
            """, unsafe_allow_html=True)

    else:
        # 초기 화면 안내
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: #1565c0; margin-bottom: 1rem;">🌟 검색을 시작해보세요</h3>
            <p style="color: #1565c0; font-size: 1.1rem; margin-bottom: 0;">
                위의 키워드 선택 또는 직접 입력을 통해<br>
                관련 정치관계법 사례를 찾아보실 수 있습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

# 푸터 섹션
st.markdown("---")
st.markdown("")

# 중앙 정렬을 위한 컬럼
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("#### 🏛️ Data-Insight LAB by Carl")
    
    st.warning("⚠️ **중요 안내**: 이 검색 결과는 참고용입니다")
    
    st.info("""
    정확한 위반 여부 판단은 선거관리위원회의 공식 유권해석을 받으시기 바랍니다.
    
    본 서비스는 정치관계법 사례 검색을 위한 참고 도구로만 활용해주세요.
    """)
    
    st.caption("© 2024 Data-Insight LAB. 정치관계법 사례예시집 기반 서비스")