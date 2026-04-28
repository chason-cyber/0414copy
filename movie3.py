import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# --- 1. Firebase 初始化 ---
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- 2. 爬蟲更新功能 (程式啟動時自動跑一次) ---
def update_movie_data():
    url = "http://www.atmovies.com.tw/movie/next/"
    data = requests.get(url)
    data.encoding = "utf-8"
    sp = BeautifulSoup(data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    
    for item in result:
        try:
            title = item.find("div", class_="filmtitle").text.strip()
            movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
            doc = {
                "title": title,
                "hyperlink": "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href"),
                "showDate": item.find("div", class_="runtime").text.replace("上映日期：", "")[:10]
            }
            db.collection("電影").document(movie_id).set(doc)
        except:
            continue
    print("資料庫更新完畢！")

# 啟動伺服器前先更新資料
update_movie_data()