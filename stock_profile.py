import os
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import yfinance as yf

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


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
                financials[period][statement] = pd.DataFrame(financials[period][statement]).reset_index()
        return financials
    except Exception as e:
        return {"error": str(e)}


# Layout components
def generate_financial_table(df):
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, className="mb-4")


def generate_tabs(data, period):
    return dbc.Tabs(
        [
            dbc.Tab(generate_financial_table(data[period]["Profit & Loss"]), label="Profit & Loss"),
            dbc.Tab(generate_financial_table(data[period]["Balance Sheet"]), label="Balance Sheet"),
            dbc.Tab(generate_financial_table(data[period]["Cash Flow"]), label="Cash Flow")
        ],
        className="mt-3"
    )


# App Layout
app.layout = dbc.Container(
    [
        html.H1("Stock Profiling & Analysis", className="my-4 text-center"),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Input(
                        id="ticker-input",
                        type="text",
                        placeholder="Enter Stock Ticker (e.g., AAPL)",
                        className="form-control mb-3",
                        debounce=True
                    ),
                    width=4,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="period-selector",
                        options=[
                            {"label": "Annual", "value": "Annual"},
                            {"label": "Quarterly", "value": "Quarterly"}
                        ],
                        value="Annual",
                        className="form-control mb-3"
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button("Fetch Data", id="fetch-button", color="primary", className="w-100 mb-3"),
                    width=4,
                ),
            ],
            className="align-items-center",
        ),
        html.Div(id="output-section"),
    ],
    fluid=True,
)


# Callbacks
@app.callback(
    Output("output-section", "children"),
    [Input("fetch-button", "n_clicks"), Input("ticker-input", "value"), Input("period-selector", "value")]
)
def update_output(n_clicks, ticker, period):
    if not ticker:
        return html.Div("Please enter a valid stock ticker.", className="text-danger text-center")

    financials = fetch_financials(ticker.upper())

    if "error" in financials:
        return html.Div(f"Error fetching data: {financials['error']}", className="text-danger text-center")

    return generate_tabs(financials, period)


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
