import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import time

st.set_page_config(layout="wide")
st.title("대전세종연구원_맛집_저녁회식")

# --- CSV 파일 불러오기 ---
@st.cache_data
def load_data():
    return pd.read_csv("place_map_template.csv", encoding='cp949')

# --- Kakao 주소 지오코딩 함수 ---
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

# --- 데이터 불러오기 ---
data = load_data()
st.write("시설 목록 미리보기", data.head())

# --- API KEY 입력창 ---
api_key = st.sidebar.text_input("Kakao REST API KEY 입력", type='password')
if api_key:
    # 좌표 컬럼 없는 경우만 지오코딩
    if not all(col in data.columns for col in ["x", "y"]):
        xs, ys = [], []
        with st.spinner("주소를 좌표로 변환 중입니다... (최대 0.2초/건)"):
            for addr in data['address']:
                x, y = get_coordinates(addr, api_key)
                xs.append(x)
                ys.append(y)
                time.sleep(0.2)
        data["x"] = xs
        data["y"] = ys

    # 지도 생성
    m = folium.Map(location=[36.3504, 127.3845], zoom_start=12)
    for _, row in data.iterrows():
        if pd.notnull(row["x"]) and pd.notnull(row["y"]):
            folium.Marker(
                location=[row["y"], row["x"]],
                popup=row.get("name", "이름 없음"),
                tooltip=row.get("name", "이름 없음")
            ).add_to(m)
    st_folium(m, width=1200, height=700)

    # 좌표 포함 CSV 다운로드
    csv_out = data.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("좌표 포함 CSV 다운로드", csv_out, "result.csv", "text/csv")
else:
    st.info("우측 사이드바에 Kakao REST API KEY를 입력하세요. (https://developers.kakao.com/)")

st.markdown("---")
st.caption("powered by Streamlit, folium, Kakao API")
