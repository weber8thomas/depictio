import sys

print(sys.path)


# Import necessary libraries
import numpy as np
from dash import html, dcc, Input, Output, State, ALL, MATCH, ctx, callback
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_draggable

import inspect
import pandas as pd
import plotly.express as px
import re
from dash_iconify import DashIconify
import ast
import dash_ag_grid as dag

min_step = 0
max_step = 3
active = 0

SELECTED_STYLE = {
    "display": "inline-block",
    "width": "250px",
    "height": "100px",
    "border": "3px solid",
    "opacity": 1,
}

UNSELECTED_STYLE = {
    "display": "inline-block",
    "width": "250px",
    "height": "100px",
    "opacity": 0.65,
}


app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        {
            "href": "https://fonts.googleapis.com/icon?family=Material+Icons",
            "rel": "stylesheet",
        },
    ],
    suppress_callback_exceptions=True,
    title="Depictio",
)

from depictio.dash.modules.card_component.frontend import (
    design_card,
    register_callbacks_card_component,
)
from depictio.dash.modules.interactive_component.frontend import (
    design_interactive,
    register_callbacks_interactive_component,
)
from depictio.dash.modules.figure_component.frontend import (
    design_figure,
    register_callbacks_figure_component,
)

register_callbacks_card_component(app)
register_callbacks_interactive_component(app)
register_callbacks_figure_component(app)


# from depictio.dash_frontend.utils import (
#     plotly_vizu_dict,
#     specific_params,
#     param_info,
#     base_elements,
#     plotly_bootstrap_mapping,
#     secondary_common_params,
#     secondary_common_params_lite,
# )

from depictio.dash.utils import (
    # create_initial_figure,
    # load_data,
    load_gridfs_file,
    list_workflows_for_dropdown,
    list_data_collections_for_dropdown,
    get_columns_from_data_collection,
)

# from depictio.dash_frontend.modules.card_component.utils import card_design_modal
from depictio.dash.modules.card_component.utils import agg_functions

# Data


def return_gridfs_df(workflow_id: str = None, data_collection_id: str = None):
    df = load_gridfs_file(workflow_id, data_collection_id)
    # print(df)
    return df

# df = return_gridfs_df()

df = load_gridfs_file(workflow_id=None, data_collection_id=None)


# df = pd.read_csv(
#     "https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv"
# )
# print(df)


backend_components = html.Div(
    [
        dcc.Interval(
            id="interval",
            interval=1000,  # Save input value every 1 second
            n_intervals=0,
        ),
        dcc.Interval(
            id="interval_long",
            interval=50000,  # Save input value every 1 second
            n_intervals=0,
        ),
        dcc.Store(id="stored-children", storage_type="memory"),
        dcc.Store(id="stored-layout", storage_type="memory"),
    ]
)

header = html.Div(
    [
        html.H1("Depictio"),
        dmc.Button(
            "Add new component",
            id="add-button",
            size="lg",
            radius="xl",
            variant="gradient",
            n_clicks=0,
        ),
        dbc.Checklist(
            id="edit-dashboard-mode-button",
            # color="secondary",
            style={"margin-left": "20px", "font-size": "22px"},
            # size="lg",
            # n_clicks=0,
            options=[
                {"label": "Edit dashboard", "value": 0},
            ],
            value=[0],
            switch=True,
        ),
        dcc.Store(
            id="stored-edit-dashboard-mode-button",
            storage_type="memory",
            data={"count": 0},
        ),
    ],
)


init_layout = dict()
init_children = list()
app.layout = dbc.Container(
    [
        html.Div(
            [
                backend_components,
                header,
                dash_draggable.ResponsiveGridLayout(
                    id="draggable",
                    clearSavedLayout=True,
                    layouts=init_layout,
                    children=init_children,
                    isDraggable=True,
                    isResizable=True,
                ),
            ],
        ),
    ],
    fluid=False,
)


# @app.callback(
#     Output("collapse", "is_open"),
#     [Input("collapse-button", "n_clicks")],
#     [State("collapse", "is_open")],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open


@app.callback(
    Output({"type": "modal", "index": MATCH}, "is_open"),
    [Input({"type": "btn-done", "index": MATCH}, "n_clicks")],
    prevent_initial_call=True,
)
def close_modal(n_clicks):
    if n_clicks > 0:
        return False
    return True


@app.callback(
    Output({"type": "workflow-selection-label", "index": MATCH}, "data"),
    # Output({"type": "workflow-selection-label", "index": MATCH}, "value"),
    [
        Input("interval_long", "n_intervals")
    ],  # or whatever triggers the workflow dropdown to update
    # prevent_initial_call=True,
)
def set_workflow_options(n_intervals):
    tmp_data = list_workflows_for_dropdown()

    # Return the data and the first value if the data is not empty
    if tmp_data:
        return tmp_data
    else:
        return dash.no_update


@app.callback(
    Output({"type": "datacollection-selection-label", "index": MATCH}, "data"),
    Output({"type": "datacollection-selection-label", "index": MATCH}, "value"),
    Input({"type": "workflow-selection-label", "index": MATCH}, "value"),
    # prevent_initial_call=True,
)
def set_datacollection_options(selected_workflow):
    if not selected_workflow:
        raise dash.exceptions.PreventUpdate

    tmp_data = list_data_collections_for_dropdown(selected_workflow)
    print("set_datacollection_options")
    print(tmp_data)

    # Return the data and the first value if the data is not empty
    if tmp_data:
        return tmp_data, tmp_data[0]["value"]
    else:
        raise dash.exceptions.PreventUpdate


