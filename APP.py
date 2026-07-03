import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from io import BytesIO

# 1. 網頁基本設定
st.set_page_config(page_title="個人資產戰情室", layout="wide")
st.title(" Stock 專屬股市戰情室：通用型突破策略監控")

# 2. 參數化設定 (側邊欄自由輸入)
st.sidebar.header("🔍 標的與策略參數設定")

# 🔓 自由輸入股號與選擇市場
stock_code = st.sidebar.text_input("1. 輸入台灣股號", value="3481")
market_type = st.sidebar.selectbox("2. 市場類型", ["上市 (.TW)", "上櫃 (.TWO)"])

# 自動組合出 yfinance 格式的代號
suffix = ".TW" if "上市" in market_type else ".TWO"
ticker_symbol = f"{stock_code}{suffix}"

# 🔓 自由輸入突破條件
target_price = st.sidebar.number_input("3. 突破目標價 (元)", value=70.0, step=0.5)
target_vol = st.sidebar.number_input("4. 突破攻擊量 (萬張)", value=70.0, step=5.0) * 10000

# 3. 獲取資料與計算指標
@st.cache_data(ttl=3600)  # 快取 1 小時，避免短時間內頻繁抓取導致被 Yahoo 鎖 IP
def load_data(ticker):
    try:
        # 抓取近半年資料
        df = yf.download(ticker, period="6mo")
        if df.empty:
            return None
        
        # 使用 ta 套件計算 KD 指標 (設定參數 9, 3)
        stoch = ta.momentum.StochasticOscillator(
            high=df['High'].squeeze(), 
            low=df['Low'].squeeze(), 
            close=df['Close'].squeeze(), 
            window=9, 
            smooth_window=3
        )
        # 將計算結果寫入 DataFrame
        df['K'] = stoch.stoch()
        df['D'] = stoch.stoch_signal()
        
        return df
    except Exception as e:
        return None

# 執行資料載入
df = load_data(ticker_symbol)

# 判斷是否有成功取得資料
if df is not None and not df.empty:
    
    # 4. 訊號判定：確保取出純數值以利比較
    close_series = df['Close'].squeeze()
    vol_series = df['Volume'].squeeze()
    
    latest_close = float(close_series.iloc[-1])
    latest_vol = float(vol_series.iloc[-1])
    
    # 判定是否符合帶量突破條件
    is_breakout = (latest_close >= target_price) and (latest_vol >= target_vol)

    # 5. 儀表板動態數據顯示
    st.subheader(f"📊 目前監控標的：{ticker_symbol}")
    col1, col2, col3 = st.columns(3)
    col1.metric("最新收盤價", f"{latest_close:.2f} 元")
    col2.metric("最新成交量", f"{latest_vol:,.0f} 張")

    if is_breakout:
        col3.error("🔥 警報：符合帶量突破條件！建議評估進場試單。")
    else:
        col3.success("🛡️ 狀態：量縮整理中，持續觀望。")

    # 6. 繪製 K 線圖 (使用 Plotly)
    fig = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df['Open'].squeeze(), 
                    high=df['High'].squeeze(),
                    low=df['Low'].squeeze(), 
                    close=df['Close'].squeeze(), 
                    name="K線")])

    fig.update_layout(
        title=f"{ticker_symbol} 近半年 K 線走勢圖", 
        height=500,
        xaxis_rangeslider_visible=False  # 關閉下方的滑桿讓畫面更乾淨
    )
    st.plotly_chart(fig, use_container_width=True)

    # 7. 自動匯出 Excel 報表功能
    st.subheader("📊 歷史數據與 KD 指標匯出")
    st.dataframe(df.tail(10)) # 顯示近 10 天數據

    # 將 DataFrame 轉為 Excel 格式提供下載
    def convert_df_to_excel(data_frame):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data_frame.to_excel(writer, index=True, sheet_name='Stock_Data')
        return output.getvalue()

    excel_data = convert_df_to_excel(df)
    st.download_button(
        label=f"📥 下載 {stock_code} 完整數據至 Excel",
        data=excel_data,
        file_name=f'{stock_code}_stock_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

else:
    # ⚠️ 防錯提示畫面
    st.warning(f"🔍 找不到代號 '{ticker_symbol}' 的股票資料。")
    st.info("請檢查：\n1. 股號是否輸入正確（例如上市輸入 3481，上櫃輸入 5347）。\n2. 市場類型（上市/上櫃）是否選擇正確。")