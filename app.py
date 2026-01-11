import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# API 서버 주소
API_URL = "http://127.0.0.1:8000"

# === 1. 설정 및 테마 로직 ===
st.set_page_config(page_title="기업 자산관리 솔루션", layout="wide", page_icon="🏢")

# 테마 정의 (한글 명칭 적용)
themes = {
    "미드나잇 글래스": {
        "bg_color": "#0e1117",
        "text_color": "#ffffff",
        "card_bg": "rgba(255, 255, 255, 0.05)",
        "card_border": "1px solid rgba(255, 255, 255, 0.1)",
        "button_grad": "linear-gradient(45deg, #4b6cb7, #182848)",
        "plotly_template": "plotly_dark",
        "accent_color": "#4b6cb7"
    },
    "코퍼레이트 라이트": {
        "bg_color": "#f0f2f6",
        "text_color": "#333333",
        "card_bg": "#ffffff",
        "card_border": "1px solid #e0e0e0",
        "button_grad": "linear-gradient(45deg, #2980b9, #6dd5fa)",
        "plotly_template": "plotly_white",
        "accent_color": "#2980b9"
    },
    "사이버펑크 네온": {
        "bg_color": "#000000",
        "text_color": "#0ff",
        "card_bg": "rgba(0, 255, 255, 0.1)",
        "card_border": "1px solid #0ff",
        "button_grad": "linear-gradient(45deg, #ff00de, #0beff9)",
        "plotly_template": "plotly_dark",
        "accent_color": "#0ff"
    },
    "오션 블루": {
        "bg_color": "#1a2a6c",
        "text_color": "#e0f7fa",
        "card_bg": "rgba(255, 255, 255, 0.1)",
        "card_border": "1px solid rgba(255, 255, 255, 0.2)",
        "button_grad": "linear-gradient(45deg, #b21f1f, #1a2a6c)",
        "plotly_template": "plotly_dark",
        "accent_color": "#4fc3f7"
    },
    "포레스트 그린": {
        "bg_color": "#1b4d3e",
        "text_color": "#dcedc8",
        "card_bg": "rgba(255, 255, 255, 0.1)",
        "card_border": "1px solid rgba(165, 214, 167, 0.3)",
        "button_grad": "linear-gradient(45deg, #56ab2f, #a8e063)",
        "plotly_template": "plotly_dark",
        "accent_color": "#a5d6a7"
    }
}

# 사이드바에서 테마 선택
st.sidebar.title("🎨 디자인 설정")
selected_theme_name = st.sidebar.selectbox("테마 선택", list(themes.keys()))
current_theme = themes[selected_theme_name]

# CSS 주입
st.markdown(f"""
    <style>
    /* 전체 배경 및 폰트 설정 */
    .stApp {{
        background-color: {current_theme['bg_color']};
        color: {current_theme['text_color']};
    }}
    /* 카드 스타일 (KPI 박스) */
    .metric-card {{
        background: {current_theme['card_bg']};
        border: {current_theme['card_border']};
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        height: 200px; /* 높이 증가: 180px -> 200px */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    /* 헤더 텍스트 색상 강제 지정 (선택사항) */
    h1, h2, h3, h4, h5, h6, .stMarkdown, p {{
        color: {current_theme['text_color']} !important;
        margin: 0; /* 마진 초기화 */
    }}
    h2 {{
        font-size: 1.2rem !important;
        margin-bottom: 5px !important;
    }}
    h1 {{
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        font-size: 2.2rem !important; /* 폰트 사이즈 조정: 2.5rem -> 2.2rem */
    }}
    p {{
        font-size: 1.0rem !important;
        margin-top: 10px !important;
        font-weight: bold;
        opacity: 0.9;
    }}
    /* 버튼 스타일 */
    .stButton>button {{
        background: {current_theme['button_grad']};
        color: white;
        border-radius: 8px;
        border: none;
        height: 45px;
        width: 100%;
        font-weight: bold;
    }}
    /* Cyberpunk 폰트 etc 특수 처리 */
    {'body { font-family: "Courier New", Courier, monospace; }' if selected_theme_name == '사이버펑크 네온' else ''}
    </style>
""", unsafe_allow_html=True)