# @app.callback(
#     Output({"type": "modal-body", "index": MATCH}, "children"),
#     [Input({"type": "btn-option", "index": MATCH, "value": ALL}, "n_clicks")],
#     [
#         State({"type": "btn-option", "index": MATCH, "value": ALL}, "id"),
#     ],
#     prevent_initial_call=True,
# )
# def update_modal(n_clicks, ids):
#     # print("update_modal")
#     # print(n_clicks, ids)
#     # print("\n")

#     # visualization_type = "scatter"
#     for n, id in zip(n_clicks, ids):
#         # print(n, id)
#         if n > 0:
#             if id["value"] == "Figure":
#                 # plot_func = plotly_vizu_dict[visualization_type]
#                 # plot_kwargs = dict(x="lifeExp", y="pop", color="continent")
#                 # print(df.columns)
#                 # plot_kwargs = dict(
#                 #     x=df.columns[0], y=df.columns[1], color=df.columns[2]
#                 # )
#                 plot_kwargs = dict()

#                 # figure = plot_func(
#                 #     df,
#                 #     **plot_kwargs,
#                 # )

#                 wfs_list = list_workflows_for_dropdown()
#                 print(wfs_list)

#                 return design_figure(id, wfs_list)
#             elif id["value"] == "Card":
#                 print("Card")
#                 print(n, id)
#                 return design_card(id, df)
#             elif id["value"] == "Interactive":
#                 # print("Interactive")
#                 return design_interactive(id, df)
#     return []


# def find_ids_recursive(dash_component):
#     """
#     Recursively search for ids in the properties of a Dash component.
#     :param dash_component: The Dash component to search in
#     :return: A list of all ids found
#     """
#     if isinstance(dash_component, dict) and "props" in dash_component:
#         # print(f"Inspecting {dash_component.get('type')}")
#         if "id" in dash_component["props"]:
#             id = dash_component["props"]["id"]
#             # print(f"Found id: {id}")
#             yield id
#         if "children" in dash_component["props"]:
#             children = dash_component["props"]["children"]
#             if isinstance(children, list):
#                 for child in children:
#                     yield from find_ids_recursive(child)
#             elif isinstance(children, dict):
#                 yield from find_ids_recursive(children)


# @app.callback(
#     Output({"type": "add-content", "index": MATCH}, "children"),
#     [
#         Input({"type": "btn-done", "index": MATCH}, "n_clicks"),
#     ],
#     [
#         State({"type": "modal-body", "index": MATCH}, "children"),
#         State({"type": "btn-done", "index": MATCH}, "id"),
#     ],
#     # prevent_initial_call=True,
# )
# def update_button(n_clicks, children, btn_id):
#     # print("update_button")
#     # children = [children[4]]
#     # print(children)

#     btn_index = btn_id["index"]
#     # print(n_clicks, btn_id)
#     # print([sub_e for e in children for sub_e in list(find_ids_recursive(e))])
#     # print("\n")

#     # print(f"Inspecting children:")
#     box_type = [sub_e for e in children for sub_e in list(find_ids_recursive(e))][0][
#         "type"
#     ]
#     print(box_type)
#     # print(children)
#     # print(box_type)
#     # print(f"Found ids: {all_ids}")

#     if box_type == "workflow-selection-label":
#         raise dash.exceptions.PreventUpdate

#     div_index = 0 if box_type == "segmented-control-visu-graph" else 2
#     if box_type:
#         if box_type == "segmented-control-visu-graph":
#             children = [children[4]]
#             child = children[div_index]["props"]["children"][0]["props"][
#                 "children"
#             ]  # Figure
#             child["props"]["id"]["type"] = (
#                 "updated-" + child["props"]["id"]["type"]
#             )  # Figure

#             # print(child)
#             # print("OK")
#         elif box_type == "card":
#             # print(children)
#             child = children[div_index]["props"]["children"][1]["props"]["children"][
#                 1
#             ]  # Card
#             # print(child)
#             child["props"]["children"]["props"]["id"]["type"] = (
#                 "updated-" + child["props"]["children"]["props"]["id"]["type"]
#             )  # Figure
#         elif box_type == "input":
#             # print(children)
#             child = children[div_index]["props"]["children"][1]["props"]["children"][
#                 1
#             ]  # Card
#             # print(child)
#             child["props"]["children"]["props"]["id"]["type"] = (
#                 "updated-" + child["props"]["children"]["props"]["id"]["type"]
#             )  # Figure
#         # elif box_type == "input":
#         #     child = children[0]["props"]["children"][1]["props"]["children"] # Card
#         #     print(child)
#         #     child["props"]["children"]["props"]["id"]["type"] = "updated-" + child["props"]["children"]["props"]["id"]["type"] # Figure

#         # edit_button = dbc.Button(
#         #     "Edit",
#         #     id={
#         #         "type": "edit-button",
#         #         "index": f"edit-{btn_id}",
#         #     },
#         #     color="secondary",
#         #     style={"margin-left": "10px"},
#         #     # size="lg",
#         # )

#         edit_button = dmc.Button(
#             "Edit",
#             id={
#                 "type": "edit-button",
#                 "index": f"edit-{btn_index}",
#             },
#             color="gray",
#             variant="filled",
#             leftIcon=DashIconify(icon="basil:edit-solid", color="white"),
#         )

#         remove_button = dmc.Button(
#             "Remove",
#             id={"type": "remove-button", "index": f"remove-{btn_index}"},
#             color="red",
#             variant="filled",
#             leftIcon=DashIconify(icon="jam:trash", color="white"),
#         )

#         new_draggable_child = html.Div(
#             [
#                 remove_button,
#                 edit_button,
#                 child,
#             ],
#             id=f"draggable-{btn_index}",
#         )

#         return new_draggable_child

#     else:
#         return html.Div()

