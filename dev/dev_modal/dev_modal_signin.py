from datetime import datetime
import json
import dash_bootstrap_components as dbc
import re
import dash
from dash import html, dcc, ctx, MATCH, Input, Output, State, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

dashboards = []
workflows = []
filepath = "dashboards.json"
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="hidden-div", style={"display": "none"}),
        html.Div(id="page-content"),
        dcc.Store(id="modal-store", storage_type="session", data={"email": "", "submitted": False}),
        dmc.Modal(
            opened=False,
            id="email-modal",
            centered=True,
            children=[
                dmc.Center(dmc.Title("Welcome to Depictio", order=1, style={"fontFamily": "Virgil"}, align="center")),
                dmc.Center(dmc.Text("Please enter your email to login:", style={"paddingTop": 15})),
                dmc.Center(dmc.Space(h=20)),
                dmc.Center(
                    dmc.TextInput(
                        label="Your Email", style={"width": 300}, placeholder="Please enter your email", icon=DashIconify(icon="ic:round-alternate-email"), id="email-input"
                    )
                ),
                dmc.Center(dmc.Space(h=20)),
                dmc.Center(dmc.Button("Login", id="submit-button", variant="filled", disabled=True, size="lg", color="black")),
            ],
            # Prevent closing the modal by clicking outside or pressing ESC
            closeOnClickOutside=False,
            closeOnEscape=False,
            withCloseButton=False,
        ),
        html.Div(id="landing-page", style={"display": "none"}),  # Initially hidden
    ]
)


def load_dashboards_from_file(filepath):
    print("Loading dashboards from file")
    print(f"{filepath}")
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {"next_index": 1, "dashboards": []}  # Return default if no file exists


def save_dashboards_to_file(data, filepath):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


@app.callback(
    Output("url", "pathname"),
    [Input({"type": "view-dashboard-button", "index": ALL, "value": ALL}, "n_clicks")],
    [State({"type": "view-dashboard-button", "index": ALL, "value": ALL}, "id")],
)
def navigate_to_dashboard(n_clicks, ids):
    print("Navigating to dashboard")
    print(n_clicks)
    print(ids)
    print(ctx.triggered)
    for i in ctx.triggered:
        if i["value"] is not None:
            print(i)
            print(ctx.triggered_id)
            return f"/dashboard/{ctx.triggered_id['index']}"


@app.callback([Output("submit-button", "disabled"), Output("email-input", "error")], [Input("email-input", "value")])
def update_submit_button(email):
    if email:
        valid = re.match(r"^[a-zA-Z0-9_.+-]+@embl\.de$", email)
        return not valid, not valid
    return True, False  # Initially disabled with no error


@app.callback(Output("modal-store", "data"), [Input("submit-button", "n_clicks")], [State("email-input", "value"), State("modal-store", "data")])
def store_email(submit_clicks, email, data):
    print(submit_clicks, email, data)
    if submit_clicks:
        data["email"] = email
        data["submitted"] = True
    return data


@app.callback(Output("email-modal", "opened"), [Input("modal-store", "data")])
def manage_modal(data):
    print(data)
    return not data["submitted"]  # Keep modal open until submitted


@app.callback(Output("landing-page", "style"), [Input("modal-store", "data")])
def show_landing_page(data):
    if data["submitted"]:
        return {"display": "block"}  # Show landing page
    return {"display": "none"}  # Hide landing page


