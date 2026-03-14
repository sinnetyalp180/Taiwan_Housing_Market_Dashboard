'''
用以顯示 map 與地區基本資料
'''

from dash import Input, Output, State, html, get_asset_url, ctx, no_update, MATCH, dash_table
import dash_leaflet as dl
from dash.exceptions import PreventUpdate           # (阻止更新)

import numpy as np
import pandas as pd
import datetime as dt
import geopandas as gpd
from io import StringIO
import json, copy
import urllib.parse

from dashboard.index import app
import dashboard.utils.functions as dash_func
import dashboard.utils.browser_automation_591 as browser_591




@app.callback(
    Output("county-dropdown", 'options'),
    Output("county-dropdown-2", 'options'),
    Output("county_and_id", 'options'),
    Input('county-data-store', 'data'),
)
def county_select_renew(geojson_data):
    # geojson_file = StringIO(geojson_data)
    # gdf_mapData = gpd.read_file(geojson_file)

    # gdf_mapData = gpd.read_file(json.loads(geojson_data))

    geojson_dict = json.loads(geojson_data)
    gdf_mapData = gpd.GeoDataFrame.from_features(geojson_dict["features"])

    unique_counties = gdf_mapData[['COUNTYID', 'COUNTYNAME', 'COUNTYENG']].drop_duplicates()
    unique_counties_sorted = unique_counties.sort_values(by='COUNTYID', ascending=True)
    # for i, row in unique_counties_sorted.iterrows():
    #     print(row['COUNTYID'], row['COUNTYNAME'], row['COUNTYENG'], '\n')
    options = [{"label": row['COUNTYNAME'], "value": row['COUNTYNAME']} for i, row in unique_counties_sorted.iterrows()]
    county_and_id = {row['COUNTYNAME']:row['COUNTYID'] for i, row in unique_counties_sorted.iterrows()}

    print(county_and_id)
    return options, options, county_and_id
    


@app.callback(
        Output('county-card-title', 'children'),
        Output('town-card-title-1', 'children'),
        Output('county-msg-box', 'children'),
        Output('county-dropdown', 'value'),
        Output('county-name-store', 'data'),
        # Output('geo-county-json', 'data'),

        Input('geo-county-json', 'hoverData'),
        Input('geo-county-json', 'n_clicks'),
        State('geo-county-json', 'clickData'),
)
def display_selected_county(hoverData, n_clicks, clickData):
    ''' (e.g.)
    hoverData['properties'] = {'COUNTYID': 'E', 
                               'COUNTYCODE': '64000', 
                               'COUNTYNAME': '高雄市', 
                               'COUNTYENG': 'Kaohsiung City', 
                               'TYPE': '直轄市', 
                               'TYPE_ENG': 'Special Municipality', 
                               'cluster': False, 
                               'id': 16}             '''
    

    if not ctx.triggered:
        raise PreventUpdate                                                          # 避免不必要的更新
    
    
    triggered_prop = ctx.triggered[0]["prop_id"]                                     # 獲取觸發的 "屬性 + ID"
    # ctx.triggered_id == 'geo-county-json'                           

    # geojson_data = dash_func.display_county_info()

       
    # for feature in geojson_data["features"]:                                         # 預設樣式（全部 reset 為藍色）
    #     feature["properties"]["style"] = {
    #         "color": "blue",
    #         "weight": 2,
    #         "fillOpacity": 0.0,
    #     }


    if (triggered_prop == 'geo-county-json.hoverData') and (hoverData is not None):
        county_name = hoverData['properties']['COUNTYNAME']
        return (f'Taiwan - {county_name}', 
                no_update, 
                dash_func.get_county_info(hoverData), 
                no_update, 
                no_update,
                # geojson_data,
        )
    elif (triggered_prop == 'geo-county-json.n_clicks') and (n_clicks > 0) and (clickData  is not None):
        county_name = clickData['properties']['COUNTYNAME']
        county_id = clickData['properties']['COUNTYID']

        # (將選取的縣市變為紫色)
        # for feature in geojson_data["features"]:
        #     # print(feature["properties"]["COUNTYID"])
        #     if feature["properties"]["COUNTYID"] == county_id:
        #         print(9999999999999999999999999999999)
        #         feature["properties"]["style"] = {
        #             "color": "blue",
        #             "weight": 3,
        #             "fillColor": "purple",
        #             "fillOpacity": 0.4,
        #         }

        return (no_update, 
                county_name, 
                no_update, 
                county_name, 
                {'COUNTYID':county_id, 'COUNTYNAME':county_name}, 
                # geojson_data,
        )
    else:      # (如果沒有點擊，顯示預設標題)
        return ("Taiwan", 
                no_update, 
                dash_func.get_county_info(hoverData), 
                no_update, 
                no_update, 
                # geojson_data,
        )  
    
        


