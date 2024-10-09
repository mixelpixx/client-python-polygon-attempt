# Advanced Stock Information App

This application provides a comprehensive tool for analyzing stock information, including real-time data, technical indicators, and sentiment analysis.

## Features


## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/advanced-stock-info-app.git
   cd advanced-stock-info-app
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Download the necessary Natural Language Toolkit (NLTK) corpora for TextBlob:
   ```
   python -m textblob.download_corpora
   ```

5. Set up your Polygon API key:
   - Sign up for a free account at https://polygon.io/
   - Set the environment variable:
     ```
     export POLYGON_API_KEY=your_api_key_here
     ```

## Usage

+Run the application:
+```
+python stock_info_app.py
+```
+
+Enter a stock symbol in the input field and click "Search" to retrieve and display the stock information.
+
+## Dependencies
+
+- pandas
+- numpy
+- yfinance
+- polygon-api-client
+- plotly
+- PyQt5
+- PyQtWebEngine
+- textblob
+
+For specific versions, refer to the `requirements.txt` file.
+
+## Contributing
+
+Contributions are welcome! Please feel free to submit a Pull Request.
+
+## License
+
+This project is licensed under the MIT License - see the LICENSE file for details.
+
+## Acknowledgments
+
+- [Polygon.io](https://polygon.io/) for providing the stock data API
+- [yfinance](https://github.com/ranaroussi/yfinance) for additional financial data
