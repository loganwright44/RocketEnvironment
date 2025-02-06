import dash
from dash import html, dcc, callback, Input, Output
from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import State
import diskcache
from time import sleep

dash.register_page(__name__, path="/simulation", order=3)

from core import api

api.postConnectSerial()
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache=cache)

layout = html.Div([
  html.Div([
    html.H1("Vehicle Simulation"),
    html.Div([
      html.Button(
        "Refresh",
        id="refresh-button",
        className="submit-button"
      ),
      dcc.Dropdown(options=[
        str(port) for port in api.serial_manager.availablePorts()
      ], id="port-dropdown", className="dropdown"),
      dcc.Dropdown(options=[
        115200,
        9600
      ], id="baud-rate-dropdown", className="dropdown"),
      html.Button(
        "Connect",
        id="connect-button",
        className="submit-button"
      )
    ], className="serial-container"),
    html.Div("Connection Status: ...", id="status-div", className="status-div"),
    html.Div([
      html.Button("Run Simulation Without Serial", id="bypass-serial-button", className="bypass-button")
    ], className="bypass-container"),
    html.Div(id="simulation-container", className="simulation-container"),
    html.Div(className="bottom-spacing")
  ])
], className="page-base")


@callback(
  Output("status-div", "children"),
  Input("connect-button", "n_clicks"),
  [
    State("port-dropdown", "value"),
    State("baud-rate-dropdown", "value")
  ],
  prevent_initial_call = True,
  manager = long_callback_manager,
  background = True,
  running=[
    (Output("connect-button", "disabled"), True, False),
    (Output("status-div", "children"), "Connection Status: LOADING...", "")
  ]
)
def try_connecting(n_clicks, port, baud_rate):
  if n_clicks:
    if port is not None and baud_rate is not None:
      res = api.postConnectSerial({"port": port, "baud_rate": baud_rate})
      print(res)
      if res["res"]:
        return "Connection Status: SUCCESS"
      else:
        return "Connection Status: FAILED"
  
  return "Connection Status: ..."


@callback(
  Output("port-dropdown", "options"),
  Input("refresh-button", "n_clicks"),
  prevent_initial_call = True
)
def refresh_port_options(n_clicks):
  if n_clicks:
    return [str(port) for port in api.serial_manager.availablePorts()]


@callback(
  Output("simulation-container", "children"),
  Input("bypass-serial-button", "n_clicks"),
  prevent_initial_call = True,
  manager=long_callback_manager,
  running=[
    (Output("simulation-container", "children"), "Processing...", "")
  ]
)
def force_simulation(n_clicks):
  if n_clicks:
    api.getSimulationResults()
    sleep(1)
    return html.Video(
      src="../assets/simulation.mp4",
      controls=True,
      autoPlay=False,
      loop=False,
      muted=True,
      title="simulation-output"
    )
  
  return ""