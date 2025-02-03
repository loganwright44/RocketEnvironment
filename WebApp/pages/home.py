import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/", order=1)

from core import api

layout = html.Div([
  html.Div([
    html.H1("Model Rocket Simulation App"),
    html.Div()
  ])
], className="page-base")