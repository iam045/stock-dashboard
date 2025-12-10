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
        
        cols_to_numeric = ['市值排名', '總市值', '股價']
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

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
        if '✅' in str(val): return 'V'
        return 'X'
    
    if '第 1 欄' in df.columns:
        df['是否在內'] = df['第 1 欄'].apply(check_status)
    else:
        df['是否在內'] = '?'

    # --- 5. 排序與重新命名欄位 ---
    df_sorted = df.sort_values(by='市值排名')
    top_150 = df_sorted.head(150)

    # 選取欄位並改名
    final_df = top_150[['股票代號', '股票名稱', '股價', '總市值', '市值排名', '名次變動', '是否在內']]
    final_df.columns = ['代號', '股票名稱', '股價', '總市值 (億)', '排名', '變動', '納入']

    # --- 6. 設定樣式 (Pandas Styler) ---
    
    # 設定格式
    styled = final_df.style.format({
        '股價': '${:.2f}',
        '總市值 (億)': '${:.0f}',
    })

    # 樣式 A: 排名紅綠燈 (背景色)
    def highlight_rank_col(val):
        if pd.isna(val): return ''
        if val <= 40: return 'background-color: #d4edda; color: black;' # 淺綠
        elif 40 < val <= 50: return 'background-color: #fff3cd; color: black;' # 淺黃
        elif 50 < val <= 60: return 'background-color: #f8d7da; color: black;' # 淺紅
        return ''
    
    # 樣式 B: 納入欄位 V/X 變色 (這裡修改了 X 的樣式)
    def style_status_col(val):
        if val == 'V': 
            return 'color: red; font-weight: bold;'
        elif val == 'X': 
            # 綠色文字 + 亮綠色背景 + 粗體
            return 'color: #006400; background-color: #ccffcc; font-weight: bold;'
        return ''

    # 套用樣式
    styled = styled.map(highlight_rank_col, subset=['排名'])\
                   .map(style_status_col, subset=['納入'])

    # --- 7. 轉換為 HTML 並注入 CSS ---
    
    html_table = styled.to_html(escape=False)
    
    custom_css = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
        }
        th, td {
            text-align: center !important; /* 強制置中 */
            padding: 12px 8px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            color: #333;
            position: sticky;
            top: 0;
            z-index: 1;
        }
        tr:hover {background-color: #f5f5f5;}
    </style>
    """

    # --- 8. 顯示 HTML 表格 ---
    st.markdown(f"""
        {custom_css}
        <div style="height: 800px; overflow-y: auto; border: 1px solid #ccc; border-radius: 5px;">
            {html_table}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("___")
    st.text(f"最後更新時間: {datetime.now().strftime('%H:%M:%S')}")

else:
    st.warning("⚠️ 尚未讀取到資料")
