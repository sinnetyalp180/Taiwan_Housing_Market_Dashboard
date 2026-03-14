import os, traceback, csv
import pandas as pd
from glob import glob


def cleaned_lines(filepath, encoding='utf-8'):                              # (刪除有問題的欄位)
    with open(filepath, encoding=encoding, errors='ignore') as f:
        for line in f:
            if line.count('"') % 2 == 0:
                yield line

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



# TN_TANKS = [f'TN{str(i).zfill(2)}' for i in range(1, 9)]
# TC_TANKS = [f'TC{str(i).zfill(2)}' for i in range(1, 22)]
# TC_JUNO_TANKS = [f'TC{str(i).zfill(2)}' for i in range(14, 22)]
# TANKS = TN_TANKS + TC_TANKS
# PI_SUMMARYTYPE = {'AVERAGE': 2, 'MINIMUM': 4, 'MAXIMUM': 8, 'RANGE': 16, 'STD_DEV': 32}
# CONNECTIONSTRING_TN_PPDA = 'oracle://training:training@TN_PPDA'
# CONNECTIONSTRING_TC_PPDA = 'oracle://training:training@TC_PPDA'

file_county_path = r"dashboard\assets\data\Taiwan_Administrative_Region\County\COUNTY_MOI_1130718.shp"
file_town_path = r"dashboard\assets\data\Taiwan_Administrative_Region\Town\TOWN_MOI_1131028.shp"

csv_file_dir = r"dashboard\assets\data\house_price\release"


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


df_dict = read_csvs(csv_file_dir, county_and_id)



