'''
以下 functions 主要用於資料擷取、過濾、計算等，包含地理資料與其他相關的數據處理
'''

from dash import html, dcc, get_asset_url
import geopandas as gpd
import dash_leaflet as dl
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

from datetime import datetime
import numpy as np
import pandas as pd
import datetime as dt
import sys, os, requests, json
import plotly.graph_objs as go


# custom_path = r"C:\Users\user\Desktop\Taiwan_House_Price_Dash\Taiwan_House_Price_Dash_v1"
custom_path = r"C:\Users\user\Desktop\Taiwan_House_Price_Dash\Taiwan_House_Price_Dash_v2"
if os.path.exists(custom_path) and custom_path not in sys.path:
    sys.path.append(custom_path)


from dashboard.index import app
import dashboard.utils.constants as constants
# from dashboard.utils.constants import TN_TANKS, TC_JUNO_TANKS, CONNECTIONSTRING_TC_PPDA, CONNECTIONSTRING_TN_PPDA, PI_SUMMARYTYPE


#%% (geography) ##########################################
##########################################################

def read_county_geographic_info(file_path=None):
    if file_path is None:
        gdf_county = gpd.read_file(r"dashboard\assets\data\Taiwan_Administrative_Region\County\COUNTY_MOI_1130718.shp")
    else:
        gdf_county = gpd.read_file(file_path)
    gdf_county = gdf_county.to_crs(epsg=4326)                    # 設定座標系統。4326 支援寫入 GeoJSON 格式
    # print(gdf_county.head())                                   # Display data 顯示前5筆 (GeoDataFrame)
    # print(gdf_county.crs)                                      # 檢查座標系統是否為 WGS 84 (EPSG:4326)
    '''
    <坐標系統及 WebGIS 常用的坐標轉換>
    https://ithelp.ithome.com.tw/articles/10194371
    '''
    ### (plot data)
    # Sample_data = gdf_county.loc[:, ['COUNTYNAME', 'geometry']]
    # Sample_data.plot()
    return gdf_county


def get_single_county_geojson(county_name="臺南市", file_path=None):
    gdf_county = read_county_geographic_info(file_path)
    
    # (篩選指定縣市)
    single_county_gdf = gdf_county[gdf_county["COUNTYNAME"] == county_name]
    
    if single_county_gdf.empty:
        raise ValueError(f"找不到名稱為「{county_name}」的縣市。")
    
    # (轉成 GeoJSON 格式)
    geojson_data = single_county_gdf.__geo_interface__

    # for feature in geojson_data["features"]:
    #     feature.setdefault("properties", {}).setdefault("style", {
    #         "color": "#ff00ff",
    #         "weight": 2,
    #         "fillOpacity": 0.0
    #     })
    return geojson_data


def display_county_info(file_path=None):
    gdf_county = read_county_geographic_info(file_path)
    geojson_data = gdf_county.__geo_interface__                                # GeoJSON 格式，適用於 Dash Leaflet，地圖可視化


    # (預設每個縣市都是藍色 (未選取))
    # for feature in geojson_data["features"]:
    #     feature.setdefault("properties", {}).setdefault("style", {
    #         "color": "blue",
    #         "weight": 2,
    #         "fillOpacity": 0.0
    #     })

    return geojson_data


def get_taiwan_border(file_path=None):
    gdf_county = read_county_geographic_info(file_path)
    geojson_data = gdf_county.__geo_interface__                                # GeoJSON 格式，適用於 Dash Leaflet

    ### 取得台灣整體邊界 (合併所有縣市)
    merged_geometry = gdf_county.geometry.union_all()                          # 合併所有縣市為一個多邊形

    ### 確保 merged_geometry 是 MultiPolygon 或 Polygon
    if isinstance(merged_geometry, MultiPolygon):
        largest_polygon = max(merged_geometry.geoms, key=lambda p: p.area)     # 取最大一塊（台灣本島）
    elif isinstance(merged_geometry, Polygon):
        largest_polygon = merged_geometry
    else:
        raise ValueError("無法解析台灣邊界，請檢查 GeoDataFrame 的 geometry 格式")

    ### 確保邊界方向為逆時針
    taiwan_hole = orient(largest_polygon, sign=1.0)

    ### 提取邊界座標 (轉換為 [[經度, 緯度], ...] 格式)
    taiwan_border = [[lon, lat] for lon, lat in taiwan_hole.exterior.coords]

    return taiwan_border


