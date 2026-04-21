import requests
from bs4 import BeautifulSoup

url = "https://www.atmovies.com.tw/movie/next/"
Data = requests.get(url)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")

# 嘗試多個可能的選擇器，確保能抓到資料
result = sp.select(".filmListAllX li")  # 你原來的選擇器
if not result:
    result = sp.select(".filmList li")  # 備用選擇器1
if not result:
    result = sp.select(".movie-list li")  # 備用選擇器2

print(f"找到 {len(result)} 個電影項目\n")
print("=" * 50)

for idx, item in enumerate(result, 1):
    a_tag = item.find("a")
    if a_tag:
        # 電影名稱：優先從 img 的 alt 屬性取得
        img_tag = item.find("img")
        if img_tag and img_tag.get("alt"):
            name = img_tag.get("alt")
        else:
            name = a_tag.get_text(strip=True)
        
        # 超鏈結組合
        href = a_tag.get("href")
        if href:
            full_link = "https://www.atmovies.com.tw" + href
        else:
            full_link = "無連結"
        
        # 印出結果
        print(f"{idx}. 電影名稱：{name}")
        print(f"   超鏈結：{full_link}")
        print("-" * 50)
    else:
        print(f"{idx}. 找不到連結")
        print("-" * 50)

print(f"\n總共抓到 {len(result)} 部電影")