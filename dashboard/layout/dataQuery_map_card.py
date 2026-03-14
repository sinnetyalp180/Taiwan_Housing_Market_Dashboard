from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import geopandas as gpd
import dash_leaflet as dl

import dashboard.utils.functions as dash_func
import dashboard.layout.dash_table as dash_tabs

'''
sample_card = dbc.Card([
    dbc.CardHeader([]),
    dbc.CardBody([]),
    dbc.CardFooter([]),
    ],
    className='mb-3',
)
'''
#%%

# taiwan_border = [[21.8969, 120.818], [25.3006, 122.000], [25.3006, 119.900], [21.8969, 119.900], [21.8969, 120.818]]
taiwan_border = dash_func.get_taiwan_border()

county_geographic_info = dash_func.read_county_geographic_info()

county_message_box = html.Div(
    children = dash_func.get_county_info(),                            # [a, b, c, d, e]
    id = "county-msg-box", className = "info_box",
    style = {"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000",
             "backgroundColor": "rgba(255, 255, 255, 0.7)",            # 透明白底 (0.7 代表 70% 不透明度)
             "padding": "10px",                                        # 內邊距，避免內容貼邊
             "borderRadius": "8px",                                    # 圓角
             "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",               # 添加陰影讓它更美觀
             }
)

#%%

county_map_card = dbc.Card([
    dbc.CardHeader(
        ['Taiwan'], id='county-card-title',
        style={
            "background": "#4F4F4F",
            "color": "white",
            "fontWeight": "bold",                                        # 加粗
            "fontSize": "20px",                                          # 字體大小
        },  
    ),       
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                # dcc.Dropdown(
                dbc.Select(
                    id = "county-dropdown", className='mb-3',
                    options = [{"label": "台北市", "value": "Taipei"}, 
                               {"label": "新北市", "value": "NewTaipei"}, 
                               {"label": "高雄市", "value": "Kaohsiung"},
                              ],
                    style={
                        "width": "80%",
                        "margin": "10px auto",                           # 上下左右外邊距，auto 可讓元件水平置中
                        "padding": "8px",                                # 內邊距
                        "border": "1px solid #ccc",                      # 灰色邊框
                        "borderRadius": "5px",                           # 邊角圓弧
                        "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",      # 輕微陰影
                    },           
                    placeholder = 'Select a numeric column...',
                ),
                dl.Map([
                    dl.TileLayer(),                                                                     # 加載 map 底圖
                    dl.Polygon(                                                                         # 台灣以外的灰色遮罩
                        positions=[[[-90, -180], [-90, 180], [90, 180], [90, -180], [-90, -180]],       # 世界外框 (逆時針)
                        # taiwan_border,                                                                # 台灣邊界 (順時針) - 應該是內部洞
                        # dash_func.get_taiwan_border(),
                        ],
                        color = "gray",
                        fillColor = "lightblue",                                # 多邊形的邊線顏色
                        fillOpacity = 0.5,                                      # 內部透明度
                    ),
                    # dl.GeoJSON(
                    #     data = dash_func.get_world_geojson(),
                    #     style = {"color": "gray", "fillColor": "gray", "fillOpacity": 0.5},
                    # ),
                    dl.GeoJSON(
                        data = dash_func.display_county_info(),
                        # data = dash_func.get_single_county_geojson(),
                        id = "geo-county-json",
                        style = {"color": "blue", "weight": 2, "fillOpacity": 0.0},
                        # style = {"color": "#ff00ff", "weight": 2, "fillOpacity": 0.0},
                        hoverStyle = {"color": "red", "weight": 2, "fillOpacity": 0.2},
                        options = {"interactive": True,                         # 確保圖層可交互
                                   },                  
                    ),
                    county_message_box,
                ],
                style={"width": "80%", "height": "400px"},
                center=[23.6978, 120.9605],                                # 台灣的中心點
                maxBounds=[[21.5, 118.5], [28.0, 124.5]],                  # 設定地圖的最大可顯示範圍，[[左下角], [右上角]]
                maxBoundsViscosity=1.0,                                    # 可以設定當用戶移出範圍時，拖動的“粘性”程度，設為 1.0 會強制用戶停留在範圍內
                id = "county-map",
                zoom=7,
                ),
                html.Div(style={"width": "100%", "height": "10px"},),      # (預留空白)
            ], 
            # lg=12,
            style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",               # 水平置中
            },
            ),

            # dbc.Col([
            #     dcc.Graph(id='scatter-graph')
            # ], lg=7),
        ],),
    
        dbc.Row([
            # dcc.Graph(id='scatter-graph'),
            dash_tabs.taiwan_data_table,
            ],
        ),
        dbc.Row([
            html.Div(style={"width": "100%", "height": "10px"},),            # (預留空白)
        ]),
        dcc.Store(id = "county-data-store",
                  data = county_geographic_info.to_json(),                    # GeoJSON 字符串
        ),
        dcc.Store(id = "county_and_id",
                  data = {}
        ),
    ],
    style={
        "height": "1150px",                      # 固定高度
        "overflowY": "auto",                     # 若內容超出高度，出現垂直捲軸
        "padding": "15px",                       # 內邊距可視情況調整
        "border": "2px solid lightgray",         # 加上邊框（可選）
    },
    ),
    dbc.CardFooter([]),
    ],
)




