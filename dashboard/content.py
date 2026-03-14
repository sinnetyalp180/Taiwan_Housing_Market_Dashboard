from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.index import app
from dashboard.layout._data_table_card import data_table_card

# from dashboard.layout.dataquery_footer import dataquery_footer
# from dashboard.layout.dataquery_footer import dataquery_map, dataquery_towm

# from dashboard.layout.distribution_card import distribution_card
from dashboard.layout.navbar import navbar
# from dashboard.layout.scatter_card import scatter_card
# from dashboard.layout.trend_card import trend_card
# from dashboard.layout.tutorial_1_markdown import tutorial_1_markdown
# from dashboard.layout.dataquery_form import dataquery_form

from dashboard.callbacks import callbacks_plot, callbacks_data
from dashboard.layout.dataQuery_map_card import county_map_card, town_map_card, ai_pairing_card



app.layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col(
                [html.Div([county_map_card]), ], lg=6),
            dbc.Col(
                [html.Div([town_map_card]), ], lg=6),
        ]),

        dbc.Row([
            html.Div([], style={"width": "100%", 'height':'50px'}),
            html.Div([ai_pairing_card]), ],
        ),
        html.Div([], style={"width": "100%", 'height':'50px'})


        # dbc.Col(html.Div([
        #     county_map_card,
        # ],)),
        # dbc.Col(html.Div([
        #     town_map_card,
        # ],)),

        # dbc.Row([
        #     # result area
        # ],),

    ], 
    fluid=True),

])



