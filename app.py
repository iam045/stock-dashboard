import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 網頁基礎設定 ---
st.set_page_config(page_title="台股市值戰情室", layout="centered")

# --- 2. 標題與說明文字區 ---
week_days = ["一", "二", "三", "四", "五", "六", "日"]
today = datetime.now()
date_str = today.strftime("%Y-%m-%d")
week_day_str = week_days[today.weekday()]

st.title(f"📅 {date_str} (週{week_day_str})")
st.header("🏆 台股市值排行榜 Top 150")

# 說明區塊
st.info("""
**ℹ️ 0050 成分股調整規則說明：**
* **公布時間**：每年 3、6、9、12 月的第一個星期五收盤後。
* **生效時間**：公布當月後的第三個星期五收盤後。
* **納入規則**：若非成分股之市值排名**上升至前 40 名**，則納入。
* **刪除規則**：若成分股之市值排名**下降至 61 名以下**，則剔除。
* *審核日推估：生效日往前 4 週的星期一 (待確認)*
""")

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
    # --- 4. 資料前處理邏輯 ---
    
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

    # --- 5. 新增：預測區塊 (入選 vs 剔除) ---
    st.markdown("---") # 分隔線
    col_in, col_out = st.columns(2)

    # 左邊：可能會入選 (排名 <= 50 且 不在內)
    with col_in:
        st.subheader("🔥 可能會入選")
        # 篩選邏輯
        potential_in = df[(df['市值排名'] <= 50) & (df['是否在內'] == 'X')].copy()
        
        if not potential_in.empty:
            # 選取顯示欄位
            display_in = potential_in[['市值排名', '股票名稱', '總市值']]
            
            # 設定樣式：前 40 名亮紅字
            def style_potential_in(row):
                # 如果排名 <= 40，整列紅字粗體
                if row['市值排名'] <= 40:
                    return ['color: red; font-weight: bold;'] * len(row)
                return [''] * len(row)

            styled_in = display_in.style.apply(style_potential_in, axis=1)\
                .format({'市值排名': '{:.0f}', '總市值': '{:.0f}'})

            st.dataframe(styled_in, hide_index=True, use_container_width=True)
        else:
            st.info("目前沒有符合條件的標的")

    # 右邊：可能會剔除 (排名 > 50 且 在內)
    with col_out:
        st.subheader("⚠️ 可能會剔除")
        # 篩選邏輯
        potential_out = df[(df['市值排名'] > 50) & (df['是否在內'] == 'V')].copy()
        
        if not potential_out.empty:
            display_out = potential_out[['市值排名', '股票名稱', '總市值']]
            
            # 這裡不特別標色，維持清爽，或者你可以依需求加
            st.dataframe(
                display_out, 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "市值排名": st.column_config.NumberColumn("排名", format="%d"),
                    "總市值": st.column_config.NumberColumn("總市值", format="%d"),
                }
            )
        else:
            st.success("目前沒有成分股掉出 50 名外")

    st.markdown("---") # 分隔線

    # --- 6. 主表格呈現 ---
    
    # 排序與選取欄位
    df_sorted = df.sort_values(by='市值排名')
    top_150 = df_sorted.head(150)
    final_df = top_150[['股票代號', '股票名稱', '股價', '總市值', '市值排名', '名次變動', '是否在內']]

    # 設定主表格樣式
    def highlight_rank_col(val):
        if pd.isna(val): return ''
        if val <= 40: return 'background-color: #d4edda; color: black;' # 綠
        elif 40 < val <= 50: return 'background-color: #fff3cd; color: black;' # 黃
        elif 50 < val <= 60: return 'background-color: #f8d7da; color: black;' # 紅
        return ''
    
    def style_status_col(val):
        if val == 'V': return 'color: red; font-weight: bold;'
        elif val == 'X': return 'color: #006400; background-color: #ccffcc; font-weight: bold;'
        return ''

    styled_main = final_df.style\
        .map(highlight_rank_col, subset=['市值排名'])\
        .map(style_status_col, subset=['是否在內'])\
        .format({
            '股價': '{:.2f}',
            '總市值': '{:.0f}',
            '市值排名': '{:.0f}'
        })

    st.dataframe(
        styled_main,
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