#%%

town_geographic_info = dash_func.read_town_geographic_info()

town_message_box = html.Div(
    children = dash_func.get_town_info(),                             # [a, b, c, d, e]
    id = "town-msg-box", className =  "info_box",
    style = {"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000",
             "backgroundColor": "rgba(255, 255, 255, 0.7)",              # 透明白底 (0.7 代表 70% 不透明度)
             "padding": "10px",                                          # 內邊距，避免內容貼邊
             "borderRadius": "8px",                                      # 圓角
             "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",                 # 添加陰影讓它更美觀
             },
)
town_map_card = dbc.Card([
    dbc.CardHeader([
        html.Div(['Town'], id='town-card-title-1', style={'display': 'inline-block', 'margin-right': '10px'}),
        html.Div([''], id='town-card-title-2', style={'display': 'inline-block'})], 
        id='town-card-title',
        style={
            "background": "#4F4F4F",
            "color": "white",
            "fontWeight": "bold",                                        # 加粗
            "fontSize": "20px",                                          # 字體大小
        },
    ),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.Select(
                    id = "town-dropdown", className='mb-3',
                    options = [{"label": "台北市", "value": "Taipei"}, 
                               {"label": "新北市", "value": "NewTaipei"}, 
                               {"label": "高雄市", "value": "Kaohsiung"},
                               ],

                    style={
                        "width": "80%",
                        "margin": "10px auto",                           # 上下左右外邊距，auto 可讓元件水平置中
                        "padding": "8px",                                # 內邊距
                        "border": "1px solid #ccc",                      # 灰色邊框
                        "borderRadius": "5px",                           # 邊角圓弧
                        "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",      # 輕微陰影
                        # "background": "#E0E0E0",
                    },                     
                    placeholder = 'Select a numeric column...',
                ),
                dl.Map([
                    dl.TileLayer(),                                            # 加載 map 底圖
                    dl.GeoJSON(data = dash_func.display_town_info(), 
                            id="geo-town-json",
                            style = {"color": "blue", "weight": 2, "fillOpacity": 0.2},
                            hoverStyle = {"color": "red", "weight": 2, "fillOpacity": 0.0},
                            options = {"interactive": True},                   # 確保圖層可交互
                            ),
                    town_message_box,
                ],
                style={"width": "80%", "height": "400px"},
                center=[23.6978, 120.9605],                                    # 台灣的中心點
                id = "town-map",
                zoom = 9,
                ),
                html.Div(style={"width": "100%", "height": "10px"}),

            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",               # 水平置中
            },
            ),
        ]),

        dbc.Row([
            # dcc.Graph(id='scatter-graph'),
            dash_tabs.county_data_table,
            ],
        ),        
    ],
    style={
        "height": "1150px",                      # 固定高度
        "overflowY": "auto",                     # 若內容超出高度，出現垂直捲軸
        "padding": "15px",                       # 內邊距可視情況調整
        "border": "2px solid lightgray",         # 加上邊框（可選）
        # "borderRadius": "8px",                 # 可選：圓角
        # "boxShadow": "2px 2px 8px rgba(0, 0, 0, 0.2)",                               # 陰影效果
        # "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"                                  # 常見浮起感
        # "boxShadow": "0 8px 16px rgba(0, 0, 0, 0.2)"                                 # 更浮動感
        # "boxShadow": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",         # Material Design 風格
    },
    ),
    dcc.Store(id = "county-name-store",
              data = "",
              ),
    dbc.CardFooter([]),
    ],

)


#%%

match_message_box = html.Div(
    children = dash_func.get_town_info(),                             # [a, b, c, d, e]
    id = "match-msg-box", className =  "info_box",
    style = {"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000",
             "backgroundColor": "rgba(255, 255, 255, 0.7)",              # 透明白底 (0.7 代表 70% 不透明度)
             "padding": "10px",                                          # 內邊距，避免內容貼邊
             "borderRadius": "8px",                                      # 圓角
             "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",                 # 添加陰影讓它更美觀
             },
)

