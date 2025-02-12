import dash
from dash import html, dcc, callback, Input, Output
from dash.dependencies import State, ALL

from utils.Builder import *
from utils.ElementTypes import *
from utils.Element import *

import numpy as np

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
  dcc.Store(id="persistent-data", storage_type="session"),
  html.Div(id="empty-div"),
  html.Div([
    html.H1("Vehicle Design Suite"),
    html.Div([
      html.Button(
        "Load Parts into Design",
        className="design-button",
        id="design-button",
        disabled=True
      )
    ], className="design-button-container"),
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
          "Cone"
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
        html.Button(
          "Show/Update Design",
          id="save-design-button",
          className="submit-button"
        )
      ], id="save-design-container", className="save-design-container"),
    ], className="dropdown-container", id="upper-container"),
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
      id="element-manipulation",
      className="manipulation-container"
    )
  ]),
  html.Div([
    dcc.Dropdown(
      options=["F15", "E12"],
      placeholder="Select motor type...",
      searchable=True,
      className="dropdown",
      id="motor-dropdown"
    ),
    html.Button(
      "Use Motor",
      className="submit-button",
      id="motor-submit"
    )
  ], className="motor-field", id="motor-field"),
  html.Div(id="finished-button-container", className="finished-button-container")
], className="page-base")


@callback(
  Output("motor-field", "children", allow_duplicate=True),
  Input("motor-submit", "n_clicks"),
  State("motor-dropdown", "value"),
  prevent_initial_call = True
)
def set_motor(n_clicks, motor):
  if n_clicks:
    api.postMotor({"motor": motor})
    api.postMakeTVC()
    return [
      html.Div([
        html.P(f"{motor}", className="summary-row"),
        html.P("Motor Offsets: ", className="arg-text"),
        dcc.Input(placeholder=f"X", type="number", id="move-motor-x", className="arg-input", value=0.0),
        dcc.Input(placeholder=f"Y", type="number", id="move-motor-y", className="arg-input", value=0.0),
        dcc.Input(placeholder=f"Z", type="number", id="move-motor-z", className="arg-input", value=0.0),
        html.Button("Submit Motor Offset", id="submit-motor-offset", className="submit-button", style={"width": "100px"})
      ], className="manipulation-row")
    ]
  else:
    return [
      dcc.Dropdown(options=["F15", "E12"], searchable=True, className="dropdown", id="motor-dropdown"),
      html.Button("Add motor", className="submit-button", id="motor-submit")
    ]


@callback(
  [
    Output("move-motor-x", "value"),
    Output("move-motor-y", "value"),
    Output("move-motor-z", "value")
  ],
  Input("submit-motor-offset", "n_clicks"),
  [
    State("move-motor-x", "value"),
    State("move-motor-y", "value"),
    State("move-motor-z", "value")
  ],
  prevent_initial_call = True
)
def offset_motor(n_clicks, offset_x, offset_y, offset_z):
  if n_clicks:
    api.postMotorAdjustment({"translation": np.array([offset_x, offset_y, offset_z])})
    
  return offset_x, offset_y, offset_z


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
  Output("design-button", "disabled", allow_duplicate=True),
  Input("save-design-button", "n_clicks"),
  prevent_initial_call = True
)
def show_save_button(n_clicks):
  if n_clicks and len(data_dict) > 0:
    return False
  
  return True


@callback(
  [
    Output("parts-div", "children"),
    Output("design-button", "disabled", allow_duplicate=True)
  ],
  Input("create-element-button", "n_clicks"),
  prevent_initial_call = True
)
def make_parts(n_clicks):
  global data_dict
  
  if n_clicks:
    global part_arg_values
    global part_args
    global part_obj
    global part_obj_dict
    global part_name
    global is_static
    
    params = {arg_name: value for arg_name, value in zip(part_args.keys(), part_arg_values)}
    params.update({"is_static": is_static})
    data_dict[part_name] = ConfigDict(Type=part_obj, Args=part_obj_dict(**params))
    
    return "", False
  
  return "", True


@callback(
  Output("element-manipulation", "children"),
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
        html.Div([
          html.P(line + "}", className="summary-row"),
          html.P("Offsets: ", className="arg-text"),
          dcc.Input(placeholder=f"X", type="number", id={"type": "x", "index": idx}, className="arg-input", value=0.0),
          dcc.Input(placeholder=f"Y", type="number", id={"type": "y", "index": idx}, className="arg-input", value=0.0),
          dcc.Input(placeholder=f"Z", type="number", id={"type": "z", "index": idx}, className="arg-input", value=0.0),
          html.Button("Submit", id={"type": "button", "index": idx}, className="submit-button", style={"width": "75px"})
        ], className="manipulation-row") for idx, line in enumerate(summary)
      ]
    else:
      return [
        "Cannot save an empty design! Add parts first."
      ], []


@callback(
  [
    Output({"type": "x", "index": ALL}, "value"),
    Output({"type": "y", "index": ALL}, "value"),
    Output({"type": "z", "index": ALL}, "value"),
  ],
  Input({"type": "button", "index": ALL}, "n_clicks"),
  [
    State({"type": "x", "index": ALL}, "value"),
    State({"type": "y", "index": ALL}, "value"),
    State({"type": "z", "index": ALL}, "value")
  ],
  prevent_initial_call = True
)
def submit_offset(n_clicks, x_vals, y_vals, z_vals):
  if n_clicks:
    idx = 0
    global data_dict
    part_ids = list(data_dict.keys())
    
    print(part_ids)
    for x, y, z in zip(x_vals, y_vals, z_vals):
      api.postElementAdjustment({"id": f"{part_ids[idx]}", "translation": np.array([x, y, z])})
      print(f"{part_ids[idx]} moved to [{x}, {y}, {z}]")
      if idx + 1 == len(part_ids):
        break
      
      idx += 1
    
    return x_vals, y_vals, z_vals


@callback(
  [
    Output("upper-container", "children"),
    Output("finished-button-container", "children")
  ],
  Input("design-button", "n_clicks"),
  prevent_initial_call = True
)
def build(n_clicks):
  if n_clicks:
    global data_dict
    for name, config in data_dict.items():
      api.postAddElement({name: config})
    
    api.postBuildDesign()
    
    return (
      "Loaded all parts into the design! Make sure to submit the final part offsets before clicking 'Save Design'.",
      html.Button("Finish", id="finished-button", className="finished-button")
    )


@callback(
  Output("empty-div", "children"),
  Input("finished-button", "n_clicks"),
  prevent_initial_call = True
)
def finish(n_clicks):
  if n_clicks:
    api.postLockStaticElements()
    api.postSetTVC({"x": 0.0, "y": 0.0})
    return "Finished design! Continue to Simulation page."
  else:
    return ""
