import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/", order=1)

from core import api

layout = html.Div([
  html.Div([
    html.H1("Advanced Rocketry Control and Design Test Platform"),
    html.Div([
      html.Video(
        src="/assets/demo.mp4",
        controls=False,
        autoPlay=True,
        loop=True,
        muted=True,
        title="simulation-demo"
      )
    ], className="video-container"),
    html.P("Model rocket running on an Estes F-15 motor with drag and random wind interactions", className="video-quote"),
    html.Div([
      html.P(
        """
        Welcome to the advanced model rocket simulation environment! The purpose of this project is to provide
        a simple testing space for both building dynamic vehicle designs as well as evaluating general control
        algorithms on an actual flight computer. Serial port connection and quaternion state transmission/servo
        angle reception allow for a smooth integration as a HIL testing environment. The intended use for this
        is to evaluate and validate control loops and checking for general kinematics of the rigid bodies.
        """,
        className="body-text"
      )
    ], className="body-text-container")
  ])
], className="page-base")