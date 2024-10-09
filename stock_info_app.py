import os
import sys
from polygon import RESTClient
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pandas as pd
import numpy as np
from textblob import TextBlob

# Set up Polygon API client
polygon_api_key = os.getenv("POLYGON_API_KEY")
if not polygon_api_key:
    raise ValueError("Please set the POLYGON_API_KEY environment variable")
client = RESTClient(polygon_api_key)

def get_stock_data(symbol, start_date, end_date):
    aggs = []
    for a in client.list_aggs(symbol, 1, "day", start_date, end_date, limit=50000):
        aggs.append(a)
    df = pd.DataFrame(aggs)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def get_company_info(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    company_info = {
        "Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "PE Ratio": info.get("trailingPE", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A"),
        "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
        "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
        "Beta": info.get("beta", "N/A"),
        "Forward PE": info.get("forwardPE", "N/A"),
        "PEG Ratio": info.get("pegRatio", "N/A"),
        "EPS": info.get("trailingEps", "N/A"),
    }
    return company_info

def get_greeks(symbol):
    ticker = yf.Ticker(symbol)
    options = ticker.options
    if not options:
        return None
    
    nearest_expiry = options[0]
    chain = ticker.option_chain(nearest_expiry)
    
    # Get ATM option
    atm_option = chain.calls[chain.calls['inTheMoney'] == False].iloc[0]
    
    greeks = {
        "Delta": atm_option.delta,
        "Gamma": atm_option.gamma,
        "Theta": atm_option.theta,
        "Vega": atm_option.vega,
        "Rho": atm_option.rho,
    }
    return greeks

def calculate_technical_indicators(df):
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['RSI'] = calculate_rsi(df['close'])
    df['MACD'], df['Signal'] = calculate_macd(df['close'])
    return df

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices, slow=26, fast=12, smooth=9):
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=smooth, adjust=False).mean()
    return macd, signal

def get_news_sentiment(symbol):
    ticker = yf.Ticker(symbol)
    news = ticker.news
    sentiments = []
    for article in news[:10]:  # Analyze sentiment for the latest 10 news articles
        blob = TextBlob(article['title'])
        sentiments.append(blob.sentiment.polarity)
    return np.mean(sentiments)

class StockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Stock Information App")
        self.setGeometry(100, 100, 1200, 800)

        layout = QVBoxLayout()

        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter stock symbol")
        layout.addWidget(self.symbol_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.update_stock_info)
        layout.addWidget(self.search_button)

        self.info_label = QLabel()
        layout.addWidget(self.info_label)

        self.plot_view = QWebEngineView()
        layout.addWidget(self.plot_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_stock_info(self):
        symbol = self.symbol_input.text().upper()
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            stock_data = get_stock_data(symbol, start_date, end_date)
            stock_data = calculate_technical_indicators(stock_data)
            company_info = get_company_info(symbol)
            greeks = get_greeks(symbol)
            sentiment = get_news_sentiment(symbol)

            info_text = "Company Information:\n"
            for key, value in company_info.items():
                info_text += f"{key}: {value}\n"

            info_text += f"\nLatest Price: ${stock_data['close'].iloc[-1]:.2f}\n"
            info_text += f"News Sentiment: {sentiment:.2f} (-1 to 1 scale)\n"

            if greeks:
                info_text += "\nOption Greeks (for nearest ATM call option):\n"
                for key, value in greeks.items():
                    info_text += f"{key}: {value:.4f}\n"
            else:
                info_text += "\nOption data not available for this stock.\n"

            self.info_label.setText(info_text)

            self.plot_stock_data(stock_data, symbol)

        except Exception as e:
            self.info_label.setText(f"An error occurred: {str(e)}")

    def plot_stock_data(self, df, symbol):
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            subplot_titles=("Stock Price", "Volume", "RSI", "MACD"),
                            row_heights=[0.5, 0.1, 0.2, 0.2])

        # Candlestick chart
        fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="OHLC"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name="20 SMA", line=dict(color='orange', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name="50 SMA", line=dict(color='red', width=1)), row=1, col=1)

        # Volume chart
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], name="Volume"), row=2, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='purple', width=1)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

        # MACD
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD", line=dict(color='blue', width=1)), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], name="Signal", line=dict(color='orange', width=1)), row=4, col=1)

        fig.update_layout(height=800, title_text=f"{symbol} Stock Analysis", showlegend=False)
        fig.update_xaxes(rangeslider_visible=False, rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ))

        self.plot_view.setHtml(fig.to_html(include_plotlyjs='cdn'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockApp()
    window.show()
    sys.exit(app.exec_())