def get_world_geojson(file_path=None):
    # world_geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    if file_path is None:
        file_path = r"dashboard\assets\data\countries.geo.json"

    if file_path.startswith("http"):                       # 如果是網路 URL
        return requests.get(file_path).json()
    else:                                                  # 如果是本地檔案
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)


def read_town_geographic_info(file_path=None):
    if file_path is None:
        gdf_town = gpd.read_file(r"dashboard\assets\data\Taiwan_Administrative_Region\Town\TOWN_MOI_1131028.shp")
    else:
        gdf_town = gpd.read_file(file_path)
    gdf_town = gdf_town.to_crs(epsg=4326)                    # 設定座標系統。4326 支援寫入 GeoJSON 格式
    return gdf_town
    # geojson_town_data = Town_data.__geo_interface__


def display_town_info(city:str = None, df_geo=None):
    if city is None:
        return None
    if df_geo is None:
        gdf_town = read_town_geographic_info()
    else:
        gdf_town = df_geo
    df_city = gdf_town[gdf_town['COUNTYNAME'].isin([city, ])]
    # df_city = gdf_town[(gdf_town['COUNTYNAME']=='臺北市') | (gdf_town['COUNTYNAME']=='新北市')]
    geojson_data = df_city.__geo_interface__
    return geojson_data


def get_county_info(hoverData=None):
    header = [html.H6("County Information", style={"fontWeight": "bold"})]
    if not hoverData:
        # print('hoverData:', hoverData)
        return header + [html.P("Hover state.")]
    
    info_list = [f"County_ID: {hoverData['properties']['COUNTYID']}", html.Br(), 
                 f"County_Code: {hoverData['properties']['COUNTYCODE']}", html.Br(),
                 f"County_Name: {hoverData['properties']['COUNTYNAME']}", html.Br(),
                 f"County_ENG: {hoverData['properties']['COUNTYENG']}", html.Br(),
                 f"Type: {hoverData['properties']['TYPE']} ({hoverData['properties']['TYPE_ENG']})", html.Br(), 
                 f"ID: {hoverData['properties']['id']}"]
    # print('info_str:', info_str)
    return header + info_list
            # ["{:.3f} people / mi".format(feature['properties']["density"]), html.Sup("2")]


def get_town_info(hoverData=None):
    header = [html.H6("Town Information", style={"fontWeight": "bold"})]
    if not hoverData:
        # print('hoverData:', hoverData)
        return header + [html.P("Hover state.")]
    
    info_list = [f"Town_ID: {hoverData['properties']['TOWNID']}", html.Br(), 
                 f"Town_Code: {hoverData['properties']['TOWNCODE']}", html.Br(),
                 f"County_Name: {hoverData['properties']['COUNTYNAME']}", html.Br(),
                 f"Town_Name: {hoverData['properties']['TOWNNAME']}", html.Br(),
                 f"Town_ENG: {hoverData['properties']['TOWNENG']}", html.Br(),
                 f"County_ID: {hoverData['properties']['COUNTYID']}", html.Br(),
                 f"County_Code: {hoverData['properties']['COUNTYCODE']}", html.Br(),
                 f"id: {hoverData['properties']['id']}"]
    # print('info_str:', info_str)
    # print('=============================')
    # print(hoverData['properties'])
    # print('=============================')
    return header + info_list


#%% (callbacks data: plot fig) ###########################
##########################################################


