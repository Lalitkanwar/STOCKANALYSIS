# FinSight - Professional Stock Market Analytics

FinSight is a production-ready, modern web application built with Python and Streamlit that provides real-time stock market data, interactive financial charts, and technical indicators.

## Features
- **Real-time Data**: Fetches live equity data using the Yahoo Finance API.
- **Interactive Visualization**: Features Plotly-based candlestick charts and volume subplots.
- **Technical Analysis**: Automatically calculates and visualizes 20-period and 50-period Moving Averages.
- **Responsive UI**: A highly optimized, custom CSS-styled dark theme layout that works elegantly across desktops and mobile devices.
- **Production Ready**: Includes robust error handling, API response caching, and loading animations.

## Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/finsight.git
   cd finsight
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Deployment

This application is ready to be deployed on Streamlit Community Cloud. Simply connect your GitHub repository and point the main file path to `app.py`.
