import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import qrcode
from io import BytesIO

# === 설정 ===
# 로컬 테스트 시에는 실행된 main.py 주소, 배포 시에는 자동으로 데모 모드로 전환됨
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Asset Master Pro X", layout="wide", page_icon="💎")

# === ✨ 고급 UI/UX (Premium Anti-Gravity & Glassmorphism) CSS ===
st.markdown("""
    <style>
    /* 1. Typography & Accessibility: Responsive fonts & High Contrast */
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
        color: #f1f5f9; /* Lighter text for better contrast on dark */
    }
    
    /* 2. Background: Deep Space Gradient */
    /* 2. Background: Lighter Deep Space Gradient */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #1e293b 0%, #0f172a 90%); /* Swapped for lighter top-left */
        background-attachment: fixed;
    }
    
    /* Add a subtle glow mesh */
    .stApp::before {
        content: "";
        position: absolute;
        top: -10%;
        left: -10%;
        width: 40%;
        height: 40%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.15), transparent 70%);
        filter: blur(80px);
        pointer-events: none;
        z-index: 0;
    }

    /* 3. Refined Glassmorphism 2.0 */
    .glass-card {
        background: rgba(255, 255, 255, 0.08); /* Increased Opacity (Brightened) */
        backdrop-filter: blur(24px); /* Stronger Blur */
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-top: 1px solid rgba(255, 255, 255, 0.25); /* Stronger highlight */
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        
        /* 4. Micro-interaction: Entry Animation */
        animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        transform: translateY(20px);
    }
    
    /* Staggered animation delay for cards would require JS or Nth-child, generic for now */
    
    /* 5. Micro-interaction: Hover Effects */
    .glass-card:hover {
        transform: translateY(-4px) scale(1.002);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        border-color: rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }

    @keyframes slideUpFade {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .kpi-title { 
        font-size: clamp(0.8rem, 2vw, 0.95rem); /* Responsive Font */
        color: #94a3b8; 
        font-weight: 600; 
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .kpi-value { 
        font-size: clamp(2rem, 4vw, 2.8rem); /* Responsive Font */
        font-weight: 800; 
        background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        margin-top: 8px;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# === 🔄 데이터 로드 함수 (하이브리드) ===
def load_data():
    try:
        # 1. API 연결 시도 (타임아웃 짧게 설정)
        response = requests.get(f"{API_URL}/assets/", timeout=1)
        if response.status_code == 200:
            return pd.DataFrame(response.json()), True # (데이터, 연결성공여부)
    except:
        pass
    
    # 2. API 연결 실패 시, 로컬 데이터 파일(local_data.csv) 확인
    try:
        df = pd.read_csv("local_data.csv")
        # Ensure 'status' column exists to prevent errors
        if 'status' not in df.columns:
            df['status'] = '정상'
        return df, False  # (데이터, 연결실패-로컬모드)
    except Exception:
        pass

    # 3. 파일도 없으면 데모 데이터 생성 (Mock Data)
    mock_data = [
        {"id": 1, "name": "MacBook Pro M3", "category": "IT Device", "status": "정상", "owner": "개발팀", "price": 3500000},
        {"id": 2, "name": "Dell Monitor 27", "category": "IT Device", "status": "정상", "owner": "디자인팀", "price": 450000},
        {"id": 3, "name": "Herman Miller Chair", "category": "Furniture", "status": "수리중", "owner": "임원실", "price": 2100000},
        {"id": 4, "name": "Genesis G80", "category": "Vehicle", "status": "정상", "owner": "법인차량", "price": 65000000},
        {"id": 5, "name": "MS Office License", "category": "Software", "status": "정상", "owner": "전사", "price": 150000},
        {"id": 6, "name": "iPad Pro 12.9", "category": "IT Device", "status": "분실", "owner": "영업1팀", "price": 1200000},
    ]
    return pd.DataFrame(mock_data), False

# 데이터 로딩
    return pd.DataFrame(mock_data), False

# 데이터 로딩
raw_df, is_connected = load_data()

# === 🎨 디자인 시스템 & 헬퍼 ===
COLOR_MAP = {
    '정상': '#3b82f6',    # Blue (Active)
    '수리중': '#ef4444',  # Red (Repair)
    '폐기': '#94a3b8',    # Slate (Disicarded)
    '분실': '#f59e0b',    # Amber (Lost)
    '반납(퇴사)': '#6366f1', # Indigo (Returned)
    '보관중': '#10b981',   # Emerald (In Storage/Idle)
    '임시저장': '#d1d5db'  # Gray (Draft)
}

# 헬퍼: 활성 자산 vs 임시저장 분리
def split_active_draft(df):
    if df.empty: return pd.DataFrame(), pd.DataFrame()
    drafts = df[df['status'] == '임시저장']
    active = df[df['status'] != '임시저장']
    return active, drafts

active_df, draft_df = split_active_draft(raw_df)

def format_korean_currency(value):
    if value >= 100000000:
        val = value/100000000
        return f"{val:.1f}억"
    elif value >= 10000:
        val = value/10000
        # 소수점 1자리까지 표시하되, .0이면 제거
        formatted = f"{val:.1f}"
        return f"{formatted.replace('.0', '')}만"
    else:
        return f"{value:,}"

# === 🧠 AI Insight Engine (Rule-Based) ===
def generate_insights(df):
    insights = []
    if df.empty: return ["데이터가 없습니다."]
    
    # 1. 고가 자산 경고
    expensive = df[df['price'] >= 5000000]
    if not expensive.empty:
        insights.append(f"💰 **고가 자산 집중**: 500만원 이상 자산이 {len(expensive)}개 감지되었습니다. (총 {format_korean_currency(expensive['price'].sum())})")
    
    # 2. 상태 불량 비율
    issue_ratio = len(df[df['status'] != '정상']) / len(df)
    if issue_ratio > 0.3:
        insights.append(f"⚠️ **자산 건전성 경고**: 비정상 자산 비율이 {issue_ratio*100:.1f}%로 높습니다. 점검이 필요합니다.")
    # 2. 상태 불량 비율
    issue_ratio = len(df[df['status'] != '정상']) / len(df)
    if issue_ratio > 0.3:
        insights.append(f"⚠️ **자산 건전성 경고**: 비정상 자산 비율이 {issue_ratio*100:.1f}%로 높습니다. 점검이 필요합니다.")
    elif issue_ratio > 0.1:
        insights.append(f"👀 **관심 필요**: 비정상 자산 비율이 {issue_ratio*100:.1f}%입니다.")
    
    if not insights:
        insights.append("✅ **특이사항 없음**: 현재 자산 상태가 양호합니다.")
        
    return insights

# === 🚀 메인 화면 ===

# 사이드바
# 사이드바 (Global Filter)
# 사이드바 (Global Filter)
# 사이드바 (Global Filter)
with st.sidebar:
    st.markdown("<h2 style='animation: slideUpFade 0.5s ease-out;'>통합 관리 콘솔</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🔍 통합 필터 (Global Filters)")
    # 필터 데이터 준비 (전체 데이터 기준)
    all_owners = sorted(active_df['owner'].unique()) if not active_df.empty else []
    all_cats = sorted(active_df['category'].unique()) if not active_df.empty else []
    
    sel_owners = st.multiselect("소유 부서/팀 (Department)", all_owners, default=all_owners)
    sel_cats = st.multiselect("자산 유형 (Category)", all_cats, default=all_cats)
    
    # 필터링 적용 (활성 자산만 필터링)
    if not active_df.empty:
        df = active_df[
            (active_df['owner'].isin(sel_owners)) & 
            (active_df['category'].isin(sel_cats))
        ]
    else:
        df = active_df
    
    st.markdown("---")
    
    if is_connected:
        st.success("🟢 실시간 서버 연결됨")
    else:
        st.warning("🟠 로컬 데이터 모드 (Deployment Mode)")
        st.caption("서버 연결 안 됨 (export된 로컬 데이터 표시 중)")
    
    st.markdown("---")
    st.caption("© 2026 Asset Master Pro X | ver 2.0")

# 상단 헤더
c1, c2 = st.columns([3, 1])
with c1: st.title("전사 자산 종합 현황판")
with c2: st.markdown(f"<div style='text-align:right; padding-top:20px; color:#94a3b8;'>총 관리 자산: {len(df)} 건</div>", unsafe_allow_html=True)

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📊 운영 지표 분석", "💎 자산 관리/운영", "⚡ 빠른 등록"])

# [TAB 1] 분석
with tab1:
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        kpis = [
            ("총 보유 자산 (TOTAL ASSETS)", f"{len(df)}", "EA", "+12 vs last month"),
            ("총 자산 가치 (TOTAL VALUE)", f"{format_korean_currency(df['price'].sum())}", "KRW", "+5% vs last month"),
            ("정상 가동률 (ACTIVE RATIO)", f"{len(df[df['status']=='정상'])/len(df)*100:.0f}%", "Health", "-2% vs last month"),
            ("관리 필요 (ISSUES)", f"{len(df[df['status']!='정상'])}", "Alerts", "+1 new alert")
        ]
        for i, (title, value, unit, trend) in enumerate(kpis):
            with [col1, col2, col3, col4][i]:
                trend_color = "#10b981" if "+" in trend else "#ef4444"
                st.markdown(f"""
                    <div class='glass-card'>
                        <div class='kpi-title'>{title}</div>
                        <div class='kpi-value'>{value} <span style='font-size:1rem; color:#64748b;'>{unit}</span></div>
                        <div style='font-size:0.8rem; color:{trend_color}; margin-top:5px;'>{trend}</div>
                    </div>
                """, unsafe_allow_html=True)

        # AI Insight 섹션
        st.markdown("### 🤖 PM's AI 자산 분석 인사이트")
        insights = generate_insights(df)
        for insight in insights:
            st.info(insight, icon="🤖")

        # 차트
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### 🗺️ 자산 계층 구조 (Treemap)")
            # Treemap: 공간 효율적이고 계층 구조 파악에 용이함 (Best Practice #3)
            fig = px.treemap(df, path=[px.Constant("All Assets"), 'category', 'status', 'name'], values='price',
                              color='status', color_discrete_map=COLOR_MAP,
                              template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, l=0, r=0, b=0))
            fig.update_traces(root_color="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.markdown("### 📊 유형별 자산 가치 상위 (Bar Chart)")
            # Horizontal Bar Chart: 항목 간 비교가 원형 차트보다 훨씬 명확함 (Best Practice #3)
            cat_sum = df.groupby('category')['price'].sum().reset_index().sort_values('price', ascending=True)
            fig2 = px.bar(cat_sum, x='price', y='category', orientation='h', 
                          text_auto='.2s', color='category', 
                          template="plotly_dark")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", 
                               plot_bgcolor="rgba(0,0,0,0)",
                               showlegend=False,
                               margin=dict(t=0, l=0, r=0, b=0),
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=False))
            st.plotly_chart(fig2, use_container_width=True)

# [TAB 2] 상세 관리
with tab2:
    col_list, col_detail = st.columns([1.5, 1])
    with col_list:
        st.markdown("### 📋 전체 자산 리스트")
        st.dataframe(df[['name', 'category', 'status', 'owner', 'price']], use_container_width=True)
    
    with col_detail:
        st.markdown("### 🔍 상세 정보 및 액션")
        if not df.empty:
            # 인덱스 초기화 이슈 방지를 위해 리스트로 변환
            sel_idx = st.selectbox("자산 선택", df.index)
            item = df.loc[sel_idx]
            
            # --- 상세 카드 표시 ---
            st.markdown(f"""
                <div class='glass-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <h2 style='color:#38bdf8; margin:0;'>{item['name']}</h2>
                        <span style='background:{COLOR_MAP.get(item['status'], '#fff')}; padding:4px 8px; border-radius:12px; font-size:0.8rem; height:fit-content;'>{item['status']}</span>
                    </div>
                    <p style='margin-top:10px; color:#cbd5e1;'>{item['category']} | {item['owner'] if item['owner'] else '미지정 (공용/창고)'}</p>
                    <p style='font-size:1.2rem; font-weight:bold;'>{format_korean_currency(item['price'])} KRW</p>
                    <p style='font-size:0.8rem; color:#64748b;'>ID: {item['id']} | Purchased: {item.get('purchase_date', '-')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # --- 액션 패널 ---
            with st.expander("🛠️ 자산 관리 액션 (Lifecycle Actions)", expanded=True):
                # 1. 상태 변경
                new_stat = st.selectbox("상태 변경", ["정상", "수리중", "보관중", "폐기", "분실"], index=0 if item['status'] not in ["정상", "수리중", "보관중", "폐기", "분실"] else ["정상", "수리중", "보관중", "폐기", "분실"].index(item['status']))
                if st.button("상태 업데이트", key="btn_update_status"):
                    if is_connected: # API Call logic same as before but generalized
                         requests.put(f"{API_URL}/assets/{item['id']}/status?status={new_stat}")
                         st.toast("✅ 상태가 업데이트 되었습니다.")
                         st.rerun()

                st.markdown("---")
                # 2. 반납 (Return) - 즉시 보관 처리
                if st.button("↩️ 반납 처리 (Return Asset)"):
                    if is_connected:
                        requests.put(f"{API_URL}/assets/{item['id']}/status?status=보관중")
                        st.toast(f"✅ {item['name']} 자산이 반납(보관중) 처리되었습니다.")
                        st.rerun()
                
                # 3. 수정 (Edit) - Form
                with st.popover("✏️ 정보 수정 (Edit Info)"):
                    st.markdown("#### 자산 정보 수정")
                    edit_name = st.text_input("자산명", value=item['name'])
                    edit_cat = st.selectbox("분류", ["IT Device", "Furniture", "Vehicle", "Software", "Others"], index=0) # Index logic omitted for brevity
                    edit_owner = st.text_input("소유자/팀", value=item['owner'])
                    edit_price = st.number_input("가격", value=item['price'])
                    if st.button("저장 (Save Changes)"):
                         # Update logic call via PUT /assets/{id}
                         # Mock payload construction
                         payload = {
                             "asset_code": item.get('asset_code', 'UNKNOWN'),
                             "name": edit_name,
                             "category": edit_cat,
                             "owner": edit_owner,
                             "purchase_date": "2024-01-01", # Validate date
                             "price": edit_price
                         }
                         if is_connected:
                             requests.put(f"{API_URL}/assets/{item['id']}", json=payload)
                             st.toast("✅ 정보가 수정되었습니다.")
                             st.rerun()

                st.markdown("---")
                # 4. 삭제 (Delete)
                if st.button("🗑️ 자산 삭제 (Delete)", type="primary"):
                    if is_connected:
                        requests.delete(f"{API_URL}/assets/{item['id']}")
                        st.toast("🗑️ 자산이 삭제되었습니다.")
                        st.rerun()


# [TAB 3] 등록 및 임시보관함
with tab3:
    t1, t2 = st.tabs(["신규 등록", "📂 임시 보관함 (Drafts)"])
    
    with t1:
        st.subheader("➕ 신규 자산 등록")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("자산명 (Asset Name)")
            cat = c1.selectbox("분류 (Category)", ["IT Device", "Furniture", "Vehicle", "Software", "Others"])
            owner = c2.text_input("소유자/팀 (Owner)")
            price = c2.number_input("가격 (Price)", step=10000)
            
            # Action Buttons
            col_a, col_b = st.columns(2)
            submit_draft = col_a.form_submit_button("📂 임시 저장 (Save Draft)")
            submit_final = col_b.form_submit_button("🚀 등록 완료 (Register)")
            
            if submit_final or submit_draft:
                status = "임시저장" if submit_draft else "정상"
                payload = {
                    "asset_code": f"TEMP-{pd.Timestamp.now().strftime('%H%M%S')}",
                    "name": name,
                    "category": cat,
                    "owner": owner,
                    "purchase_date": str(pd.Timestamp.now().date()),
                    "price": int(price)
                }
                
                if is_connected:
                    # Create Asset logic
                    res = requests.post(f"{API_URL}/assets/", json=payload)
                    # If it's a draft, we might need to update status immediately if Backend defaults to 'Normal'
                    if res.status_code == 200:
                        new_id = res.json()['id']
                        if status == '임시저장':
                            requests.put(f"{API_URL}/assets/{new_id}/status?status=임시저장")
                        st.success(f"{'임시 저장' if submit_draft else '등록'} 완료!")
                        st.rerun()
    
    with t2:
        st.subheader(f"📂 임시 보관함 ({len(draft_df)})")
        if not draft_df.empty:
            for idx, row in draft_df.iterrows():
                with st.expander(f"{row['name']} ({row['category']})"):
                    st.write(f"가격: {format_korean_currency(row['price'])}")
                    if st.button("🚀 정식 등록 (Publish)", key=f"pub_{row['id']}"):
                        if is_connected:
                            requests.put(f"{API_URL}/assets/{row['id']}/status?status=정상")
                            st.toast("✅ 정식 자산으로 등록되었습니다.")
                            st.rerun()
        else:
            st.info("임시 저장된 자산이 없습니다.")
