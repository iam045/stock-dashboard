import streamlit as st
import pandas as pd
import plotly.express as px

# 設定網頁標題
st.set_page_config(page_title="台股市值戰情室", layout="wide")
st.title("📊 台灣股市市值變動儀表板")

# 讀取資料
@st.cache_data
def load_data():
    # 注意：這裡的檔名要跟你剛剛上傳到 GitHub 的檔名一模一樣！
    # 如果你上傳的是 .csv 就改 .csv，是 .xlsx 就改 .xlsx
    file_path = "data.xlsx"  

    try:
        # 嘗試讀取 Excel
        df = pd.read_excel(file_path)
        # 如果你的檔案是 CSV，請改用下面這行：
        # df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"讀取失敗，請確認 GitHub 上的檔名是否為 {file_path}")
        return pd.DataFrame()

    # 資料清理 (根據你的 Excel 欄位調整)
    if '第 1 欄' in df.columns:
        df = df.rename(columns={'第 1 欄': '是否為0050'})
        df['是否為0050'] = df['是否為0050'].fillna('非成分股')
        df['是否為0050'] = df['是否為0050'].apply(lambda x: '0050成分股' if str(x).strip() != 'nan' and str(x).strip() != '非成分股' else '非成分股')

    # 確保數值正確
    df['總市值'] = pd.to_numeric(df['總市值'], errors='coerce')
    df['市值排名'] = pd.to_numeric(df['市值排名'], errors='coerce')

    return df

df = load_data()

if not df.empty:
    # 側邊欄與內容
    st.sidebar.header("篩選條件")
    show_only_0050 = st.sidebar.checkbox("只顯示 0050 成分股", value=False)

    filtered_df = df[df['是否為0050'] == '0050成分股'] if show_only_0050 else df
    filtered_df = filtered_df.sort_values(by='市值排名')

    # 顯示 KPI
    top_stock = filtered_df.iloc[0]
    col1, col2 = st.columns(2)
    col1.metric("👑 市值王", f"{top_stock['股票名稱']}")
    col2.metric("💰 總市值", f"{top_stock['總市值']:,.0f}")

    # 圖表
    st.subheader("市值排行")
    fig = px.bar(filtered_df.head(20), x='股票名稱', y='總市值', color='總市值')
    st.plotly_chart(fig, use_container_width=True)

    # 資料表
    st.dataframe(filtered_df)
