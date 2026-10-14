
import os
from datetime import datetime, timezone

from flask import Flask, request, jsonify, render_template
from supabase import create_client

app = Flask(__name__)


def get_db():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise RuntimeError("Konfigurasi Supabase belum lengkap")

    return create_client(url, key)


def save_log(event_type, latitude=None, longitude=None,
             accuracy_m=None, consent_given=False):
    row = {
        "event_type": event_type,
        "consent_given": consent_given,
    }

    if latitude is not None:
        row["latitude"] = latitude
        row["longitude"] = longitude
        row["accuracy_m"] = accuracy_m

    get_db().table("location_logs").insert(row).execute()


@app.get("/")
def index():
    # Catat kunjungan halaman tanpa mengambil koordinat.
    try:
        save_log("page_visit", consent_given=False)
    except Exception:
        app.logger.exception("Gagal menyimpan kunjungan")

    return render_template("index.html")


@app.post("/share-location")
def share_location():
    data = request.get_json(silent=True) or {}

    # Endpoint ini hanya menerima pengiriman eksplisit dari tombol izin.
    if data.get("consent") is not True:
        return jsonify({"error": "Persetujuan diperlukan"}), 403

    try:
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        accuracy = float(data["accuracy_m"])

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Koordinat di luar rentang")

        if not (0 <= accuracy <= 100000):
            raise ValueError("Akurasi tidak valid")

        save_log(
            "location_shared_with_consent",
            latitude=lat,
            longitude=lon,
            accuracy_m=accuracy,
            consent_given=True,
        )
        return jsonify({"status": "ok"})

    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Data lokasi tidak valid"}), 400
    except Exception:
        app.logger.exception("Gagal menyimpan lokasi ke database")
        return jsonify({"error": "Penyimpanan gagal"}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
