import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Set page configuration - Must be the first Streamlit command
st.set_page_config(
    page_title="FinSight | Market Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for production-ready styling, mobile responsiveness, and footer
def apply_custom_css():
    st.markdown("""
        <style>
        /* Main branding */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #00ff99;
            margin-bottom: 0px;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #a0a0a0;
            margin-bottom: 30px;
        }
        /* Card styling for metrics */
        div[data-testid="metric-container"] {
            background-color: #1e2130;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        /* Custom Footer */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #0e1117;
            color: #888;
            text-align: center;
            padding: 10px 0;
            font-size: 0.9rem;
            border-top: 1px solid #333;
            z-index: 100;
        }
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #12141e;
        }
        /* Mobile responsiveness improvements */
        @media (max-width: 768px) {
            .main-header { font-size: 1.8rem; }
            .sub-header { font-size: 0.9rem; }
            div[data-testid="metric-container"] { padding: 10px; }
        }
        </style>
    """, unsafe_allow_html=True)

# Function to fetch data with robust caching and error handling
@st.cache_data(ttl=300, show_spinner=False) # Cache data for 5 minutes
def get_stock_data(ticker, period="1y", interval="1d"):
    try:
        stock = yf.Ticker(ticker)
        # Verify ticker validity
        if stock.info.get('regularMarketPrice', None) is None and stock.info.get('previousClose', None) is None:
            # Fallback check
            hist_check = stock.history(period="1d")
            if hist_check.empty:
                return None, None, "Invalid ticker symbol or delisted stock."
                
        hist = stock.history(period=period, interval=interval)
        if hist.empty:
            return None, None, f"No historical data found for {ticker} over {period}."
            
        info = stock.info
        return hist, info, None
    except Exception as e:
        return None, None, f"API Connection Error: {str(e)}"

# Main Application
def main():
    apply_custom_css()
    
    st.markdown('<p class="main-header">📈 FinSight Market Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Professional-grade real-time equity market data and technical visualization.</p>', unsafe_allow_html=True)

    # Sidebar Navigation & Setup
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/line-chart--v1.png", width=60)
        st.markdown("### FinSight Terminal")
        st.markdown("---")
        
        st.header("🔍 Market Search")
        ticker_input = st.text_input("Ticker Symbol", value="AAPL", placeholder="e.g. MSFT, TSLA").upper().strip()
        
        st.header("⏱️ Timeframe")
        period_options = {
            "1 Day": {"period": "1d", "interval": "5m"},
            "1 Week": {"period": "5d", "interval": "15m"},
            "1 Month": {"period": "1mo", "interval": "1d"},
            "6 Months": {"period": "6mo", "interval": "1d"},
            "1 Year": {"period": "1y", "interval": "1d"}
        }
        selected_period = st.selectbox("Resolution", options=list(period_options.keys()), index=4)
        
        st.markdown("---")
        st.caption("Data provided by Yahoo Finance.")

    if ticker_input:
        # Loading animation
        with st.spinner(f"Aggregating real-time market data for {ticker_input}..."):
            # Simulate a brief delay for UX if cached
            time.sleep(0.5) 
            p_opts = period_options[selected_period]
            hist, info, error_msg = get_stock_data(ticker_input, period=p_opts["period"], interval=p_opts["interval"])

        if error_msg:
            st.error(f"⚠️ **Error loading data:** {error_msg}")
        elif hist is not None and not hist.empty:
            # Successfully fetched data
            company_name = info.get('shortName', ticker_input)
            st.subheader(f"📊 {company_name} ({ticker_input})")
            
            # --- Key Metrics ---
            try:
                latest_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else info.get('previousClose', latest_price)
                price_change = latest_price - prev_close
                pct_change = (price_change / prev_close) * 100 if prev_close != 0 else 0
                
                day_high = info.get('dayHigh', hist['High'].max())
                day_low = info.get('dayLow', hist['Low'].min())
                volume = info.get('volume', hist['Volume'].iloc[-1])
                market_cap = info.get('marketCap', 'N/A')
                
                def format_market_cap(mc):
                    if isinstance(mc, (int, float)):
                        if mc >= 1e12: return f"${mc/1e12:.2f}T"
                        elif mc >= 1e9: return f"${mc/1e9:.2f}B"
                        elif mc >= 1e6: return f"${mc/1e6:.2f}M"
                    return str(mc)

                # Display Metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Live Price", f"${latest_price:.2f}", f"{price_change:.2f} ({pct_change:.2f}%)")
                with col2:
                    st.metric("Day High", f"${day_high:.2f}" if isinstance(day_high, (int, float)) else "N/A")
                with col3:
                    st.metric("Day Low", f"${day_low:.2f}" if isinstance(day_low, (int, float)) else "N/A")
                with col4:
                    st.metric("Market Cap", format_market_cap(market_cap))
                with col5:
                    st.metric("Volume", f"{volume:,.0f}" if isinstance(volume, (int, float)) else "N/A")
            except Exception as metric_err:
                st.warning("⚠️ Some metrics could not be calculated. Displaying available data.")

            st.divider()
            
            # --- Interactive Chart ---
            try:
                hist['20_MA'] = hist['Close'].rolling(window=20).mean()
                hist['50_MA'] = hist['Close'].rolling(window=50).mean()
                
                colors = ['#00ff99' if row['Close'] >= row['Open'] else '#ff4b4b' for index, row in hist.iterrows()]
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                    vertical_spacing=0.03, 
                                    row_width=[0.2, 0.7])
                
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                    name="Price", increasing_line_color='#00ff99', decreasing_line_color='#ff4b4b'
                ), row=1, col=1)
                
                # MAs
                fig.add_trace(go.Scatter(x=hist.index, y=hist['20_MA'], line=dict(color='#e0e0e0', width=1.5), name="20 MA"), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['50_MA'], line=dict(color='#ff9900', width=1.5), name="50 MA"), row=1, col=1)
                
                # Volume
                fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=colors, name="Volume"), row=2, col=1)
                
                fig.update_layout(
                    template="plotly_dark",
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=650,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                fig.update_xaxes(rangeslider_visible=False)
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as chart_err:
                st.error(f"⚠️ Error rendering charts: {chart_err}")

    # Footer
    st.markdown('<div class="footer"><p>FinSight © 2024 | Built with Streamlit & yfinance | For Educational Purposes</p></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
