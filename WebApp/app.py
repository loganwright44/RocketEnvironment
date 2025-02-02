import dash
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px

app = Dash(__name__, use_pages=True, assets_folder="./assets")

from core import api

app.layout = html.Div([
  dcc.Location(id="url", refresh=False),
  html.Title(children="Rocket Simulation App"),
  html.Div([
    html.Div([
      dcc.Link(f"{page['name']}", href=page["relative_path"], className="nav-link", id=f"{page['name']}-link", refresh=True) for page in dash.page_registry.values()
    ], className="nav-container")
  ]),
  dash.page_container,
], className="web-app")


@callback(
  [Output(f"{page['name']}-link", "className") for page in dash.page_registry.values()],
  Input("url", "pathname")
)
def update_active_link(pathname):
  return [
    "nav-link-active" if pathname == f"/{page['name'].lower() if page['name'].lower() != 'home' else ''}" else "nav-link" for page in dash.page_registry.values()
  ]


if __name__ == "__main__":
  app.run(debug=True)