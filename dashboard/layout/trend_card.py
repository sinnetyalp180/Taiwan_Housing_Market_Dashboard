from dash import dcc
import dash_bootstrap_components as dbc

trend_card = dbc.Card([
    dbc.CardHeader("Trend Chart"),
    dbc.CardBody([        
        dcc.Dropdown(id="trend-numeric-dropdown", placeholder='Select a numeric column...', className='mb-3'),
        dcc.Dropdown(id="trend-datetime-dropdown", placeholder='Select a datetime column...', className='mb-3'),
        dcc.Graph(id='trend-graph', style={'height': '250px'})
    ])
], class_name='mb-3')
