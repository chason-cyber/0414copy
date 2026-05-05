import requests
import json

# 台中市交通事故資料 API 網址
url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"

try:
    # 取得資料並忽略 SSL 驗證 (如原始程式碼所示)
    response = requests.get(url, verify=False)
    response.encoding = 'utf-8' # 確保中文不亂碼
    
    # 解析 JSON 資料
    json_data = json.loads(response.text)

    # 1. 進行排序：根據 "總件數" 從大到小排序 (reverse=True)
    # 使用 int() 確保它是以數字進行比較，避免字串排序錯誤
    sorted_data = sorted(json_data, key=lambda x: int(x["總件數"]), reverse=True)

    # 2. 取出前 10 名
    top_10 = sorted_data[:10]

    print("=== 台中市十大肇事路口排行榜 ===")
    print("-" * 40)

    for i, item in enumerate(top_10, 1):
        name = item["路口名稱"]
        count = item["總件數"]
        print(f"第 {i:2d} 名 | {name}")
        print(f"       | 總事故件數：{count} 件")
        print("-" * 40)

except Exception as e:
    print(f"發生錯誤：{e}")