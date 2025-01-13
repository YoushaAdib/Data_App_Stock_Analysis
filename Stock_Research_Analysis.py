import os
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import yfinance as yf

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Function to fetch financial data
def fetch_financials(ticker):
    try:
        stock = yf.Ticker(ticker)
        financials = {
            "Annual": {
                "Profit & Loss": stock.financials,
                "Balance Sheet": stock.balance_sheet,
                "Cash Flow": stock.cashflow
            },
            "Quarterly": {
                "Profit & Loss": stock.quarterly_financials,
                "Balance Sheet": stock.quarterly_balance_sheet,
                "Cash Flow": stock.quarterly_cashflow
            }
        }

        # Convert to DataFrames
        for period in financials:
            for statement in financials[period]:
                if financials[period][statement] is not None:
                    df = pd.DataFrame(financials[period][statement]).reset_index()

                    # Replace NaN with 0
                    df.fillna(0, inplace=True)

                    # Ensure columns are numeric before calculation
                    numeric_columns = df.columns[1:]
                    for col in numeric_columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                    # Calculate percentage change between consecutive years
                    for i in range(1, len(numeric_columns) - 1):
                        current_col = numeric_columns[i]
                        previous_col = numeric_columns[i + 1]
                        try:
                            df[f"{current_col}-%"] = (
                                (df[current_col] - df[previous_col]) / abs(df[previous_col]).replace(0, float('inf')) * 100
                            ).fillna(0).round(0)  # No decimals for percentage
                        except Exception as e:
                            print(f"Error calculating percentage change for {current_col} and {previous_col}: {e}")

                    # Format numeric columns with commas and parentheses for negatives
                    def format_number(value):
                        if isinstance(value, (int, float)):
                            value = int(value)  # Convert to integer to remove decimals
                            if value < 0:
                                return f"({abs(value):,})"
                            return f"{value:,}"
                        return value

                    for col in numeric_columns:
                        df[col] = df[col].apply(format_number)

                    # Add color formatting to percentage change columns
                    for col in df.filter(like='%').columns:
                        df[col] = df[col].apply(
                            lambda x: html.Span(
                                f"{x:+.0f} %", style={"color": "green" if x > 0 else "red" if x < 0 else "white"}
                            ) if isinstance(x, (int, float)) and pd.notnull(x) else "0 %"
                        )

                    financials[period][statement] = df.iloc[::-1]  # Reverse the order of rows
                else:
                    financials[period][statement] = pd.DataFrame()  # Empty DataFrame

        # Basic Stock Info
        stock_info = stock.info or {}

        # Financial KPI Data (extended from stock.info)
        kpi_data = {
            "Metric": [
                "Return on Equity", "Debt to Equity", "Current Ratio", "Gross Margins", "Operating Margins", "Profit Margins", "EBITDA Margins", "Quick Ratio", "Payout Ratio", "Beta"
            ],
            "Value": [
                f"{stock_info.get('returnOnEquity', 0) * 100:.0f} %" if stock_info.get('returnOnEquity') is not None else "N/A",
                f"{int(stock_info.get('debtToEquity', 0))}" if stock_info.get('debtToEquity') is not None else "N/A",
                f"{int(stock_info.get('currentRatio', 0))}" if stock_info.get('currentRatio') is not None else "N/A",
                f"{stock_info.get('grossMargins', 0) * 100:.0f} %" if stock_info.get('grossMargins') is not None else "N/A",
                f"{stock_info.get('operatingMargins', 0) * 100:.0f} %" if stock_info.get('operatingMargins') is not None else "N/A",
                f"{stock_info.get('profitMargins', 0) * 100:.0f} %" if stock_info.get('profitMargins') is not None else "N/A",
                f"{stock_info.get('ebitdaMargins', 0) * 100:.0f} %" if stock_info.get('ebitdaMargins') is not None else "N/A",
                f"{int(stock_info.get('quickRatio', 0))}" if stock_info.get('quickRatio') is not None else "N/A",
                f"{stock_info.get('payoutRatio', 0) * 100:.0f} %" if stock_info.get('payoutRatio') is not None else "N/A",
                f"{stock_info.get('beta', 0):.0f}" if stock_info.get('beta') is not None else "N/A",
            ],
        }
        kpi_df = pd.DataFrame(kpi_data)

        return financials, stock_info, kpi_df
    except Exception as e:
        return None, {"error": str(e)}, None