@app.callback(
    [Output({"type": "dashboard-list", "index": MATCH}, "children"), Output({"type": "dashboard-index-store", "index": MATCH}, "data")],
    [
        Input({"type": "create-dashboard-button", "index": MATCH}, "n_clicks"),
        State({"type": "create-dashboard-button", "index": MATCH}, "id"),
        # State({"type": "dashboard-index-store", "index": MATCH}, "data"),
        # Input({"type": "dashboard-index-store", "index": MATCH}, "data"),
    ],
    # prevent_initial_call=True
)
def create_dashboard(n_clicks, id):
    # if not n_clicks:
    #     return dash.no_update, dash.no_update

    # Load existing dashboards
    index_data = load_dashboards_from_file(filepath)

    # Assuming index_data also stores a list of dashboards
    dashboards = index_data.get("dashboards", [])

    print(f"Creating dashboard for {id['index']}")
    print(f"Existing dashboards: {dashboards}")

    if n_clicks:

        next_index = index_data.get("next_index", 1)  # Default to 1 if not found

        # Creating a new dashboard entry
        new_dashboard = {
            "title": f"Dashboard {next_index}",
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "V1",
            "owner": id["index"],
            "index": next_index,
        }

        dashboards.append(new_dashboard)

        # Updating the store data to include the new list of dashboards and the incremented index
        new_index_data = {"next_index": next_index + 1, "dashboards": dashboards}
        save_dashboards_to_file(new_index_data, filepath)
    else:
        new_index_data = index_data

    # Creating views for each dashboard
    dashboards_view = [
        dmc.Paper(
            dmc.Group(
                [
                    html.Div(
                        [
                            dmc.Title(dashboard["title"], order=5),
                            dmc.Text(f"Last Modified: {dashboard['last_modified']}"),
                            dmc.Text(f"Version: {dashboard['version']}"),
                            dmc.Text(f"Owner: {dashboard['owner']}"),
                        ],
                        style={"flex": "1"},
                    ),
                    dmc.Button(
                        f"View Dashboard {dashboard['index']}",
                        id={"type": "view-dashboard-button", "value": dashboard["owner"], "index": dashboard["index"]},
                        variant="outline",
                        color="dark",
                        style={"marginRight": 20},
                    ),
                ],
                align="center",
                position="apart",
                grow=False,
                noWrap=False,
                style={"width": "100%"},
            ),
            shadow="xs",
            p="md",
            style={"marginBottom": 20},
        )
        for dashboard in dashboards
    ]

    return dashboards_view, new_index_data


def render_welcome_section(email):
    return dmc.Container(
        [
            dmc.Title(f"Welcome, {email}!", order=2, align="center"),
            dmc.Center(
                dmc.Button(
                    "+ Create New Dashboard",
                    id={"type": "create-dashboard-button", "index": email},
                    n_clicks=0,
                    variant="gradient",
                    gradient={"from": "black", "to": "grey", "deg": 135},
                    style={"margin": "20px 0", "fontFamily": "Virgil"},
                    size="xl",
                )
            ),
            dcc.Store(id={"type": "dashboard-index-store", "index": email}, storage_type="session", data={"next_index": 1}),  # Store for dashboard index management
            # dcc.Store(id={"type": "dashboards-store", "index": email}, storage_type="session", data={"dashboards": []}),  # Store to cache workflows
            dmc.Divider(style={"margin": "20px 0"}),
        ]
    )


def render_dashboard_list_section(email):
    return html.Div(id={"type": "dashboard-list", "index": email}, style={"padding": "20px"})


def render_data_collection_item(data_collection):
    return dmc.AccordionItem(
        [
            dmc.AccordionControl(dmc.Title(data_collection["title"], order=5)),
            dmc.AccordionPanel(
                dmc.Paper(
                    dmc.Group(
                        [
                            html.Div(
                                dmc.List(
                                    [
                                        dmc.ListItem(f"Type: {data_collection['type']}"),
                                        dmc.ListItem(f"Description: {data_collection['description']}"),
                                        dmc.ListItem(f"Creation time: {data_collection['creation_time']}"),
                                        dmc.ListItem(f"Last update time: {data_collection['last_update_time']}"),
                                    ]
                                )
                            ),
                            dmc.Button("View Data", variant="outline", color="dark", style={"marginRight": 20}),
                        ],
                        align="center",
                        position="apart",
                        grow=False,
                        noWrap=False,
                        style={"width": "100%"},
                    ),
                    shadow="xs",
                    p="md",
                    style={"marginBottom": 20},
                ),
            ),
        ],
        value=f"{data_collection['title']}-{data_collection['type']}",
    )


@app.callback(Output("landing-page", "children"), [Input("url", "pathname"), Input("modal-store", "data")])
def update_landing_page(pathname, data):
    ctx = dash.callback_context

    # Check which input triggered the callback
    if not ctx.triggered:
        return no_update
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Respond to URL changes
    if trigger_id == "url":
        if pathname:
            if pathname.startswith("/dashboard/"):
                dashboard_id = pathname.split("/")[-1]
                # Fetch dashboard data based on dashboard_id and return the appropriate layout
                return html.Div([f"Displaying Dashboard {dashboard_id}", dbc.Button("Go back", href="/", color="black", external_link=True)])
            # Add more conditions for other routes
            # return html.Div("This is the home page")
            return no_update

    # Respond to modal-store data changes
    elif trigger_id == "modal-store":
        if data and data.get("submitted"):
            return html.Div(
                [
                    render_welcome_section(data["email"]),
                    dmc.Title("Your Dashboards", order=3),
                    render_dashboard_list_section(data["email"]),
                ]
            )
        # return html.Div("Please login to view this page.")
        return no_update

    return no_update


if __name__ == "__main__":
    app.run_server(debug=True)