def plot_average_unit_price(county, df, year_range=[2010, datetime.now().year]):
    # (確保欄位為數值型態，若無法轉換則為 NaN)
    df["西元年"] = pd.to_numeric(df["西元年"], errors="coerce")
    df["單價元坪"] = pd.to_numeric(df["單價元坪"], errors="coerce")
    df = df.dropna(subset=["西元年", "單價元坪"])                                        # 移除有缺失值的列
    df = df[df["西元年"].between(year_range[0], year_range[1])]                         # 篩選有效年份

    town_avg = df.groupby(["鄉鎮市區", "西元年"])["單價元坪"].mean().reset_index()

    overall_avg = df.groupby("西元年")["單價元坪"].mean().reset_index()
    overall_avg["鄉鎮市區"] = "全區平均"                                                # 統一格式

    # (合併兩者)
    plot_df = pd.concat([town_avg, overall_avg], ignore_index=True)

    # (建立折線圖)
    fig = go.Figure()
    for town in plot_df["鄉鎮市區"].unique():
        df_town = plot_df[plot_df["鄉鎮市區"] == town]
        
        if town == "全區平均":                                                         # 特別處理「全區平均」的樣式
            fig.add_trace(go.Scatter(
                x=df_town["西元年"],
                y=df_town["單價元坪"] / 1000,                                          # 換成千元單位
                mode="lines+markers+text",
                name=town,
                line=dict(color="black", width=4, dash="dash"),                       # 粗黑虛線
                marker=dict(symbol="diamond", size=10, color="black"),
                text=[f"{v/1000:.1f}K" for v in df_town["單價元坪"]],
                textposition="top center",                                            # 或 middle right、top right、bottom center
                textfont=dict(color="blue", size=8, family="Arial"),                  # Arial Black  
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df_town["西元年"],
                y=df_town["單價元坪"] / 1000,
                mode="lines+markers",
                name=town,
                line=dict(width=2),
                marker=dict(size=6),
                visible='legendonly',
            ))

    fig.update_layout(
        title=f"{county} 各鄉鎮市區每年平均房價（每坪）",
        xaxis=dict(
            title="西元年",
            tickmode="array",
            tickvals=list(range(year_range[0], year_range[1] + 1, 2)),
        ),
        yaxis=dict(
            title="平均單價（千元 / 坪）",
            tickformat=",",
            range=[0, (df_town["單價元坪"] / 1000).max()*1.2],
        ),
        template="plotly_white",
        # height=600,                                       # 整張圖固定高度
        
        margin=dict(t=120, b=120, l=80, r=40),              # 固定邊界避免 legend 擠壓主圖，可以依情況調整
        legend=dict(
            title="鄉鎮市區",                                # 小視窗叫 legend 或圖例
            orientation="h",                                # 水平橫向排列 legend
            yanchor="top",                                  # 以上邊為對齊點
            y=-0.45,                                        # 負值表示往圖表下方移動
            xanchor="center",                               # 以中間為對齊點
            x=0.5,                                          # 水平置中
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
        ),
        hovermode="x unified",
    )
    return fig


def plot_town_volume_bar(county, df, selected_year=2022):
    # (確保年份、成交量可轉為數字)
    df["西元年"] = pd.to_numeric(df["西元年"], errors="coerce")

    # (過濾條件)
    df = df.dropna(subset=["西元年", "鄉鎮市區"])
    # df = df[df["西元年"].between(year_range[0], year_range[1])]
    df = df[df["西元年"] == selected_year]

    # (計算各鄉鎮市區的總成交量)
    volume_df = df.groupby("鄉鎮市區").size().reset_index(name="成交量")

    # (依成交量排序 (從高到低))
    volume_df = volume_df.sort_values(by="成交量", ascending=False)

    # (繪製直方圖)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=volume_df["鄉鎮市區"],
        y=volume_df["成交量"],
        text=volume_df["成交量"],
        textposition="auto",
        marker_color="steelblue",                    # marker_color="tomato",
    ))
    fig.update_layout(
        title=f"{county} 各鄉鎮市區總成交量（{selected_year} 年）",
        xaxis_title="鄉鎮市區",
        yaxis_title="成交量（筆數）",
        xaxis_tickangle=-45,
        template="plotly_white"
    )

    return fig


