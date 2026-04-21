import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, jsonify, Response

import random
import os
import json
from flask import Flask, render_template, request
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore


# --- Firebase 初始化邏輯 (加強版) ---
if not firebase_admin._apps:  # 避免 Vercel 重複初始化導致報錯
    try:
        if os.path.exists('serviceAccountKey.json'):
            # 本地開發環境
            cred = credentials.Certificate('serviceAccountKey.json')
        else:
            # Vercel 雲端環境：從環境變數讀取
            firebase_config = os.getenv('FIREBASE_CONFIG')
            if firebase_config:
                # 確保 JSON 格式正確解析
                cred_dict = json.loads(firebase_config)
                cred = credentials.Certificate(cred_dict)
            else:
                print("錯誤：找不到 FIREBASE_CONFIG 環境變數")
                cred = None
        
        if cred:
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase 初始化失敗: {e}")

# 初始化資料庫
db = firestore.client() if firebase_admin._apps else None

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入陳宇謙的網站網頁</h1>"
    link += "<a href='/mis'>課程</a><hr>"
    link += "<a href='/today'>今天日期</a><hr>"
    link += "<a href='/about'>關於宇謙</a><hr>"
    link += "<a href='/welcome?nick=宇謙'>GET傳值</a><hr>"
    link += "<a href='/account'>POST傳值(帳號密碼)</a><hr>"
    link += "<a href='/operation'>數學運算</a><hr>"
    link += "<a href='/cup'>擲茭</a><hr>"
    link += "<a href='/read'>讀取firestore資料(搜尋老師)</a><br><hr>"
    link += "<a href='/spider1'>蜘蛛</a><br><hr>"
    link += "<a href='movie'>即將上線電影</a><br><hr>"
    return link

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    now = datetime.now()
    date_str = now.strftime("%Y/%m/%d")
    return render_template("today.html", datetime=date_str)

@app.route("/about")
def about():
    return render_template("my.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.args.get("nick", "訪客")
    return render_template("welcome.html", name=user)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form.get("user")
        pwd = request.form.get("pwd")
        return f"您輸入的帳號是：{user}; 密碼為：{pwd}"
    return render_template("account.html")

@app.route("/operation", methods=["GET", "POST"])
def operation():
    if request.method == "POST":
        try:
            x = float(request.form.get("x", 0))
            y = float(request.form.get("y", 0))
            opt = request.form.get("opt")
            if opt == "+": result = x + y
            elif opt == "-": result = x - y
            elif opt == "*": result = x * y
            elif opt == "/": result = x / y if y != 0 else "不能除以0"
            else: result = "運算子錯誤"
        except Exception:
            result = "輸入格式錯誤"
        return render_template("operation.html", result=result)
    return render_template("operation.html", result=None)

@app.route('/cup', methods=["GET"])
def cup():
    action = request.args.get('action')
    result = None
    if action == 'toss':
        x1, x2 = random.randint(0, 1), random.randint(0, 1)
        if x1 != x2: msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0: msg = "笑筊：表示神明一笑、不解，或者考慮中。"
        else: msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
        result = {
            "cup1": f"/static/{x1}.jpg",
            "cup2": f"/static/{x2}.jpg",
            "message": msg
        }
    return render_template('cup.html', result=result)

@app.route("/read", methods=["GET", "POST"])
def read():
    # 這裡保留你原本的 HTML 字串構建方式，但加入 db 檢查
    html_content = """
    <html><head><title>老師搜尋系統</title></head><body>
    <h1>搜尋老師關鍵字</h1>
    <form method="POST">
        <input type="text" name="keyword" placeholder="請輸入老師名字">
        <input type="submit" value="搜尋">
    </form><hr>
    """
    
    if request.method == "POST":
        keyword = request.form.get("keyword")
        if not db:
            html_content += "<p style='color:red;'>資料庫未成功連線</p>"
        else:
            collection_ref = db.collection("靜宜資管")
            docs = collection_ref.get()
            found = False
            html_content += f"<h3>搜尋「{keyword}」的結果：</h3>"
            for doc in docs:
                user = doc.to_dict()
                if keyword and "name" in user and keyword in user["name"]:
                    found = True
                    html_content += f"<p>👉 <strong>{user.get('name')}</strong> 老師的研究室在 {user.get('lab')}，信箱：{user.get('mail')}</p><hr>"
            if not found:
                html_content += "<p>找不到符合條件的老師。</p>"

    html_content += '<br><a href="/">回到首頁</a></body></html>'
    return html_content

@app.route("/spider1")
def sp1():
    R=""
    url="https://0414copy.vercel.app/about"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select("td a")

    for item in result:
        R +=item.text + "<br>" + item.get("href") + "<br><br>"
    return R



@app.route("/movie")
def movie():
    url = "https://www.atmovies.com.tw/movie/next/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    Data = requests.get(url, headers=headers)
    Data.encoding = "utf-8"
    
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    
    movies = []
    for item in result:
        a_tag = item.find("a")
        if a_tag:
            img_tag = item.find("img")
            if img_tag and img_tag.get("alt"):
                name = img_tag.get("alt")
            else:
                name = a_tag.get_text(strip=True)
            
            href = a_tag.get("href")
            if href:
                full_link = "https://www.atmovies.com.tw" + href
            else:
                full_link = "#"
            
            movies.append({"name": name, "link": full_link})
    
    # 產生 HTML（每個電影名稱都是超連結）
    html = '<meta charset="UTF-8"><h1>即將上映電影</h1><ul>'
    for m in movies:
        html += f'<li><a href="{m["link"]}" target="_blank">{m["name"]}</a></li>'
    html += '</ul>'
    
    return Response(html, mimetype='text/html; charset=utf-8')


if __name__ == "__main__":
    app.run(debug=True)