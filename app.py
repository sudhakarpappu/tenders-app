from flask import Flask, render_template, request, jsonify
import requests
from flask_assets import Environment, Bundle

app = Flask(__name__)
assets = Environment(app)

API_BASE = "https://tenders.guru/api"
TRANSLATE_API = "https://ftapi.pythonanywhere.com/translate"   # ✅ new endpoint


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
    data = request.get_json()
    texts = data.get("texts", [])
    target_lang = data.get("target", "en")

    try:
        # Send whole list at once
        r = requests.post(
            TRANSLATE_API,
            json={"text": texts, "dl": target_lang},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        r.raise_for_status()

        result = r.json()

        # If API returns a single string (for one input)
        if isinstance(result.get("destination-text"), str):
            translated_list = [result["destination-text"]]
        else:
            translated_list = result.get("destination-text", texts)

        return jsonify({"translations": translated_list})

    except Exception as e:
        print("Translation error:", e)
        return jsonify({"translations": texts})


    return jsonify({"translations": translated_list})

if __name__ == "__main__":
    app.run(debug=True)
