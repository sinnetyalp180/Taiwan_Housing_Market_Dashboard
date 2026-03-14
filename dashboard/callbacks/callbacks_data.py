'''
用以顯示各種數據以方便分析:

1. 單價元坪
2. 年成長率 (%)
3. 區域熱度指標（交易量）: 統計每年每區的成交筆數（count），觀察熱度變化：
4. 房價指數（Base Year = 100）: 選定基準年，將各年平均單價轉為「房價指數」，更方便比較相對變動：
5. 區域排名: 每年依據平均單價排序，並標示每區名次變化，觀察哪些區域崛起或下滑。
6. CAGR（年均成長率）: 若關注長期表現，可針對每區計算複合年成長率（Compound Annual Growth Rate）
7. 區域集中度分析: 計算平均單價前 3 高的區域佔全體的比例，了解市場是否集中在少數高價區域。
8. 價格分佈分析（箱型圖、直方圖）: 比較每年每區價格的分布，辨識是否有極端值、是否趨於集中。
9. 價格波動指標（變異性）: 計算每年每區的標準差或變異係數（CV），了解哪個區域波動較大

'''

from dash import Input, Output, State, html, get_asset_url, ctx, no_update, MATCH
from dash.exceptions import PreventUpdate           # (阻止更新)
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from collections import defaultdict
from datetime import datetime


from dashboard.index import app
import dashboard.utils.constants as constants
import dashboard.utils.functions as funcs


# (固定各區的顏色對應)
region_colors = {
    "臺北市": "#636EFA",  # 藍
    "新北市": "#EF553B",  # 橘紅
    "桃園市": "#00CC96",  # 綠
    "臺中市": "#AB63FA",  # 紫
    "臺南市": "#FFA15A",  # 橘
    "高雄市": "#19D3F3",  # 青藍
    "基隆市": "#FF6692",  # 粉紅
    "新竹市": "#B6E880",  # 青綠
    "嘉義市": "#FF97FF",  # 粉紫
    "新竹縣": "#FECB52",  # 黃
    "嘉義縣": "#A1CAF1",  # 淡藍
    "苗栗縣": "#FFB6B6",  # 粉
    "彰化縣": "#B0E0E6",  # 淺藍
    "南投縣": "#D3FFCE",  # 淺綠
    "雲林縣": "#FFD700",  # 金黃
    "屏東縣": "#ADD8E6",  # 天藍
    "宜蘭縣": "#C1FFC1",  # 淺草綠
    "花蓮縣": "#F0E68C",  # 卡其
    "臺東縣": "#E6E6FA",  # 淡紫
    "澎湖縣": "#FFE4E1",  # 淡粉
    "金門縣": "#8DD3C7",  # 青綠
    "連江縣": "#BC80BD",  # 淺紫
}

price_bins = [0, 500, 1000, 1500, 2000, 3000, 5000, 10000, float('inf')]
price_labels = ["0-500", "500-1K", "1K-1.5K", "1.5K-2K", "2K-3K", "3K-5K", "5K-10K", "10K+"]

def get_overall_data():
    # (儲存各年份的總加權金額 (mean * count) 與總筆數)
    year_total = defaultdict(float)
    year_count = defaultdict(int)

    # (儲存各區域資料 (供圖表使用))
    region_avg = defaultdict(lambda: defaultdict(float))          # 各區年平均單價
    region_growth = {}                                            # 各區成長率
    summary_list = []                                             # 成交價格分布

    df_dict = constants.df_dict

    for name, df in df_dict.items():
        if df.empty:
            continue                                                              # 跳過空資料

        df = df.copy()
        # 確保欄位為數值型態，若無法轉換則為 NaN
        df["西元年"] = pd.to_numeric(df["西元年"], errors="coerce")
        df["單價元坪"] = pd.to_numeric(df["單價元坪"], errors="coerce")
        df = df.dropna(subset=["西元年", "單價元坪"])                              # 移除有缺失值的列
        df = df[df["西元年"].between(2000, datetime.now().year)]                  # 篩選有效年份

        # 依年份分組，取得平均單價與資料筆數
        grouped = df.groupby("西元年")["單價元坪"].agg(["mean", "count"])

        # 加總每個年份的加權價格與筆數
        for year, row in grouped.iterrows():
            year_total[year] += row["mean"] * row["count"]
            year_count[year] += row["count"]
            region_avg[name][year] = row["mean"]                                 # 儲存各區域每年平均單價

        # 成交價格區間
        # bins = [0, 500, 1000, 2000, 5000, 10000, float('inf')]
        # labels = ["0-500", "500-1000", "1000-2000", "2000-5000", "5000-10000", "10000+"]
        temp_df = df.copy()
        temp_df['區域'] = name
        temp_df = temp_df[temp_df['總價元'].notna()]                             # 確保總價元有值
        temp_df['價格區間'] = pd.cut(temp_df['總價元'] / 10000, bins=price_bins, labels=price_labels, right=False)
        yearly_counts = temp_df.groupby(['西元年', '價格區間'], observed=False).size().reset_index(name='成交量')
        yearly_counts['區域'] = name
        summary_list.append(yearly_counts)

    ###################################################################
    # 建立加權平均單價的資料表
    overall_df = pd.DataFrame({
        "西元年": list(year_total.keys()),
        "平均單價 (坪)": [year_total[y] / year_count[y] for y in year_total]
    }).sort_values("西元年")
    overall_df["年成長率 (%)"] = overall_df["平均單價 (坪)"].pct_change() * 100

    ### 各區成長率 ###
    for region, data in region_avg.items():
        temp_df = pd.DataFrame({"西元年": list(data.keys()), "平均單價 (坪)": list(data.values())})
        temp_df = temp_df.sort_values("西元年")
        temp_df["年成長率 (%)"] = temp_df["平均單價 (坪)"].pct_change() * 100
        temp_df["成交量"] = temp_df["西元年"].map(lambda y: df_dict[region][df_dict[region]["西元年"] == y].shape[0])
        region_growth[region] = temp_df

    ### 各區成交價格分布 ###
    df_summary = pd.concat(summary_list, ignore_index=True)
    
    # (save)
    overall_df.to_csv(r'temp\overall_data.csv')
    for region, df in region_growth.items():
        df.to_csv(fr'temp\region_{region}_data.csv')

    # Note: region_growth 為處理後的數據，包含各區域的平均、成長率等
    return overall_df, region_growth, df_summary




