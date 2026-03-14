# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 18:18:21 2025

@author: user
"""


import os, traceback, csv
import pandas as pd
from glob import glob
from datetime import datetime


# import dashboard.utils.constants as constants
# import constants



# csv_file_dir = r"dashboard\assets\data\house_price\release"
csv_file_dir = r'C:\Users\user\Desktop\Taiwan_House_Price_Dash\Taiwan_House_Price_Dash_v2\dashboard\assets\data\house_price\release'


county_and_id = {'臺北市': 'A', '臺中市': 'B', '基隆市': 'C', '臺南市': 'D', 
                 '高雄市': 'E', '新北市': 'F', '宜蘭縣': 'G', '桃園市': 'H', 
                 '嘉義市': 'I', '新竹縣': 'J', '苗栗縣': 'K', '南投縣': 'M', 
                 '彰化縣': 'N', '新竹市': 'O', '雲林縣': 'P', '嘉義縣': 'Q', 
                 '屏東縣': 'T', '花蓮縣': 'U', '臺東縣': 'V', '金門縣': 'W', 
                 '澎湖縣': 'X', '連江縣': 'Z',}

id_and_county = {'A': "臺北市", 'B': "臺中市", 'C': "基隆市", 'D': "臺南市",
                 'E': "高雄市", 'F': "新北市", 'G': "宜蘭縣", 'H': "桃園市",
                 'I': "嘉義市", 'J': "新竹縣", 'K': "苗栗縣", 'M': "南投縣",
                 'N': "彰化縣", 'O': "新竹市", 'P': "雲林縣", 'Q': "嘉義縣",
                 'T': "屏東縣", 'U': "花蓮縣", 'V': "臺東縣", 'W': "金門縣",
                 'X': "澎湖縣", 'Z': "連江縣",}




def read_csvs(dir_path, county_and_id):
    df_dict = {}
    for c, c_id in county_and_id.items():
        csv_paths = glob(os.path.join(dir_path, fr'*\{c_id.lower()}_lvr_land_[a-z].csv'))
        # csv_paths = glob(os.path.join(dir_path, fr'*\b_lvr_land_[a-c].csv'))             # (test)
        df_list = []
        for csv_path in csv_paths:
            csv_dir_path, basename = os.path.split(csv_path)
            county_id = basename.split('_')[0]

            df = pd.read_csv(csv_path,
                             header=[0, 1],
                             on_bad_lines='skip',                        # 當資料出現錯誤，則跳過
                             # error_bad_lines=False,                    # 舊版 pandas < 1.3
                             encoding='utf-8',
                             quoting=csv.QUOTE_NONE,
                             low_memory=False)                           # 一次性讀取整個檔案，並自行判斷每個欄位的最佳型態
            # df = pd.read_csv(csv_path, header=[0, 1])
            df.columns = df.columns.get_level_values(0)                  # 只保留中文欄名
            df["county_id"] = county_id                                  # 新增一欄記錄來源
            df_list.append(df)

        df_merged = pd.concat(df_list, ignore_index=True)
        df_merged["單價元坪"] = df_merged["單價元平方公尺"] * 3.305785
        df_merged["民國年"] = df_merged["交易年月日"] // 10000
        df_merged["西元年"] = df_merged["民國年"] + 1911

        df_dict[c_id.lower()] = df_merged                               # {'a': pd.DataFrame(), 'b': pd.DataFrame(), ...}
    return df_dict



def process_city_data(county_id, df, base_year=None):
    df = df.copy()
    df["西元年"] = pd.to_numeric(df["西元年"], errors="coerce")
    df["單價元坪"] = pd.to_numeric(df["單價元坪"], errors="coerce")
    df["總價元"] = pd.to_numeric(df["總價元"], errors="coerce")
    df = df.dropna(subset=["西元年", "單價元坪", "總價元", "鄉鎮市區"])
    df["縣市"] = id_and_county[county_id.upper()]

    # 設定前一年（如未指定）
    if base_year is None:
        base_year = int(df["西元年"].max()) - 1

    # --- 計算每年平均房價（每鄉鎮） ---
    town_year_avg = df.groupby(["縣市", "鄉鎮市區", "西元年"])["單價元坪"].mean().reset_index()

    # --- 計算成長率 ---
    town_year_avg.sort_values(by=["縣市", "鄉鎮市區", "西元年"], inplace=True)
    town_year_avg["年成長率"] = town_year_avg.groupby(["縣市", "鄉鎮市區"])["單價元坪"].pct_change() * 100  # 百分比

    # --- 篩出過去三年的成長率並平均 ---
    growth_df = town_year_avg[town_year_avg["西元年"].between(base_year - 2, base_year)]
    avg_growth = growth_df.groupby(["縣市", "鄉鎮市區"])["年成長率"].mean().reset_index()
    avg_growth.rename(columns={"年成長率": "過去三年平均成長率"}, inplace=True)

    # --- 前一年房價與成交價 ---
    prev_year_df = df[df["西元年"] == base_year]
    summary = prev_year_df.groupby(["縣市", "鄉鎮市區"]).agg(
        交易量=("單價元坪", "count"),
        前一年平均房價_坪=("單價元坪", "mean"),
        前一年平均成交價=("總價元", "mean"),
    ).reset_index()

    # --- 合併所有欄位 ---
    final_df = pd.merge(summary, avg_growth, on=["縣市", "鄉鎮市區"], how="left")

    return final_df



if __name__ == "__main__":
    
    print('Start')

    df_dict = read_csvs(csv_file_dir, county_and_id)
    # print(read_csvs.keys())

    final_dfs = []
    for k, df in df_dict.items():
        processed_df  = process_city_data(k.upper(), df, base_year=datetime.now().year-1)
        final_dfs.append(processed_df)

    combined_df = pd.concat(final_dfs, ignore_index=True)
    combined_df.to_csv("房市分析彙總表.csv", index=False, encoding="utf-8-sig")    # encoding="utf-8-sig"：使用 UTF-8 帶 BOM，讓 Excel 開啟時不會亂碼（特別是有中文時）。

    print('Done\n')











