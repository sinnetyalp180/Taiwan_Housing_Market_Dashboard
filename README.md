# Taiwan Housing Market Dashboard (台灣房價觀測儀表板)
這是一個基於 Python Dash 結合地圖應用與資料視覺化，開發的互動式網頁應用程式。
旨在提供台灣房價數據的視覺化分析與趨勢觀察，並可利用 AI 推薦以提供更多資訊了連結。


## 系統需求 (Environment)
- **Python 版本**: "3.10.11" (建議版本)
- **主要套件**: 詳見 `requirements.txt`


## 資料準備與路徑說明 (Data Setup)
由於 GitHub 的檔案大小限制，本專案不包含原始數據。執行程式前，請依照以下說明手動下載並配置數據：

### 1. 地圖數據 (Map Data)
- **縣市界線 (County)**:
    - [下載連結](https://data.gov.tw/dataset/7442) (請選擇 SHP 格式)。
    - 解壓縮至：`dashboard/assets/data/Taiwan_Administrative_Region/County`
- **鄉鎮市區界線 (Town)**:
    - [下載連結](https://data.gov.tw/dataset/7441) (請選擇 SHP 格式)。
    - 解壓縮至：`dashboard/assets/data/Taiwan_Administrative_Region/Town`

### 2. 房屋交易數據 (Housing Transactions)
- **來源**: [內政部不動產成交案件實際資訊](https://plvr.land.moi.gov.tw/DownloadOpenData)
- **步驟**: 
    1. 點選「非本期下載」，選擇「CSV」格式。
    2. 依季度下載後，在 `dashboard/assets/data/house_price/release/` 下建立對應資料夾（例如：`lvr_landcsv_114_2`）。
    3. 將下載的 CSV 檔案解壓縮至該資料夾內。


### 預期目錄結構 (Project Structure)
請確保您的檔案路徑如下所示，否則 `app.py` 將無法讀取資料：

```text
Taiwan_Housing_Market_Dashboard/
├── app.py                       # 程式執行主入口
├── requirements.txt             # 必要套件清單
├── .env                         # 環境變數設定 (自行建立)
├── dashboard/
│   ├── callbacks/
│   ├── layout/
│   ├── utils/
│   └── assets/
│       ├── img/
│       │   └── .gitkeep
│       │
│       └── data/
│           ├── Taiwan_Administrative_Region/
│           │   ├── County/                           # 放置縣市界線 SHP 相關檔案
│           │   └── Town/                             # 放置鄉鎮市區界線 SHP 相關檔案
│           │
│           └── house_price/
│               └── release/                          # 需依照年分與季度建立資料夾，如 lvr_landcsv_114_2
│                   ├── lvr_landcsv_114_2/            # 放置該季度的原始 CSV 檔案
│                   │   └── .gitkeep
│                   └── lvr_landcsv_114_3/            # 放置該季度的原始 CSV 檔案
│                       └── .gitkeep
│
└── temp/                                             # 程式執行產生的快取資料