@app.callback(
    Output("geo-town-json", "data"),
    Output("town-map", "center"),
    Output("town-dropdown", "options"),

    Input("county-dropdown", "value"),
    # Input("town-data-store", "data"),
)
def town_map_renew(county):
    gdf_mapData = dash_func.read_town_geographic_info()

    ### <display map> ###
    df_county = gdf_mapData[gdf_mapData['COUNTYNAME'].isin([county, ])]
    geojson_data = df_county.__geo_interface__
    # print(geojson_data)
    """
    Columns: [geometry, TOWNID, TOWNCODE, COUNTYNAME, TOWNNAME, TOWNENG, COUNTYID, COUNTYCODE]
    """
    ### <center: maximum & minimum> ###
    # bounds = df_county.total_bounds                                        # [minx, miny, maxx, maxy]
    # center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]    # [lat, lon]
    ### <center: 將最大區域視為地圖中心> ###
    # df_county['area'] = df_county.geometry.area
    # main_region = df_county.loc[df_county['area'].idxmax()]
    # bounds = main_region.geometry.bounds                                   # (minx, miny, maxx, maxy)
    # center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

    ### <center: 所有地區的加權中心> ###
    '''
    GeoDataFrame 使用的是 EPSG:4326（WGS 84 經緯度座標系統），這個座標系統不適合直接計算面積，因為它的單位是度數（degree），而不是平方公尺（m²）。
    解決方案：先將 GeoDataFrame 轉換成適合的投影座標系統（如 EPSG:3826 或 EPSG:3857）再計算面積。'''
    df_projected = df_county.to_crs(epsg=3826)                                # 轉換到投影座標系統（適合台灣的 TWD97 EPSG:3826）
    df_projected["area"] = df_projected.geometry.area                         # 計算面積（現在是平方公尺）
    df_projected["centroid"] = df_projected.geometry.centroid                 # 計算中心點（仍然是投影座標系統）
    # (計算加權平均中心點)
    weighted_x = (df_projected["centroid"].x * df_projected["area"]).sum() / df_projected["area"].sum()
    weighted_y = (df_projected["centroid"].y * df_projected["area"]).sum() / df_projected["area"].sum()
    # (轉回 WGS 84 (EPSG:4326))
    # weighted_center_geom = gpd.GeoSeries([gpd.points_from_xy([weighted_x], [weighted_y])], crs=3826).to_crs(epsg=4326)
    weighted_center_geom = gpd.GeoSeries(gpd.points_from_xy([weighted_x], [weighted_y]), crs=3826).to_crs(epsg=4326)
    # (取得經緯度中心點)
    center = [weighted_center_geom.y.iloc[0], weighted_center_geom.x.iloc[0]]
    
    ### <options> ###
    unique_counties = df_county[['TOWNID', 'TOWNNAME', 'TOWNENG']].drop_duplicates()
    unique_counties_sorted = unique_counties.sort_values(by='TOWNID', ascending=True)
    options = [{"label": row['TOWNNAME'], "value": row['TOWNNAME']} for i, row in unique_counties_sorted.iterrows()]
    return geojson_data, center, options


@app.callback(
    Output('town-card-title-2', 'children'),
    Output('town-msg-box', 'children'),

    Input('geo-town-json', 'hoverData'),
    Input('geo-town-json', 'n_clicks'),
    State('geo-town-json', 'clickData'),
    # State('county-name-store' , 'data'),
)
def display_selected_town(hoverData, n_clicks, clickData):
    '''
    hoverData['properties'] = {'TOWNID': 'U13', 
                               'TOWNCODE': '10015130', 
                               'COUNTYNAME': '花蓮縣', 
                               'TOWNNAME': '卓溪鄉', 
                               'TOWNENG': 'Zhuoxi Township', 
                               'COUNTYID': 'U', 
                               'COUNTYCODE': '10015', 
                               'cluster': False, 
                               'id': 277}'''
    
    if not ctx.triggered:
        raise PreventUpdate                                             # 避免不必要的更新

    triggered_prop = ctx.triggered[0]["prop_id"]                        # 獲取觸發的 "屬性 + ID"
    
    if (triggered_prop == 'geo-town-json.hoverData') and (hoverData is not None):
        town_name = hoverData['properties']['TOWNNAME']
        # print(town_name)
        return f' - {town_name}', dash_func.get_town_info(hoverData)

    elif (triggered_prop == 'geo-town-json.n_clicks') and (n_clicks > 0) and (clickData  is not None):
        # county_name = hoverData['properties']['TOWNNAME']
        return no_update, no_update
    
    else:
        return "", dash_func.get_town_info(hoverData)                   # 如果沒有點擊，顯示預設標題




