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

Run the application:
