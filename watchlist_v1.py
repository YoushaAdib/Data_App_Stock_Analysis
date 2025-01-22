from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import yfinance as yf
import dash_bootstrap_components as dbc

# Initialize the Dash app with a dark theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Function to fetch current prices and analyst targets for multiple tickers
def get_stock_data(tickers):
    """Fetch the current prices and analyst targets for multiple stock tickers."""
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            data.append({
                "Ticker": ticker,
                "Current Price (USD)": info.get("currentPrice", "N/A"),
                "Yesterday's Close": info.get("previousClose", "N/A"),
                "Today's Open": info.get("open", "N/A"),
                "Today's High": info.get("dayHigh", "N/A"),
                "Today's Low": info.get("dayLow", "N/A"),
                "Analyst High": info.get("targetHighPrice", "N/A"),
                "Analyst Mean": info.get("targetMeanPrice", "N/A"),
                "Analyst Low": info.get("targetLowPrice", "N/A"),
            })
        except Exception as e:
            data.append({
                "Ticker": ticker,
                "Current Price (USD)": "Error",
                "Yesterday's Close": "N/A",
                "Today's Open": "N/A",
                "Today's High": "N/A",
                "Today's Low": "N/A",
                "Analyst High": "N/A",
                "Analyst Mean": str(e),
                "Analyst Low": "N/A",
            })
    return data

# App Layout
app.layout = html.Div([
    html.H1("Stock Price Viewer", style={'textAlign': 'center', 'fontFamily': 'Roboto'}),

    html.Div([
        html.Label("Enter Stock Tickers (comma-separated):", style={'fontFamily': 'Roboto'}),
        dcc.Input(
            id="ticker-input",
            type="text",
            placeholder="AAPL, MSFT, GOOGL",
            style={'width': '60%', 'margin-right': '10px'}
        ),
        html.Button("Get Prices", id="submit-button", n_clicks=0, style={'margin-left': '10px'})
    ], style={'margin-bottom': '20px', 'fontFamily': 'Roboto'}),

    dash_table.DataTable(
        id="stock-price-table",
        columns=[
            {"name": "Ticker", "id": "Ticker"},
            {"name": "Current Price (USD)", "id": "Current Price (USD)", "presentation": "markdown"},

            {"name": "Yesterday's Close", "id": "Yesterday's Close"},
            {"name": "Today's Open", "id": "Today's Open"},
            {"name": "Today's High", "id": "Today's High"},
            {"name": "Today's Low", "id": "Today's Low"},

            {"name": "Analyst High", "id": "Analyst High"},
            {"name": "Analyst Mean", "id": "Analyst Mean"},
            {"name": "Analyst Low", "id": "Analyst Low"}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'fontFamily': 'Roboto', 'backgroundColor': '#1a1a1a', 'color': '#ffffff'},
        style_header={'backgroundColor': '#333333', 'color': '#ffffff', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'column_id': 'Current Price (USD)'},
                'backgroundColor': '#2a9d8f',
                'color': '#ffffff',
                'fontWeight': 'bold',
            }
        ],
        style_as_list_view=True,  # Compact view
        page_action="native",  # Enable pagination
        sort_action="native",  # Enable sorting
        filter_action="native"  # Enable filtering
    ),

    dcc.Interval(
        id="interval-component",
        interval=60*1000,  # Refresh every 1 minute
        n_intervals=0
    )
], style={'backgroundColor': '#121212', 'color': '#ffffff', 'padding': '20px', 'fontFamily': 'Roboto'})

# Callback to update the table with current data
@app.callback(
    Output("stock-price-table", "data"),
    [Input("submit-button", "n_clicks"), Input("interval-component", "n_intervals")],
    [State("ticker-input", "value")]
)
def update_table(n_clicks, n_intervals, ticker_input):
    if not ticker_input:
        return []
    try:
        # Parse tickers and fetch stock data
        tickers = [ticker.strip().upper() for ticker in ticker_input.split(",")]
        data = get_stock_data(tickers)
        return data
    except Exception as e:
        return [{"Ticker": "Error", "Current Price (USD)": str(e), "Yesterday's Close": "N/A", "Today's Open": "N/A", "Today's High": "N/A", "Today's Low": "N/A", "Analyst High": "N/A", "Analyst Mean": "N/A", "Analyst Low": "N/A"}]

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True, port=8052)
