'''
群組	            特性
-------------------------------------------
0	    熱門、交易量高、成長快(蛋黃區)
1	    安靜、交易少但潛力中等(蛋白區)
2	    成長性低、交易低(偏鄉或已飽和)

'''



import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans


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
        return pd.DataFrame(columns=['鄉鎮市區', '配對百分比'])
    

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
    df_filtered['配對百分比'] = scaler.fit_transform(df_filtered[['總分']]) * 100


    # === 5. 可選：KMeans 分群標籤 ===
    if use_kmeans:
        features = df_filtered[col_list + ['清幽指標']]
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df_filtered['群組'] = kmeans.fit_predict(features)

    # === 6. 排序取前 K ===
    result_cols = ['鄉鎮市區', '配對百分比']
    if use_kmeans:
        result_cols.append('群組')

    return df_filtered.sort_values(by='配對百分比', ascending=False).head(top_k)[result_cols]



if __name__ == "__main__":

    # (模擬使用者偏好)
    user_pref = {
        '縣市': '臺南市',
        '購屋預算': 15000000,
        '偏好權重': {'交易熱區': 3,'成長性': 3,'清幽': 0, '價格適配': 2}
        }
    

    # (使用推薦系統)
    df = pd.read_csv('房市分析彙總表.csv')
    top_recommendations = recommend_townships(df, user_pref, use_kmeans=True)
    print(top_recommendations)