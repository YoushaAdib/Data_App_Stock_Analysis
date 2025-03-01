import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime
from pytz import timezone

# Initialize the app
app = dash.Dash(__name__)
app.title = "Stock Rader"

# Define app layout
app.layout = html.Div(
    style={
        "backgroundColor": "#121212",
        "color": "#ffffff",
        "fontFamily": "Roboto",
        "minHeight": "100vh",
        "padding": "20px",
    },
    children=[
        # App header
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "marginBottom": "20px",
            },
            children=[
                html.H1("Stock Rader", style={"margin": 0}),
                html.Div(
                    id="clocks",
                    style={"display": "flex", "gap": "20px"},
                ),
            ],
        ),

        # Input for stock tickers
        html.Div(
            style={"marginBottom": "20px"},
            children=[
                dcc.Input(
                    id="ticker-input",
                    type="text",
                    placeholder="Enter tickers (comma separated)",
                    style={
                        "width": "60%",
                        "padding": "10px",
                        "borderRadius": "5px",
                        "border": "1px solid #555",
                        "backgroundColor": "#222",
                        "color": "#fff",
                    },
                ),
                html.Button(
                    "Search",
                    id="search-button",
                    style={
                        "marginLeft": "10px",
                        "padding": "10px 20px",
                        "backgroundColor": "#1f77b4",
                        "color": "#fff",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer",
                    },
                ),
            ],
        ),

        # Table for stock data
        dash_table.DataTable(
            id="stock-table",
            style_header={"backgroundColor": "#333", "color": "#fff"},
            style_cell={
                "backgroundColor": "#222",
                "color": "#fff",
                "border": "1px solid #444",
                "textAlign": "center",
                "fontFamily": "Roboto",
            },
        ),

        # Dropdowns for ticker, interval, duration, and chart type
        html.Div(
            style={"marginTop": "20px", "display": "flex", "gap": "10px"},
            children=[
                dcc.Dropdown(
                    id="ticker-dropdown",
                    placeholder="Select a ticker",
                    style={"backgroundColor": "#fff", "color": "#000", "flex": "1"},
                ),
                dcc.Dropdown(
                    id="interval-dropdown",
                    options=[
                        {"label": "1 Minute", "value": "1m"},
                        {"label": "15 Minutes", "value": "15m"},
                        {"label": "1 Hour", "value": "1h"},
                        {"label": "1 Day", "value": "1d"},
                    ],
                    placeholder="Select an interval",
                    style={"backgroundColor": "#fff", "color": "#000", "flex": "1"},
                ),
                dcc.Dropdown(
                    id="duration-dropdown",
                    options=[
                        {"label": "1 Day", "value": "1d"},
                        {"label": "5 Days", "value": "5d"},
                        {"label": "1 Month", "value": "1mo"},
                        {"label": "3 Months", "value": "3mo"},
                        {"label": "1 Year", "value": "1y"},
                    ],
                    placeholder="Select a duration",
                    style={"backgroundColor": "#fff", "color": "#000", "flex": "1"},
                ),
                dcc.Dropdown(
                    id="chart-type-dropdown",
                    options=[
                        {"label": "Line Chart", "value": "line"},
                        {"label": "Candlestick Chart", "value": "candlestick"},
                    ],
                    placeholder="Select a chart type",
                    style={"backgroundColor": "#fff", "color": "#000", "flex": "1"},
                ),
            ],
        ),

        # Main stock price chart
        dcc.Graph(
            id="stock-chart",
            style={"marginTop": "20px"},
        ),

        # Indicator chart
        dcc.Graph(
            id="indicator-chart",
            style={"marginTop": "20px"},
        ),

        # Interval for auto-refresh (Table and Chart)
        dcc.Interval(
            id="interval",
            interval=60*1000,  # 1 minute
            n_intervals=0
        ),

        # Interval for live clock
        dcc.Interval(
            id="clock-interval",
            interval=1000,  # 1 second
            n_intervals=0
        ),
    ],
)

# Update clocks
@app.callback(Output("clocks", "children"), [Input("clock-interval", "n_intervals")])
def update_clocks(_):
    london_time = datetime.now(timezone("Europe/London")).strftime("%H:%M:%S")
    new_york_time = datetime.now(timezone("America/New_York")).strftime("%H:%M:%S")
    return [
        html.Div(f"London: {london_time}"),
        html.Div(f"New York: {new_york_time}"),
    ]

