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

results = pd.read_csv("assets/bilingual_results_with_region_codes.tsv", sep="\t")
language_pairs = pd.read_csv("assets/language_pairs.csv")
geo_table = gpd.read_file("assets/recombined_shape_files.zip")
columns = ["Percent_age_0_to_4", "Percent_age_5_to_9", "Percent_age_0_to_9"]
column_label = ["0 to 4 years", "5 to 9 years", "Combined: 0 to 9 years"]
vmax = results[columns].max().max()

# Merge bilingual pairs and region results
language_pairs["name"] = [
    row.area
    if row.type == "cma"
    else row.province
    if row.type == "province"
    else row.type
    for rid, row in language_pairs.iterrows()
]
language_table = pd.merge(
    language_pairs,
    results.query('area != "zz_other"')[["Region", "name"]],
    on="name",
    how="left",
)
language_table = pd.concat((language_table, language_pairs.query('type == "canada"')))
col_map = {
    "language_pair_collapsed": "Language Pair",
    "percent_bilingual_children_age_0_to_4": "% bilinguals 0-4y",
    "percent_bilingual_children_age_5_to_9": "% bilinguals 5-9y",
    "percent_bilingual_children_age_0_to_9": "% bilinguals 0-9y",
    "percent_all_children_age_0_to_4": "% all children 0-4y",
    "percent_all_children_age_5_to_9": "% all children 5-9y",
    "percent_all_children_age_0_to_9": "% all children 0-9y",
}
lang_columns = [{"name": col_map[idx], "id": idx} for idx in col_map.keys()]


def make_figure(overlay=None):
    if overlay is None:
        overlay = "Percent_age_0_to_9"

    fig = px.choropleth_mapbox(
        results,
        geojson=geo_table,
        locations="Region",
        featureidkey="properties.PK",
        color=overlay,
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        height=700,
        zoom=2.3,
        center={"lat": 60, "lon": -98.1},
        opacity=0.6,
        hover_name="name",
        range_color=(0, vmax),
        hover_data={
            "province": True,
            "Percent_age_0_to_4": True,
            "Percent_age_5_to_9": True,
            "Percent_age_0_to_9": True,
            "Region": False,
        },
        labels={
            "province": "Province",
            "Percent_age_0_to_4": "Home Bilingualism<br>among children aged 0-4",
            "Percent_age_5_to_9": "Home Bilingualism<br>among children aged 5-9",
            "Percent_age_0_to_9": "Home Bilingualism<br>among children aged 0-9",
        },
    )
    fig["layout"].update(margin=dict(l=0, r=0, b=0, t=30))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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
                            href="https://github.com/e-schott/BilingalismCanada",
                        )
                    ),
                    dbc.Col(
                        dbc.NavbarBrand(
                            "The youngest bilingual Canadians: Insights from the 2016 Census regarding children aged 0-9"
                        )
                    ),
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
        {"label": col_label, "value": col_name}
        for col_name, col_label in zip(columns, column_label)
    ],
    value="Percent_age_0_to_9",
)

figure_card = dbc.Card(
    [
        dbc.CardHeader(html.H2("Home bilingualism in Canada")),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.B("Choose the age group to display:"),
                            width={"offset": 4},
                            align="center",
                        ),
                        dbc.Col(color_drop),
                    ],
                    align="right",
                ),
                dbc.Row(dbc.Col(figure_box)),
            ]
        ),
        dbc.CardFooter(
            dbc.Row(
                html.Div(
                    [
                        "Data Preparation & Analysis: ",
                        html.A("Esther Schott", href="https://github.com/e-schott"),
                        " Dashboard: ",
                        html.A("Sebastian Urchs", href="https://github.com/surchs"),
                    ],
                    style={"display": "inline-block"},
                )
            )
        ),
    ]
)

table_card = dbc.Card(
    [
        dbc.CardHeader([dbc.Row(["Most Common Language Pairs"])]),
        dbc.CardBody(
            [
                dbc.Row([html.Div(id="region_name")]),
                dbc.Row(
                    dash_table.DataTable(
                        id="table-lang",
                        columns=lang_columns,
                        data=language_table.query("Region==0").to_dict("records"),
                        filter_action="native",
                        style_table={"height": None},
                        fixed_rows={"headers": False, "data": 0},
                        style_cell={"width": "85px"},
                    ),
                ),
                dcc.Store(id="store"),
            ]
        ),
    ]
)

abstract_card = dbc.Card(
    [
        dbc.CardHeader(html.H3("Abstract")),
        dbc.CardBody(
            dbc.Row(
                dbc.Col(
                    [
                        html.P(
                            "This study used the 2016 Canadian Census data to examine home bilingualism amongst children aged 0–9 years. Across Canada, 18 percent of children used at least two languages at home, which rose to more than 25 percent in large cities, and the Canadian territories. English and French was the most common language pair in Quebec and Ontario, and various other pairs were spoken in most provinces. In the territories, 17 percent of children spoke an Indigenous language and English, and we discuss specific opportunities and challenges for Indigenous language revitalization. The presence of bilingual adults in the home, and immigration generation were the strongest predictors of children's home bilingualism. We conclude by discussing how policies can encourage child bilingualism, such as by supporting children’s home language in early and primary education settings. Such policies must be tailored to the needs of the specific communities to optimally support bilingual children and their families. "
                        ),
                        html.A(
                            "For more information, find the full paper at https://psyarxiv.com/6q9jg/",
                            href="https://psyarxiv.com/6q9jg/",
                        ),
                    ]
                )
            )
        ),
    ]
)

app.layout = html.Div(
    [
        header,
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(figure_card, md=6),
                    dbc.Col(
                        [table_card, abstract_card],
                    ),
                ]
            ),
            fluid=True,
        ),
    ]
)


@app.callback(Output("graph", "figure"), Input("color-drop-menu", "value"))
def update_overlay(selected_overlay):
    return make_figure(selected_overlay)


@app.callback(
    Output("store", "data"),
    Input("graph", "clickData"),
    State("store", "data"),
    prevent_initial_call=True,
)
def set_mode(click, store):
    print(store)
    return True if store is None else None


@app.callback(
    [
        Output("table-lang", "data"),
        Output("region_name", "children"),
        Output("table-lang", "columns"),
    ],
    [Input("graph", "hoverData"), Input("color-drop-menu", "value")],
    State("store", "data"),
)
def update_table(hover, age_val, mode):
    # Get age
    age = age_val.strip("Percent_age_")
    age_columns = [
        {"name": col_map[idx], "id": idx}
        for idx in col_map.keys()
        if "percent" not in idx or age in idx
    ]
    region_name = "Region: "
    if mode is None:
        if hover is None:
            subset = language_table.query('type == "canada"')
            region_name += "All of Canada"
            return subset.to_dict("records"), region_name, age_columns
        else:
            hover_location = hover["points"][0]["location"]
            hover_name = hover["points"][0]["hovertext"]
            # Hardcoded fix for Ottawa and Northern Canada
            if "Ottawa" in hover_name or hover_name in [
                "Northwest Territories",
                "Nunavut",
                "Yukon",
            ]:
                if "Ottawa" in hover_name:
                    hover_name = "Ottawa"
                else:
                    hover_name = "Northern Canada"
                subset = language_table.query("name == @hover_name")
                return subset.to_dict("records"), region_name + hover_name, age_columns
            subset = language_table.query("Region == @hover_location")
            return subset.to_dict("records"), region_name + hover_name, age_columns
    return dash.no_update, dash.no_update, age_columns


if __name__ == "__main__":
    app.run_server(debug=True)