ai_pairing_card = dbc.Card([
    dbc.CardHeader([
        html.Div(['AI Matchmaking']),
    ],
    style={
        "background": "#4F4F4F",
        "color": "white",
        "fontWeight": "bold",                                             # 加粗
        "fontSize": "20px",                                               # 字體大小
    },
    ),

    dbc.CardBody([

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div(['偏好選擇 (可複選)'], style={"fontWeight": "bold",}),
                    html.Br(),
                    html.Div([
                        dcc.Checklist(id='check-A1', options=[{'label': ' 縣市區域', 'value': 'A1'}], value=[]),
                        dbc.Select(
                            id = "county-dropdown-2", className='mb-3',
                            # options = [{"label": "台北市", "value": "Taipei"}, 
                            #         {"label": "新北市", "value": "NewTaipei"}, 
                            #         {"label": "高雄市", "value": "Kaohsiung"},
                            #         ],
                            style={
                                "width": "80%",
                                "margin": "10px 10px 0px 60px left",              # 上右下左 分別為 10 10 0 60 像素
                                "marginLeft": "20px",
                                "padding": "8px",                                 # 內邊距
                                "border": "1px solid #ccc",                       # 灰色邊框
                                "borderRadius": "5px",                            # 邊角圓弧
                                "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",       # 輕微陰影
                                "pointerEvents": "none",                          # 禁止點擊
                                "opacity": "0.5",                                 # 淡化外觀
                                "backgroundColor": "#f0f0f0"                    # 類似 disabled 視覺效果
                            },           
                            placeholder = '',
                        ),
                        ]
                    ),
                    html.Div([
                        dcc.Checklist(id='check-A2', options=[{'label': ' 購屋預算(萬)', 'value': 'A2'}], value=[]),
                        dcc.Slider(
                            id="price-slider",
                            min=500,
                            max=5000,
                            step=100,
                            value=1500,                                          # 預設當前價格
                            marks={y: str(y) for y in range(500, 5500, 1500)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            included=False,                                      # ✅ 不顯示區間區塊，讓它更像單點選擇器
                            disabled=True,
                        ),
                        html.Br(),
                        ]
                    ),
                    html.Div([dcc.Checklist(id='check-A3', options=[{'label': ' 交易熱區', 'value': 'A3'}], value=[], style={"margin-bottom": "5px"}),]),
                    html.Div([dcc.Checklist(id='check-A4', options=[{'label': ' 房價成長性', 'value': 'A4'}], value=[], style={"margin-bottom": "5px"}),]),
                    html.Div([dcc.Checklist(id='check-A5', options=[{'label': ' 環境清幽', 'value': 'A5'}], value=[], style={"margin-bottom": "5px"}),]),

                    dbc.Button("偏好配對 -->", color="primary", id="pair-btn",
                        style={
                            "width": "40%",
                            "position": "absolute",
                            "bottom": "10px",
                            "right": "10px",
                            "fontWeight": "bold",
                        },),
                    ],
                style={
                    "width": "100%", "height": "400px", 
                    "padding": "20px",
                    "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",
                    "position": "relative",
                    },
                ),
            ],
            lg=4),

            dbc.Col([
                html.Div([
                    dash_table.DataTable(
                        columns=[
                            {'name':'分類群組', 'id':'group'}, {'name':'說明', 'id':'explain'}],
                        data=[
                            {'group':'0', 'explain':'熱門、交易量高、成長快(蛋黃區)'},
                            {'group':'1', 'explain':'安靜、交易少但潛力中等(蛋白區)'},
                            {'group':'2', 'explain':'成長性低、交易低(偏鄉或已飽和)'},
                        ],
                        style_cell={                                      # 預設置中
                            'textAlign': 'center',
                            'padding': '5px',
                            },
                        style_cell_conditional=[{                         # 特定欄位調整
                            'if': {'column_id': 'explain'},
                            'textAlign': 'center',
                            'paddingLeft': '0px',                         # 左側空格
                            }
                        ],
                        style_header={
                            'textAlign': 'center',
                            'fontWeight': 'bold'
                        },
                    ),
                    ]
                ),
                # html.Br(),
                html.Div([
                    html.H5(['配對結果',], id='match-result-title', 
                            style={'fontSize':'18px', 'fontWeight':'bold'}),
                    # html.Br(),
                    html.Div(id='table-container'),
                    ],
                    style={
                        "border": "1px solid #e0e0e0",                         # 邊框
                        "borderRadius": "12px",                                # 圓角
                        "backgroundColor": "#fafafa",                        # 淺底色
                        "padding": "16px",                                     # 內距
                        "marginTop": "20px",                                   # 上方空間
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                    },
                ),
            ], lg=4),


            dbc.Col([
                dl.Map([
                    dl.TileLayer(
                        # url="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
                        url="https://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
                        attribution="© OpenStreetMap",
                    ),                                            # 加載 map 底圖
                    dl.GeoJSON(data = dash_func.display_town_info(), 
                            id="geo-match-json",
                            style = {"color": "#00FFFF", "weight": 1, "fillOpacity": 0.2},
                            hoverStyle = {"color": "#FF0000", "weight": 2, "fillOpacity": 0.0},
                            options = {"interactive": True},                   # 確保圖層可交互
                            ),
                    match_message_box,
                ],
                style={"width": "100%", "height": "400px"},
                center=[23.6978, 120.9605],                                    # 台灣的中心點
                id = "match-map",
                zoom = 10,
                ),



            ],
            style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",               # 水平置中
            }, 
            lg=4),
        ]),
    
    ],
    style={
        "border": "2px solid lightgray",             # 加上邊框（可選）
    }
    ),

    dbc.CardFooter([]),


])


# dcc.Checklist(
#     id="my-checklist",
#     options=[
#         {"label": "選項 A", "value": "A"},
#         {"label": "選項 B", "value": "B"},
#         {"label": "選項 C", "value": "C"},
#     ],
# value=["A"],
# labelStyle={"display": "block"},  # 垂直排列
# style={"margin": "10px"}
# ),