#     # print("\nEND")

#     # if n_clicks > 0:
#     #     # print(children)
#     #     # figure = children[0]["props"]["children"][0]["props"]["children"]["props"]["figure"]
#     #     # print(children)
#     #     # print(list(child["props"].keys()))
#     #     # print(child_id)
#     #     # child = children[0]["props"]["children"][0]["props"]["children"]["props"]["children"]
#     #     # print(child)
#     #     # if child["props"]["type"] is not "Card":
#     #     # else:
#     #     #     child["props"]["children"]["type"] = (
#     #     #         "updated-" + child["props"]["id"]["type"]
#     #     #     )

#     #     # print(child)
#     #     # # print(figure)
#     #     # return dcc.Graph(
#     #     #     figure=figure, id={"type": "graph", "index": btn_id["index"]}
#     #     # )


# Add a callback to update the isDraggable property
@app.callback(
    [
        Output("draggable", "isDraggable"),
        Output("draggable", "isResizable"),
        Output("add-button", "disabled"),
    ],
    [Input("edit-dashboard-mode-button", "value")],
)
def freeze_layout(value):
    # switch based on button's value
    switch_state = True if len(value) > 0 else False
    if switch_state is False:
        return False, False, True
    else:
        return True, True, False


@app.callback(
    Output({"type": "stepper-basic-usage", "index": MATCH}, "active"),
    Output({"type": "next-basic-usage", "index": MATCH}, "disabled"),
    Input({"type": "back-basic-usage", "index": MATCH}, "n_clicks"),
    Input({"type": "next-basic-usage", "index": MATCH}, "n_clicks"),
    Input({"type": "workflow-selection-label", "index": MATCH}, "value"),
    Input({"type": "datacollection-selection-label", "index": MATCH}, "value"),
    Input({"type": "btn-option", "index": MATCH, "value": ALL}, "n_clicks"),
    State({"type": "stepper-basic-usage", "index": MATCH}, "active"),
    prevent_initial_call=True,
)
def update(back, next_, workflow_selection, data_selection, btn_component, current):
    print("update")
    print(back, next_, current, workflow_selection, data_selection, btn_component)

    if back is None and next_ is None:
        if workflow_selection is not None and data_selection is not None:
            disable_next = False
        else:
            disable_next = True

        print(current, disable_next)
        return current, disable_next
    else:
        button_id = ctx.triggered_id
        print(button_id)
        step = current if current is not None else active

        if button_id["type"] == "back-basic-usage":
            step = step - 1 if step > min_step else step
            return step, False

        else:
            step = step + 1 if step < max_step else step
            return step, False


@app.callback(
    [
        Output({"type": "btn-option", "index": MATCH, "value": "Figure"}, "style"),
        Output({"type": "btn-option", "index": MATCH, "value": "Card"}, "style"),
        Output({"type": "btn-option", "index": MATCH, "value": "Interactive"}, "style"),
    ],
    [
        Input({"type": "btn-option", "index": MATCH, "value": "Figure"}, "n_clicks"),
        Input({"type": "btn-option", "index": MATCH, "value": "Card"}, "n_clicks"),
        Input(
            {"type": "btn-option", "index": MATCH, "value": "Interactive"}, "n_clicks"
        ),
    ],
    prevent_initial_call=True,
)
def update_button_style(figure_clicks, card_clicks, interactive_clicks):
    ctx_triggered = dash.callback_context.triggered

    # Reset all buttons to unselected style
    figure_style = UNSELECTED_STYLE
    card_style = UNSELECTED_STYLE
    interactive_style = UNSELECTED_STYLE

    # Check which button was clicked and update its style
    if ctx_triggered:
        button_id = ctx_triggered[0]["prop_id"].split(".")[0]
        button_value = eval(button_id)["value"]

        if button_value == "Figure":
            figure_style = SELECTED_STYLE
        elif button_value == "Card":
            card_style = SELECTED_STYLE
        elif button_value == "Interactive":
            interactive_style = SELECTED_STYLE

    return figure_style, card_style, interactive_style