# === 2. 메인 타이틀 ===
st.title("🏢 기업 자산관리 솔루션 (EAM)")
st.markdown(f"### {selected_theme_name} 에디션")

# === 3. 데이터 가져오기 (API 호출) ===
try:
    response = requests.get(f"{API_URL}/assets/")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        # [데이터 전처리] 부서 정보 추출 (전역 사용을 위해 위로 이동)
        if not df.empty:
            df['dept'] = df['owner'].apply(lambda x: x.split()[0] if isinstance(x, str) and len(x.split()) > 0 else '공용/미배정')
            # 날짜 형변환 및 연차 계산
            df['purchase_date'] = pd.to_datetime(df['purchase_date'])
            df['years_old'] = (pd.Timestamp.now() - df['purchase_date']).dt.days / 365.0
    else:
        st.error("서버 연결 실패")
        df = pd.DataFrame()
except:
    st.error("백엔드 서버가 실행되지 않았습니다. (python main.py 실행 필요)")
    df = pd.DataFrame()

# === [고도화] 사이드바 - 글로벌 필터 및 AI 인사이트 ===
st.sidebar.markdown("---")
st.sidebar.title("🔍 검색 및 필터")

view_df = df.copy()
if not df.empty:
    # 1. 부서 필터
    dept_list = sorted(list(df['dept'].unique()))
    selected_depts = st.sidebar.multiselect("부서별 보기", dept_list, default=dept_list)
    
    # 2. 카테고리 필터
    cat_list = sorted(list(df['category'].unique()))
    selected_cats = st.sidebar.multiselect("카테고리별 보기", cat_list, default=cat_list)
    
    # 필터 적용
    if selected_depts:
        view_df = view_df[view_df['dept'].isin(selected_depts)]
    if selected_cats:
        view_df = view_df[view_df['category'].isin(selected_cats)]

# === 4. 대시보드 (KPI & Chart) ===
def format_currency(value):
    if value >= 100000000:  # 1억 이상
        return f"{value/100000000:.2f} 억원"
    elif value >= 10000:    # 1만 이상
        return f"{value/10000:,.0f} 만원"
    else:
        return f"{value:,.0f} 원"

# 상태별 색상 매핑
status_colors = {
    "정상": "#2ecc71",       # 초록 (Green)
    "수리중": "#f1c40f",     # 노랑 (Yellow)
    "반납(퇴사)": "#ffa726", # 주황 (Orange)
    "폐기": "#e74c3c",       # 빨강 (Red)
    "매각": "#9b59b6",       # 보라 (Purple)
    "분실": "#95a5a6"        # 회색 (Gray)
}

# [고도화] AI 인사이트 요약
if not view_df.empty:
    st.markdown("### 💡 AI Asset Insight")
    # 로직 기반 인사이트 생성
    top_val_dept = view_df.groupby('dept')['price'].sum().idxmax()
    old_assets_count = len(view_df[(view_df['years_old'] >= 3) & (view_df['status'] == '정상')])
    
    insight_text = f"""
    <div style="background-color: {current_theme['card_bg']}; padding: 15px; border-radius: 10px; border-left: 5px solid {current_theme['accent_color']}; margin-bottom: 20px;">
        <ul style="margin: 0; padding-left: 20px;">
            <li>현재 <b>{top_val_dept}</b>에서 가장 높은 자산 가치를 보유하고 있습니다.</li>
            <li>정상 자산 중 <b>{old_assets_count}개</b>가 구매한 지 3년이 경과하여 교체 검토가 필요합니다. (노후화 경고)</li>
            <li>전체 자산 중 수리/폐기 비율은 <b>{len(view_df[view_df['status'].isin(['수리중','폐기'])]) / len(view_df) * 100:.1f}%</b> 입니다.</li>
        </ul>
    </div>
    """
    st.markdown(insight_text, unsafe_allow_html=True)

