from dash_iconify import DashIconify
from dash import Dash, html,  Output, Input, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

app = Dash(__name__)

sc = html.Div(
    [
        dmc.SegmentedControl(
            id="segmented",
            value="ng",
            data=[
                {"value": "react", "label": "react", "icon":},
                {"value": "ng", "label": "Angular"},
                {"value": "svelte", "label": "Svelte"},
                {"value": "vue", "label": "Vue"},
            ],
            mt=10,
        ),
        # dmc.Text(id="segmented-value"),
    ]
)


# @callback(Output("segmented-value", "children"), Input("segmented", "value"))
# def select_value(value):
#     return value

app.layout = sc

if __name__ == "__main__":
    app.run_server(debug=True)