@app.callback(
    Output('county-dropdown-2', 'style'),
    Output('county-dropdown-2', 'placeholder'),
    Output('price-slider', 'disabled'),
    Input('check-A1', 'value'),
    Input('check-A2', 'value'),
)
def preference_ckeck(selected_1, selected_2):

    if not ctx.triggered:
        raise PreventUpdate                                         # 避免不必要的更新
    
    style_1 = {
        "pointerEvents": "auto", 
        "opacity": "1.0", 
        "padding": "8px",                                           # 內邊距
        "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",                 # 輕微陰影
        "width": "80%",
        "margin": "10px 10px 0px 60px left",                        # 上右下左 分別為 10 10 0 60 像素
        "marginLeft": "20px",
        "border": "1px solid #ccc",                                 # 灰色邊框
        "borderRadius": "5px",                                      # 邊角圓弧
    }
    
    style_2 = {
        "pointerEvents": "none",                                    # 禁止點擊
        "opacity": "0.5",                                           # 淡化外觀
        "padding": "8px",                                           # 內邊距
        "backgroundColor": "#f0f0f0",                             # 類似 disabled 視覺效果
        "boxShadow": "2px 2px 5px rgba(0,0,0,0.3)",
        "width": "80%",
        "margin": "10px 10px 0px 60px left",                        # 上右下左 分別為 10 10 0 60 像素
        "marginLeft": "20px",
        "border": "1px solid #ccc",                                 # 灰色邊框
        "borderRadius": "5px",                                      # 邊角圓弧
    }
  
    triggered_prop = ctx.triggered[0]["prop_id"]                        # 獲取觸發的 "屬性 + ID"

    if (triggered_prop == 'check-A1.value') and ('A1' in selected_1):
        return style_1, "縣市(必選)", no_update
    elif (triggered_prop == 'check-A1.value') and (selected_1 == []):
        return style_2, "", no_update
    
    elif (triggered_prop == 'check-A2.value') and ('A2' in selected_2):
        return no_update, no_update, False
    
    elif (triggered_prop == 'check-A2.value') and (selected_2 == []):
        return no_update, no_update, True



@app.callback(
    # Output('county-dropdown-2', 'style'),
    Output('table-container', 'children'),
    Output('match-result-title', 'children'),
    Input('pair-btn', 'n_clicks'),
    State('check-A1', 'value'),
    State('check-A2', 'value'),
    State('check-A3', 'value'),
    State('check-A4', 'value'),
    State('check-A5', 'value'),
    State('county-dropdown-2', 'value'),
    State('price-slider', 'value'),
)
def preference_recommendation(n_click, A1, A2, A3, A4, A5, city, price):
    # (模擬使用者偏好)
    user_pref = {
        '縣市': '臺南市',
        '購屋預算': 15000000,
        '偏好權重': {'交易熱區': 3, '成長性': 3, '清幽': 0, '價格適配': 2}
        }
    

    
    user_pref['縣市'] = city if len(A1) != 0 else ''
    if len(A2) != 0: 
        user_pref['購屋預算'] = price

    user_pref['偏好權重']['交易熱區'] = 3 if A3 == ['A3'] else 0
    user_pref['偏好權重']['成長性'] = 3 if A4 == ['A4'] else 0
    user_pref['偏好權重']['清幽']   = 3 if A5 == ['A5'] else 0


    # (使用推薦系統)
    df = pd.read_csv(r'dashboard\utils\ai_model\房市分析彙總表.csv')
    top_recommendations = dash_func.recommend_townships(df, user_pref, use_kmeans=True)
    top_recommendations['適配率'] = top_recommendations['適配率'].map(lambda x: f"{x:.2f}%")
    top_recommendations['更多資訊'] = top_recommendations['鄉鎮市區'].apply(
        # lambda x: f"[查看](https://example.com/detail/{urllib.parse.quote(str(x))})"
        lambda x: f"[查看->591]({browser_591.generate_url(city, x)})"
        )

    result_table = dash_table.DataTable(
        columns=[
            {'name': col, 'id': col, 'presentation': 'markdown'} if col == "更多資訊" else {'name': col, 'id': col} for col in top_recommendations.columns],
        data=top_recommendations.to_dict('records'),
        style_cell={'textAlign': 'center',},
        style_cell_conditional=[
            {
                'if': {'column_id': '更多資訊'},
                'alignItems': 'center',              # 垂直置中
                'textAlign': 'center',               # (保險起見)
                'verticalAlign': 'middle',
                'justifyContent': 'center',          # 水平置中
            }],
        style_table={
            'border': '1px solid black',             # 加整體邊框
            'marginLeft': '0px',                     # 移除左邊距
            'marginRight': 'auto',                   # 可視需要設定對齊方式
            'overflowX': 'auto'
        },
        css=[{                                       # markdown 外觀設定
            'selector': '.dash-spreadsheet td div.cell-markdown p',
            'rule': 'text-align: center; margin: 0;'
        }],
        page_size=5,
    )

    return result_table, f'配對結果 ({city})'


