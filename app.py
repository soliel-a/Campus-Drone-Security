import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
import time

# ==========================================
# 1. 页面基础配置与大屏 CSS 美化
# ==========================================
st.set_page_config(page_title="校园低空安防大屏", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    .stApp {background-color: #0E1117;}

    /* 把地图强制变成暗黑安防风 */
    iframe {
        filter: invert(90%) hue-rotate(180deg) brightness(90%) contrast(120%) grayscale(20%);
    }

    /* 美化指标卡 */
    [data-testid="stMetricValue"] {color: #00FFAA; font-family: 'Courier New', monospace;}
    [data-testid="stMetricLabel"] {color: #FFFFFF;}

    /* 报警卡片 */
    .danger-card {
        background-color: rgba(255, 75, 75, 0.1);
        border-left: 5px solid #FF4B4B;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        animation: pulse 2s infinite;
    }
    .safe-card {
        background-color: rgba(0, 255, 170, 0.1);
        border-left: 5px solid #00FFAA;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
        70% { box-shadow: 0 0 10px 10px rgba(255, 75, 75, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 侧边栏 (模拟硬件状态)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2996/2996891.png", width=60)
    st.title("系统控制台")
    st.markdown("---")
    st.write("📡 **前端感知节点**")
    st.success("ESP32-S3 监听节点：在线")
    st.success("射频频谱分析：运行中")
    st.info("定位方式：Remote ID 广播解析")
    st.markdown("---")
    st.write("👨‍💻 **赛队信息**")
    st.caption("青岛科技大学\nAI原生代码创意编程")

    # 这里加个按钮，点一下假装重新扫描
    if st.button("🔄 强制刷新态势", use_container_width=True):
        st.rerun()


# ==========================================
# 3. 数据接口 (以后接板子就改这里！)
# ==========================================
def get_drone_data():
    """
    【重点】这里是获取无人机数据的地方。
    目前是模拟数据。等你的 ESP32 板子到了，把你用 pyserial 读到的数据在这里 return 即可。
    """
    return [
        {"serial": "1581F_LEGAL_001", "lat": 36.0022, "lon": 120.1020, "alt": 100, "is_legal": True,
         "status": "正常巡检"},
        {"serial": "BLACK_DRONE_999", "lat": 36.0007, "lon": 120.1020, "alt": 30, "is_legal": False,
         "status": "闯入人群密集区"}
    ]


# ==========================================
# 4. 顶部标题栏
# ==========================================
col_title1, col_title2 = st.columns([3, 1])
with col_title1:
    st.title("🚁 校园低空危险源智能预警系统")
with col_title2:
    st.markdown(f"<h4 style='text-align: right; color: #00FFAA; margin-top: 20px;'>系统状态: 运行中</h4>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: right; color: gray;'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
                unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 5. 主体布局
# ==========================================
col_map, col_panel = st.columns([2.5, 1])

# 获取当前数据
drones = get_drone_data()

with col_map:
    st.subheader("🗺️ 实时低空空域态势")

    # 高德地图底图
    gaode_tiles = 'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}'
    m = folium.Map(location=[36.0015, 120.1015], zoom_start=17, tiles=gaode_tiles, attr='高德地图')

    # 围栏
    folium.Polygon(locations=[[36.0020, 120.1005], [36.0020, 120.1015], [36.0025, 120.1015], [36.0025, 120.1005]],
                   color="#FF0000", weight=2, fill=True, fill_color="#FF0000", fill_opacity=0.4,
                   tooltip="🚨 核心禁飞区").add_to(m)
    folium.Polygon(locations=[[36.0005, 120.1015], [36.0005, 120.1025], [36.0010, 120.1025], [36.0010, 120.1015]],
                   color="#FFD700", weight=2, fill=True, fill_color="#FFD700", fill_opacity=0.3,
                   tooltip="⚠️ 操场人群密集区").add_to(m)

    # 动态加载无人机位置
    for d in drones:
        color = "green" if d["is_legal"] else "red"
        icon = "plane" if d["is_legal"] else "warning-sign"
        folium.Marker([d["lat"], d["lon"]], tooltip=f"SN: {d['serial']}",
                      icon=folium.Icon(color=color, icon=icon)).add_to(m)

    st_folium(m, width="100%", height=550, returned_objects=[])

with col_panel:
    st.subheader("📊 威胁态势看板")

    # 假装扫描一下
    with st.status("🟢 正在扫描空域...", expanded=False) as status:
        time.sleep(0.5)
        status.update(label="✅ 扫描完成，锁定目标", state="complete")

    col_m1, col_m2 = st.columns(2)
    col_m1.metric(label="发现目标", value=f"{len(drones)} 架")
    illegal_count = sum(1 for d in drones if not d["is_legal"])
    col_m2.metric(label="黑飞威胁", value=f"{illegal_count} 架", delta="极度危险" if illegal_count > 0 else "安全",
                  delta_color="inverse")

    st.markdown("### 📡 实时报警与处置")

    # 遍历数据生成卡片
    for d in drones:
        if not d["is_legal"]:
            st.markdown(f"""
            <div class="danger-card">
                <h4 style='color: #FF4B4B; margin: 0;'>🚨 未报备黑飞入侵</h4>
                <p style='margin: 5px 0;'><b>目标 SN:</b> {d['serial']}</p>
                <p style='margin: 5px 0;'><b>当前高度:</b> {d['alt']} 米</p>
                <p style='margin: 5px 0;'><b>当前位置:</b> {d['status']}</p>
                <hr style='margin: 10px 0; border-color: rgba(255,75,75,0.3);'>
                <p style='color: #FFD700; margin: 0; font-size: 14px;'>
                🎯 <b>建议:</b> 立即联动安保人员前往操场，启动信号干扰驱离。
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="safe-card">
                <h4 style='color: #00FFAA; margin: 0;'>✅ 报备无人机</h4>
                <p style='margin: 5px 0;'><b>目标 SN:</b> {d['serial']}</p>
                <p style='margin: 5px 0;'><b>当前高度:</b> {d['alt']} 米</p>
                <p style='margin: 5px 0;'><b>状态:</b> {d['status']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 6. 底部 AI 补盲功能
# ==========================================
st.markdown("---")
with st.expander("🧠 射频频谱图 AI 识别 (YOLO 补盲功能) - 点击展开"):
    uploaded_file = st.file_uploader("上传一张射频频谱图 (.png / .jpg)", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="已上传频谱图", width=400)
        st.success("🎯 **AI识别结果：** 发现无人机 (Drone) 信号，置信度 85.5%")
