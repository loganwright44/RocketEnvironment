import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/data")

from core import api

layout = html.Div([
  html.Div([
    html.H1("Flight Data")
  ])
], className="page-base")