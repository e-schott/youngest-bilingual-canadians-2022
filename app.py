import dash
import dash_bootstrap_components as dbc
import geopandas as gpd
import pandas as pd
import plotly.express as px
from dash import html, dcc
from dash.dependencies import Input, Output

external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/styles.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

results = pd.read_csv('assets/bilingual_results_with_region_codes.tsv', sep='\t')
geo_table = gpd.read_file('assets/recombined_shape_files.zip')
columns = [col_name for col_name in results.columns if 'Percent' in col_name]
(vmin, vmax) = results[columns].min().min(), results[columns].max().max()


def make_figure(overlay=None):
    if overlay is None:
        overlay = 'Percent_age_0_to_9'

    fig = px.choropleth_mapbox(results,
                               geojson=geo_table, locations='Region', featureidkey='properties.PK', color=overlay,
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               height=800,
                               zoom=2, center={"lat": 62.4, "lon": -96.5},
                               opacity=0.6,
                               hover_name='name',
                               range_color=(vmin, vmax),
                               hover_data={'province': True,
                                           'Percent_age_0_to_4': True,
                                           'Percent_age_5_to_9': True,
                                           'Percent_age_0_to_9': True,
                                           'Region': False
                                           },
                               labels={'province': 'Province',
                                       'Percent_age_0_to_4': '% age 0-4',
                                       'Percent_age_5_to_9': '% age 5-9',
                                       'Percent_age_0_to_9': '% age 0-9'},
                               )
    return fig


# Define Header Layout
header = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.A(
                            html.Img(
                                src=app.get_asset_url("Flag_of_Canada_(Pantone).svg"),
                                height="30px",
                            ),
                            href="https://neurodatascience.github.io/",
                        )
                    ),
                    dbc.Col(dbc.NavbarBrand("Canadian Bilingualism Dashboard")),
                ],
                align="center",
            ),
            dbc.Row(
                dbc.Col(
                    [
                        dbc.NavbarToggler(id="navbar-toggler"),
                        dbc.Collapse(
                            dbc.Nav(
                                [],
                                className="ml-auto",
                                navbar=True,
                            ),
                            id="navbar-collapse",
                            navbar=True,
                        ),
                    ]
                ),
                align="center",
            ),
        ],
        fluid=True,
    ),
    color="dark",
    dark=True,
)

figure_box = dcc.Graph(
    id="graph",
    figure=make_figure(),
)

color_drop = dcc.Dropdown(
    id="color-drop-menu",
    options=[
        {"label": col_name.capitalize(), "value": col_name}
        for col_name in results.columns if 'Percent' in col_name
    ],
    value=None,
)

figure_card = dbc.Card(
    [
        dbc.CardHeader(html.H2("Geographical distribution of bilingualism")),
        dbc.CardBody(
            dbc.Row(
                dbc.Col(
                    figure_box
                )
            )
        ),
        dbc.CardFooter(
            dbc.Row(
                [
                    dbc.Col(
                        "Use the dropdown menu to select which variable to base the colorscale on:"
                    ),
                    dbc.Col(color_drop)
                ],
                align="center",
            ),
        ),
    ]
)

app.layout = html.Div(
    [
        header,
        dbc.Container([
            dbc.Row(dbc.Col(figure_card, md=8))
        ], fluid=True)
    ]
)


@app.callback(
    Output("graph", "figure"),
    Input("color-drop-menu", "value")
)
def update_overlay(selected_overlay):
    return make_figure(selected_overlay)


if __name__ == "__main__":
    app.run_server(debug=True)
