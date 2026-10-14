import os
from supabase import create_client

def get_db():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        raise RuntimeError("Konfigurasi Supabase belum lengkap")
    return create_client(url, key)

def save_test_event():
    db = get_db()
    result = db.table("location_logs").insert({
        "event_type": "connection_test",
        "consent_given": False
    }).execute()
    return result.data
