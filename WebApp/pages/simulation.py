import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/simulation", order=3)

layout = html.Div([
  html.Div([
    html.H1("Simulate A Spacecraft")
  ])
], className="page-base")