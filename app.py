from flask import Flask, render_template, request, jsonify
import requests
from flask_assets import Environment, Bundle

app = Flask(__name__)
assets = Environment(app)

API_BASE = "https://tenders.guru/api"
TRANSLATE_API = "https://ftapi.pythonanywhere.com/translate"   # ✅ new endpoint
scss = Bundle(
    'style.scss',  # input file in /static/
    filters='libsass',  # or 'libsass'
    output='style.css'  # compiled output
)

assets.register('scss_all', scss)
# ✅ Build assets at startup
scss.build()

@app.route("/", methods=["GET"])
def home():
    country = request.args.get("country", "es")   # default Spain
    query = request.args.get("q", "")             # search query
    page = int(request.args.get("page", 1))       # our own page number
    per_page = 10                                 # show only 10 tenders per page

    url = f"{API_BASE}/{country}/tenders?page={page}"
    params = {}
    if query:
        params["q"] = query
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", [])
    except Exception as e:
        print("Error fetching tenders:", e)
        data = []

    # Slice results → only 10 items
    start = (page - 1) * per_page
    end = start + per_page
    tenders_page = data[start:end]

    return render_template("index.html",
                           tenders=tenders_page,
                           country=country,
                           query=query,
                           page=page)

@app.route("/translate", methods=["POST"])
def translate():
    texts = request.json.get("texts", [])   # list of strings
    target_lang = request.json.get("target", "en")
    headers = {"Content-Type": "application/json"}

    translated_list = []
    for text in texts:
        params = {"dl": target_lang, "text": text}
        try:
            r = requests.get(TRANSLATE_API, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            dst = r.json().get("destination-text", text)
            translated_list.append(dst)
        except Exception as e:
            print("Translation error:", e)
            translated_list.append(text)

    return jsonify({"translations": translated_list})

if __name__ == "__main__":
    app.run(debug=True)
