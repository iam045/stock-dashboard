import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 網頁基礎設定 ---
st.set_page_config(page_title="台股市值戰情室", layout="centered")

# --- 2. 顯示今日日期與標題 ---
# 取得今天是星期幾 (0=週一, 6=週日)
week_days = ["一", "二", "三", "四", "五", "六", "日"]
today = datetime.now()
date_str = today.strftime("%Y-%m-%d")
week_day_str = week_days[today.weekday()]

st.title(f"📅 {date_str} (週{week_day_str})")
st.header("🏆 台股市值排行榜 Top 150")
st.caption("資料來源：Google Sheet 自動連線 | 每 60 秒更新")

# --- 3. 讀取與處理資料 ---
@st.cache_data(ttl=60) # 設定快取 60 秒，避免頻繁讀取卡住
def load_data():
    # 👇 請記得將此網址換成你自己的 Google Sheet CSV 連結
    # 這裡我先放一個測試用的連結，確保你現在執行看得到畫面
    # 實際上線時，請把下面這行換成： url = "你的_CSV_連結"
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNB2FmsuJKu4Uh9xh2Qt-9yWrtE_ILjNL-oSEyYLHyrJ2amMiAbGreOYpm6rrryWmCdU_zmsFx7kL0/pub?gid=0&single=true&output=csv"
    
    try:
        df = pd.read_csv(url)
        
        # 強制轉型為數字，避免資料有髒汙導致錯誤
        cols_to_numeric = ['市值排名', '總市值', '股價']
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # --- 處理「昨日排名」邏輯 ---
        # 如果你的 Google Sheet 還沒設定好「昨日排名」欄位，程式會自己補上，避免報錯
        if '昨日排名' not in df.columns:
            df['昨日排名'] = df['市值排名'] # 暫時假設沒變動
        else:
            df['昨日排名'] = pd.to_numeric(df['昨日排名'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"資料讀取失敗，請檢查連結。錯誤訊息: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- 4. 計算名次變動 ---
    # 變動 = 昨日 - 今日 (例如昨天第5，今天第3，5-3=2，代表進步2名)
    df['變動數'] = df['昨日排名'] - df['市值排名']

    # 定義顯示格式的函式
    def format_change(val):
        if pd.isna(val) or val == 0:
            return "➖"      # 持平
        elif val > 0:
            return f"⬆️ {int(val)}" # 進步 (紅色概念)
        elif val < 0:
            return f"⬇️ {int(abs(val))}" # 退步 (綠色概念)
        else:
            return "➖"

    df['名次變動'] = df['變動數'].apply(format_change)

    # --- 5. 篩選與排序 ---
    # 確保依照市值排名排序
    df_sorted = df.sort_values(by='市值排名')
    
    # 只取前 150 名
    top_150 = df_sorted.head(150)

    # --- 6. 整理表格欄位 ---
    # 只留下要顯示的欄位，並調整順序
    # 注意：這裡的欄位名稱要跟你 Excel 裡的名稱對應
    final_df = top_150[['市值排名', '名次變動', '股票代號', '股票名稱', '股價', '總市值']]

    # --- 7. 顯示美化後的表格 ---
    st.dataframe(
        final_df,
        height=1000, # 表格高度拉長
        hide_index=True, # 隱藏最左邊的 0,1,2 索引
        use_container_width=True, # 填滿畫面寬度
        column_config={
            "股票代號": st.column_config.TextColumn("代號"), # 改成文字以免出現逗號 (如 2,330),
            "股價": st.column_config.NumberColumn("股價", format="$ %.2f"),
            "總市值": st.column_config.NumberColumn("總市值 (億)", format="$ %.1f")
            "市值排名": st.column_config.NumberColumn("排名", format="%d")
            "名次變動": st.column_config.TextColumn("變動"), # 文字欄位,
        }
    )
    
    # 頁尾資訊
    st.markdown(f"___")
    st.text(f"最後更新時間: {datetime.now().strftime('%H:%M:%S')}")

else:
    st.warning("⚠️ 尚未讀取到資料，請確認你的 Google Sheet 連結是否正確且已發布為 CSV。")
