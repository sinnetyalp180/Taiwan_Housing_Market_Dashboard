from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

data_table_card = dbc.Card([
    dbc.CardHeader("Datatable (10 rows per page)"),

    dbc.CardBody([                            
        dbc.Spinner(dash_table.DataTable(
            id='datatable',
            page_current=0,
            page_size=10,
            page_action='custom',
            style_table={'overflowX': 'auto'}
        ))
    ]),

    dbc.CardFooter([
        dbc.Button([
            html.Span(html.I(className='bi bi-download'), className='me-2'), 
            "Download"
        ], size="sm", color='dark', id='download-btn'),        
        dcc.Download(id="download-csv"),

        html.Div(id='datastore-shape')
    ], className='d-flex justify-content-between')
], class_name='mb-3')
