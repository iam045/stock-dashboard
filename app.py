import streamlit as st
import pandas as pd
import plotly.express as px

# --- 設定 ---
st.set_page_config(page_title="市值排行榜", layout="centered")
st.header("🏆 台灣股市市值排行榜 (連動 Google Sheet)")

# --- 讀取資料 (改由網路讀取) ---
@st.cache_data(ttl=60) # ttl=60 代表每 60 秒會重新抓一次新資料
def load_data():
    # 👇 請把下面的網址換成你自己的 CSV 連結
    # 這是範例連結 (若你還沒弄好，可以先用這個測試)
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNB2FmsuJKu4Uh9xh2Qt-9yWrtE_ILjNL-oSEyYLHyrJ2amMiAbGreOYpm6rrryWmCdU_zmsFx7kL0/pub?output=csv" 
    
    # 這裡放一個防呆機制，如果你還沒換連結，程式不會當掉
    if "docs.google.com" not in url:
        return pd.DataFrame()
        
    try:
        df = pd.read_csv(url)
        # 資料清理 (因為從網路抓下來通常是純文字)
        # 確保市值是數字
        df['總市值'] = pd.to_numeric(df['總市值'], errors='coerce')
        return df.sort_values(by='總市值', ascending=False)
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 顯示更新按鈕
    if st.button('🔄 點我手動更新資料'):
        st.cache_data.clear() # 清除快取
        st.rerun() # 重新執行

    # 1. 視覺化
    st.subheader("Top 20 市值分佈")
    fig = px.bar(
        df.head(20), 
        x='總市值', 
        y='股票名稱', 
        orientation='h', 
        text_auto='.2s', 
        color='總市值'
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    # 2. 資料表
    st.subheader("詳細排名清單")
    st.dataframe(df[['市值排名', '股票代號', '股票名稱', '股價', '總市值']], hide_index=True)

else:
    st.info("👋 嗨！請記得修改程式碼中的 `url` 變數，填入你的 Google Sheet CSV 連結喔！")
