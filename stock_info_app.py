import os
from polygon import RESTClient
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Set up Polygon API client
polygon_api_key = os.getenv("POLYGON_API_KEY")
if not polygon_api_key:
    raise ValueError("Please set the POLYGON_API_KEY environment variable")
client = RESTClient(polygon_api_key)

def get_stock_data(symbol, start_date, end_date):
    aggs = []
    for a in client.list_aggs(symbol, 1, "day", start_date, end_date, limit=50000):
        aggs.append(a)
    return aggs

def get_company_info(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "PE Ratio": info.get("trailingPE", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A"),
    }

def get_greeks(symbol):
    ticker = yf.Ticker(symbol)
    options = ticker.options
    if not options:
        return None
    
    nearest_expiry = options[0]
    chain = ticker.option_chain(nearest_expiry)
    
    # Get ATM option
    atm_option = chain.calls[chain.calls['inTheMoney'] == False].iloc[0]
    
    return {
        "Delta": atm_option.delta,
        "Gamma": atm_option.gamma,
        "Theta": atm_option.theta,
        "Vega": atm_option.vega,
        "Rho": atm_option.rho,
    }

def plot_stock_data(aggs, symbol):
    dates = [datetime.fromtimestamp(a.timestamp / 1000) for a in aggs]
    closes = [a.close for a in aggs]
    
    plt.figure(figsize=(12, 6))
    plt.plot(dates, closes)
    plt.title(f"{symbol} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.show()

def main():
    while True:
        symbol = input("Enter a stock symbol or company name (or 'quit' to exit): ").upper()
        if symbol.lower() == 'quit':
            break
        
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            
            stock_data = get_stock_data(symbol, start_date, end_date)
            company_info = get_company_info(symbol)
            greeks = get_greeks(symbol)
            
            print("\nCompany Information:")
            for key, value in company_info.items():
                print(f"{key}: {value}")
            
            print("\nStock Data:")
            print(f"Latest Price: ${stock_data[-1].close:.2f}")
            print(f"52-week High: ${max(a.high for a in stock_data):.2f}")
            print(f"52-week Low: ${min(a.low for a in stock_data):.2f}")
            
            if greeks:
                print("\nOption Greeks (for nearest ATM call option):")
                for key, value in greeks.items():
                    print(f"{key}: {value:.4f}")
            else:
                print("\nOption data not available for this stock.")
            
            plot_stock_data(stock_data, symbol)
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        print("\n")

if __name__ == "__main__":
    main()
