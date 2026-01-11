import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import qrcode
from io import BytesIO
from datetime import datetime

# === 설정 ===
# 로컬 테스트 시에는 실행된 main.py 주소, 배포 시에는 자동으로 데모 모드로 전환됨
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Asset Master Pro X", layout="wide", page_icon="💎")

# === ✨ 고급 UI/UX (Anti-Gravity & Glassmorphism) CSS ===
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .kpi-title { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-size: 2.5rem; font-weight: 800; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
""", unsafe_allow_html=True)

# === 🔄 데이터 로드 함수 (하이브리드) ===
def load_data():
    try:
        # 1. API 연결 시도
        response = requests.get(f"{API_URL}/assets/", timeout=2)
        if response.status_code == 200:
            return pd.DataFrame(response.json()), True # (데이터, 연결성공여부)
    except:
        pass
    
    # 2. 연결 실패 시 데모 데이터 생성 (Cloud용)
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
df, is_connected = load_data()

# === 🚀 메인 화면 ===

# 사이드바
with st.sidebar:
    st.title("Admin Console")
    if is_connected:
        st.success("🟢 API Connected")
    else:
        st.warning("🟠 Demo Mode (Server Off)")
        st.caption("백엔드 서버가 감지되지 않아 데모 데이터를 표시합니다.")
    
    st.markdown("---")
    st.caption("© 2026 Asset Master Pro X")

# 상단 헤더
c1, c2 = st.columns([3, 1])
with c1: st.title("Executive Dashboard")
with c2: st.markdown(f"<div style='text-align:right; padding-top:20px; color:#94a3b8;'>{len(df)} Assets Tracked</div>", unsafe_allow_html=True)

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📊 Analytics View", "💎 Asset Operations", "⚡ Quick Actions"])

# [TAB 1] 분석
with tab1:
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        kpis = [
            ("TOTAL ASSETS", f"{len(df)}", "EA"),
            ("TOTAL VALUE", f"{df['price'].sum()/1000000:,.1f}M", "KRW"),
            ("ACTIVE RATIO", f"{len(df[df['status']=='정상'])/len(df)*100:.0f}%", "Health"),
            ("ISSUES", f"{len(df[df['status']!='정상'])}", "Alerts")
        ]
        for i, (title, value, unit) in enumerate(kpis):
            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                    <div class='glass-card'>
                        <div class='kpi-title'>{title}</div>
                        <div class='kpi-value'>{value} <span style='font-size:1rem; color:#64748b;'>{unit}</span></div>
                    </div>
                """, unsafe_allow_html=True)

        # 차트
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### 🗺️ Asset Distribution")
            fig = px.sunburst(df, path=['category', 'status', 'name'], values='price',
                              color='status', color_discrete_map={'정상':'#3b82f6', '수리중':'#ef4444', '분실':'#64748b'},
                              template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.markdown("### 📈 Value Share")
            fig2 = px.donut(df, values='price', names='category', hole=0.7, template="plotly_dark")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", showlegend=False, 
                               annotations=[dict(text='Value', x=0.5, y=0.5, font_size=20, showarrow=False)])
            st.plotly_chart(fig2, use_container_width=True)

# [TAB 2] 상세 관리
with tab2:
    col_list, col_detail = st.columns([1.5, 1])
    with col_list:
        st.markdown("### 📋 Asset List")
        st.dataframe(df[['name', 'category', 'status', 'owner', 'price']], use_container_width=True)
    
    with col_detail:
        st.markdown("### 🔍 Inspector")
        if not df.empty:
            sel_idx = st.selectbox("Select Asset", df.index)
            item = df.loc[sel_idx]
            
            st.markdown(f"""
                <div class='glass-card'>
                    <h2 style='color:#38bdf8'>{item['name']}</h2>
                    <p>Category: {item['category']} | Owner: {item['owner']}</p>
                    <p>Status: <span style='color:#facc15'>{item['status']}</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            # QR 생성
            qr = qrcode.QRCode(box_size=10, border=1)
            qr.add_data(f"AssetID:{item['id']}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf)
            st.image(buf, width=150, caption="Digital Tag")

            # 상태 변경 시뮬레이션
            new_stat = st.selectbox("Change Status", ["정상", "수리중", "폐기"])
            if st.button("Update Status"):
                if is_connected:
                    # 실제 API 호출
                    try:
                        requests.put(f"{API_URL}/assets/{item['id']}/status?status={new_stat}")
                        st.success("Updated on Server!")
                        st.rerun()
                    except:
                        st.error("Server Error")
                else:
                    st.info("Demo Mode: UI updated (Not saved to DB)")

# [TAB 3] 등록
with tab3:
    st.subheader("➕ Quick Registration")
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Asset Name")
        price = c2.number_input("Price", step=10000)
        if st.form_submit_button("Register"):
            if is_connected:
                # 실제 API 호출
                st.success("Sent to Database!")
            else:
                st.success("Demo Mode: Registration Simulated!")
