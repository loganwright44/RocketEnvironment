import dash
from dash import Dash, html, dcc
import plotly.express as px

app = Dash(__name__, use_pages=True, external_stylesheets=["./assets/styles.css"])

app.layout = [
  html.Title(children="Rocket Simulation App", className="title"),
  html.Div([
    html.Div(
      dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    ) for page in dash.page_registry.values()
  ]),
  dash.page_container
]

if __name__ == "__main__":
  app.run(debug=True)