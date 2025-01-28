from dash import Dash, html
import plotly.express as px

app = Dash()

app.layout = [
  html.Title(children="Rocket Simulation App", className="title")
]

if __name__ == "__main__":
  app.run(debug=True)