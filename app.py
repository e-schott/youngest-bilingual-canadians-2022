import dash
import dash_bootstrap_components as dbc
import geopandas as gpd
import pandas as pd
import plotly.express as px
from dash import dash_table
from dash import html, dcc
from dash.dependencies import Input, Output, State

external_stylesheets = [dbc.themes.FLATLY, "assets/styles.css"]
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
    " - ".join([reg.strip(" ") for reg in row.area.split("–")])
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
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, b=0, t=30),
        uirevision=True,
    )
    return fig


button_gh = dbc.Button(
    "View Code on github",
    outline=True,
    color="light",
    href="https://github.com/e-schott/youngest-bilingual-canadians-2022",
    id="gh-link",
    style={"text-transform": "none"},
)

# Define Header Layout
header = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
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
                                [dbc.NavItem(button_gh)],
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
    color="secondary",
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

button_group = html.Div(
    [
        dbc.RadioItems(
            id="age_radios",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",
            options=[
                {"label": col_label, "value": col_name}
                for col_name, col_label in zip(columns, column_label)
            ],
            value="Percent_age_0_to_9",
        ),
        html.Div(id="output"),
    ],
    className="radio-group",
)


figure_card = dbc.Card(
    [
        dbc.CardHeader(html.H3("Home bilingualism in Canada")),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.B("Choose the age group to display:"),
                            width={"offset": 4},
                            align="center",
                        ),
                        dbc.Col(button_group, md=6),
                    ],
                    align="right",
                ),
                dbc.Row(dbc.Col(figure_box)),
            ]
        ),
        dbc.CardFooter(
            dbc.Row(
                [
                    html.P(
                        "Adapted from Statistics Canada, 2016 Census of Population Public Use Microdata File Individuals File, 2019. This does not constitute an endorsement by Statistics Canada of this product."
                    ),
                    html.Div(
                        [
                            "Data Analysis: ",
                            html.A("Esther Schott", href="https://github.com/e-schott"),
                        ],
                        style={"display": "inline-block"},
                    ),
                    html.Div(
                        [
                            "Dashboard: ",
                            html.A("Esther Schott", href="https://github.com/e-schott"),
                            " & ",
                            html.A("Sebastian Urchs", href="https://github.com/surchs"),
                        ],
                        style={"display": "inline-block"},
                    ),
                ]
            )
        ),
    ]
)

table_card = dbc.Card(
    [
        dbc.CardHeader([dbc.Row([html.H3("Most Common Language Pairs")])]),
        dbc.CardBody(
            [
                dbc.Row([html.H5(id="region_name")]),
                dbc.Row(
                    dash_table.DataTable(
                        id="table-lang",
                        columns=lang_columns,
                        data=language_table.query("Region==0").to_dict("records"),
                        filter_action="none",
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
        dbc.CardHeader(html.H3("More about our paper")),
        dbc.CardBody(
            dbc.Row(
                dbc.Col(
                    [  # html.H3("Most Common Language Pairs"),
                        html.P(
                            "This study used the 2016 Canadian Census data to examine home bilingualism amongst children aged 0–9 years. Across Canada, 18 percent of children used at least two languages at home, which rose to more than 25 percent in large cities, and the Canadian territories. English and French was the most common language pair in Quebec and Ontario, and various other pairs were spoken in most provinces. In the territories, 17 percent of children spoke an Indigenous language and English, and we discuss specific opportunities and challenges for Indigenous language revitalization. The presence of bilingual adults in the home, and immigration generation were the strongest predictors of children's home bilingualism. We conclude by discussing how policies can encourage child bilingualism, such as by supporting children’s home language in early and primary education settings. Such policies must be tailored to the needs of the specific communities to optimally support bilingual children and their families. "
                        ),
                        html.A(
                            "For more information, find the full paper at https://psyarxiv.com/6q9jg/",
                            href="https://psyarxiv.com/6q9jg/",
                        ),
                        html.P(""),
                        html.H5("Authors"),
                        html.A(
                            "Esther Schott",
                            href="https://e-schott.github.io/",
                        ),
                        ", ",
                        html.A(
                            "Lena V. Kremin",
                            href="https://www.lenavkremin.com/",
                        ),
                        " & ",
                        html.A(
                            "Krista Byers-Heinlein",
                            href="http://infantresearch.ca/team",
                        ),
                    ]
                )
            )
        ),
    ]
)

faq_card = dbc.Card(
    [
        dbc.CardHeader(html.H3("FAQs")),
        dbc.CardBody(
            html.Div(
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                "Young children learn so much about language in the first few years, and as our analysis shows, at least 17 % of children in Canada grow up with at least two languages. It's important to learn about young bilinguals, to be able to better support them in ",
                                html.A(
                                    "school, and in their community.",
                                    href="https://osf.io/jerty",
                                ),
                            ],
                            title="Why do you focus on children?",
                            item_id="item-1",
                        ),
                        dbc.AccordionItem(
                            [
                                html.P(
                                    "In the dataset, we only have information about the children's home languagues. For all children, the adults living with them indicated which languages they speak (for older kids) or hear (for kids who don't speak yet). So, especially older kids may use other languages in school that isn't captured in our data, so the numbers of bilinguals almost certainly underestimates the total number of bilingual children."
                                ),
                            ],
                            title="What do you mean by home bilingualism?",
                            item_id="item-2",
                        ),
                        dbc.AccordionItem(
                            [
                                html.P(
                                    "We used the 'Individuals' dataset from the Public Use Microdata Files from Statistics Canada. These data were collected as part of the 2016 Census."
                                ),
                            ],
                            title="Where do your data come from?",
                            item_id="item-3",
                        ),
                        dbc.AccordionItem(
                            "The data that Statistics Canada released are chosen so no identifiable details are revealed about the respondents. This is easier in big cities, and hard in less populated areas. For this reason, we have specific info about the location of residents of big cities, and know only the province for residents of less populated areas.",
                            title="Why is there detailed info on some areas (big cities) but not others?",
                            item_id="item-1",
                        ),
                        dbc.AccordionItem(
                            [
                                "If you're interested in reading more about bilingual children and babies in particular,  ",
                                html.A(
                                    "this paper",
                                    href="https://osf.io/jerty",
                                ),
                                " geared towards parents is a great place to start. You can also find information about studies with bilingual babies and children ",
                                html.A(
                                    "on our website. ",
                                    href="http://infantresearch.ca/welcome",
                                ),
                            ],
                            title="Where can I learn more about young bilinguals?",
                            item_id="item-4",
                        ),
                    ],
                    active_item="item-4",
                )
            )
        ),
    ]
)


app.layout = html.Div(
    [
        header,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(figure_card),
                        dbc.Col(
                            [table_card, abstract_card],
                        ),
                    ]
                ),
                dbc.Row(dbc.Col(faq_card)),
            ],
            fluid=True,
        ),
    ]
)


@app.callback(Output("graph", "figure"), Input("age_radios", "value"))
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
    [Input("graph", "hoverData"), Input("age_radios", "value")],
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
            hover_province = hover["points"][0]["customdata"][0]
            # Hardcoded fix for Ottawa and Northern Canada
            if "Ottawa" in hover_name or hover_name in [
                "Northwest Territories",
                "Nunavut",
                "Yukon",
            ]:
                if "Ottawa" in hover_name and hover_province == "Quebec":
                    hover_name = "Gatineau"
                elif "Ottawa" in hover_name and hover_province == "Ontario":
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
