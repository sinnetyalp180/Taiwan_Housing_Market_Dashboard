from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime
                           

# 建立資料 (test)
df = pd.DataFrame({
    "年份": [2018, 2019, 2020, 2021, 2022],
    "人口": [2700000, 2720000, 2740000, 2750000, 2765000]
})

# df_2 = px.data.gapminder().query("country == 'Taiwan'")
fig = px.line(df, x="年份", y="人口", title="人口成長趨勢")

# taiwan_data_table = dbc.Spinner(
#     dash_table.DataTable(
#             id='datatable',
#             page_current=0,
#             page_size=10,
#             page_action='custom',
#             style_table={'overflowX': 'auto'}
#         ))


tab_style = {
    'padding': '10px',
    'fontWeight': 'bold',
    'fontSize': '16px',
    'color': 'gray',
    'border': '1px solid #d6d6d6',
    'borderRadius': '10px 10px 0 0',
    'marginRight': '5px',
    'backgroundColor': '#f9f9f9',
}
tab_selected_style = {
    'padding': '10px',
    'fontWeight': 'bold',
    'fontSize': '16px',
    'color': 'white',
    'backgroundColor': '#007BFF',
    'borderRadius': '10px 10px 0 0',
    'border': '1px solid #007BFF',
}


taiwan_data_table = dbc.Spinner(
    html.Div(children=[
        dcc.Tabs(id='tabs-example', value='tab-4', children=[                    # 啟動頁面時，callback tab-1
            
            dcc.Tab(label='房屋價格分佈', value='tab-4', children=[
                html.Div([html.Br(), "選擇年份"]),
                dcc.Slider(
                    id="year-slider-single-t4",
                    min=2010,
                    max=datetime.now().year,
                    step=1,
                    value=datetime.now().year -1 ,                       # 預設當前年份
                    marks={y: str(y) for y in range(2000, datetime.now().year + 1, 1)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    included=False,                                      # ✅ 不顯示區間區塊，讓它更像單點選擇器
                ),
                # dcc.Graph(figure=fig),                                # (sample)
                dcc.Graph(id="box-plot"),
            ],
            style=tab_style,
            selected_style=tab_selected_style,
            ),
            
            dcc.Tab(label='成交比例', value='tab-1', children=[
                html.Div([html.Br(), "選擇年份"]),
                # dcc.Dropdown(
                #     [year for year in range(2010, datetime.now().year + 1, 1)],
                #     id="year-dropdown"),
                dcc.Slider(
                    id="year-slider-single-t1",
                    min=2010,
                    max=datetime.now().year,
                    step=1,
                    value=datetime.now().year -1 ,                       # 預設當前年份
                    marks={y: str(y) for y in range(2000, datetime.now().year + 1, 1)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    included=False,                                      # ✅ 不顯示區間區塊，讓它更像單點選擇器
                ),
                # dcc.Graph(figure=fig),                                # (sample)
                dcc.Graph(id="volume-pie"),
            ],
            style=tab_style,
            selected_style=tab_selected_style,
            ),
 
            dcc.Tab(label='平均單價(坪)', value='tab-2', children=[
                html.Div([html.Br(), "滑動選擇年份區間"]),
                dcc.RangeSlider(
                    id="year-slider-p2",
                    min=2010,
                    max=datetime.now().year,
                    step=1,
                    marks={y: str(y) for y in range(2010, datetime.now().year + 1, 2)},
                    value=[2010, datetime.now().year],
                ),
                dcc.Graph(id='line-chart-2'),
            ],
            style=tab_style,
            selected_style=tab_selected_style,
            ),
            
            dcc.Tab(label='成長率(坪)', value='tab-3', children=[
                html.Div([html.Br(), "滑動選擇年份區間"]),
                dcc.RangeSlider(
                    id="year-slider-p3",
                    min=2010,
                    max=datetime.now().year,
                    step=1,
                    marks={y: str(y) for y in range(2010, datetime.now().year + 1, 2)},
                    value=[2010, datetime.now().year],
                ),
                dcc.Graph(id='line-chart-3'),
            ],
            style=tab_style,
            selected_style=tab_selected_style,
            ),


            # dcc.Tab(label='AI', value='tab-5', children=[
            #     dash_table.DataTable(
            #         id='table',
            #         data=df.to_dict('records'),
            #         columns=[{'name': i, 'id': i} for i in df.columns],
            #         page_size=10,
            #         style_table={'overflowX': 'auto'},
            #         style_cell={'textAlign': 'center'},
            #     ),
            # ],
            # style=tab_style,
            # selected_style=tab_selected_style,
            # ), 
        ],
        colors= {
            "border": "lightgray",
            "primary": "blue",
            "background": "white",
        },
        style={
            'margin': '20px',
        },
        ),
        html.Div(id='tabs-content'),
    ],
    # style={'height': '600px'}, 
    )
)



county_data_table = dbc.Spinner(
    html.Div(children=[
        dcc.Tabs(id='tabs-example_C', value='tab-1c', children=[
            dcc.Tab(label='平均單價(坪)', value='tab-1c', children=[
                html.Div([html.Br(), "滑動選擇年份區間"]),
                dcc.RangeSlider(
                    id="year-slider-1c",
                    min=2010,
                    max=datetime.now().year,
                    step=1,
                    marks={y: str(y) for y in range(2010, datetime.now().year + 1, 2)},
                    value=[2010, datetime.now().year],
                ),
                dcc.Graph(id="line-chart-1c"),
            ],
            style=tab_style,
            selected_style=tab_selected_style,
            ),
            dcc.Tab(label='成交量', value='tab-2c', children=[
                html.Div([html.Br(), "選擇年份"]),
                dcc.Slider(
                    id="year-slider-single-2c",
                    min=2010,
                    max=datetime.now().year,
                    step=1,
                    value=datetime.now().year -1 ,                       # 預設當前年份
                    marks={y: str(y) for y in range(2000, datetime.now().year + 1, 1)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    included=False,                                      # ✅ 不顯示區間區塊，讓它更像單點選擇器
                ),
                dcc.Graph(id="line-chart-2c"),
            ],
            style=tab_style,
            selected_style=tab_selected_style,
            ),
            dcc.Tab(label='房屋成交價格分布', value='tab-3c', children=[
                html.Div([html.Br(), "選擇年份"]),
                dcc.Slider(
                    id="year-slider-single-3c",
                    min=2010,
                    max=datetime.now().year,
                    step=1,
                    value=datetime.now().year -1 ,                       # 預設當前年份
                    marks={y: str(y) for y in range(2000, datetime.now().year + 1, 1)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    included=False,                                      # ✅ 不顯示區間區塊，讓它更像單點選擇器
                ),
                dcc.Graph(id="line-chart-3c"),
            ],
            style=tab_style,
            selected_style=tab_selected_style,
            ),
            dcc.Tab(label='成長率(坪)', value='tab-4c', children=[
                html.Div([html.Br(), "滑動選擇年份區間"]),
                dcc.RangeSlider(
                    id="year-slider-4c",
                    min=2010,
                    max=datetime.now().year,
                    step=1,
                    marks={y: str(y) for y in range(2010, datetime.now().year + 1, 2)},
                    value=[2010, datetime.now().year],
                ),
                dcc.Graph(id="line-chart-4c"),
            ],
            style=tab_style,
            selected_style=tab_selected_style,
            ),
        ],
        colors= {
            "border": "lightgray",
            "primary": "blue",
            "background": "white",
        },
        style={
            'margin': '20px',
        },
        )
    ], 
    # style={'height': '600px'}, 
    )
)

