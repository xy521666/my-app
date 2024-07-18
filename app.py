import time
import akshare as ak
import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Today's date
end_date = (datetime.datetime.now() + datetime.timedelta(days=0)).strftime('%Y%m%d')

# Define the data fetching function using AkShare
def get_data(symbol, start_date, end_date):
    try:
        df = ak.stock_us_hist(symbol=str(symbol), period='daily', start_date=start_date, end_date=end_date, adjust="qfq")
        df = df.sort_values(by='日期')
        df['日期'] = pd.to_datetime(df['日期'])
        df.set_index('日期', inplace=True)
        df.rename(columns={
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume',
            '成交额': 'Turnover'
        }, inplace=True)
        time.sleep(0.2)
        return df
    except Exception as e:
        st.error(f"Exception occurred while fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

# 设置页面标题
st.title('Apple Stock Price Dashboard')

# 选择时间间隔
interval_map = {
    '1 day': 1,
    '5 days': 5,
    '1 month': 30,
    '3 months': 90
}
interval = st.selectbox('Select Time Interval', ['1 day', '5 days', '1 month', '3 months'])

# Calculate the start date based on the selected interval
start_date = (datetime.datetime.now() - datetime.timedelta(days=interval_map[interval])).strftime('%Y%m%d')

# 获取苹果股票数据
@st.cache_data(ttl=60*5)
def load_data(symbol, start_date, end_date, retries=3):
    for i in range(retries):
        data = get_data(symbol, start_date=start_date, end_date=end_date)
        if not data.empty:
            return data
        st.warning(f"Attempt {i+1} of {retries} failed.")
        time.sleep(2)  # 等待2秒后重试
    st.error("Failed to fetch data after multiple attempts.")
    return pd.DataFrame()

# 根据选择的时间间隔加载数据
data = load_data('105.AAPL', start_date, end_date)

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