def plot_price_distribution(county, df, selected_year=2022):
    price_bins = [0, 500, 1000, 1500, 2000, 3000, 5000, 10000, float('inf')]
    price_labels = ["0-500", "500-1K", "1K-1.5K", "1.5K-2K", "2K-3K", "3K-5K", "5K-10K", "10K+"]

    # (確保數值格式正確)
    df["西元年"] = pd.to_numeric(df["西元年"], errors="coerce")
    df["總價元"] = pd.to_numeric(df["總價元"], errors="coerce")

    # (篩選指定年份並過濾資料)
    df_year = df[df["西元年"] == selected_year].dropna(subset=["總價元"])
    df_year["價格區間"] = pd.cut(df_year["總價元"] / 10000, bins=price_bins, labels=price_labels, right=False)

    # (成交量、比例、累計比例)
    counts = df_year["價格區間"].value_counts().reindex(price_labels, fill_value=0)
    total = counts.sum()
    proportions = (counts / total * 100).round(1)
    cumulative = proportions.cumsum()


    fig = go.Figure()

    # (成交量長條圖)
    fig.add_bar(
        x=price_labels,
        y=counts,
        name="成交量",
        yaxis="y1",
    )
    # (累積比例折線圖)
    fig.add_trace(go.Scatter(
        x=price_labels,
        y=cumulative,
        mode="lines+markers+text",
        name="累積比例 (%)",
        yaxis="y2",
        line=dict(color="green", dash="dash"),
        text=[f"{p:.1f}%" for p in cumulative],    # 顯示到小數點一位
        textposition="top center",                            # 標籤位置：點上方中央
        textfont=dict(
            color='#1A3816',                                  # 文字顏色
            size=14,                                          # 文字大小
            family='Arial Black',                             # 可以用不同字型（達成粗體效果）
    )))
    # (比例折線圖)
    fig.add_trace(go.Scatter(
        x=price_labels,
        y=proportions,
        mode="lines+markers+text",
        name="比例 (%)",
        yaxis="y2",
        line=dict(color="red"),
        text=[f"{p:.1f}%" for p in proportions],              # 顯示到小數點一位
        textposition="top center",                            # 標籤位置：點上方中央
        textfont=dict(
            # color='green',                                  # 文字顏色
            size=14,                                          # 文字大小
            family='Arial Black',                             # 可以用不同字型（達成粗體效果）
    )))
    fig.update_layout(
        title=f"{selected_year} 年房屋價格分布（{county}）",
        xaxis_title="價格區間（萬元）",
        yaxis=dict(
            title="成交量",
            side="left",
            range=[0, 30000],
        ),
        yaxis2=dict(
            title="比例 (%)",
            overlaying="y",
            side="right",
            range=[0, 115],
        ),
        template="plotly_white",
        legend=dict(
            # title="圖例說明",                       # 小視窗叫 legend 或圖例
            x=0.70,                                  # 調整水平位置（0=最左, 1=最右）
            y=0.75,                                  # 調整垂直位置（0=最下, 1=最上）
            bgcolor="rgba(255,255,255,0.3)",         # 半透明背景避免擋住
            bordercolor="gray",
            borderwidth=1,
        )
    )
    return fig


def plot_yearly_growth(county, df, year_range=[2010, datetime.now().year]):
    df["西元年"] = pd.to_numeric(df["西元年"], errors="coerce")
    df["單價元坪"] = pd.to_numeric(df["單價元坪"], errors="coerce")
    df = df.dropna(subset=["西元年", "單價元坪"])
    df = df[df["西元年"].between(year_range[0], year_range[1])]                         # 篩選有效年份

    # (--- 各區成長率 ---)
    town_avg = df.groupby(["鄉鎮市區", "西元年"])["單價元坪"].mean().reset_index()

    growth_list = []
    for town in town_avg["鄉鎮市區"].unique():
        town_df = town_avg[town_avg["鄉鎮市區"] == town].sort_values("西元年")
        town_df["年成長率"] = town_df["單價元坪"].pct_change() * 100
        growth_list.append(town_df)
    growth_df = pd.concat(growth_list).dropna(subset=["年成長率"])

    # (--- 全區平均成長率 ---)
    overall_avg = df.groupby("西元年")["單價元坪"].mean().reset_index()
    overall_avg = overall_avg.sort_values("西元年")
    overall_avg["年成長率"] = overall_avg["單價元坪"].pct_change() * 100
    overall_avg["鄉鎮市區"] = "全區平均"
    overall_avg = overall_avg.dropna(subset=["年成長率"])

    # (合併所有成長資料)
    full_df = pd.concat([growth_df, overall_avg], ignore_index=True)

    # (--- 繪圖 ---)
    fig = go.Figure()
    for town in full_df["鄉鎮市區"].unique():
        df_town = full_df[full_df["鄉鎮市區"] == town]

        if town == "全區平均":
            fig.add_trace(go.Scatter(
                x=df_town["西元年"],
                y=df_town["年成長率"],
                mode="lines+markers+text",
                name="全區平均",
                text=[f"{v:.1f}%" for v in df_town["年成長率"]],
                textposition="top center",
                line=dict(color="black", width=4, dash="dash"),
                marker=dict(symbol="diamond", size=10, color="black"),
                textfont=dict(color="black", size=12, family="Arial"),
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df_town["西元年"],
                y=df_town["年成長率"],
                mode="lines+markers",
                name=town,
                line=dict(width=2),
                marker=dict(size=6),
                visible='legendonly',                     # 預設隱藏其他區域，可搭配 legend filter
            ))

    fig.update_layout(
        title=f"{county} 各鄉鎮市區每坪單價年成長率 (%)",

        xaxis=dict(
            title="西元年",
            tickmode="array",
            tickvals=list(range(year_range[0], year_range[1] + 1, 2)),
        ),
        yaxis=dict(
            title="年成長率 (%)",
            tickformat=".1f",
            range=[-20, 20]
        ),
        template="plotly_white",
        height=450,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.4,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
        ),
        margin=dict(t=80, b=120, l=80, r=40),
    )

    return fig




