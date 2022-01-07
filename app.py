import dash
import dash_bootstrap_components as dbc
import geopandas as gpd
import pandas as pd
import plotly.express as px
from dash import html, dcc
from dash.dependencies import Input, Output

external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/styles.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Home bilingualism in Canada"
server = app.server

results = pd.read_csv('assets/bilingual_results_with_region_codes.tsv', sep='\t')
geo_table = gpd.read_file('assets/recombined_shape_files.zip')
columns = [col_name for col_name in results.columns if 'Percent' in col_name]
vmax = results[columns].max().max()


def make_figure(overlay=None):
    if overlay is None:
        overlay = 'Percent_age_0_to_9'

    fig = px.choropleth_mapbox(results,
                               geojson=geo_table, locations='Region', featureidkey='properties.PK', color=overlay,
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               height=700,
                               zoom=2.5, center={"lat": 60, "lon": -98.1},
                               opacity=0.6,
                               hover_name='name',
                               range_color=(0, vmax),
                               hover_data={'province': True,
                                           'Percent_age_0_to_4': True,
                                           'Percent_age_5_to_9': True,
                                           'Percent_age_0_to_9': True,
                                           'Region': False
                                           },
                               labels={'province': 'Province',
                                       'Percent_age_0_to_4': 'Home Bilingualism among children aged 0-4',
                                       'Percent_age_5_to_9': 'Home Bilingualism among children aged 5-9',
                                       'Percent_age_0_to_9': 'Home Bilingualism among children aged 0-9'},
                               )
    fig['layout'].update(margin=dict(l=0, r=0, b=0, t=30))
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
                            href="https://github.com/e-schott/BilingalismCanada",
                        )
                    ),
                    dbc.Col(dbc.NavbarBrand("Information from the 2016 Canadian Census")),
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
        dbc.CardHeader(html.H2("Home bilingualism in Canada")),
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
                        "Choose the age group to display:"
                    ),
                    dbc.Col(color_drop)
                ],
                align="center",
            ),
        ),
    ]
)

abstract_card = dbc.Card(
    [

        dbc.CardBody(
            dbc.Row(
                dbc.Col([
                    html.H3('Abstract'),
                    html.P(
                        "This study used the 2016 Canadian Census data to examine home bilingualism amongst children aged 0–9 years. Across Canada, 18 percent of children used at least two languages at home, which rose to more than 25 percent in large cities, and the Canadian territories. English and French was the most common language pair in Quebec and Ontario, and various other pairs were spoken in most provinces. In the territories, 17 percent of children spoke an Indigenous language and English, and we discuss specific opportunities and challenges for Indigenous language revitalization. The presence of bilingual adults in the home, and immigration generation were the strongest predictors of children's home bilingualism. We conclude by discussing how policies can encourage child bilingualism, such as by supporting children’s home language in early and primary education settings. Such policies must be tailored to the needs of the specific communities to optimally support bilingual children and their families. "),
                    html.A("For more information, find the full paper at https://psyarxiv.com/6q9jg/",
                           href="https://psyarxiv.com/6q9jg/")
                ]

                )
            )
        ),
    ]
)

app.layout = html.Div(
    [
        header,
        dbc.Container([
            dbc.Row(dbc.Col(figure_card, md=8), justify='center'),
            dbc.Row(dbc.Col(abstract_card, md=8), justify='center')
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
