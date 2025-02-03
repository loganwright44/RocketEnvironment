import dash
from dash import html, dcc, callback, Input, Output

from utils.Builder import *

part_args = {}
data_dict = {}
part_arg_values = []
part_name = ""
part_obj = None
part_obj_dict = None

DashTypes = {
  "float": "number",
  "str": "text",
  "bool": "number"
}

from utils.ElementTypes import *
from utils.Element import *

ElementDictTypes = {
  "CylinderDictD": CylinderDictD,
  "TubeDictD": TubeDictD,
  "ConeDictD": ConeDictD,
  "HollowConeDictD": HollowConeDictD,
  "CylinderDictS": CylinderDictS,
  "TubeDictS": TubeDictS,
  "ConeDictS": ConeDictS,
  "HollowConeDictS": HollowConeDictS
}

ElementTypes = {
  "Element": Element,
  "Cylinder": Cylinder,
  "Tube": Tube,
  "Cone": Cone
}

dash.register_page(__name__, path="/design", order=2)

from core import api

layout = html.Div([
  html.Div([
    html.H1("Spacecraft Design"),
    html.Div([
      dcc.Input(
        type="text",
        placeholder="Enter part name...",
        id="name-entry",
        className="text-field",
        required=True
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
        placeholder="Select element type...",
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
    html.Div([
      html.Div(
        id="element-fields",
        className="args-container"
      ),
      html.Div(
        id="submit-div",
        className="button-container"
      )
    ], className="args-container"),
    html.Div(
      id="parts-div"
    ),
    html.Div([
      html.Button("Save Design", id="save-design-button", className="submit-button")
    ], id="save-design-container", className="save-design-container")
  ])
], className="page-base")



@callback(
  Output("element-fields", "children"),
  [
    Input("name-entry", "value"),
    Input("element-dropdown", "value"),
    Input("dynamic-dropdown", "value")
  ]
)
def create_element_fields(name, element_name, dynamic_or_static):
  if name and element_name and dynamic_or_static:
    dict_type = element_name + "Dict" + dynamic_or_static[0]
    
    global part_args
    global part_name
    global part_obj
    global part_obj_dict
    
    part_obj_dict = ElementDictTypes[dict_type]
    part_obj = ElementTypes[element_name]
    part_name = name
    part_args = {key: value.__forward_arg__ for key, value in part_obj_dict.__annotations__.items()}
    
    return [html.Div([
        html.P(f"{arg.title()}:", className="args-text"),
        dcc.Input(placeholder=f"{arg.title()}", id={"type": "arg-input", "index": arg}, className="arg-input", type=f"{DashTypes[part_args[arg]]}", required=True)
      ], className="arg-row") for arg in part_args.keys()]
  
  return ""


@callback(
  Output("submit-div", "children"),
  Input({"type": "arg-input", "index": dash.ALL}, "value")
)
def show_submit_button(values):
  if all(values) and len(values) > 0:
    global part_arg_values
    part_arg_values = list(values)
    return html.Button("Create Part", className="submit-button", id="create-element-button")
  else:
    return ""


@callback(
  Output("parts-div", "children"),
  Input("create-element-button", "n_clicks")
)
def make_and_show_parts(n_clicks):
  if n_clicks:
    global part_arg_values
    global part_args
    global part_obj
    global part_obj_dict
    global part_name
    global data_dict
    
    params = {arg_name: value for arg_name, value in zip(part_args.keys(), part_arg_values)}
    data_dict[part_name] = ConfigDict(Type=part_obj, Args=part_obj_dict(**params))
  
  return [
    html.H3(f"{name}", className="part-row") for name in data_dict.keys()
  ]


@callback(
  Output("save-design-container", "children"),
  Input("save-design-button", "n_clicks"),
  prevent_initial_call = True
)
def save_design(n_clicks):
  if n_clicks:
    if len(data_dict) > 0:
      return "Saved!"
    else:
      return [
        "Cannot save an empty design! Add parts first.",
        html.Button("Save Design", id="save-design-button", className="submit-button")
      ]
  
