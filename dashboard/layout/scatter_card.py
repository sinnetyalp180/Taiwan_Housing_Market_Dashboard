from dash import dcc
import dash_bootstrap_components as dbc

scatter_card = dbc.Card([
    dbc.CardHeader("Scatter Chart"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id="scatter-y-dropdown", placeholder='Select Y-axis...', className='mb-3'),
                dcc.Dropdown(id="scatter-x-dropdown", placeholder='Select X-axis...')
            ], lg=4),
            dbc.Col([
                dcc.Graph(id='scatter-graph')
            ], lg=8)
        ])
    ])
], class_name='mb-3')
