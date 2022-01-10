import dash
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dash_table import Format
import geopandas as gpd
import pandas as pd
import plotly.express as px
from dash import html, dcc
from dash.dependencies import Input, Output, State

external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/styles.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Home bilingualism in Canada"
server = app.server

results = pd.read_csv('assets/bilingual_results_with_region_codes.tsv', sep='\t')
language_pairs = pd.read_csv('assets/bilingual_language_pairs.csv')
geo_table = gpd.read_file('assets/recombined_shape_files.zip')
columns = [col_name for col_name in results.columns if 'Percent' in col_name]
vmax = results[columns].max().max()

# Merge bilingual pairs and region results
biling_index = [area in language_pairs.area.unique() for area in results.area.values]
_res_biling = results[biling_index][['area', 'Region', 'name']]
language_table = pd.merge(language_pairs, _res_biling, on='area')
language_columns = [('language_pair', 'language_pair_collapsed'),
                    ('% bil 0-4', 'percent_bilingual_children_age_0_to_4'),
                    ('% bil 5-9', 'percent_bilingual_children_age_5_to_9'),
                     ('% bil 0-9', 'percent_bilingual_children_age_0_to_9'),
                      ('% all 0-4', 'percent_all_children_age_0_to_4'),
                       ('% all 5-9', 'percent_all_children_age_5_to_9'),
                        ('% all 0-9', 'percent_all_children_age_0_to_9')
                    ]
lang_columns = [{"name": name, "id": idx} for name, idx in language_columns]

def make_figure(overlay=None):
    if overlay is None:
        overlay = 'Percent_age_0_to_9'

    fig = px.choropleth_mapbox(results,
                               geojson=geo_table, locations='Region', featureidkey='properties.PK', color=overlay,
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               height=700,
                               zoom=2.3, center={"lat": 60, "lon": -98.1},
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
                                       'Percent_age_0_to_4': 'Home Bilingualism<br>among children aged 0-4',
                                       'Percent_age_5_to_9': 'Home Bilingualism<br>among children aged 5-9',
                                       'Percent_age_0_to_9': 'Home Bilingualism<br>among children aged 0-9'},
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

table_card = dbc.Card(
    [
        dbc.CardHeader('This is a table'),
        dbc.CardBody(
            [
                dbc.Row([
                    'In the City of:',
                    html.Div(id='city_name')
                ]
                ),
            dbc.Row(dash_table.DataTable(
                            id="table-lang",
                            columns=lang_columns,
                            data=language_table.query('Region==0').to_dict("records"),
                            filter_action="native",
                            style_table={"overflowY": "scroll"},
                            fixed_rows={"headers": False, "data": 0},
                            style_cell={"width": "85px"},
                        ),
            ),
                ]
        ),
        dbc.CardFooter('Here is the footer')
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
            dbc.Row(
                [
                    dbc.Col(figure_card, md=8),
                    dbc.Col(table_card, md=4)
], justify='center'),
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


@app.callback(
    [Output('table-lang', 'data'), Output('city_name', 'children')],
    Input("graph", "hoverData")
)
def update_table(hover):
    if hover is None:
        return dash.no_update, 'Nowhere'
    hover_location = hover['points'][0]['location']
    if not hover_location in language_table.Region.values:
        return dash.no_update, dash.no_update
    subset = language_table.query('Region == @hover_location')
    return subset.to_dict("records"), hover['points'][0]['hovertext']


if __name__ == "__main__":
    app.run_server(debug=True)