if not view_df.empty:
    total_value_sum = view_df['price'].sum()
    formatted_total_value = format_currency(total_value_sum)
    
    col1, col2, col3, col4, col5 = st.columns(5) # 5개 컬럼으로 확장 (노후자산 추가)
    with col1:
        # 총 자산: 건수 + (총액)
        st.markdown(f"<div class='metric-card'><h2>📦 총 자산</h2><h1>{len(view_df)}개</h1><p>총 {formatted_total_value}</p></div>", unsafe_allow_html=True)
    with col2:
        # 총 가액: 금액 + (평균단가)
        avg_price = total_value_sum / len(view_df) if len(view_df) > 0 else 0
        formatted_avg = format_currency(avg_price)
        st.markdown(f"<div class='metric-card'><h2>💰 총 예산</h2><h1>{formatted_total_value}</h1><p>평균 {formatted_avg}</p></div>", unsafe_allow_html=True)
    with col3:
        repair_df = view_df[view_df['status'] == '수리중']
        repair_cnt = len(repair_df)
        repair_val = repair_df['price'].sum()
        formatted_repair_val = format_currency(repair_val)
        st.markdown(f"<div class='metric-card'><h2>🔧 수리 중</h2><h1 style='color:{status_colors['수리중']}'>{repair_cnt}건</h1><p>{formatted_repair_val}</p></div>", unsafe_allow_html=True)
    with col4:
        return_df = view_df[view_df['status'] == '반납(퇴사)']
        return_cnt = len(return_df)
        return_val = return_df['price'].sum()
        formatted_return_val = format_currency(return_val)
        st.markdown(f"<div class='metric-card'><h2>↩️ 반납(퇴사)</h2><h1 style='color:{status_colors['반납(퇴사)']}'>{return_cnt}건</h1><p>{formatted_return_val}</p></div>", unsafe_allow_html=True)
    with col5:
        # [신규] 교체 권장 (3년 이상 정상 자산)
        old_df = view_df[(view_df['years_old'] >= 3) & (view_df['status'] == '정상')]
        old_cnt = len(old_df)
        old_val = old_df['price'].sum()
        formatted_old_val = format_currency(old_val)
        st.markdown(f"<div class='metric-card'><h2>⚠️ 교체 권장</h2><h1 style='color:#e74c3c'>{old_cnt}건</h1><p>{formatted_old_val}</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # 차트 영역 (view_df 사용)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📊 카테고리별 자산 현황")
        fig = px.bar(view_df, x='category', y='price', color='status', 
                     title="자산 가치 분포", 
                     template=current_theme['plotly_template'],
                     color_discrete_map=status_colors)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("🍩 상태 비율")
        fig2 = px.pie(view_df, names='status', 
                      title="자산 상태 점유율", 
                      template=current_theme['plotly_template'], 
                      hole=0.4,
                      color='status',
                      color_discrete_map=status_colors)
        st.plotly_chart(fig2, use_container_width=True)

    # === [고도화] 부서별 분석 & 최신 등록 자산 ===
    st.markdown("---")
    st.subheader("📈 부서별 예산 관리 및 현황")
    
    # 부서 정보 (이미 전처리됨) - view_df 기준 집계
    dept_stats = view_df.groupby('dept')[['price', 'id']].agg({'price': 'sum', 'id': 'count'}).reset_index()
    dept_stats.columns = ['부서', '총자산액', '보유수량']
    dept_stats = dept_stats.sort_values(by='총자산액', ascending=False)
    
    dc1, dc2 = st.columns([1, 1])
    with dc1:
        st.markdown("##### 🏢 부서별 자산 규모 (금액)")
        fig_dept_val = px.treemap(dept_stats, path=['부서'], values='총자산액',
                                  title="부서별 예산 점유율 (Treemap)",
                                  template=current_theme['plotly_template'])
        st.plotly_chart(fig_dept_val, use_container_width=True)
        
    with dc2:
        st.markdown("##### 🔢 부서별 보유 수량")
        fig_dept_cnt = px.bar(dept_stats, x='부서', y='보유수량', 
                              title="부서별 자산 보유량",
                              template=current_theme['plotly_template'],
                              color='보유수량',
                              color_continuous_scale='Viridis') # Green tone
        st.plotly_chart(fig_dept_cnt, use_container_width=True)

    # 최신 등록 자산 목록
    st.markdown("#### 🆕 최근 최근 자산 (Top 5)")
    recent_df = view_df.sort_values(by='purchase_date', ascending=False).head(5)
    st.dataframe(recent_df[['asset_code', 'name', 'category', 'owner', 'purchase_date', 'status', 'price']], use_container_width=True, hide_index=True)

