import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/motors", order=5)

layout = html.Div([
  html.Div([
    html.P("Estes F-15 Motor", style={"padding": "10px"}),
    html.Img(src="../assets/F15.png", style={"border-radius": "8px", "width": "500px"}),
    html.A("(source)", href="https://www.thrustcurve.org/simfiles/5f4294d20002e900000007e5/", target="_blank", className="dataset-link")
  ], className="motor-data-container"),
  html.Div([
    html.P("Estes E-12 Motor", style={"padding": "10px"}),
    html.Img(src="../assets/E12.png", style={"border-radius": "8px", "width": "500px"}),
    html.A("(source)", href="https://www.thrustcurve.org/simfiles/5f4294d20002e900000007ad/", target="_blank", className="dataset-link")
  ], className="motor-data-container"),
  html.Div([
    html.P("Estes E-9 Motor", style={"padding": "10px"}),
    html.Img(src="../assets/E9.png", style={"border-radius": "8px", "width": "500px"}),
    html.A("(source)", href="https://www.thrustcurve.org/simfiles/5f4294d20002e90000000416/", target="_blank", className="dataset-link")
  ], className="motor-data-container")
], className="page-base")
