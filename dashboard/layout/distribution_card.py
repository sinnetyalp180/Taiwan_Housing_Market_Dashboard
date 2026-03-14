from dash import dcc
import dash_bootstrap_components as dbc

distribution_card = dbc.Card([
    dbc.CardHeader("Distribution Chart"),
    dbc.CardBody([        
        dcc.Dropdown(
            id = "dist-dropdown", className='mb-3',
            options = [{"label": "台北市", "value": "Taipei"}, 
                       {"label": "新北市", "value": "NewTaipei"}, 
                       {"label": "高雄市", "value": "Kaohsiung"}],
            placeholder = 'Select a numeric column...', 
            ),
        dcc.Graph(id='dist-graph', style={'height': '250px'})
    ])
], class_name='mb-3')
