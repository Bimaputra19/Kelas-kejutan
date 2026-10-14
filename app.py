from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
from pathlib import Path
import json

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "access_log.jsonl"


def write_log(data):
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


@app.get("/")
def index():
    write_log({
        "event": "page_visit",
        "time_utc": datetime.now(timezone.utc).isoformat()
    })
    return render_template("index.html")


@app.post("/share-location")
def share_location():
    data = request.get_json(silent=True) or {}

    try:
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        accuracy = float(data["accuracy_m"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Koordinat tidak valid"}), 400

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify({"error": "Koordinat di luar rentang"}), 400

    if not (0 <= accuracy <= 100000):
        return jsonify({"error": "Akurasi tidak valid"}), 400

    write_log({
        "event": "location_shared_with_consent",
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "latitude": lat,
        "longitude": lon,
        "accuracy_m": accuracy
    })

    return jsonify({"status": "ok"})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
