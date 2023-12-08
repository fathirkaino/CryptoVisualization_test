import config2
from binance import Client
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd

# Replace with your Binance API key and secret
api_key = config2.APIKey
api_secret = config2.SecretKey

# Set up the Binance client
#client = Client(api_key, api_secret)
client = Client(api_key, api_secret,tld='us')

# Function to fetch historical cryptocurrency data from Binance
def get_crypto_data_binance(symbol, start_date, end_date, timeframe):
    klines = client.get_historical_klines(symbol, timeframe, start_date, end_date)
    
    # Create a Pandas DataFrame
    df = pd.DataFrame(klines, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    
    # Convert timestamps to datetime
    df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
    df["Close Time"] = pd.to_datetime(df["Close Time"], unit="ms")
    
    # Set the index to the open time
    df.set_index("Open Time", inplace=True)
    
    return df[['Open', 'High', 'Low', 'Close']]

# title
st.title(":orange[Crypto Currency Visualization App]")

# Sidebar for user input
st.sidebar.header(':blue[Input Values]', divider='rainbow')

# Get a list of available cryptocurrency symbols from Binance
exchange_info = client.get_exchange_info()
crypto_symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING']

# Select cryptocurrency using a dropdown menu
default_crypto_index = crypto_symbols.index('BTCUSDT') if 'BTCUSDT' in crypto_symbols else 0
crypto_symbol = st.sidebar.selectbox('Select Cryptocurrency :', crypto_symbols, index=default_crypto_index)

# Select date range
start_date_default = datetime.now() - timedelta(days=30)
start_date = st.sidebar.date_input('Start Date', value=start_date_default)
end_date = st.sidebar.date_input('End Date', value=datetime.now())

# Select time interval
timeframes = {
    '1 Minute': Client.KLINE_INTERVAL_1MINUTE,
    '3 Minutes': Client.KLINE_INTERVAL_3MINUTE,
    '5 Minutes': Client.KLINE_INTERVAL_5MINUTE,
    '15 Minutes': Client.KLINE_INTERVAL_15MINUTE,
    '1 Hour': Client.KLINE_INTERVAL_1HOUR,
    '4 Hours': Client.KLINE_INTERVAL_4HOUR,
    '1 Day': Client.KLINE_INTERVAL_1DAY,
    '1 Week': Client.KLINE_INTERVAL_1WEEK,
    '1 Month': Client.KLINE_INTERVAL_1MONTH,
}

#selected_timeframe = st.sidebar.selectbox('Select Time Interval:', list(timeframes.keys()))
default_timeframe = '1 Day'
selected_timeframe = st.sidebar.selectbox('Select Time Interval:', list(timeframes.keys()), index=list(timeframes.keys()).index(default_timeframe))



# Fetch data from Binance
crypto_data = get_crypto_data_binance(crypto_symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), timeframes[selected_timeframe])

# Allow user to pick the number of rows to display
num_rows = st.sidebar.slider('Select the number of rows to display:', min_value=1, max_value=len(crypto_data), value=5)

# Display the selected number of rows in descending order
st.write(f'**:green[{crypto_symbol} Historical Data (OHLC) (Top {num_rows} rows)]**')
st.write(crypto_data.sort_index(ascending=False).head(num_rows))

# Line chart with all values (Open, High, Low, Close)
line_chart_ohlc = go.Figure()
line_chart_ohlc.add_trace(go.Scatter(x=crypto_data.index, y=crypto_data['Open'], mode='lines', name='Open'))
line_chart_ohlc.add_trace(go.Scatter(x=crypto_data.index, y=crypto_data['High'], mode='lines', name='High'))
line_chart_ohlc.add_trace(go.Scatter(x=crypto_data.index, y=crypto_data['Low'], mode='lines', name='Low'))
line_chart_ohlc.add_trace(go.Scatter(x=crypto_data.index, y=crypto_data['Close'], mode='lines', name='Close'))

line_chart_ohlc.update_layout(xaxis_title='Date', yaxis_title='Price (USD)',
                              title=dict(text=f'{crypto_symbol} OHLC Prices Over Time ({selected_timeframe})', font=dict(color='green')))

st.plotly_chart(line_chart_ohlc)

# Candlestick chart
candlestick_chart = go.Figure(data=[go.Candlestick(x=crypto_data.index,
                                                    open=crypto_data['Open'],
                                                    high=crypto_data['High'],
                                                    low=crypto_data['Low'],
                                                    close=crypto_data['Close'])])

candlestick_chart.update_layout(xaxis_title='Date', yaxis_title='Price (USD)',
                                title=dict(text=f'{crypto_symbol} Candlestick Chart ({selected_timeframe})', font=dict(color='green')))

st.plotly_chart(candlestick_chart)
