import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 網頁基礎設定 ---
st.set_page_config(page_title="台股市值戰情室", layout="centered")

# --- 2. 顯示今日日期與標題 ---
week_days = ["一", "二", "三", "四", "五", "六", "日"]
today = datetime.now()
date_str = today.strftime("%Y-%m-%d")
week_day_str = week_days[today.weekday()]

st.title(f"📅 {date_str} (週{week_day_str})")
st.header("🏆 台股市值排行榜 Top 150")
st.caption("資料來源：Google Sheet 自動連線 | 每 60 秒更新")

# --- 3. 讀取與處理資料 ---
@st.cache_data(ttl=60) 
def load_data():
    # 👇 請記得將此網址換成你自己的 Google Sheet CSV 連結
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNB2FmsuJKu4Uh9xh2Qt-9yWrtE_ILjNL-oSEyYLHyrJ2amMiAbGreOYpm6rrryWmCdU_zmsFx7kL0/pub?gid=0&single=true&output=csv"
    
    try:
        df = pd.read_csv(url)
        
        # 強制轉型為數字
        cols_to_numeric = ['市值排名', '總市值', '股價']
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 處理「昨日排名」
        if '昨日排名' not in df.columns:
            df['昨日排名'] = df['市值排名'] 
        else:
            df['昨日排名'] = pd.to_numeric(df['昨日排名'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"資料讀取失敗: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- 4. 計算名次變動 ---
    df['變動數'] = df['昨日排名'] - df['市值排名']

    def format_change(val):
        if pd.isna(val) or val == 0:
            return "➖"      
        elif val > 0:
            return f"⬆️ {int(val)}" 
        elif val < 0:
            return f"⬇️ {int(abs(val))}" 
        else:
            return "➖"

    df['名次變動'] = df['變動數'].apply(format_change)

    # --- 5. 篩選與排序 ---
    df_sorted = df.sort_values(by='市值排名')
    top_150 = df_sorted.head(150)

    # --- 6. 整理表格欄位 (這裡做了你要的順序修改) ---
    # 順序：股票代號 -> 股票名稱 -> 股價 -> 總市值 -> 市值排名 -> 名次變動
    final_df = top_150[['股票代號', '股票名稱', '股價', '總市值', '市值排名', '名次變動']]

    # --- 7. 顯示美化後的表格 ---
    st.dataframe(
        final_df,
        height=1000, 
        hide_index=True, 
        use_container_width=True, 
        column_config={
            "股票代號": st.column_config.TextColumn("代號"), 
            "股價": st.column_config.NumberColumn("股價", format="$ %.2f"),
            # 這裡改成 "%d" 代表整數，不要小數點
            "總市值": st.column_config.NumberColumn("總市值 (億)", format="$ %d"), 
            "市值排名": st.column_config.NumberColumn("排名", format="%d"),
            "名次變動": st.column_config.TextColumn("變動"), 
        }
    )
    
    st.markdown(f"___")
    st.text(f"最後更新時間: {datetime.now().strftime('%H:%M:%S')}")

else:
    st.warning("⚠️ 尚未讀取到資料")
