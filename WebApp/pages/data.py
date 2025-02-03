import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/data", order=4)

from core import api

layout = html.Div([
  html.Div([
    html.H1("Data Analysis Suite")
  ])
], className="page-base")