def recommend_townships(df, user_pref:dict, use_kmeans:bool=False, n_clusters:int=3, top_k:int=5):
    """
    給定區域資料與使用者偏好，回傳推薦區域列表

    參數:
        df: 包含必要欄位的 DataFrame（縣市、鄉鎮市區、前一年平均成交價、交易量、過去三年平均成長率）
        user_pref: dict，包含必要條件與偏好設定
        use_kmeans: 是否加入無監督學習分群（標記用）
        n_clusters: 分群數（僅用於 kmeans）
        top_k: 回傳推薦的前幾名

    回傳:
        排序後推薦結果（含配對百分比與可選群組標籤）
    """

    col_list = ['交易量', '前一年平均房價_坪', '前一年平均成交價', '過去三年平均成長率']

    # === 1. 必要條件過濾 ===
    df_filtered = df[(df['縣市'] == user_pref['縣市'])].copy()
    
    if df_filtered.empty:
        return pd.DataFrame(columns=['鄉鎮市區', '適配率'])
    

    # === 2. 偏好指標正規化 ===
    scaler = MinMaxScaler()
    df_filtered[col_list] = scaler.fit_transform(df_filtered[col_list])
    df_filtered['清幽指標'] = 1 - df_filtered['交易量']                            # 交易量越低越清幽

    df_filtered['價格適配度'] = 1 - abs(df_filtered['前一年平均成交價'] - user_pref['購屋預算']) / user_pref['購屋預算']
    df_filtered['價格適配度'] = df_filtered['價格適配度'].clip(lower=0)            # 不讓它變負



    # === 3. 加權總分 ===
    w = user_pref['偏好權重']
    df_filtered['總分'] = (
        df_filtered['交易量'] * w['交易熱區'] +
        df_filtered['過去三年平均成長率'] * w['成長性'] +
        df_filtered['清幽指標'] * w['清幽']+
        df_filtered['價格適配度'] * w['價格適配']
    ) / sum(w.values())

    # === 4. 百分比分數 ===
    df_filtered['適配率'] = scaler.fit_transform(df_filtered[['總分']]) * 100


    # === 5. 可選：KMeans 分群標籤 ===
    if use_kmeans:
        features = df_filtered[col_list + ['清幽指標']]
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df_filtered['群組'] = kmeans.fit_predict(features)

    # === 6. 排序取前 K ===
    result_cols = ['鄉鎮市區', '適配率']
    if use_kmeans:
        result_cols.append('群組')

    return df_filtered.sort_values(by='適配率', ascending=False).head(top_k)[result_cols]




if __name__ == "__main__":
    file_path = r'C:\Users\user\Desktop\Taiwan_House_Price_Dash\Taiwan_House_Price_Dash_v1\dashboard\assets\data\Taiwan_Administrative_Region\County\COUNTY_MOI_1130718.shp'
    county_geographic_info = read_county_geographic_info(file_path)

    tb = get_taiwan_border(file_path)

    # print(county_geographic_info['geometry'])
    print(len(tb))

