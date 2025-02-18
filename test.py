# import streamlit as st, pandas as pd, numpy as np, yfinance as yf
# import plotly.express as px
# st.title('Stock Dashboard')
# ticker = st.sidebar.text_input('Ticker')
# start_date = st.sidebar.date_input('Start Date')
# end_date = st.sidebar.date_input('End Date')

# data = yf.download(ticker, start=start_date, end=end_date)
# # fig=px.line(data, x = data.index, y = data['Adj Close'], title = ticker)

# # Fixing by ensuring 'data["Adj Close"]' is a Series (1D) instead of a DataFrame (2D) // new line added 
# fig = px.line(data, x=data.index, y=data['Adj Close'].squeeze(), title=ticker)

# st.plotly_chart (fig)

# pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

# with pricing_data:
#     st.header('Price Movements')
#     data2 = data
#     data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1)-1
#     data2.dropna(inplace=True)
#     st.write(data2)
#     annual_return = data2 [ '% Change'].mean()*252*100
#     st.write('Annual Return is ',annual_return, '%')
#     stdev = np.std(data2 ['% Change'])*np.sqrt(252)
#     st.write('Standard Deviation is ',stdev*100, '%')
#     st.write('Risk Adj. Return is ',annual_return/(stdev*100))

# from alpha_vantage.fundamentaldata import FundamentalData
# with fundamental_data:
#     key = 'HBCBDH6V4IWF4YAU'
#     fd=FundamentalData(key,output_format='pandas')
#     st.subheader('Balance sheet')
#     balance_sheet=fd.get_balance_sheet_annual(ticker)[0]
#     bs=balance_sheet.T[2:]
#     bs.columns=list(balance_sheet.T.iloc[0])
#     st.write(bs)
#     st.subheader('Income Statement')
#     income_statement= fd.get_income_statement_annual(ticker)[0]
#     is1=income_statement.T[2:]
#     is1.columns=list(income_statement.T.iloc[0])
#     st.write(is1)
#     st.subheader('cash Flow Statement')
#     cash_flow= fd.get_cash_flow_annual(ticker)[0]
#     cf=cash_flow.T[2:]
#     cf.columns=list(cash_flow.T.iloc[0])
#     st.write(cf)



# from stocknews import StockNews
# with news:
#     st.header(f'News of {ticker}')
#     sn=StockNews(ticker, save_news=False)
#     df_news= sn.read_rss()
#     for i in range(10):
#         st.subheader(f'News {i+1}')
#         st.write(df_news['published'][i])
#         st.write(df_news['title'][i])
#         st.write(df_news['summary'][i])
#         title_sentiment=df_news['sentiment_title'][i]
#         st.write(f'Title Sentiment {title_sentiment}')
#         news_sentiment=df_news['sentiment_summary'][i]
#         st.write(f'News Sentiment {news_sentiment}')
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

# Title
st.title('📈 Stock Dashboard')

# Sidebar Inputs
ticker = st.sidebar.text_input('Enter Stock Ticker (e.g., AAPL, TSLA)', value="AAPL")
start_date = st.sidebar.date_input('Start Date', pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input('End Date', pd.to_datetime("today"))

# Ensure the user entered a valid ticker
if not ticker:
    st.error("❌ Please enter a stock ticker symbol!")
    st.stop()

# Fetch Stock Data
try:
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if data.empty:
        st.error(f"❌ No data found for **{ticker}**. Please check the ticker and date range.")
        st.stop()

    # Use 'Close' if 'Adj Close' is missing
    if "Adj Close" not in data.columns:
        st.warning("⚠️ Adjusted Close price not available. Using Close price instead.")
        data["Adj Close"] = data["Close"]

    # Plot Stock Price
    fig = px.line(data, x=data.index, y=data['Adj Close'], title=f'{ticker} Stock Prices')
    st.plotly_chart(fig)

except Exception as e:
    st.error(f"⚠️ Error fetching stock data: {e}")
    st.stop()

# Tabs for additional data
pricing_data, fundamental_data, news = st.tabs(["📊 Pricing Data", "📑 Fundamental Data", "📰 Latest News"])

# ✅ PRICING DATA TAB
with pricing_data:
    st.header('📉 Price Movements')
    
    # Calculate % Change
    data["% Change"] = data['Adj Close'].pct_change()
    data.dropna(inplace=True)
    st.write(data)

    # Financial Metrics
    annual_return = data["% Change"].mean() * 252 * 100
    stdev = np.std(data["% Change"]) * np.sqrt(252)
    risk_adj_return = annual_return / (stdev * 100)

    # Display Metrics
    st.metric(label="📈 Annual Return", value=f"{annual_return:.2f}%")
    st.metric(label="📊 Standard Deviation (Risk)", value=f"{stdev*100:.2f}%")
    st.metric(label="⚖️ Risk-Adjusted Return", value=f"{risk_adj_return:.2f}")

# ✅ FUNDAMENTAL DATA TAB
with fundamental_data:
    try:
        key = 'HBCBDH6V4IWF4YAU'  # Replace with your Alpha Vantage API Key
        fd = FundamentalData(key, output_format='pandas')

        st.subheader("📊 Balance Sheet")
        balance_sheet = fd.get_balance_sheet_annual(ticker)[0].T[2:]
        balance_sheet.columns = list(fd.get_balance_sheet_annual(ticker)[0].T.iloc[0])
        st.write(balance_sheet)

        st.subheader("📑 Income Statement")
        income_statement = fd.get_income_statement_annual(ticker)[0].T[2:]
        income_statement.columns = list(fd.get_income_statement_annual(ticker)[0].T.iloc[0])
        st.write(income_statement)

        st.subheader("💰 Cash Flow Statement")
        cash_flow = fd.get_cash_flow_annual(ticker)[0].T[2:]
        cash_flow.columns = list(fd.get_cash_flow_annual(ticker)[0].T.iloc[0])
        st.write(cash_flow)

    except Exception as e:
        st.error(f"⚠️ Error fetching fundamental data: {e}")

# ✅ NEWS TAB
with news:
    try:
        st.header(f"📰 Latest News for {ticker}")
        sn = StockNews(ticker, save_news=False)
        df_news = sn.read_rss()

        for i in range(min(10, len(df_news))):
            st.subheader(f"📰 News {i+1}")
            st.write(f"🕒 Published: {df_news['published'][i]}")
            st.write(f"📌 {df_news['title'][i]}")
            st.write(df_news['summary'][i])
            st.write(f"📊 Title Sentiment: {df_news['sentiment_title'][i]}")
            st.write(f"📰 News Sentiment: {df_news['sentiment_summary'][i]}")
            st.divider()

    except Exception as e:
        st.error(f"⚠️ Error fetching news data: {e}")

