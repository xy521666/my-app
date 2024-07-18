import time
import akshare as ak
import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# Today's date
end_date = (datetime.datetime.now()).strftime('%Y%m%d')

# Define the data fetching function using AkShare
def get_data(symbol, start_date, end_date, period):
    try:
        df = ak.stock_us_hist(symbol=str(symbol), period=period, start_date=start_date, end_date=end_date, adjust="qfq")
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
    'Daily': 'daily',
    'Weekly': 'weekly',
    'Monthly': 'monthly'
}
interval = st.selectbox('Select Time Interval', ['Daily', 'Weekly', 'Monthly'])

# Calculate the start date based on the selected interval
start_date = '20240101'  # Starting from the beginning of the year

# 获取苹果股票数据
@st.cache_data(ttl=60*5)
def load_data(symbol, start_date, end_date, period, retries=3):
    for i in range(retries):
        data = get_data(symbol, start_date=start_date, end_date=end_date, period=period)
        if not data.empty:
            return data
        st.warning(f"Attempt {i+1} of {retries} failed.")
        time.sleep(2)  # 等待2秒后重试
    st.error("Failed to fetch data after multiple attempts.")
    return pd.DataFrame()

# 根据选择的时间间隔加载数据
data = load_data('105.AAPL', start_date, end_date, interval_map[interval])

# 检查数据是否加载成功
if not data.empty:
    # 选择指标
    indicators = st.multiselect(
        'Select Indicators',
        ['SMA', 'EMA', 'Bollinger Bands']
    )

    # 绘制股票价格图
    st.subheader(f'Apple Stock Price ({interval})')
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Candlestick'))

    # 添加技术指标
    if 'SMA' in indicators:
        data['SMA'] = data['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name='SMA'))

    if 'EMA' in indicators:
        data['EMA'] = data['Close'].ewm(span=20, adjust=False).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA'], mode='lines', name='EMA'))

    if 'Bollinger Bands' in indicators:
        data['SMA'] = data['Close'].rolling(window=20).mean()
        data['stddev'] = data['Close'].rolling(window=20).std()
        data['Upper'] = data['SMA'] + (data['stddev'] * 2)
        data['Lower'] = data['SMA'] - (data['stddev'] * 2)
        fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], mode='lines', name='Upper Band'))
        fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], mode='lines', name='Lower Band'))

    fig.update_layout(
        title='Apple Stock Price',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig)

    # 显示数据表
    st.subheader('Data Table')
    st.write(data.tail(10))

# 刷新按钮
if st.button('Refresh Data'):
    st.experimental_rerun()
