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
    link += "<a href='movie2'>讀取開眼電影即將上映影片，寫入Firestore</a><br><hr>"
    link += "<a href='movie3'>查詢相關電影資訊</a><br><hr>"
    link += "<a href='road'>台中市十大肇事路口</a><br><hr>"
    link += "<a href='weather'>輸入欲查詢的縣市</a><br><hr>"
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


@app.route("/movie2")
def movie2():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    # 這是頁面的基礎 CSS 樣式，讓結果好看一點 (非外部檔案)
    style = """
    <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; }
        .movie-item { border-bottom: 1px solid #ccc; padding: 10px 0; }
        .title { color: #2c3e50; font-size: 1.2em; font-weight: bold; }
    </style>
    """
    
    if request.method == "POST":
        # 取得使用者輸入
        keyword = request.form.get("MovieTitle", "").strip()
        
        if not keyword:
            return f"{style}<h2>請輸入關鍵字！</h2><a href='/movie3'>返回</a>"

        # 模擬查詢結果介面
        header = f"{style}<h1>即將上映查詢</h1>"
        header += f"<h3>查詢結果 (關鍵字: {keyword}):</h3><hr>"
        
        # 從 Firebase 篩選
        movies_ref = db.collection("電影")
        docs = movies_ref.stream()

        results_html = ""
        count = 0
        for doc in docs:
            movie = doc.to_dict()
            if keyword.lower() in movie['title'].lower():
                count += 1
                results_html += f"""
                <div class="movie-item">
                    <div class="title">{count}. {movie['title']}</div>
                    <div>上映日期: {movie['showDate']}</div>
                    <div>連結: <a href="{movie['hyperlink']}" target="_blank">查看詳情</a></div>
                </div>
                """
        
        if count == 0:
            results_html = "<p>查無相關電影資訊。</p>"
        
        return header + results_html + '<br><a href="/movie3">繼續查詢</a>'

    else:
        # GET 請求：顯示輸入框
        return f"""
        {style}
        <h1>即將上映查詢</h1>
        <form action="/movie3" method="POST">
            <label>請輸入電影片名關鍵字：</label>
            <input type="text" name="MovieTitle" placeholder="例如：人" required>
            <button type="submit">查詢</button>
        </form>
        """

@app.route("/road")
def road():
    Result = "<h2>路口</h2><hr>"
    local_file = os.path.join(os.path.dirname(__file__), "臺中市113年10月份十大高肇事路口.JSON")
    if os.path.exists(local_file):
        with open(local_file, "r", encoding="utf-8") as f:
            JsonData = json.load(f)
    else:
        url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
        Data = requests.get(url, timeout=10)
        Data.raise_for_status()
        try:
            JsonData = Data.json()
        except ValueError:
            JsonData = json.loads(Data.text)

    if not isinstance(JsonData, list):
        return "資料格式錯誤，無法讀取路口資料。"

    for item in JsonData:
        Result += f"{item.get('路口名稱', '')}：發生{item.get('總件數', '')}件，主因是{item.get('主要肇因', '')}<br>"
    return Result

@app.route("/weather", methods=["GET", "POST"])
def weather():
    # 建立基礎的 HTML 介面
    Result = "<h2>縣市天氣查詢</h2><hr>"
    Result += """
        <form method="POST">
            請輸入欲查詢的縣市：<input type="text" name="city" placeholder="例如：臺中市">
            <button type="submit">查詢</button>
        </form>
        <br>
    """

    if request.method == "POST":
        city_input = request.form.get("city")
        if city_input:
            city = city_input.replace("台", "臺")
            token = "rdec-key-123-45678-011121314"
            url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={token}&format=JSON&locationName={city}"
            
            try:
                # 取得 API 資料
                Data = requests.get(url, verify=False, timeout=10)
                Data.raise_for_status()
                JsonData = Data.json()
                
                # 依照你原本 weather.py 的解析邏輯提取資料
                # 這裡加入判斷，防止找不到縣市時程式崩潰
                if JsonData["records"]["location"]:
                    location_data = JsonData["records"]["location"][0]
                    weather_element = location_data["weatherElement"]
                    
                    # 取得天氣現象 (Wx) 與 降雨機率 (PoP)
                    weather_desc = weather_element[0]["time"][0]["parameter"]["parameterName"]
                    rain_chance = weather_element[1]["time"][0]["parameter"]["parameterName"]
                    
                    Result += f"<b>{city}</b> 目前預報：{weather_desc}，降雨機率：{rain_chance}%"
                else:
                    Result += f"<span style='color:red;'>找不到「{city}」的資料，請確認名稱是否輸入正確。</span>"
                    
            except Exception as e:
                Result += f"<span style='color:red;'>系統錯誤或無法連接 API：{str(e)}</span>"
        else:
            Result += "請輸入縣市名稱。"

    return Result
        
if __name__ == "__main__":
    app.run(debug=True) 