# === 5. 자산 등록 & 관리 탭 ===
tab1, tab2 = st.tabs(["📝 신규 자산 등록", "🔍 자산 조회 및 수정"])

with tab1:
    with st.form("add_asset_form"):
        col_new1, col_new2 = st.columns(2)
        with col_new1:
            asset_code = st.text_input("자산관리번호", placeholder="예: IT-24001")
            name = st.text_input("자산명", placeholder="예: MacBook Pro 16")
            category = st.selectbox("분류", ["IT기기", "가구", "소프트웨어", "차량", "기타"])
        with col_new2:
            owner = st.text_input("관리자/사용자", placeholder="예: 영업1팀 김철수")
            price = st.number_input("구매 가격 (원)", min_value=0, step=10000)
            p_date = st.date_input("구매일")
        
        submitted = st.form_submit_button("자산 등록하기")
        
        if submitted:
            if not asset_code:
                st.error("자산관리번호를 입력해주세요.")
            else:
                payload = {
                    "asset_code": asset_code,
                    "name": name, "category": category, "owner": owner,
                    "purchase_date": str(p_date), "price": price
                }
                res = requests.post(f"{API_URL}/assets/", json=payload)
                if res.status_code == 200:
                    st.success("✅ 자산이 성공적으로 등록되었습니다!")
                    st.rerun()
                else:
                    st.error("등록 실패")

with tab2:
    # === [고도화] 엑셀/CSV 다운로드 기능 ===
    st.markdown("#### 📂 데이터 내보내기 (필터 적용됨)")
    # 필터핑된 데이터(view_df)를 다운로드
    csv = view_df.to_csv(index=False).encode('utf-8-sig') # 한글 깨짐 방지 utf-8-sig
    st.download_button(
        label="📥 현재 목록 다운로드 (CSV)",
        data=csv,
        file_name='asset_list_filtered.csv',
        mime='text/csv',
    )
    st.markdown("---")

    # === 검색 기능 추가 ===
    st.markdown("#### 🔍 자산 검색")
    col_search1, col_search2 = st.columns([3, 1])
    with col_search1:
        search_query = st.text_input("검색어 입력 (자산관리번호, 사용자명)", placeholder="예: IT-23 또는 김철수")
    
    # 필터링 로직 (Global Filter + Search Query)
    filtered_df = view_df.copy() # Global Filter가 적용된 view_df 사용
    if search_query:
        # ID(관리번호)는 숫자로, Owner는 문자열로 검색
        filtered_df = filtered_df[
            filtered_df['asset_code'].str.contains(search_query, na=False) | 
            filtered_df['owner'].str.contains(search_query, na=False)
        ]
    
    st.info(f"검색 결과: 총 {len(filtered_df)}건")
    st.dataframe(filtered_df, use_container_width=True)

    # 간단한 상태 수정 기능
    st.markdown("#### 🛠 상태 변경 (검색된 자산 대상)")
    if not filtered_df.empty:
        col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
        with col_s1:
            # 검색된 목록 내에서 ID 선택
            # Display asset_code in selection if possible, currently using ID for backend
            # Make the selectbox show asset_code too
            filtered_df['display_label'] = filtered_df['id'].astype(str) + " | " + filtered_df['asset_code'] + " (" + filtered_df['name'] + ")"
            
            selected_label = st.selectbox("변경할 자산 선택 (ID | 관리번호 | 자산명)", filtered_df['display_label'].tolist())
            target_id = int(selected_label.split(" | ")[0])
            
        with col_s2:
            current_status = filtered_df[filtered_df['id'] == target_id]['status'].values[0]
            new_status = st.selectbox("변경할 상태", 
                                    ["정상", "수리중", "폐기", "매각", "분실", "반납(퇴사)"],
                                    index=["정상", "수리중", "폐기", "매각", "분실", "반납(퇴사)"].index(current_status) if current_status in ["정상", "수리중", "폐기", "매각", "분실", "반납(퇴사)"] else 0)
        with col_s3:
            st.write("") # 간격용
            st.write("") 
            if st.button("상태 업데이트"):
                res = requests.put(f"{API_URL}/assets/{target_id}/status?status={new_status}")
                if res.status_code == 200:
                    st.success("상태 변경 완료!")
                    st.rerun()
    else:
        st.warning("검색 결과가 없습니다.")