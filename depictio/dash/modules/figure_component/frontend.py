# Import necessary libraries
import numpy as np
from dash import html, dcc, Input, Output, State, ALL, MATCH
import dash
import dash_bootstrap_components as dbc
import dash_draggable
import dash_mantine_components as dmc
import inspect
import pandas as pd
import plotly.express as px
import re
from dash_iconify import DashIconify
import ast


# Depictio imports
from depictio.dash.modules.figure_component.utils import (
    specific_params,
    param_info,
    plotly_bootstrap_mapping,
    secondary_common_params,
    base_elements,
    secondary_common_params_lite,
    plotly_vizu_dict,
)
from depictio.dash.utils import (
    get_columns_from_data_collection,
    load_gridfs_file,
)


def register_callbacks_figure_component(app):
    # Define the callback to update the specific parameters dropdowns
    @dash.callback(
        [
            Output({"type": "collapse", "index": MATCH}, "children"),
        ],
        [
            Input({"type": "edit-button", "index": MATCH}, "n_clicks"),
            Input({"type": "segmented-control-visu-graph", "index": MATCH}, "value"),
            Input({"type": "workflow-selection-label", "index": MATCH}, "value"),
            Input({"type": "datacollection-selection-label", "index": MATCH}, "value"),
        ],
        [State({"type": "edit-button", "index": MATCH}, "id")],
        prevent_initial_call=True,
    )
    def update_specific_params(
        n_clicks,
        visu_type,
        workflow,
        data_collection,
        edit_button_id,
    ):
        # print("update_specific_params")
        # print(app._callback_list)

        # print(n_clicks, edit_button_id)
        print("\n\n\n")
        print("update_specific_params")
        print(n_clicks, visu_type, edit_button_id, workflow, data_collection)

        columns_json = get_columns_from_data_collection(workflow, data_collection)
        print(columns_json)

        columns = columns_json["columns_list"]
        print(columns)
        print("\n\n\n")

        value = visu_type.lower()
        # value = "scatter"
        if value is not None:
            specific_params_options = [
                {"label": param_name, "value": param_name}
                for param_name in specific_params[value]
            ]

            specific_params_dropdowns = list()
            for e in specific_params[value]:
                processed_type_tmp = param_info[value][e]["processed_type"]
                allowed_types = ["str", "int", "float", "column"]
                if processed_type_tmp in allowed_types:
                    input_fct = plotly_bootstrap_mapping[processed_type_tmp]
                    tmp_options = dict()

                    if processed_type_tmp == "column":
                        tmp_options = {
                            "options": columns,
                            # "options": list(df.columns),
                            "value": None,
                            "persistence": True,
                            "id": {
                                "type": f"tmp-{e}",
                                "index": edit_button_id["index"],
                            },
                        }
                    if processed_type_tmp == "str":
                        tmp_options = {
                            "placeholder": e,
                            "type": "text",
                            "persistence": True,
                            "id": {
                                "type": f"tmp-{e}",
                                "index": edit_button_id["index"],
                            },
                            "value": None,
                        }
                    if processed_type_tmp in ["int", "float"]:
                        tmp_options = {
                            "placeholder": e,
                            "type": "number",
                            "persistence": True,
                            "id": {
                                "type": f"tmp-{e}",
                                "index": edit_button_id["index"],
                            },
                            "value": None,
                        }
                    input_fct_with_params = input_fct(**tmp_options)
                    accordion_item = dbc.AccordionItem(
                        [dbc.Row(input_fct_with_params)],
                        className="my-2",
                        title=e,
                    )
                    specific_params_dropdowns.append(accordion_item)

            secondary_common_params_dropdowns = list()
            primary_common_params_dropdowns = list()
            for e in secondary_common_params:
                # print(e)
                processed_type_tmp = param_info[value][e]["processed_type"]
                # allowed_types = ["str", "int", "float", "column", "list"]
                allowed_types = ["str", "int", "float", "column"]
                if processed_type_tmp in allowed_types:
                    input_fct = plotly_bootstrap_mapping[processed_type_tmp]
                    tmp_options = dict()

                    if processed_type_tmp == "column":
                        tmp_options = {
                            "options": columns,
                            # "options": list(df.columns),
                            "value": None,
                            "persistence": True,
                            "style": {"width": "100%"},
                            "id": {
                                "type": f"tmp-{e}",
                                "index": edit_button_id["index"],
                            },
                        }
                    if processed_type_tmp == "str":
                        tmp_options = {
                            "placeholder": e,
                            "type": "text",
                            "persistence": True,
                            "id": {
                                "type": f"tmp-{e}",
                                "index": edit_button_id["index"],
                            },
                            "value": None,
                        }
                    if processed_type_tmp in ["int", "float"]:
                        tmp_options = {
                            "placeholder": e,
                            "type": "number",
                            "persistence": True,
                            "id": {
                                "type": f"tmp-{e}",
                                "index": edit_button_id["index"],
                            },
                            "value": None,
                        }

                    # if processed_type_tmp is "list":
                    #     tmp_options = {
                    #         # "options": list(df.columns),
                    #         # "value": None,
                    #         "persistence": True,
                    #         "id": {
                    #             "type": f"tmp-{e}",
                    #             "index": edit_button_id["index"],
                    #         },
                    #     }

                    input_fct_with_params = input_fct(**tmp_options)

                    # input_fct_with_params = dmc.Tooltip(
                    #     children=[input_fct(**tmp_options)], label="TEST"
                    # )
                    accordion_item = dbc.AccordionItem(
                        [dbc.Row(input_fct_with_params, style={"width": "100%"})],
                        className="my-2",
                        title=e,
                    )
                    if e not in base_elements:
                        secondary_common_params_dropdowns.append(accordion_item)
                    else:
                        primary_common_params_dropdowns.append(accordion_item)

            # print(secondary_common_params_dropdowns)

            primary_common_params_layout = [
                dbc.Accordion(
                    dbc.AccordionItem(
                        [
                            dbc.Accordion(
                                primary_common_params_dropdowns,
                                flush=True,
                                always_open=True,
                                persistence_type="session",
                                persistence=True,
                                id="accordion-sec-common",
                            ),
                        ],
                        title="Base parameters",
                    ),
                    start_collapsed=True,
                )
            ]

            secondary_common_params_layout = [
                dbc.Accordion(
                    dbc.AccordionItem(
                        [
                            dbc.Accordion(
                                secondary_common_params_dropdowns,
                                flush=True,
                                always_open=True,
                                persistence_type="session",
                                persistence=True,
                                id="accordion-sec-common",
                            ),
                        ],
                        title="Generic parameters",
                    ),
                    start_collapsed=True,
                )
            ]
            dynamic_specific_params_layout = [
                dbc.Accordion(
                    dbc.AccordionItem(
                        [
                            dbc.Accordion(
                                specific_params_dropdowns,
                                flush=True,
                                always_open=True,
                                persistence_type="session",
                                persistence=True,
                                id="accordion",
                            ),
                        ],
                        title=f"{value.capitalize()} specific parameters",
                    ),
                    start_collapsed=True,
                )
            ]
            return [
                primary_common_params_layout
                + secondary_common_params_layout
                + dynamic_specific_params_layout
            ]
        else:
            return html.Div()

    def generate_dropdown_ids(value):
        specific_param_ids = [
            f"{value}-{param_name}" for param_name in specific_params[value]
        ]
        secondary_param_ids = [f"{value}-{e}" for e in secondary_common_params]

        return secondary_param_ids + specific_param_ids

    @app.callback(
        Output(
            {
                "type": "collapse",
                "index": MATCH,
            },
            "is_open",
        ),
        [
            Input(
                {
                    "type": "edit-button",
                    "index": MATCH,
                },
                "n_clicks",
            )
        ],
        [
            State(
                {
                    "type": "collapse",
                    "index": MATCH,
                },
                "is_open",
            )
        ],
        prevent_initial_call=True,
    )
    def toggle_collapse(n, is_open):
        # print(n, is_open, n % 2 == 0)
        if n % 2 == 0:
            return False
        else:
            return True

    @app.callback(
        Output({"type": "dict_kwargs", "index": MATCH}, "value"),
        [
            Input({"type": "collapse", "index": MATCH}, "children"),
            # Input("interval", "n_intervals"),
        ],
        [State({"type": "dict_kwargs", "index": MATCH}, "data")],
        # prevent_initial_call=True,
    )
    def get_values_to_generate_kwargs(*args):
        # print("get_values_to_generate_kwargs")
        # print(args)
        # print("\n")

        children = args[0]
        # print(children)
        # visu_type = args[1]
        # print(children)
        existing_kwargs = args[-1]

        accordion_primary_common_params_args = dict()
        accordion_secondary_common_params_args = dict()
        specific_params_args = dict()
        # print(existing_kwargs)
        # print(children)

        # l[0]["props"]["children"]["props"]["children"][0]["props"]["children"][0]

        if children:
            # accordion_secondary_common_params = children[0]["props"]["children"]["props"]["children"]
            accordion_primary_common_params = children[0]["props"]["children"]["props"][
                "children"
            ][0]["props"]["children"]

            # accordion_secondary_common_params = children[1]["props"]["children"]
            if accordion_primary_common_params:
                # print("TOTO")
                accordion_primary_common_params = [
                    param["props"]["children"][0]["props"]["children"]
                    for param in accordion_primary_common_params
                ]

                accordion_primary_common_params_args = {
                    elem["props"]["id"]["type"].replace("tmp-", ""): elem["props"][
                        "value"
                    ]
                    for elem in accordion_primary_common_params
                }

                # print(accordion_primary_common_params_args)
                # print(accordion_primary_common_params)

                # print(accordion_secondary_common_params)
                # return accordion_secondary_common_params_args
            accordion_secondary_common_params = children[1]["props"]["children"][
                "props"
            ]["children"][0]["props"]["children"]

            # accordion_secondary_common_params = children[1]["props"]["children"]
            if accordion_secondary_common_params:
                # print("TOTO")
                accordion_secondary_common_params = [
                    param["props"]["children"][0]["props"]["children"]
                    for param in accordion_secondary_common_params
                ]

                accordion_secondary_common_params_args = {
                    elem["props"]["id"]["type"].replace("tmp-", ""): elem["props"][
                        "value"
                    ]
                    for elem in accordion_secondary_common_params
                }
                # print(accordion_secondary_common_params_args)
                # if not {
                #     k: v
                #     for k, v in accordion_secondary_common_params_args.items()
                #     if v is not None
                # }:
                #     accordion_secondary_common_params_args = {
                #         **accordion_secondary_common_params_args,
                #         **existing_kwargs,
                #     }
                # print(accordion_secondary_common_params_args)
                # print(accordion_secondary_common_params)
                # return accordion_secondary_common_params_args
            specific_params = children[2]["props"]["children"]["props"]["children"][0][
                "props"
            ]["children"]

            # accordion_secondary_common_params = children[1]["props"]["children"]
            if specific_params:
                # print("specific_params")
                specific_params = [
                    param["props"]["children"][0]["props"]["children"]
                    for param in specific_params
                ]

                specific_params_args = {
                    elem["props"]["id"]["type"].replace("tmp-", ""): elem["props"][
                        "value"
                    ]
                    for elem in specific_params
                }
                # print(specific_params_args)

            return_dict = dict(
                **specific_params_args,
                **accordion_secondary_common_params_args,
                **accordion_primary_common_params_args,
            )
            return_dict = {k: v for k, v in return_dict.items() if v is not None}

            if not return_dict:
                return_dict = {
                    **return_dict,
                    **existing_kwargs,
                }
                # print("BLANK DICT, ROLLBACK TO EXISTING KWARGS")
                # print(return_dict)

            if return_dict:
                # print("RETURNING DICT")
                # print(return_dict)
                # print(accordion_secondary_common_params)
                return return_dict
            else:
                # print("EXISTING KWARGS")
                return existing_kwargs

            # else:
            #     return existing_kwargs
        else:
            return existing_kwargs

            # accordion_specific_params = args[0][3]

    @app.callback(
        Output({"type": "graph", "index": MATCH}, "figure"),
        [
            Input({"type": "dict_kwargs", "index": MATCH}, "value"),
            Input({"type": "segmented-control-visu-graph", "index": MATCH}, "value"),
            Input({"type": "workflow-selection-label", "index": MATCH}, "value"),
            Input({"type": "datacollection-selection-label", "index": MATCH}, "value"),
            [
                Input({"type": f"tmp-{e}", "index": MATCH}, "children")
                for e in secondary_common_params_lite
            ],
            # Input("interval", "n_intervals"),
        ],
        prevent_initial_call=True,
    )
    def update_figure(*args):
        dict_kwargs = args[0]

        visu_type = args[1]
        workflow = args[2]
        data_collection = args[3]
        print(args)

        # print("update figure")
        # print(dict_kwargs)
        # print(visu_type)
        # # print(app._callback_list)

        # print(dict_kwargs)
        dict_kwargs = {k: v for k, v in dict_kwargs.items() if v is not None}
        df = load_gridfs_file(workflow, data_collection)
        # print(dict_kwargs)
        if dict_kwargs:
            figure = plotly_vizu_dict[visu_type.lower()](df, **dict_kwargs)
            # figure = px.scatter(df, **dict_kwargs)
            # print(figure)
            # figure.update_layout(uirevision=1)

            return figure
        # print("\n")

        # accordion_specific_params = args[0][3]


