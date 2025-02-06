import dash
from dash import html, dcc, callback, Input, Output
from dash.dependencies import State
import asyncio

dash.register_page(__name__, path="/simulation", order=3)

from core import api

asyncio.run(api.postConnectSerial())

layout = html.Div([
  html.Div([
    html.H1("Vehicle Simulation"),
    html.Div([
      dcc.Dropdown(options=[
        str(port) for port in api.serial_manager.availablePorts()
      ], id="port-dropdown", className="dropdown"),
      dcc.Dropdown(options=[
        115200,
        9600
      ], id="baud-rate-dropdown", className="dropdown"),
      html.Button("Connect", id="connect-button", className="submit-button")
    ], className="serial-container"),
    html.Div("Connection Status: ...", id="status-div", className="status-div"),
    html.Div([
      html.Button("Run Simulation Without Serial", id="bypass-serial-button", className="bypass-button")
    ], className="bypass-container"),
    html.Div(id="simulation-container", className="simulation-container")
  ])
], className="page-base")


@callback(
  Output("status-div", "children"),
  Input("connect-button", "n_clicks"),
  [
    State("port-dropdown", "value"),
    State("baud-rate-dropdown", "value")
  ],
  prevent_initial_call = True
)
def try_connecting(n_clicks, port, baud_rate):
  if n_clicks:
    if port is not None and baud_rate is not None:
      res = asyncio.run(api.postConnectSerial({"port": port, "baud_rate": baud_rate}))
      print(res)
      if res["res"]:
        return "Connection Status: SUCCESS"
      else:
        return "Connection Status: FAILED"
  
  return "Connection Status: ..."


