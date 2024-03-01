import numpy as np
from dash import html, Input, Output, State, ALL, MATCH, ctx
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_draggable
import ast

# Depictio imports
from depictio.api.v1.configs.config import settings

# Depictio components imports - design step
from depictio.dash.modules.card_component.frontend import register_callbacks_card_component
from depictio.dash.modules.interactive_component.frontend import register_callbacks_interactive_component
from depictio.dash.modules.figure_component.frontend import register_callbacks_figure_component
from depictio.dash.modules.jbrowse_component.frontend import register_callbacks_jbrowse_component

# Depictio layout imports
from depictio.dash.layouts.stepper import register_callbacks_stepper
from depictio.dash.layouts.stepper_parts.part_one import register_callbacks_stepper_part_one
from depictio.dash.layouts.stepper_parts.part_two import register_callbacks_stepper_part_two
from depictio.dash.layouts.stepper_parts.part_three import register_callbacks_stepper_part_three
from depictio.dash.layouts.header import register_callbacks_header
from depictio.dash.layouts.draggable import register_callbacks_draggable


# Depictio utils imports
from depictio.dash.utils import (
    analyze_structure_and_get_deepest_type,
    load_depictio_data,
    load_deltatable,
)

# Depictio layout imports for stepper
from depictio.dash.layouts.stepper import (
    # create_stepper_dropdowns,
    # create_stepper_buttons,
    create_stepper_output,
)

# Depictio layout imports for header
from depictio.dash.layouts.header import design_header, enable_box_edit_mode, enable_box_edit_mode_dev


# TODO: move to depictio.dash.utils or somewhere else


# Start the app
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


# Register callbacks for layout
register_callbacks_stepper(app)
register_callbacks_stepper_part_one(app)
register_callbacks_stepper_part_two(app)
register_callbacks_stepper_part_three(app)
register_callbacks_header(app)
register_callbacks_draggable(app)


# Register callbacks for components
register_callbacks_card_component(app)
register_callbacks_interactive_component(app)
register_callbacks_figure_component(app)
register_callbacks_jbrowse_component(app)


# Load depictio data from JSON
data = load_depictio_data()


# Init layout and children if data is available, else set to empty
init_layout = data["stored_layout_data"] if data else {}
init_children = data["stored_children_data"] if data else list()

# Generate header and backend components
header, backend_components = design_header(data)


# APP Layout
app.layout = dbc.Container(
    [
        html.Div(
            [
                # Backend components & header
                backend_components,
                header,
                # Draggable layout
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
    fluid=True,
)


if __name__ == "__main__":
    app.run_server(debug=True, host=settings.dash.host, port=settings.dash.port)