# Calculate RSI
import numpy as np
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Update table and dropdown options
@app.callback(
    [Output("stock-table", "data"), Output("stock-table", "columns"), Output("ticker-dropdown", "options")],
    [Input("search-button", "n_clicks"), Input("ticker-input", "value")],
    prevent_initial_call=True,
)
def update_table_and_dropdown(n_clicks, tickers):
    if not tickers:
        return [], [], []

    tickers = [t.strip() for t in tickers.split(",")]
    data = []
    options = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period="1mo")
        close_price = history["Close"][-1] if not history.empty else 0
        open_price = history["Open"][-1] if not history.empty else 0
        beta = info.get("beta", "N/A")

        # Calculate RSI for the last available period
        rsi = calculate_rsi(history['Close']).iloc[-1] if not history.empty else None

        data.append(
            {
                "Ticker": ticker,
                "Company Name": info.get("shortName", ticker),
                "Current Price": round(info.get("currentPrice", 0), 2),
                "Day Range": f"{info.get('dayLow', 0)} - {info.get('dayHigh', 0)}",
                "52W Range": f"{info.get('fiftyTwoWeekLow', 0)} - {info.get('fiftyTwoWeekHigh', 0)}",
                "Close - Open": f"{round(close_price, 2)} - {round(open_price, 2)}",
                "Beta": beta,
                "Trading Volume": f"{info.get('volume', 0):,}",
                "RSI": round(rsi, 2) if rsi else "N/A",
            }
        )

        options.append({"label": ticker, "value": ticker})

    columns = [
        {"name": col, "id": col} for col in [
            "Ticker", "Company Name", "Current Price", "Day Range", "52W Range", "Close - Open", "Beta", "Trading Volume", "RSI"
        ]
    ]

    return data, columns, options

# Update main chart and indicator chart
@app.callback(
    [Output("stock-chart", "figure"), Output("indicator-chart", "figure")],
    [
        Input("ticker-dropdown", "value"),
        Input("interval-dropdown", "value"),
        Input("duration-dropdown", "value"),
        Input("chart-type-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def update_charts(selected_ticker, selected_interval, selected_duration, chart_type):
    if not selected_ticker or not selected_interval or not selected_duration or not chart_type:
        return go.Figure(), go.Figure()

    stock = yf.Ticker(selected_ticker)
    history = stock.history(interval=selected_interval, period=selected_duration)

    # Main chart
    fig_main = go.Figure()
    if chart_type == "line":
        fig_main.add_trace(
            go.Scatter(x=history.index, y=history["Close"], mode="lines", line=dict(color="#89CFF0"))
        )
    elif chart_type == "candlestick":
        fig_main.add_trace(
            go.Candlestick(
                x=history.index,
                open=history["Open"],
                high=history["High"],
                low=history["Low"],
                close=history["Close"],
            )
        )

    # Add trading volume as a bar chart, colored by positive (green) or negative (red) trading sentiment
    colors = ["green" if history["Close"][i] >= history["Open"][i] else "red" for i in range(len(history))]
    fig_main.add_trace(
        go.Bar(
            x=history.index,
            y=history["Volume"],
            marker_color=colors,
            yaxis="y2",
        )
    )

    fig_main.update_layout(
        template="plotly_dark",
        title=f"{selected_ticker} Trends ({selected_interval} Interval, {selected_duration} Duration)",
        xaxis_title="Time",
        yaxis_title="Price",
        yaxis2={
            "title": "Volume",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
        },
        showlegend=False,
    )

    # Indicator chart
    fig_indicator = go.Figure()
    fig_indicator.add_trace(
        go.Scatter(x=history.index, y=calculate_rsi(history["Close"]), mode="lines", line=dict(color="orange"), name="RSI")
    )

    fig_indicator.update_layout(
        template="plotly_dark",
        title="Indicator Trends (RSI)",
        xaxis_title="Time",
        yaxis_title="Indicator Value",
        showlegend=True,
    )

    return fig_main, fig_indicator

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8052)
