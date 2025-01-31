import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/simulation")

layout = html.Div([
  html.H1("Simulation page")
])