@app.callback(
    Output("geo-match-json", "data"),
    Output("match-map", "center"),

    Input('county-dropdown-2', 'value'),
    # Input('pair-btn', 'n_clicks'),
    # State('county-dropdown-2', 'value'),
)
def match_map_renew(county):

    if county is None:
        return no_update, no_update
    
    gdf_mapData = dash_func.read_town_geographic_info()

    df_county = gdf_mapData[gdf_mapData['COUNTYNAME'].isin([county, ])]
    geojson_data = df_county.__geo_interface__

    """
    Columns: [geometry, TOWNID, TOWNCODE, COUNTYNAME, TOWNNAME, TOWNENG, COUNTYID, COUNTYCODE]
    """
    df_projected = df_county.to_crs(epsg=3826)                                # 轉換到投影座標系統（適合台灣的 TWD97 EPSG:3826）
    df_projected["area"] = df_projected.geometry.area                         # 計算面積（現在是平方公尺）
    df_projected["centroid"] = df_projected.geometry.centroid                 # 計算中心點（仍然是投影座標系統）

    # (計算加權平均中心點)
    area_sum = df_projected["area"].sum()
    if area_sum == 0:
        center = [23.6978, 120.9605]
    else:
        weighted_x = (df_projected["centroid"].x * df_projected["area"]).sum() / df_projected["area"].sum()
        weighted_y = (df_projected["centroid"].y * df_projected["area"]).sum() / df_projected["area"].sum()

        # (轉回 WGS 84 (EPSG:4326))
        # weighted_center_geom = gpd.GeoSeries([gpd.points_from_xy([weighted_x], [weighted_y])], crs=3826).to_crs(epsg=4326)
        weighted_center_geom = gpd.GeoSeries(gpd.points_from_xy([weighted_x], [weighted_y]), crs=3826).to_crs(epsg=4326)

        # (取得經緯度中心點)
        center = [weighted_center_geom.y.iloc[0], weighted_center_geom.x.iloc[0]]

    return geojson_data, center


@app.callback(
    Output('match-msg-box', 'children'),

    Input('geo-match-json', 'hoverData'),
    Input('geo-match-json', 'n_clicks'),
    State('geo-match-json', 'clickData'),
    # State('county-name-store' , 'data'),
)
def display_matchMap_town(hoverData, n_clicks, clickData):
    '''
    hoverData['properties'] = {'TOWNID': 'U13', 
                               'TOWNCODE': '10015130', 
                               'COUNTYNAME': '花蓮縣', 
                               'TOWNNAME': '卓溪鄉', 
                               'TOWNENG': 'Zhuoxi Township', 
                               'COUNTYID': 'U', 
                               'COUNTYCODE': '10015', 
                               'cluster': False, 
                               'id': 277}'''
    
    if not ctx.triggered:
        raise PreventUpdate                                             # 避免不必要的更新

    triggered_prop = ctx.triggered[0]["prop_id"]                        # 獲取觸發的 "屬性 + ID"
    
    if (triggered_prop == 'geo-town-json.hoverData') and (hoverData is not None):
        town_name = hoverData['properties']['TOWNNAME']
        # print(town_name)
        return dash_func.get_town_info(hoverData)

    elif (triggered_prop == 'geo-town-json.n_clicks') and (n_clicks > 0) and (clickData  is not None):
        # county_name = hoverData['properties']['TOWNNAME']
        return no_update
    
    else:
        return dash_func.get_town_info(hoverData)


