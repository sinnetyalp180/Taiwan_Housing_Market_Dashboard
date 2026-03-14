from dash import html, dcc
import dash_bootstrap_components as dbc
import datetime as dt
from dashboard.utils.constants import TANKS, PI_SUMMARYTYPE

dataquery_form = html.Div([
    dbc.Label("Line"),
    dcc.Dropdown(id="tank-dropdown", options=TANKS, className='mb-3'),

    dbc.Label("Date Interval"),
    dcc.DatePickerRange(
        id='date-picker',
        min_date_allowed=dt.date(2011, 1, 1), 
        month_format='YYYY-MM',
        display_format='Y-M-D',
        start_date=dt.date(2023, 6, 1),
        className='d-block mb-3'),

    dbc.Label("Product"),
    dbc.Spinner(dcc.Dropdown(id="product-dropdown", placeholder='Select a product', className='mb-3'), size="sm"),

    dbc.Label("Y Tag"),
    dcc.Dropdown(id="ytag-dropdown", placeholder='Select a Y tag', className='mb-3'),

    dbc.Label("X Tags"),
    dcc.Dropdown(id="xtags-dropdown", placeholder='Select X tags', className='mb-3', multi=True),

    dbc.Label("Time Interval"),
    html.Div([
        dbc.Input(id='time-input', value=1, type="number", min=1, step=1, class_name='me-3'), 
        dbc.RadioItems(id='time-unit', value='Hours', inline=True, class_name='text-nowrap', 
                       options = ['Hours', 'Minutes'])
    ], className='mb-3 d-flex align-items-center'),

    dbc.Label("Summary Type"),
    dcc.Dropdown(
        id="summarytype-dropdown", 
        options=[{'label': t, 'value': PI_SUMMARYTYPE[t]} for t in PI_SUMMARYTYPE.keys()], 
        multi=True, 
        value=PI_SUMMARYTYPE['AVERAGE'],
        className='mb-4'
    ),
    html.Br(),

], style={'backgroundColor': '#f0f0f0'})