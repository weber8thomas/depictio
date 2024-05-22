# Import necessary libraries
from dash import html, dcc, Input, Output, MATCH
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import httpx


from depictio.dash.modules.jbrowse_component.utils import build_jbrowse, build_jbrowse_frame
from depictio.dash.utils import list_workflows, return_mongoid

# Depictio imports

from depictio.dash.utils import (
    UNSELECTED_STYLE,
)
from depictio.api.v1.configs.config import API_BASE_URL, TOKEN


def register_callbacks_jbrowse_component(app):
    @app.callback(
        Output({"type": "jbrowse-body", "index": MATCH}, "children"),
        [
            Input({"type": "workflow-selection-label", "index": MATCH}, "value"),
            Input({"type": "datacollection-selection-label", "index": MATCH}, "value"),
            Input({"type": "btn-jbrowse", "index": MATCH}, "n_clicks"),
            Input({"type": "btn-jbrowse", "index": MATCH}, "id"),
        ],
        prevent_initial_call=True,
    )
    def update_jbrowse(wf_id, dc_id, n_clicks, id):
        workflows = list_workflows(TOKEN)

        workflow_id = [e for e in workflows if e["workflow_tag"] == wf_id][0]["_id"]
        data_collection_id = [f for e in workflows if e["_id"] == workflow_id for f in e["data_collections"] if f["data_collection_tag"] == dc_id][0]["_id"]

        dc_specs = httpx.get(
            f"{API_BASE_URL}/depictio/api/v1/datacollections/specs/{workflow_id}/{data_collection_id}",
            headers={
                "Authorization": f"Bearer {TOKEN}",
            },
        ).json()

        # Get DC ID that are joined
        if "join" in dc_specs["config"]:
            dc_specs["config"]["join"]["with_dc_id"] = list()
            for dc_tag in dc_specs["config"]["join"]["with_dc"]:
                _, dc_id = return_mongoid(workflow_id=workflow_id, data_collection_tag=dc_tag)
                dc_specs["config"]["join"]["with_dc_id"].append(dc_id)

        jbrowse_kwargs = {
            "index": id["index"],
            "wf_id": workflow_id,
            "dc_id": data_collection_id,
            "dc_config": dc_specs["config"],
        }

        jbrowse_body = build_jbrowse(**jbrowse_kwargs)
        return jbrowse_body


def design_jbrowse(id):
    row = [
        dbc.Row(
            dmc.Center(
                dmc.Button(
                    "Display JBrowse",
                    id={"type": "btn-jbrowse", "index": id["index"]},
                    n_clicks=0,
                    style=UNSELECTED_STYLE,
                    size="xl",
                    color="yellow",
                    leftIcon=DashIconify(icon="material-symbols:table-rows-narrow-rounded", color="white"),
                ),
            ),
        ),
        dbc.Row(
            html.Div(build_jbrowse_frame(index=id["index"]), id={"type": "component-container", "index": id["index"]}),
            # dbc.Card(
            #     dbc.CardBody(
            #         id={
            #             "type": "jbrowse-body",
            #             "index": id["index"],
            #         },
            #     ),
            #     id={
            #         "type": "component-container",
            #         "index": id["index"],
            #     },
            # )
        ),
    ]
    return row


def create_stepper_jbrowse_button(n, disabled=False):
    button = dbc.Col(
        dmc.Button(
            "JBrowse2",
            id={
                "type": "btn-option",
                "index": n,
                "value": "JBrowse2",
            },
            n_clicks=0,
            style=UNSELECTED_STYLE,
            size="xl",
            color="yellow",
            leftIcon=DashIconify(icon="material-symbols:table-rows-narrow-rounded", color="white"),
            disabled=disabled,
        )
    )
    store = dcc.Store(
        id={
            "type": "store-btn-option",
            "index": n,
            "value": "JBrowse2",
        },
        data=0,
        storage_type="memory",
    )

    return button, store
