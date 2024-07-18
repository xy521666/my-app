import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time

# 设置页面标题
st.title('Apple Stock Price Dashboard')

# 获取苹果股票数据
@st.cache_data(ttl=60*5)
def load_data(ticker, period, interval, retries=3):
    for i in range(retries):
        try:
            data = yf.download(ticker, period=period, interval=interval)
            if data.empty:
                st.error("No data fetched, please try again later.")
            return data
        except Exception as e:
            st.warning(f"Attempt {i+1} of {retries} failed: {e}")
            time.sleep(2)  # 等待2秒后重试
    st.error("Failed to fetch data after multiple attempts.")
    return pd.DataFrame()

# 选择时间间隔
interval = st.selectbox('Select Time Interval', ['1m', '5m', '15m', '30m', '1h', '1d'])

# 根据选择的时间间隔加载数据
data = load_data('AAPL', period='5d', interval=interval)

# 检查数据是否加载成功
if not data.empty:
    # 选择指标
    indicators = st.multiselect(
        'Select Indicators',
        ['SMA', 'EMA', 'Bollinger Bands']
    )

    # 绘制股票价格图
    st.subheader(f'Apple Stock Price ({interval})')
    fig, ax = plt.subplots()
    ax.plot(data.index, data['Close'], label='Close Price')

    # 添加技术指标
    if 'SMA' in indicators:
        data['SMA'] = data['Close'].rolling(window=20).mean()
        ax.plot(data.index, data['SMA'], label='SMA')

    if 'EMA' in indicators:
        data['EMA'] = data['Close'].ewm(span=20, adjust=False).mean()
        ax.plot(data.index, data['EMA'], label='EMA')

    if 'Bollinger Bands' in indicators:
        data['SMA'] = data['Close'].rolling(window=20).mean()
        data['stddev'] = data['Close'].rolling(window=20).std()
        data['Upper'] = data['SMA'] + (data['stddev'] * 2)
        data['Lower'] = data['SMA'] - (data['stddev'] * 2)
        ax.plot(data.index, data['Upper'], label='Upper Band')
        ax.plot(data.index, data['Lower'], label='Lower Band')

    ax.legend()
    st.pyplot(fig)

    # 显示数据表
    st.subheader('Data Table')
    st.write(data.tail(10))

# 刷新按钮
if st.button('Refresh Data'):
    st.experimental_rerun()
