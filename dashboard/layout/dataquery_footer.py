from dash import html, dcc
import dash_bootstrap_components as dbc
import geopandas as gpd
import dash_leaflet as dl

from dashboard.callbacks._callbacks_plot import geopandas_test, get_info, geopandas_town_test


upload_button = dcc.Upload(                            
    dbc.Button('Upload', color='dark', class_name='me-2', id='upload-btn'), 
    id='data-upload'
)

submit_button = dbc.Button("Submit", color="primary", id='submit-btn')



dataquery_info = html.Div(children=get_info(), id="map_info", className="info",
                          style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000",
                                 "backgroundColor": "rgba(255, 255, 255, 0.7)",           # 透明白底 (0.7 代表 70% 不透明度)
                                 "padding": "10px",                                       # 內邊距，避免內容貼邊
                                 "borderRadius": "8px",                                   # 圓角
                                 "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",              # 添加陰影讓它更美觀
                                 })

geojson_data = geopandas_test()
geoMap = dl.Map([dl.TileLayer(),                                       # 加載 map 底圖
                 dl.GeoJSON(data=geojson_data, id="geojson", 
                            style={"color": "blue", "weight": 2, "fillOpacity": 0.2},
                            hoverStyle={"color": "red", "weight": 2},
                            options={"interactive": True},             # 確保圖層可交互
                            ),
                 dataquery_info,
                 ], 
                style={"width": "100%", "height": "500px"}, 
                center=[23.6978, 120.9605],                            # 台灣的中心點
                zoom=7,
                )

geojson_town_data = geopandas_town_test()
geoTown = dl.Map([dl.TileLayer(),                                       # 加載 map 底圖
                  dl.GeoJSON(data=geojson_town_data, id="geojson_town", 
                             style={"color": "blue", "weight": 2, "fillOpacity": 0.2},
                             hoverStyle={"color": "red", "weight": 2},
                             options={"interactive": True},             # 確保圖層可交互
                             ),
                #   dataquery_info,
                  ], 
                 style={"width": "100%", "height": "500px"}, 
                 center=[23.6978, 120.9605],                            # 台灣的中心點
                 zoom=7,
                 )



dataquery_footer = html.Div([
    html.Div([upload_button, 
              submit_button,
              ], className='d-flex'),
    dbc.Spinner(html.Div(id='datastore-status'), size='sm')    
], className='d-flex justify-content-between', style={'backgroundColor': '#f9f9f9'})


dataquery_map = html.Div([html.H1("Taiwan"), geoMap],  style={"fontSize": "20px", "color": "blue"}, id='geo-map')
dataquery_towm = html.Div([html.H1("Town"), geoTown],  style={"fontSize": "20px", "color": "blue"}, id='geo-town')

