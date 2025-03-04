import dash
from dash import html, dcc, callback, Input, Output, dash_table
import pandas as pd

dash.register_page(__name__, path="/data", order=4)

from core import api

data_dir = "~/Desktop/RocketSimulationApp/WebApp/assets/simulation.csv"
data = pd.read_csv(data_dir)

style_data_conditional = [
  {"if": {"column_id": col}, "backgroundColor": "rgb(145, 75, 75)", "color": "black"} if i % 2 == 0
  else {"if": {"column_id": col}, "backgroundColor": "#e6f7ff", "color": "black"}
  for i, col in enumerate(data.columns)
]

style_data_conditional.append(
    {"if": {"column_id": "Row"}, "minWidth": "80px", "maxWidth": "100px"}
)

layout = html.Div([
  html.Div([
    html.H1("Data Analysis Suite"),
    dash_table.DataTable(
      id="flight-data",
      columns=[{"name": col, "id": col} for col in data.columns],
      data=data.to_dict("records"),
      style_data_conditional=style_data_conditional,
      fixed_columns={"headers": True, "data": 1},
      style_header={"backgroundColor": "rgb(100, 175, 195)", "fontWeight": "bold"},
      style_cell={"minWidth": "100px", "width": "auto", "maxWidth": "300px", "textAlign": "center"},
      page_action="none",
      style_table={"height": "600px", "overflowY": "auto", "width": "100%", "overflowX": "auto"},
    )
  ])
], className="page-base")