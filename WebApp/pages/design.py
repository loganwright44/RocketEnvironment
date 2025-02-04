import dash
from dash import html, dcc, callback, Input, Output

from utils.Builder import *

data_dict = {}

part_args = {}
data_dict = {}
part_arg_values = []
part_name = ""
part_obj = None
part_obj_dict = None
is_static = False

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
    html.H1("Vehicle Design Suite"),
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
      ),
      html.Div([
        html.Button("Show/Update Design", id="save-design-button", className="submit-button")
      ], id="save-design-container", className="save-design-container"),
      ], className="dropdown-container"),
    html.Div([
      html.Div(
        id="element-fields",
        className="elements-container"
      ),
      html.Div(
        id="submit-div",
        className="button-container"
      )
    ], className="args-container"),
    html.Div(
      id="parts-div",
      className="parts-container"
    ),
    html.Div(
      id="design-display",
      className="design-display"
    ),
    html.Div(
      id="element-manipulation",
      className="manipulation-container"
    )
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
    global is_static
    
    is_static = True if dict_type[-1] == "S" else False
    part_obj_dict = ElementDictTypes[dict_type]
    part_obj = ElementTypes[element_name]
    part_name = name
    part_args = {key: value.__forward_arg__ for key, value in part_obj_dict.__annotations__.items()}
    _ = part_args.pop("is_static")
    
    return [html.Div([
        html.P(f"{arg.title()}: ", className="arg-text"),
        dcc.Input(placeholder=f"{arg.title()}", id={"type": "arg-input", "index": arg}, className="arg-input", type=f"{DashTypes[part_args[arg]]}", required=True)
      ], className="arg-row") for arg in part_args.keys()]
  
  return ""


@callback(
  Output("submit-div", "children"),
  Input({"type": "arg-input", "index": dash.ALL}, "value")
)
def show_submit_button(values):
  if all([value != None for value in values]) and len(values) > 0:
    global part_arg_values
    part_arg_values = list(values)
    return html.Button("Create Part", className="submit-button", id="create-element-button")
  else:
    return ""


@callback(
  Output("parts-div", "children"),
  Input("create-element-button", "n_clicks")
)
def make_parts(n_clicks):
  if n_clicks:
    global part_arg_values
    global part_args
    global part_obj
    global part_obj_dict
    global part_name
    global data_dict
    global is_static
    
    params = {arg_name: value for arg_name, value in zip(part_args.keys(), part_arg_values)}
    params.update({"is_static": is_static})
    data_dict[part_name] = ConfigDict(Type=part_obj, Args=part_obj_dict(**params))
  
  return [
    html.H3(f"{name}", className="part-row") for name in data_dict.keys()
  ]


@callback(
  [
    Output("design-display", "children"),
    Output("element-manipulation", "children")
  ],
  Input("save-design-button", "n_clicks"),
  prevent_initial_call = True
)
def update_design(n_clicks):
  if n_clicks:
    if len(data_dict) > 0:
      for name, config in data_dict.items():
        api.postAddElement({name: config})
      
      summary: str = api.getDesignSummary()["res"]
      summary = summary[1:-2]
      summary = summary.split("}, ")
      
      return [
        html.P(line + "}", className="summary-row") for line in summary
      ], [
        html.Div([
          dcc.Input(placeholder=f"X", type="number", id={"type": "x", "index": idx}, className="arg-input"),
          dcc.Input(placeholder=f"Y", type="number", id={"type": "y", "index": idx}, className="arg-input"),
          dcc.Input(placeholder=f"Z", type="number", id={"type": "z", "index": idx}, className="arg-input")
        ]) for idx in range(len(summary))
      ]
    else:
      return [
        "Cannot save an empty design! Add parts first."
      ], []
  
