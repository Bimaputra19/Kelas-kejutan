from db_store import save_test_event

try:
    result = save_test_event()
    print("BERHASIL: data tes masuk ke Supabase.")
    print(result)
except Exception as exc:
    print("Tes gagal. Periksa konfigurasi dan izin database.")
    print(type(exc).__name__, str(exc)[:300])
