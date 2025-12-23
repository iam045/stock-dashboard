import streamlit as st
import pandas as pd
import time

# --- 1. 基礎設定 ---
st.set_page_config(page_title="風險預警中心", layout="wide", page_icon="🔥")

# --- 2. 核心函式：檢查股票狀態 ---
def check_official_status(stock_code):
    """
    檢查股票狀態，並處理可能的非字串或空值錯誤
    """
    try:
        # 防錯處理：如果 stock_code 是 NaN、None 或不是字串/數字
        if pd.isna(stock_code) or stock_code is None:
            return "數據缺失", "無效的代碼格式"

        # 強制轉為字串並移除小數點（處理 2330.0 這種情況）
        s_code = str(stock_code).split('.')[0]
        
        # 過濾出數字部分
        target_code = ''.join(filter(str.isdigit, s_code))
        
        if not target_code:
            return "格式錯誤", f"無法辨識: {stock_code}"

        # --- 這裡是你原本檢查官方狀態的邏輯 ---
        # 範例邏輯（請根據你實際的 API 或網頁爬蟲需求修改）：
        # status = some_api_call(target_code)
        # 暫時回傳模擬狀態
        return "已連接", f"股票代碼 {target_code} 正常"
        
    except Exception as e:
        return "系統錯誤", str(e)

# --- 3. 主程式介面 ---
def main():
    st.title("🔥 風險預警中心")
    
    # 顯示更新狀態
    st.markdown(f"🕒 **更新狀態**：已連結 GitHub 機器人資料庫 (`history_db.csv`) ")

    try:
        # 讀取資料庫
        # 建議加入 low_memory=False 避免型別警告
        df = pd.read_csv('history_db.csv')
        
        # 如果 CSV 為空，給予提示
        if df.empty:
            st.warning("資料庫中目前沒有資料。")
            return

        # 取得需要分析的股票清單 (假設欄位名稱為 '股票代號'，請依實際欄位名修改)
        # 這裡會自動處理欄位名稱，如果找不到正確欄位，請將 '股票代號' 修改為你 CSV 的抬頭
        col_name = '股票代號' if '股票代號' in df.columns else df.columns[0]
        stock_list = df[col_name].tolist()
        total_stocks = len(stock_list)

        # 進度顯示
        progress_text = f"正在分析資料庫中 {total_stocks} 檔股票..."
        my_bar = st.progress(0, text=progress_text)
        
        results = []

        # --- 4. 迴圈分析 ---
        for i, code in enumerate(stock_list):
            # 更新進度條
            step = (i + 1) / total_stocks
            my_bar.progress(step, text=f"({i+1}/{total_stocks}) 正在檢查: {code}")

            # 執行狀態檢查 (這就是原本出錯的地方，現在已加上防錯)
            status, reason = check_official_status(code)
            
            results.append({
                "股票代碼": code,
                "分析狀態": status,
                "詳細資訊": reason
            })
            
            # 模擬分析耗時，避免過快導致 UI 閃爍
            # time.sleep(0.05) 

        # --- 5. 顯示結果 ---
        st.success("✅ 分析完成")
        res_df = pd.DataFrame(results)
        st.dataframe(res_df, use_container_width=True)

    except FileNotFoundError:
        st.error("找不到 `history_db.csv` 檔案，請確認檔案已上傳至 GitHub 倉庫。")
    except Exception as e:
        st.error(f"執行過程中發生未預期的錯誤: {e}")

if __name__ == "__main__":
    main()