def design_figure(id, wfs_list):
    figure_row = [
        
        dbc.Row(
            [
                html.H5("Select your visualisation type"),
                dmc.SegmentedControl(
                    data=[e.capitalize() for e in sorted(plotly_vizu_dict.keys())],
                    orientation="horizontal",
                    size="lg",
                    radius="lg",
                    id={
                        "type": "segmented-control-visu-graph",
                        "index": id["index"],
                    },
                    persistence=True,
                    persistence_type="session",
                    value=[e.capitalize() for e in sorted(plotly_vizu_dict.keys())][-1],
                ),
            ],
            style={"height": "5%"},
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        # figure=figure,
                        id={"type": "graph", "index": id["index"]},
                        config={"editable": True},
                    ),
                    width="auto",
                ),
                # dbc.Col(width=0.5),
                dbc.Col(
                    [
                        html.Br(),
                        html.Div(
                            children=[
                                dmc.Button(
                                    "Edit figure",
                                    id={
                                        "type": "edit-button",
                                        "index": id["index"],
                                    },
                                    n_clicks=0,
                                    # size="lg",
                                    style={"align": "center"},
                                ),
                                html.Hr(),
                                dbc.Collapse(
                                    id={
                                        "type": "collapse",
                                        "index": id["index"],
                                    },
                                    is_open=False,
                                ),
                            ]
                        ),
                    ],
                    width="auto",
                    style={"align": "center"},
                ),
            ]
        ),
        dcc.Store(
            id={"type": "dict_kwargs", "index": id["index"]},
            data={},
            storage_type="memory",
        ),
    ]
    return figure_row