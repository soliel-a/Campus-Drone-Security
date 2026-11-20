import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point, Polygon
import os

st.set_page_config(page_title="校园低空安全预警", layout="wide")

st.title("🚁 校园低空危险源智能预警系统")
st.markdown("**当前模式：** 模拟数据演示 (ESP32 硬件待接入)")

# 页面分成左右两列
col_left, col_right = st.columns([2, 1])

# 左侧：地图
with col_left:
    st.subheader("🗺️ 实时空域监控地图")
    # 默认地图中心点（假设是青科大）
    m = folium.Map(location=[36.001, 120.101], zoom_start=16)

    # 在地图上画出操场人群密集区
    playground_coords = [
        [36.000, 120.100], [36.000, 120.102],
        [36.002, 120.102], [36.002, 120.100]
    ]
    folium.Polygon(
        locations=playground_coords,
        color="orange", fill=True, fill_color="orange", fill_opacity=0.3,
        popup="操场人群密集区"
    ).add_to(m)

    # 在地图上标出无人机
    # 合法无人机（绿点）
    folium.Marker(
        [36.003, 120.103],
        popup="合法: 1581F_LEGAL_001",
        icon=folium.Icon(color="green", icon="plane")
    ).add_to(m)

    # 黑飞无人机（红点）
    folium.Marker(
        [36.001, 120.101],
        popup="黑飞: BLACK_DRONE_999 (人群密集区危险)",
        icon=folium.Icon(color="red", icon="warning-sign")
    ).add_to(m)

    # 渲染地图
    st_folium(m, width="100%", height=400, returned_objects=[])

# 右侧：业务逻辑判定
with col_right:
    st.subheader("📡 监控报警与处理")

    mock_drones = [
        {"serial": "1581F_LEGAL_001", "lat": 36.003, "lon": 120.103, "alt": 100},
        {"serial": "BLACK_DRONE_999", "lat": 36.001, "lon": 120.101, "alt": 30}
    ]

    for data in mock_drones:
        sn = data["serial"]
        is_legal = (sn == "1581F_LEGAL_001")
        in_playground = (data["lat"] >= 36.000 and data["lat"] <= 36.002 and
                         data["lon"] >= 120.100 and data["lon"] <= 120.102)

        if is_legal:
            st.success(f"✅ 报备机: {sn} | 高度: {data['alt']}米")
        else:
            st.error(f"🚨 黑飞机: {sn} | 高度: {data['alt']}米")
            if in_playground:
                st.warning("⚠️ 警报：闯入操场人群密集区！建议立刻驱离！")

st.divider()

# 底部：YOLO 模型推理接口
st.subheader("🧠 射频频谱图 AI 识别 (YOLO 补盲)")
st.write("当黑飞无人机不报备（不发送Remote ID）时，通过侦测电磁波频谱图发现目标。")
uploaded_file = st.file_uploader("上传一张射频频谱图 (.png / .jpg)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="上传的频谱图", width=300)
    st.info("⏳ 模拟推理中：YOLO 模型已识别到目标...")
    # 这里未来接入你的 best.pt 模型进行推理
    st.success("🎯 识别结果：发现无人机 (Drone) 信号，置信度 85.5%")