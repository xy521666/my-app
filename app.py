import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 设置页面标题
st.title('Apple Stock Price Dashboard')

# 获取苹果股票数据
@st.cache_data(ttl=60*5)
def load_data(ticker):
    data = yf.download(ticker, period='1d', interval='1m')
    return data

# 加载数据
data = load_data('AAPL')

# 添加选择时间间隔的选项
interval = st.selectbox('Select Time Interval', ['1m', '5m', '15m', '30m', '1h', '1d'])

# 根据选择的时间间隔加载数据
data = yf.download('AAPL', period='5d', interval=interval)

# 添加指标选择
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
