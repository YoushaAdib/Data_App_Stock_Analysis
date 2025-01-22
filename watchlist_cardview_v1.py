from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import yfinance as yf
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# Initialize the Dash app with a dark theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Function to fetch current prices and analyst targets for multiple tickers
def get_stock_data(tickers):
    """Fetch the current prices and additional metrics for multiple stock tickers."""
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            historical = stock.history(interval="1m", period="1d")
            close_prices = historical['Close'].tolist()
            dates = historical.index.strftime('%H:%M:%S').tolist()

            # Calculate price change if both currentPrice and previousClose are available
            current_price = info.get("currentPrice")
            previous_close = info.get("previousClose")
            price_change = (
                float(current_price) - float(previous_close)
                if current_price is not None and previous_close is not None
                else "N/A"
            )

            data.append({
                "Ticker": ticker,
                "Current Price": current_price if current_price else "N/A",
                "Price Change": price_change,
                "Close": previous_close if previous_close else "N/A",
                "Open": info.get("open", "N/A"),
                "Day Range": f"{info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}",
                "52W Range": f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}",
                "Volume Traded": info.get("volume", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "Beta": info.get("beta", "N/A"),
                "Analyst Range": f"{info.get('targetLowPrice', 'N/A')} - {info.get('targetHighPrice', 'N/A')}",
                "Close Prices": close_prices,
                "Dates": dates
            })
        except Exception as e:
            data.append({
                "Ticker": ticker,
                "Error": str(e)
            })
    return data

# Function to create cards for each ticker
def create_stock_cards(data):
    """Generate cards displaying stock information for each ticker."""
    cards = []
    for stock in data:
        if "Error" in stock:
            cards.append(html.Div(f"Error fetching data for {stock['Ticker']}: {stock['Error']}", style={"color": "red"}))
            continue

        trend_color = "#2a9d8f" if stock['Price Change'] != "N/A" and stock['Price Change'] >= 0 else "#e63946"

        # Generate a rich line chart for stock trend
        line_chart = dcc.Graph(
            figure={
                "data": [
                    go.Scatter(
                        x=stock["Dates"],
                        y=stock["Close Prices"],
                        mode="lines+markers",
                        line=dict(color="#2a9d8f", width=2),
                        marker=dict(size=4, color="#2a9d8f"),
                        showlegend=False
                    )
                ],
                "layout": go.Layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=150,
                    xaxis=dict(showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(showgrid=False, zeroline=False, visible=False),
                    paper_bgcolor="#1f1f1f",
                    plot_bgcolor="#1f1f1f",
                )
            },
            config={"displayModeBar": False}
        )

        card = dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.Div(stock["Ticker"], style={"fontWeight": "bold", "fontSize": "20px", "color": "#ffffff"}),
                    html.Div(f"${stock['Current Price']} ({stock['Price Change']:+.2f})" if stock['Price Change'] != "N/A" else f"${stock['Current Price']} (N/A)", style={"fontSize": "18px", "color": trend_color})
                ], style={"display": "flex", "justifyContent": "space-between"})
            ], style={"backgroundColor": "#333333", "padding": "10px"}),
            dbc.CardBody([
                html.Div([
                    html.Div("Open", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "left"}),
                    html.Div(stock['Open'], style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "right"})
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
                html.Div([
                    html.Div("Day Range", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "left"}),
                    html.Div(stock['Day Range'], style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "right"})
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
                html.Div([
                    html.Div("52W Range", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "left"}),
                    html.Div(stock['52W Range'], style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "right"})
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
                html.Div([
                    html.Div("Analyst Range", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "left"}),
                    html.Div(stock['Analyst Range'], style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "right"})
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
                line_chart,
                html.Div([
                    html.Div("Volume", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "left"}),
                    html.Div(f"{stock['Volume Traded']:,}", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "right"})
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
                html.Div([
                    html.Div("Mkt Cap", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "left"}),
                    html.Div(f"${stock['Market Cap']:,}", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "right"})
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
                html.Div([
                    html.Div("Beta", style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "left"}),
                    html.Div(stock['Beta'], style={"fontSize": "14px", "color": "#ffffff", "flex": "1", "textAlign": "right"})
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
            ], style={"backgroundColor": "#1f1f1f", "color": "#ffffff"})
        ], style={"marginBottom": "20px", "border": "1px solid #ffffff", "borderRadius": "8px", "boxShadow": "0 4px 8px rgba(0,0,0,0.2)", "padding": "10px", "width": "300px"})
        cards.append(card)
    return cards

# App Layout
app.layout = html.Div([
    html.Div([
        html.H1("Stock Watchlist", style={'textAlign': 'left', 'fontFamily': 'Fira Sans', 'padding': '10px', 'color': '#2a9d8f'}),
        html.Div([
            dcc.Input(
                id="ticker-input",
                type="text",
                placeholder="AAPL, MSFT, GOOGL",
                style={'width': '300px', 'margin-right': '10px', 'borderRadius': '20px', 'padding': '10px'}
            ),
            html.Button("Search", id="submit-button", n_clicks=0, style={'padding': '10px 20px', 'backgroundColor': '#2a9d8f', 'color': '#ffffff', 'border': 'none', 'borderRadius': '20px', 'cursor': 'pointer'})
        ], style={'float': 'right'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'padding': '10px'}),

    html.Div(id="stock-cards", style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "justifyContent": "center"}),

    dcc.Interval(
        id="interval-component",
        interval=60*1000,  # Refresh every 1 minute
        n_intervals=0
    )
], style={'backgroundColor': '#121212', 'color': '#ffffff', 'padding': '20px', 'fontFamily': 'Roboto'})

# Callback to update the cards with current data
@app.callback(
    Output("stock-cards", "children"),
    [Input("submit-button", "n_clicks"), Input("interval-component", "n_intervals")],
    [State("ticker-input", "value")]
)
def update_cards(n_clicks, n_intervals, ticker_input):
    if not ticker_input:
        return []
    try:
        # Parse tickers and fetch stock data
        tickers = [ticker.strip().upper() for ticker in ticker_input.split(",")]
        data = get_stock_data(tickers)
        return create_stock_cards(data)
    except Exception as e:
        return [html.Div(f"Error: {e}", style={"color": "red"})]

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True, port=8052)
