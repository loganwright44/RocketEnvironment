import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/design")

layout = html.Div([
  html.H1("Spacecraft Design")
], className="page-base")