# Layout components
def generate_financial_table(df):
    if df.empty:
        return html.Div("No data available for this section.", className="text-center text-danger")
    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        className="table-dark",
        style={"font-family": "Roboto", "textAlign": "right"},
    )

def generate_tabs(data, period, kpi_df):
    return dbc.Tabs(
        [
            dbc.Tab(generate_financial_table(kpi_df), label="Financial KPIs"),
            dbc.Tab(generate_financial_table(data[period]["Profit & Loss"]), label="Profit & Loss"),
            dbc.Tab(generate_financial_table(data[period]["Balance Sheet"]), label="Balance Sheet"),
            dbc.Tab(generate_financial_table(data[period]["Cash Flow"]), label="Cash Flow"),
        ],
        className="mt-3",
    )

def generate_stock_info(info):
    return html.Div(
        [
            html.H4("Stock Info", className="mt-4", style={"font-family": "Roboto"}),
            dbc.Table(
                [
                    html.Tbody(
                        [
                            html.Tr([html.Td("Name"), html.Td(info.get("longName", "N/A"))]),
                            html.Tr([html.Td("Symbol"), html.Td(info.get("symbol", "N/A"))]),
                            html.Tr([html.Td("Sector"), html.Td(info.get("sector", "N/A"))]),
                            html.Tr([html.Td("Industry"), html.Td(info.get("industry", "N/A"))]),
                            html.Tr([html.Td("Market Cap"), html.Td(f"${info.get('marketCap', 0):,}" if info.get('marketCap') else "N/A")]),
                            html.Tr([html.Td("52 Week High"), html.Td(info.get("fiftyTwoWeekHigh", "N/A"))]),
                            html.Tr([html.Td("52 Week Low"), html.Td(info.get("fiftyTwoWeekLow", "N/A"))]),
                            html.Tr([html.Td("Dividend Yield"), html.Td(info.get("dividendYield", "N/A"))]),
                            html.Tr([html.Td("PE Ratio"), html.Td(info.get("trailingPE", "N/A"))]),
                            html.Tr([html.Td("EPS"), html.Td(info.get("trailingEps", "N/A"))]),
                        ]
                    )
                ],
                bordered=True,
                hover=True,
                striped=True,
                className="table-dark",
                style={"font-family": "Roboto"},
            ),
        ]
    )

# App Layout
app.layout = dbc.Container(
    [
        html.H1(
            "Stock Profiling & Analysis",
            className="my-4 text-center",
            style={"font-family": "Roboto"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Input(
                        id="ticker-input",
                        type="text",
                        placeholder="Enter Stock Ticker (e.g., AAPL)",
                        className="form-control",
                        debounce=True,
                        style={"font-family": "Roboto"},
                    ),
                    width=6,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="period-selector",
                        options=[
                            {"label": "Annual", "value": "Annual"},
                            {"label": "Quarterly", "value": "Quarterly"},
                        ],
                        value="Annual",
                        className="form-control",
                        style={"font-family": "Roboto"},
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Fetch Data", id="fetch-button", color="primary", className="w-100"
                    ),
                    width=2,
                ),
            ],
            className="align-items-center mb-4",
        ),
        html.Div(id="output-section"),
    ],
    fluid=True,
)

# Callbacks
@app.callback(
    Output("output-section", "children"),
    [
        Input("fetch-button", "n_clicks"),
        Input("ticker-input", "value"),
        Input("period-selector", "value"),
    ],
)
def update_output(n_clicks, ticker, period):
    if not ticker:
        return html.Div(
            "Please enter a valid stock ticker.", className="text-danger text-center"
        )

    financials, stock_info, kpi_df = fetch_financials(ticker.upper())

    if stock_info and "error" in stock_info:
        return html.Div(
            f"Error fetching data: {stock_info['error']}",
            className="text-danger text-center",
        )

    return dbc.Tabs(
        [
            dbc.Tab(generate_stock_info(stock_info), label="Info"),
            dbc.Tab(generate_tabs(financials, period, kpi_df), label="Financial Statements"),
        ]
    )

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)