import dash
from dash import html, dcc, callback, Input, Output
from inspect import signature

from utils.ElementTypes import *

ElementTypes = {
  "CylinderDictD": CylinderDictD,
  "TubeDictD": TubeDictD,
  "ConeDictD": ConeDictD,
  "HollowConeDictD": HollowConeDictD,
  "CylinderDictS": CylinderDictS,
  "TubeDictS": TubeDictS,
  "ConeDictS": ConeDictS,
  "HollowConeDictS": HollowConeDictS,
}

dash.register_page(__name__, path="/design")

from core import api

layout = html.Div([
  html.Div([
    html.H1("Spacecraft Design"),
    html.Div([
      dcc.Input(
        type="text",
        placeholder="Enter part name...",
        id="name-entry",
        className="text-field"
      ),
      dcc.Dropdown(
        [
          "Cylinder",
          "Tube",
          "Cone",
          "HollowCone"
        ],
        searchable=True,
        id="element-dropdown",
        className="dropdown",
        placeholder="Select element type..."
      ),
      dcc.Dropdown(
        [
          "Static",
          "Dynamic"
        ],
        searchable=True,
        id="dynamic-dropdown",
        className="dropdown",
        placeholder="Select static or dynamic type..."
      )
    ], className="dropdown-container"),
    html.Div(
      id="element-fields",
      className="fields-container"
    )
  ])
], className="page-base")



@callback(
  Output("element-fields", "children"),
  [
    Input("name-entry", "value"),
    Input("element-dropdown", "value"),
    Input("dynamic-dropdown", "value")
  ],
  prevent_initial_call = True
)
def create_element_fields(name, element_name, dynamic_or_static):
  if name and element_name and dynamic_or_static:
    dict_type = element_name + "Dict" + dynamic_or_static[0]
    obj = ElementTypes[dict_type]
    sig = signature(obj.__init__)
    args = sig.parameters.keys()
    return [dcc.Input(placeholder=f"{arg.title()}", className="test-field") for arg in args]
  
  return []
