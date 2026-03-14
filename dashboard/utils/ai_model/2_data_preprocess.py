'''
前處理必須做：標準化、編碼、缺失值處理

監督式學習要標籤，無的話就用無監督或規則結合方式

可先用加權評分模型＋距離計算實現初版
'''

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

df = pd.read_csv('房市分析彙總表.csv')

# (1. 缺失值檢查)
print('<Missing Values>')
print(df.isnull().sum())
print()



# (2. 編碼類別欄位 (One-Hot))
# df = pd.get_dummies(df, columns=['縣市', '鄉鎮市區'])
# print(df.head())


#%%

# (3. 數值欄位 Min-Max 正規化 (Normalization / Scaling))
scaler = MinMaxScaler()
col_list = ['交易量', '前一年平均房價_坪', '前一年平均成交價', '過去三年平均成長率']

df[col_list] = scaler.fit_transform(df[col_list])        # 將數據壓縮至0~1區間
df['清幽指標'] = 1 - df['交易量']
print(df.head(), '\n')
 

#%%

user_pref = {
    '縣市': '臺南市',
    '預算上限': 33000000,
    '偏好權重': {'交易熱區': 0.4, '成長性': 0.4, '清幽': 0.2}
}


# === 1. 必要條件過濾 ===
df_filtered = df[(df['縣市']==user_pref['縣市']) & (df['前一年平均成交價']<=user_pref['預算上限'])].copy()

# === 2. 偏好配對評分 ===
# df_filtered['清幽指標'] = 1 - df_filtered['交易量']              # 需已 MinMaxScaler 過
df_filtered['總分'] = (
    df_filtered['交易量'] * user_pref['偏好權重']['交易熱區'] +
    df_filtered['過去三年平均成長率'] * user_pref['偏好權重']['成長性'] +
    df_filtered['清幽指標'] * user_pref['偏好權重']['清幽']
)


scaler = MinMaxScaler()
df_filtered['配對百分比'] = scaler.fit_transform(df_filtered[['總分']]) * 100


# === 3. 顯示推薦前三名 ===
top3 = df_filtered.sort_values(by='配對百分比', ascending=False)
print(top3[['鄉鎮市區', '配對百分比']], '\n')


#%%

features = df_filtered[col_list]
kmeans = KMeans(n_clusters=3, random_state=0)
df_filtered['區域群'] = kmeans.fit_predict(features)
print(df_filtered, '\n')
