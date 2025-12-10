import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 網頁基礎設定 ---
st.set_page_config(page_title="台股市值戰情室", layout="centered")

# --- 2. 標題區 ---
week_days = ["一", "二", "三", "四", "五", "六", "日"]
today = datetime.now()
date_str = today.strftime("%Y-%m-%d")
week_day_str = week_days[today.weekday()]

st.title(f"📅 {date_str} (週{week_day_str})")
st.header("🏆 台股市值排行榜 Top 150")
st.caption("資料來源：Google Sheet 自動連線 | 🔴紅色:50-60名 | 🟡黃色:40-50名 | 🟢綠色:前40名")

# --- 3. 讀取資料 ---
@st.cache_data(ttl=60) 
def load_data():
    # 👇 請確認這裡還是你的 Google Sheet CSV 連結
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNB2FmsuJKu4Uh9xh2Qt-9yWrtE_ILjNL-oSEyYLHyrJ2amMiAbGreOYpm6rrryWmCdU_zmsFx7kL0/pub?gid=0&single=true&output=csv"
    
    try:
        df = pd.read_csv(url)
        
        # 轉型為數字
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
    # --- 4. 資料處理邏輯 ---
    
    # (A) 計算名次變動
    df['變動數'] = df['昨日排名'] - df['市值排名']
    def format_change(val):
        if pd.isna(val) or val == 0: return "➖"
        elif val > 0: return f"⬆️ {int(val)}"
        elif val < 0: return f"⬇️ {int(abs(val))}"
        return "➖"
    df['名次變動'] = df['變動數'].apply(format_change)

    # (B) 判斷「是否在內」
    def check_status(val):
        if '✅' in str(val):
            return 'V'
        return 'X'
    
    if '第 1 欄' in df.columns:
        df['是否在內'] = df['第 1 欄'].apply(check_status)
    else:
        df['是否在內'] = '?'

    # --- 5. 排序與欄位順序調整 (納入移到最後) ---
    df_sorted = df.sort_values(by='市值排名')
    top_150 = df_sorted.head(150)

    # 這裡把 '是否在內' 移到 list 的最後面
    final_df = top_150[['股票代號', '股票名稱', '股價', '總市值', '市值排名', '名次變動', '是否在內']]

    # --- 6. 設定樣式 (Styles) ---
    
    # 樣式 A: 排名紅綠燈 (背景色)
    def highlight_rank_col(val):
        color = ''
        if pd.isna(val): return ''
        if val <= 40: color = '#d4edda'      # 綠
        elif 40 < val <= 50: color = '#fff3cd' # 黃
        elif 50 < val <= 60: color = '#f8d7da' # 紅
        return f'background-color: {color}; color: black;' if color else ''

    # 樣式 B: 納入欄位 V紅X綠 (文字顏色+粗體)
    def style_status_col(val):
        if val == 'V':
            return 'color: red; font-weight: bold;'
        elif val == 'X':
            return 'color: green; font-weight: bold;'
        return ''

    # 套用所有樣式
    styled_df = final_df.style\
        .map(highlight_rank_col, subset=['市值排名'])\
        .map(style_status_col, subset=['是否在內'])\
        .set_properties(**{'text-align': 'center'}) # 全體置中

    # --- 7. 顯示表格 ---
    st.dataframe(
        styled_df,
        height=1000, 
        hide_index=True, 
        use_container_width=True, 
        column_config={
            "股票代號": st.column_config.TextColumn("代號"), 
            "股票名稱": st.column_config.TextColumn("股票名稱"),
            "股價": st.column_config.NumberColumn("股價", format="$ %.2f"),
            "總市值": st.column_config.NumberColumn("總市值 (億)", format="$ %d"), 
            "市值排名": st.column_config.NumberColumn("排名", format="%d"),
            "名次變動": st.column_config.TextColumn("變動"), 
            "是否在內": st.column_config.TextColumn("納入", width="small"),
        }
    )
    
    st.markdown("___")
    st.text(f"最後更新時間: {datetime.now().strftime('%H:%M:%S')}")

else:
    st.warning("⚠️ 尚未讀取到資料")