overall_df, region_growth, df_summary = get_overall_data()

@app.callback(
    Output('county_and_id', 'data'),
    Output('line-chart-2', 'figure'), 
    # Output(''),
    # Input(),
    Input('county_and_id', 'data'),
    Input('year-slider-p2', 'value'),
)
def dsiplay_average(data, year_range):
    region_data = region_growth.copy()
    # print(region_data)
    
    id_and_county = constants.id_and_county

    # (建立一個折線圖的圖層)
    fig = go.Figure()

    # (加入每個區域的平均價格折線)
    visible_region = ['臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市']
    for region, df in region_data.items():
        df = df[df["西元年"].between(2000, datetime.now().year)]
        # df = df[df["西元年"].between(year_range[0], year_range[1])]     # 根據使用者選擇的範圍過濾資料

        county_name = id_and_county[region.upper()]
        fig.add_trace(go.Scatter(
            x=df["西元年"],
            y=df["平均單價 (坪)"],
            mode="lines+markers",
            name=f"{county_name}",
            line=dict(width=2),
            opacity=0.5,
            visible=True if county_name in visible_region else "legendonly",
        ))

    yearly_counts = df_summary.groupby(['西元年'], observed=True)['成交量'].sum().reset_index()
    # print(yearly_counts)

    # (全國的平均價格折線)
    fig.add_trace(go.Scatter(
        x=overall_df["西元年"],
        y=overall_df["平均單價 (坪)"],
        mode="lines+markers",
        name="全國平均單價",
        line=dict(width=6, dash='dash', color='black')
    ))
    
    # (年成交量圖)
    fig.add_trace(go.Scatter(
        x=yearly_counts['西元年'],
        y=yearly_counts['成交量'],
        mode='lines+markers+text',
        line=dict(width=6, dash='dash', color='blue'),
        # text=[f"{v:,}" for v in yearly_counts['成交量']],  # 用逗號格式
        # text=[f"{v/1000:.1f}K" for v in yearly_counts['成交量']],
        text=[f"{v/1000:.0f}K" for v in yearly_counts['成交量']],
        textposition='top center',
        name='每年成交量',
        yaxis="y2",
    ))

    # (圖表美化設定)
    fig.update_layout(
        title="縣市年度平均單價",
        xaxis_title="西元年",
        # yaxis_title="平均單價(元/坪)",
        yaxis=dict(
            title="平均單價(元/坪)",
            side="left",
            # range=[0, 200000],
        ),
        yaxis2=dict(
            title='年度方屋交易量',
            overlaying="y",
            side="right",
            range=[0, 600000],
        ),
        template="plotly_white",
        legend=dict(
            # title="圖例說明",            # 小視窗叫 legend 或圖例
            orientation="h",              # 水平橫向排列 legend
            yanchor="bottom",             # 以下邊為對齊點
            y=-1.1,                       # 負值表示往圖表下方移動
            xanchor="center",             # 以中間為對齊點
            x=0.5,                        # 水平置中
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(range=[year_range[0], year_range[1]])
    return data, fig



@app.callback(
    # Output('county_and_id', 'data'),
    Output('line-chart-3', 'figure'), 
    # Output(''),
    # Input(),
    Input('county_and_id', 'data'),
    Input('year-slider-p3', 'value'),
)
def dsiplay_growth_rate(data, year_range):
# def update_figure(year_range):
    region_data = region_growth.copy()

    id_and_county = constants.id_and_county

    # (建立一個折線圖的圖層)
    fig = go.Figure()

    # (加入每個區域的平均價格折線)
    visible_region = ['臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市']
    for region, df in region_data.items():
        # df = df[df["西元年"].between(2000, datetime.now().year)]
        df = df[df["西元年"].between(year_range[0], year_range[1])]     # 根據使用者選擇的範圍過濾資料

        county_name = id_and_county[region.upper()]
        fig.add_trace(go.Scatter(
            x=df["西元年"],
            y=df["年成長率 (%)"],
            mode="lines+markers",
            name=f"{county_name}",
            line=dict(width=2),
            opacity=0.6,
            visible=True if county_name in visible_region else "legendonly",
        ))

    fig.add_trace(go.Scatter(
        x=overall_df["西元年"],
        y=overall_df["年成長率 (%)"],
        mode="lines+markers",
        name="年成長率",
        line=dict(width=3, color="black"),
        opacity=0.6,
    ))
    # (圖表美化設定)
    fig.update_layout(
        title="全國年成長率",
        xaxis_title="年份",
        yaxis_title="成長率 (%)",
        template="plotly_white",      # 使用白色主題樣式
        hovermode="x unified",
    )
    fig.update_xaxes(range=[year_range[0], year_range[1]])
    fig.update_yaxes(range=[-50, 50])
    return fig



@app.callback(
    Output("volume-pie", "figure"),
    # Input("year-dropdown", "value")
    Input("year-slider-single-t1", "value")
)
def update_pie_chart(selected_year):
    id_and_county = constants.id_and_county

    pie_data = {id_and_county[region.upper()]: df[df["西元年"] == selected_year]["成交量"].values[0]
                for region, df in region_growth.items()
                if selected_year in df["西元年"].values and not df[df["西元年"] == selected_year].empty}
    
    # 確保 pie_data 中的每個 region 都有顏色，否則 fallback 用 gray
    colors = [region_colors.get(region, "#CCCCCC") for region in pie_data.keys()]

    fig = go.Figure(data=[go.Pie(
        labels=list(pie_data.keys()),
        values=list(pie_data.values()),
        hole=0.3,
        marker=dict(colors=colors),
    )])
    fig.update_layout(title=f"{selected_year} 縣市成交量比例")
    return fig



@app.callback(
    Output("box-plot", "figure"), 
    Input("year-slider-single-t4", "value"),
)
def update_distribution(selected_year):
    # bins = [0, 500, 1000, 2000, 5000, 10000, float('inf')]
    # labels = ["0-500", "500-1K", "1K-1.5K", "2K-3K", "3K-5K", "5K-10K", "10K+"]

    filtered_df = df_summary[df_summary["西元年"] == selected_year]
    total_count = filtered_df['成交量'].sum()

    counts = filtered_df.groupby(['價格區間'], observed=True)['成交量'].sum().reindex(price_labels, fill_value=0)
    if total_count > 0:
        proportions = counts / total_count * 100 
    else:
        proportions = counts * 0
    
    cumulative_proportion = proportions.cumsum()

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
        y=cumulative_proportion,
        mode="lines+markers+text",
        name="累積比例 (%)",
        yaxis="y2",
        line=dict(color="green", dash="dash"),
        text=[f"{p:.1f}%" for p in cumulative_proportion],    # 顯示到小數點一位
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
        title=f"{selected_year} 年房屋價格分布（所有縣市）",
        xaxis_title="價格區間（萬元）",
        yaxis=dict(
            title="成交量",
            side="left",
            range=[0, 200000],
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




@app.callback(
    Output("line-chart-1c", "figure"),
    Output("line-chart-2c", "figure"),
    Output("line-chart-3c", "figure"),
    Output("line-chart-4c", "figure"),
    Input("county-dropdown", "value"),

    Input("year-slider-1c", "value"),
    Input("year-slider-single-2c", "value"),
    Input("year-slider-single-3c", "value"),
    Input("year-slider-4c", "value"),
)
def town_data(county, year_range_1, selected_year_2, selected_year_3, year_range_4):

    if not ctx.triggered:
        raise PreventUpdate                                             # 避免不必要的更新

    county_and_id = constants.county_and_id
    county_id = county_and_id[county].lower()
    df_county = constants.df_dict[county_id]

    triggered_prop = ctx.triggered[0]["prop_id"]                        # 獲取觸發的 "屬性 + ID"
    

    if triggered_prop == 'year-slider-1c.value':
        fig_1 = funcs.plot_average_unit_price(county, df_county, year_range_1)
        return fig_1, no_update, no_update, no_update
    elif triggered_prop == 'year-slider-single-2c.value':
        fig_2 = funcs.plot_town_volume_bar(county, df_county, selected_year_2)
        return no_update, fig_2, no_update, no_update
    elif triggered_prop == 'year-slider-single-3c.value':
        fig_3 = funcs.plot_price_distribution(county, df_county, selected_year_3)
        return no_update, no_update, fig_3, no_update
    elif triggered_prop == 'year-slider-4c.value':
        fig_4 = funcs.plot_yearly_growth(county, df_county, year_range_4)
        return no_update, no_update, no_update, fig_4
    else:
        fig_1 = funcs.plot_average_unit_price(county, df_county)
        fig_2 = funcs.plot_town_volume_bar(county, df_county)
        fig_3 = funcs.plot_price_distribution(county, df_county)
        fig_4 = funcs.plot_yearly_growth(county, df_county)
        return fig_1, fig_2, fig_3, fig_4

    
    
    
