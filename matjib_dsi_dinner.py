import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import time

# 1. Kakao API Key 하드코딩
API_KEY = "3954ac5e45b2aacab5d7158785e8c349"

st.set_page_config(layout="wide")
st.title("대전세종연구원_맛집_저녁회식")

# 2. CSV 불러오기 (파일명 고정)
@st.cache_data
def load_data():
    return pd.read_csv("place_map_template.csv", encoding='cp949')

# 3. Kakao 지오코딩 함수
def get_coordinates(address, api_key):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=3)
        if resp.status_code == 200:
            result = resp.json()
            if result['documents']:
                x = float(result['documents'][0]['x'])
                y = float(result['documents'][0]['y'])
                return x, y
        return None, None
    except:
        return None, None

# 4. 데이터 준비
data = load_data()
st.write("시설 목록 미리보기", data.head())

# 5. 좌표 컬럼 없으면 Kakao 지오코딩 (최초 1회만)
if not all(col in data.columns for col in ["x", "y"]):
    xs, ys = [], []
    with st.spinner("주소를 좌표로 변환 중입니다... (최대 0.2초/건)"):
        for addr in data['address']:
            x, y = get_coordinates(addr, API_KEY)
            xs.append(x)
            ys.append(y)
            time.sleep(0.2)
    data["x"] = xs
    data["y"] = ys

# 6. folium 지도 그리기
m = folium.Map(location=[36.3504, 127.3845], zoom_start=12)

for _, row in data.iterrows():
    if pd.notnull(row["x"]) and pd.notnull(row["y"]):
        facility_name = str(row.get("name", "이름 없음"))
        # (1) 기본 마커 + (2) 항상 보이는 텍스트 레이블 추가
        folium.Marker(
            location=[row["y"], row["x"]],
            icon=folium.Icon(color='red', icon='cutlery', prefix='fa'),  # 마커모양(원하면 'info-sign' 등 가능)
        ).add_to(m)
        # 이름을 항상 지도에 표시 (DivIcon)
        folium.map.Marker(
            [row["y"], row["x"]],
            icon=folium.DivIcon(html=f"""<div style="font-size: 13px; color: black; background: rgba(255,255,255,0.8); padding: 2px 4px; border-radius: 5px; border:1px solid #ddd; display:inline-block;">{facility_name}</div>""")
        ).add_to(m)

st_folium(m, width=1200, height=700)

# 7. 좌표 포함 CSV 다운로드 버튼
csv_out = data.to_csv(index=False, encoding="utf-8-sig")
st.download_button("좌표 포함 CSV 다운로드", csv_out, "result.csv", "text/csv")

st.markdown("---")
st.caption("powered by Streamlit, folium, Kakao API")