@app.callback(
    Output({"type": "dropdown-output", "index": MATCH}, "children"),
    Input({"type": "workflow-selection-label", "index": MATCH}, "value"),
    Input({"type": "datacollection-selection-label", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def update_step_2(workflow_selection, data_collection_selection):
    if workflow_selection is not None and data_collection_selection is not None:

        df = return_gridfs_df(workflow_selection, data_collection_selection)
        columnDefs = [{"field": c} for c in list(df.columns)]

        title = dmc.Title("Data previsualization", order=3, align="left", weight=500)
        grid = dag.AgGrid(
            id="get-started-example-basic",
            rowData=df.head(50).to_dict("records"),
            columnDefs=columnDefs,
        )
        layout = [title, html.Hr(), grid]
        return layout
    else:
        return html.Div()


@app.callback(
    Output({"type": "output-stepper-step-3", "index": MATCH}, "children"),
    Output({"type": "store-btn-option", "index": MATCH, "value": ALL}, "data"),
    Input({"type": "workflow-selection-label", "index": MATCH}, "value"),
    Input({"type": "datacollection-selection-label", "index": MATCH}, "value"),
    Input({"type": "btn-option", "index": MATCH, "value": ALL}, "n_clicks"),
    Input({"type": "store-btn-option", "index": MATCH, "value": ALL}, "data"),
    State({"type": "btn-option", "index": MATCH, "value": ALL}, "id"),
    prevent_initial_call=True,
)
def update_step_2(
    workflow_selection,
    data_collection_selection,
    btn_component,
    store_btn_component,
    ids,
):
    if (
        workflow_selection is not None
        and data_collection_selection is not None
        and btn_component is not None
    ):
        print("update_step_2")
        # retrieve value in btn_component that is higher than the previous value in store_btn_component at the same index
        btn_index = [
            i
            for i, (x, y) in enumerate(zip(btn_component, store_btn_component))
            if x > y
        ]
        if btn_index:

            df = return_gridfs_df(workflow_selection, data_collection_selection)

            components_list = ["Figure", "Card", "Interactive"]
            component_selected = components_list[btn_index[0]]
            id = ids[btn_index[0]]
            if component_selected == "Figure":
                return design_figure(id, df), btn_component
            elif component_selected == "Card":
                return design_card(id, df), btn_component
            elif component_selected == "Interactive":
                return design_interactive(id, df), btn_component



        else:
            raise dash.exceptions.PreventUpdate

    else:
        return html.Div(), []


@app.callback(
    [
        Output("draggable", "children"),
        Output("draggable", "layouts"),
        Output("stored-layout", "data"),
        Output("stored-children", "data"),
        Output("stored-edit-dashboard-mode-button", "data"),
    ],
    # [
    #     Input(f"add-plot-button-{plot_type.lower().replace(' ', '-')}", "n_clicks")
    #     for plot_type in AVAILABLE_PLOT_TYPES.keys()
    # ]
    # +
    [
        Input("add-button", "n_clicks"),
        Input("edit-dashboard-mode-button", "value"),
        Input({"type": "remove-button", "index": dash.dependencies.ALL}, "n_clicks"),
        Input({"type": "input-component", "index": dash.dependencies.ALL}, "value"),
        # Input("time-input", "value"),
        Input("stored-layout", "data"),
        Input("stored-children", "data"),
        Input("draggable", "layouts"),
    ],
    [
        State("draggable", "children"),
        State("draggable", "layouts"),
        State("stored-layout", "data"),
        State("stored-children", "data"),
        State("stored-edit-dashboard-mode-button", "data"),
    ],
    prevent_initial_call=True,
)
def update_draggable_children(
    # n_clicks, selected_year, current_draggable_children, current_layouts, stored_figures
    *args,
):
    # for arg in [*args]:
    #     print("\n")
    #     print(arg)
    # print("______________________")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    ctx = dash.callback_context
    ctx_triggered = ctx.triggered
    print(f"CTX triggered: {ctx.triggered}")

    triggered_input = ctx.triggered[0]["prop_id"].split(".")[0]
    print(triggered_input)
    print(f"REMOVE BUTTON ARGS {args[-10]}")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    stored_layout_data = args[-8]
    stored_children_data = args[-7]
    new_layouts = args[-6]
    # print(args[-10])

    # remove-button -7
    # selected_year = args[-6]

    current_draggable_children = args[-5]
    current_layouts = args[-4]
    stored_layout = args[-3]
    stored_figures = args[-2]
    stored_edit_dashboard = args[-1]

    switch_state = True if len(args[-11]) > 0 else False
    switch_state_index = -1 if switch_state is True else -1
    # print(f"Switch state: {switch_state}")
    # print(f"Switch state value: {stored_edit_dashboard}")

    filter_dict = {}

    # Enumerate through all the children
    for j, child in enumerate(current_draggable_children):
        # print(f"TOTO-{j}")
        # print(child["props"]["id"])
        # print(child["props"]["children"][switch_state_index]["props"])

        # Filter out those children that are not input components
        if (
            "-input" in child["props"]["id"]
            and "value"
            in child["props"]["children"][switch_state_index]["props"]["children"][-1][
                "props"
            ]
        ):
            # Extract the id and the value of the input component
            # print(f"TATA-{j}")

            id_components = child["props"]["children"][switch_state_index]["props"][
                "children"
            ][-1]["props"]["id"]["index"].split("-")[2:]
            value = child["props"]["children"][switch_state_index]["props"]["children"][
                -1
            ]["props"]["value"]

            # Construct the key for the dictionary
            key = "-".join(id_components)

            # Add the key-value pair to the dictionary
            filter_dict[key] = value

    # if current_draggable_children is None:
    #     current_draggable_children = []
    # if current_layouts is None:
    #     current_layouts = dict()

    if "add-button" in triggered_input:
        # print(ctx.triggered[0])
        # print(ctx.triggered[0]["value"])
        n = ctx.triggered[0]["value"]
        # print("add_new_div")
        # print(n)
        # print(app._callback_list)

        # print("index: {}".format(n))
        new_plot_id = f"graph-{n}"
        # print(new_plot_id)

        stepper_dropdowns = html.Div(
            [
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            dmc.Select(
                                id={"type": "workflow-selection-label", "index": n},
                                label=html.H4(
                                    [
                                        DashIconify(icon="flat-color-icons:workflow"),
                                        "Workflow selection",
                                    ]
                                ),
                                data=["Test1", "Test2"],
                                style={
                                    "height": "100%",
                                    "display": "inline-block",
                                    "width": "100%",
                                    # "display": "flex",
                                    # "flex-direction": "column",
                                    # "flex-grow": "0",
                                },
                            )
                        ),
                        dbc.Col(
                            dmc.Select(
                                id={
                                    "type": "datacollection-selection-label",
                                    "index": n,
                                },
                                label=html.H4(
                                    [
                                        DashIconify(icon="bxs:data"),
                                        "Data collection selection",
                                    ]
                                ),
                                data=["Test3", "Test4"],
                                style={
                                    "height": "100%",
                                    "width": "100%",
                                    "display": "inline-block",
                                    # "display": "flex",
                                    # "flex-direction": "column",
                                    # "flex-grow": "0",
                                },
                            )
                        ),
                    ],
                    # style={"width": "80%"},
                ),
                html.Hr(),
                dbc.Row(html.Div(id={"type": "dropdown-output", "index": n})),
            ],
            style={
                "height": "100%",
                "width": "822px",
                # "display": "flex",
                # "flex-direction": "column",
                # "flex-grow": "0",
            },
        )

        stepper_buttons = dbc.Row(
            [
                dcc.Store(
                    id={
                        "type": "store-btn-option",
                        "index": n,
                        "value": "Figure",
                    },
                    data=0,
                    storage_type="memory",
                ),
                dcc.Store(
                    id={
                        "type": "store-btn-option",
                        "index": n,
                        "value": "Card",
                    },
                    data=0,
                    storage_type="memory",
                ),
                dcc.Store(
                    id={
                        "type": "store-btn-option",
                        "index": n,
                        "value": "Interactive",
                    },
                    data=0,
                    storage_type="memory",
                ),
                html.Hr(),
                dbc.Col(
                    dmc.Button(
                        "Figure",
                        id={
                            "type": "btn-option",
                            "index": n,
                            "value": "Figure",
                        },
                        n_clicks=0,
                        # style={
                        #     "display": "inline-block",
                        #     "width": "250px",
                        #     "height": "100px",
                        # },
                        style=UNSELECTED_STYLE,
                        size="xl",
                        color="grape",
                        leftIcon=DashIconify(icon="mdi:graph-box"),
                    )
                ),
                dbc.Col(
                    dmc.Button(
                        "Card",
                        id={
                            "type": "btn-option",
                            "index": n,
                            "value": "Card",
                        },
                        n_clicks=0,
                        # style={
                        #     "display": "inline-block",
                        #     "width": "250px",
                        #     "height": "100px",
                        # },
                        style=UNSELECTED_STYLE,
                        size="xl",
                        color="violet",
                        leftIcon=DashIconify(icon="formkit:number", color="white"),
                    )
                ),
                dbc.Col(
                    dmc.Button(
                        "Interactive",
                        id={
                            "type": "btn-option",
                            "index": n,
                            "value": "Interactive",
                        },
                        n_clicks=0,
                        # style={
                        #     "display": "inline-block",
                        #     "width": "250px",
                        #     "height": "100px",
                        # },
                        style=UNSELECTED_STYLE,
                        size="xl",
                        color="indigo",
                        leftIcon=DashIconify(icon="bx:slider-alt", color="white"),
                    )
                ),
            ]
        )

        new_element = html.Div(
            [
                html.Div(id={"type": "add-content", "index": n}),
                dbc.Modal(
                    id={"type": "modal", "index": n},
                    children=[
                        dbc.ModalHeader(html.H5("Design your new dashboard component")),
                        dbc.ModalBody(
                            [
                                dmc.Stepper(
                                    id={"type": "stepper-basic-usage", "index": n},
                                    active=active,
                                    # color="green",
                                    breakpoint="sm",
                                    children=[
                                        dmc.StepperStep(
                                            label="Data selection",
                                            description="Select your workflow and data collection",
                                            children=stepper_dropdowns,
                                            id={"type": "stepper-step-1", "index": n},
                                        ),
                                        dmc.StepperStep(
                                            label="Component selection",
                                            description="Select your component type",
                                            children=stepper_buttons,
                                            id={"type": "stepper-step-2", "index": n},
                                        ),
                                        dmc.StepperStep(
                                            label="Design your component",
                                            description="Customize your component as you wish",
                                            children=html.Div(
                                                id={
                                                    "type": "output-stepper-step-3",
                                                    "index": n,
                                                }
                                            ),
                                            id={"type": "stepper-step-3", "index": n},
                                        ),
                                        dmc.StepperCompleted(
                                            children=[
                                                dmc.Center(
                                                    [
                                                        dmc.Button(
                                                            "Add to dashboard",
                                                            id={
                                                                "type": "btn-done",
                                                                "index": n,
                                                            },
                                                            n_clicks=0,
                                                            size="xl",
                                                            color="grape",
                                                            style={
                                                                "display": "block",
                                                                "align": "center",
                                                                "height": "100px",
                                                            },
                                                        ),
                                                    ]
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                dmc.Group(
                                    position="center",
                                    mt="xl",
                                    children=[
                                        dmc.Button(
                                            "Back",
                                            id={"type": "back-basic-usage", "index": n},
                                            variant="default",
                                        ),
                                        dmc.Button(
                                            "Next step",
                                            id={"type": "next-basic-usage", "index": n},
                                            disabled=True,
                                        ),
                                    ],
                                ),
                                # dbc.Row(
                                #     [
                                #         dbc.Col(
                                #             dmc.Button(
                                #                 "Figure",
                                #                 id={
                                #                     "type": "btn-option",
                                #                     "index": n,
                                #                     "value": "Figure",
                                #                 },
                                #                 n_clicks=0,
                                #                 style={
                                #                     "display": "inline-block",
                                #                     "width": "250px",
                                #                     "height": "100px",
                                #                 },
                                #                 size="xl",
                                #                 color="grape",
                                #                 leftIcon=DashIconify(
                                #                     icon="mdi:graph-box"
                                #                 ),
                                #             )
                                #         ),
                                #         dbc.Col(
                                #             dmc.Button(
                                #                 "Card",
                                #                 id={
                                #                     "type": "btn-option",
                                #                     "index": n,
                                #                     "value": "Card",
                                #                 },
                                #                 n_clicks=0,
                                #                 style={
                                #                     "display": "inline-block",
                                #                     "width": "250px",
                                #                     "height": "100px",
                                #                 },
                                #                 size="xl",
                                #                 color="violet",
                                #                 leftIcon=DashIconify(
                                #                     icon="formkit:number", color="white"
                                #                 ),
                                #             )
                                #         ),
                                #         dbc.Col(
                                #             dmc.Button(
                                #                 "Interaction",
                                #                 id={
                                #                     "type": "btn-option",
                                #                     "index": n,
                                #                     "value": "Interactive",
                                #                 },
                                #                 n_clicks=0,
                                #                 style={
                                #                     "display": "inline-block",
                                #                     "width": "250px",
                                #                     "height": "100px",
                                #                 },
                                #                 size="xl",
                                #                 color="indigo",
                                #                 leftIcon=DashIconify(
                                #                     icon="bx:slider-alt", color="white"
                                #                 ),
                                #             )
                                #         ),
                                #     ]
                                # ),
                            ],
                            id={"type": "modal-body", "index": n},
                            style={
                                "display": "flex",
                                "justify-content": "center",
                                "align-items": "center",
                                "flex-direction": "column",
                                "height": "100%",
                                "width": "100%",
                            },
                        ),
                    ],
                    is_open=True,
                    size="xl",
                    backdrop=False,
                    style={
                        "height": "100%",
                        "width": "100%",
                        # "display": "flex",
                        # "flex-direction": "column",
                        # "flex-grow": "0",
                    },
                ),
            ],
            id=new_plot_id,
        )

        current_draggable_children.append(new_element)
        new_layout_item = {
            "i": f"{new_plot_id}",
            "x": 10 * ((len(current_draggable_children) + 1) % 2),
            "y": n * 10,
            "w": 6,
            "h": 5,
        }

        # Update the layouts property for both 'lg' and 'sm' sizes
        updated_layouts = {}
        for size in ["lg", "sm"]:
            if size not in current_layouts:
                current_layouts[size] = []
            current_layouts[size] = current_layouts[size] + [new_layout_item]
        return (
            current_draggable_children,
            current_layouts,
            current_layouts,
            current_draggable_children,
            stored_edit_dashboard,
        )

    #     return (
    #         updated_draggable_children,
    #         updated_layouts,
    #         # selected_year,
    #         updated_layouts,
    #         updated_draggable_children,
    #         # selected_year,
    #     )

    # if triggered_input.startswith("add-plot-button-"):
    #     plot_type = triggered_input.replace("add-plot-button-", "")

    #     n_clicks = ctx.triggered[0]["value"]
    #     print(n_clicks)

    #     new_plot_id = f"graph-{n_clicks}-{plot_type.lower().replace(' ', '-')}"
    #     new_plot_type = plot_type
    #     print(new_plot_type)

    #     if "-card" in new_plot_type:
    #         new_plot = html.Div(
    #             create_initial_figure(df, new_plot_type), id=new_plot_id
    #         )
    #     elif "-input" in new_plot_type:
    #         print(new_plot_id)
    #         # input_id = f"{plot_type.lower().replace(' ', '-')}"

    #         new_plot = create_initial_figure(df, new_plot_type, id=new_plot_id)
    #     else:
    #         new_plot = dcc.Graph(
    #             id=new_plot_id,
    #             figure=create_initial_figure(df, new_plot_type),
    #             responsive=True,
    #             style={
    #                 "width": "100%",
    #                 "height": "100%",
    #             },
    #             # config={"staticPlot": False, "editable": True},
    #         )
    #     # print(new_plot)

    #     # new_draggable_child = new_plot
    #     edit_button = dbc.Button(
    #         "Edit",
    #         id={
    #             "type": "edit-button",
    #             "index": f"edit-{new_plot_id}",
    #         },
    #         color="secondary",
    #         style={"margin-left": "10px"},
    #         # size="lg",
    #     )
    #     new_draggable_child = html.Div(
    #         [
    #             dbc.Button(
    #                 "Remove",
    #                 id={"type": "remove-button", "index": f"remove-{new_plot_id}"},
    #                 color="danger",
    #             ),
    #             edit_button,
    #             new_plot,
    #         ],
    #         id=f"draggable-{new_plot_id}",
    #     )
    #     # print(current_draggable_children)
    #     # print(len(current_draggable_children))

    #     updated_draggable_children = current_draggable_children + [new_draggable_child]

    #     # Define the default size and position for the new plot
    #     if "-card" not in new_plot_type:
    #         new_layout_item = {
    #             "i": f"draggable-{new_plot_id}",
    #             "x": 10 * ((len(updated_draggable_children) + 1) % 2),
    #             "y": n_clicks * 10,
    #             "w": 6,
    #             "h": 14,
    #         }
    #     else:
    #         new_layout_item = {
    #             "i": f"draggable-{new_plot_id}",
    #             "x": 10 * ((len(updated_draggable_children) + 1) % 2),
    #             "y": n_clicks * 10,
    #             "w": 4,
    #             "h": 5,
    #         }

    #     # Update the layouts property for both 'lg' and 'sm' sizes
    #     updated_layouts = {}
    #     for size in ["lg", "sm"]:
    #         if size not in current_layouts:
    #             current_layouts[size] = []
    #         updated_layouts[size] = current_layouts[size] + [new_layout_item]

    #     # Store the newly created figure in stored_figures
    #     # stored_figures[new_plot_id] = new_plot

    #     return (
    #         updated_draggable_children,
    #         updated_layouts,
    #         # selected_year,
    #         updated_layouts,
    #         updated_draggable_children,
    #         # selected_year,
    #     )

    # import ast

    # if "-input" in triggered_input and "remove-" not in triggered_input:
    #     input_id = ast.literal_eval(triggered_input)["index"]
    #     updated_draggable_children = []

    #     for j, child in enumerate(current_draggable_children):
    #         if child["props"]["id"].replace("draggable-", "") == input_id:
    #             updated_draggable_children.append(child)
    #         elif (
    #             child["props"]["id"].replace("draggable-", "") != input_id
    #             and "-input" not in child["props"]["id"]
    #         ):
    #             # print(child["props"]["id"]["index"])
    #             index = -1 if switch_state is True else 0
    #             graph = child["props"]["children"][index]
    #             if type(graph["props"]["id"]) is str:
    #                 # Extract the figure type and its corresponding function
    #                 figure_type = "-".join(graph["props"]["id"].split("-")[2:])
    #                 graph_id = graph["props"]["id"]
    #                 updated_fig = create_initial_figure(
    #                     df,
    #                     figure_type,
    #                     input_id="-".join(input_id.split("-")[2:]),
    #                     filter=filter_dict,
    #                 )

    #                 if "-card" in graph_id:
    #                     graph["props"]["children"] = updated_fig

    #                 else:
    #                     graph["props"]["figure"] = updated_fig
    #                 rm_button = dbc.Button(
    #                     "Remove",
    #                     id={
    #                         "type": "remove-button",
    #                         "index": child["props"]["id"],
    #                     },
    #                     color="danger",
    #                 )
    #                 edit_button = dbc.Button(
    #                     "Edit",
    #                     id={
    #                         "type": "edit-button",
    #                         "index": child["props"]["id"],
    #                     },
    #                     color="secondary",
    #                     style={"margin-left": "10px"},
    #                 )
    #                 children = (
    #                     [rm_button, edit_button, graph]
    #                     if switch_state is True
    #                     else [graph]
    #                 )
    #                 updated_child = html.Div(
    #                     children=children,
    #                     id=child["props"]["id"],
    #                 )

    #                 updated_draggable_children.append(updated_child)
    #         else:
    #             updated_draggable_children.append(child)

    #     return (
    #         updated_draggable_children,
    #         current_layouts,
    #         current_layouts,
    #         updated_draggable_children,
    #     )

    # if the remove button was clicked, return an empty list to remove all the plots

    elif "remove-" in triggered_input and [e for e in args[-10] if e]:
        print("\nREMOVE")
        print(triggered_input, type(triggered_input))
        # print(current_draggable_children)
        input_id = ast.literal_eval(triggered_input)["index"]
        # print(input_id)

        # new_filter_dict = filter_dict
        # print(new_filter_dict)
        for child in current_draggable_children:
            # print("-".join(child["props"]["id"].split("-")[1:]))
            # print("-".join(input_id.split("-")[1:]))
            if "-".join(child["props"]["id"].split("-")[1:]) == "-".join(
                input_id.split("-")[1:]
            ):
                current_draggable_children.remove(child)
        #         input_id = "-".join(input_id.split("-")[2:])

        #         # Remove the corresponding entry from filter dictionary
        #         tmp_input_id = "-".join(input_id.split("-")[1:])
        #         if "-".join(input_id.split("-")[1:]) in new_filter_dict:
        #             del new_filter_dict[tmp_input_id]
        #         print(new_filter_dict)

        # updated_draggable_children = []

        # for j, child in enumerate(current_draggable_children):
        #     if child["props"]["id"].replace("draggable-", "") == input_id:
        #         updated_draggable_children.append(child)
        #     elif (
        #         child["props"]["id"].replace("draggable-", "") != input_id
        #         and "-input" not in child["props"]["id"]
        #     ):
        #         # print(child["props"]["id"]["index"])
        #         index = -1 if switch_state is True else 0
        #         graph = child["props"]["children"][index]
        #         if type(graph["props"]["id"]) is str:
        #             print("TEST")
        #             # Extract the figure type and its corresponding function
        #             figure_type = "-".join(graph["props"]["id"].split("-")[2:])
        #             graph_id = graph["props"]["id"]
        #             updated_fig = create_initial_figure(
        #                 df,
        #                 figure_type,
        #                 input_id="-".join(input_id.split("-")[2:]),
        #                 filter=new_filter_dict,
        #             )

        #             if "-card" in graph_id:
        #                 graph["props"]["children"] = updated_fig

        #             else:
        #                 graph["props"]["figure"] = updated_fig
        #             rm_button = dbc.Button(
        #                 "Remove",
        #                 id={
        #                     "type": "remove-button",
        #                     "index": child["props"]["id"],
        #                 },
        #                 color="danger",
        #             )
        #             edit_button = dbc.Button(
        #                 "Edit",
        #                 id={
        #                     "type": "edit-button",
        #                     "index": child["props"]["id"],
        #                 },
        #                 color="secondary",
        #                 style={"margin-left": "10px"},
        #             )
        #             children = (
        #                 [rm_button, edit_button, graph]
        #                 if switch_state is True
        #                 else [graph]
        #             )
        #             updated_child = html.Div(
        #                 children=children,
        #                 id=child["props"]["id"],
        #             )

        #             updated_draggable_children.append(updated_child)
        #     else:
        #         updated_draggable_children.append(child)

        return (
            current_draggable_children,
            new_layouts,
            # selected_year,
            new_layouts,
            current_draggable_children,
            stored_edit_dashboard
            # selected_year,
        )
        # return (
        #     updated_draggable_children,
        #     current_layouts,
        #     current_layouts,
        #     updated_draggable_children,
        # )

    # elif triggered_input == "stored-layout" or triggered_input == "stored-children":
    #     if stored_layout_data and stored_children_data:
    #         return (
    #             stored_children_data,
    #             stored_layout_data,
    #             stored_layout_data,
    #             stored_children_data,
    #         )
    #     else:
    #         # Load data from the file if it exists
    #         loaded_data = load_data()
    #         if loaded_data:
    #             return (
    #                 loaded_data["stored_children_data"],
    #                 loaded_data["stored_layout_data"],
    #                 loaded_data["stored_layout_data"],
    #                 loaded_data["stored_children_data"],
    #             )
    #         else:
    #             return (
    #                 current_draggable_children,
    #                 {},
    #                 stored_layout,
    #                 stored_figures,
    #             )

    elif triggered_input == "draggable":
        return (
            current_draggable_children,
            new_layouts,
            # selected_year,
            new_layouts,
            current_draggable_children,
            stored_edit_dashboard
            # selected_year,
        )

    # div_index = 4 if box_type == "segmented-control-visu-graph" else 2
    # if box_type:
    #     if box_type == "segmented-control-visu-graph":
    #         child = children[div_index]["props"]["children"][0]["props"][
    #             "children"
    #         ]  # Figure
    #         child["props"]["id"]["type"] = (
    #             "updated-" + child["props"]["id"]["type"]
    #         )  # Figure

    #         # print(child)
    #         print("OK")
    #     elif box_type == "card":
    #         # print(children)
    #         child = children[div_index]["props"]["children"][1]["props"]["children"][
    #             1
    #         ]  # Card
    #         print(child)
    #         child["props"]["children"]["props"]["id"]["type"] = (
    #             "updated-" + child["props"]["children"]["props"]["id"]["type"]
    #         )  # Figure
    #     elif box_type == "input":
    #         # print(children)
    #         child = children[div_index]["props"]["children"][1]["props"]["children"][
    #             1
    #         ]  # Card
    #         print(child)
    #         child["props"]["children"]["props"]["id"]["type"] = (
    #             "updated-" + child["props"]["children"]["props"]["id"]["type"]

    # edit_button = dmc.Button(
    #     "Edit",
    #     id={
    #         "type": "edit-button",
    #         "index": f"edit-{btn_index}",
    #     },
    #     color="gray",
    #     variant="filled",
    #     leftIcon=DashIconify(icon="basil:edit-solid", color="white"),
    # )

    # remove_button = dmc.Button(
    #     "Remove",
    #     id={"type": "remove-button", "index": f"remove-{btn_index}"},
    #     color="red",
    #     variant="filled",
    #     leftIcon=DashIconify(icon="jam:trash", color="white"),
    # )

    # new_draggable_child = html.Div(
    #     [
    #         html.Div([remove_button, edit_button]),
    #         child,
    #     ],
    #     id=f"draggable-{btn_id}",
    # )

    elif triggered_input == "edit-dashboard-mode-button":
        # print("\n\n")
        stored_edit_dashboard["count"] = (
            stored_edit_dashboard["count"] + 1
            if switch_state
            else stored_edit_dashboard["count"]
        )

        # switch_state = True if len(ctx.triggered[0]["value"]) > 0 else False
        # print(switch_state)
        # print(stored_edit_dashboard)
        # print(current_draggable_children)
        # assuming the switch state is added as the first argument in args
        updated_draggable_children = []
        # print(len(current_draggable_children))
        for child in current_draggable_children:
            print("\n\n")
            print(child)
            print("\n\n")

            # print(len(child))
            # print(child["props"]["id"])
            # print(len(child["props"]["children"]))
            # graph = child["props"]["children"][0]["props"]["children"][
            #     -2
            # ]  # Assuming graph is always the last child
            #     graph = child["props"]["children"][0]["props"]["children"][0]["props"]["children"]
            #     print(child["props"]["children"])
            if switch_state:  # If switch is 'on', add the remove button
                # if "graph" in child["props"]["id"]:
                graph = child["props"]["children"][0]
                # print(graph["props"]["id"])

                edit_button = dmc.Button(
                    "Edit",
                    id={
                        "type": "edit-button",
                        "index": child["props"]["id"],
                    },
                    color="gray",
                    variant="filled",
                    leftIcon=DashIconify(icon="basil:edit-solid", color="white"),
                )

                remove_button = dmc.Button(
                    "Remove",
                    id={"type": "remove-button", "index": child["props"]["id"]},
                    color="red",
                    variant="filled",
                    leftIcon=DashIconify(icon="jam:trash", color="white"),
                )

                updated_child = html.Div(
                    [
                        remove_button,
                        edit_button,
                        graph,
                    ],
                    id=child["props"]["id"],
                )

                # remove_button = dbc.Button(
                #     "Remove",
                #     id={
                #         "type": "remove-button",
                #         "index": child["props"]["id"],
                #     },
                #     color="danger",
                # )
                # edit_button = dbc.Button(
                #     "Edit",
                #     id={
                #         "type": "edit-button",
                #         "index": child["props"]["id"],
                #     },
                #     color="secondary",
                #     style={"margin-left": "10px"},
                # )

                # updated_child = html.Div(
                #     [remove_button, edit_button, graph],
                #     id=child["props"]["id"],
                # )
            elif (
                switch_state is False and stored_edit_dashboard["count"] == 0
            ):  # If switch is 'off', remove the button
                graph = child["props"]["children"][0]["props"]["children"]["props"][
                    "children"
                ][2]
                # print(graph["props"]["id"])

                updated_child = html.Div(
                    [graph],
                    id=child["props"]["id"],
                )
            else:
                graph = child["props"]["children"][-1]
                # print(child["props"]["id"])

                updated_child = html.Div(
                    [graph],
                    id=child["props"]["id"],
                )
        updated_draggable_children.append(updated_child)

        return (
            updated_draggable_children,
            new_layouts,
            # selected_year,
            new_layouts,
            updated_draggable_children,
            stored_edit_dashboard
            # selected_year,
        )

    # # Add an else condition to return the current layout when there's no triggering input
    else:
        raise dash.exceptions.PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True, port="5080")