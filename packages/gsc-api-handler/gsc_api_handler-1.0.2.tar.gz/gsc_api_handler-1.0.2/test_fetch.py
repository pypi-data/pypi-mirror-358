# test_fetch.py

import os
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path

from gsc_api_handler.fetcher import fetch_and_store_gsc_data

# --- KONFIGURACIJA ---
SITE_URL = 'sc-domain:wettbasis.com' # Zamenite sa VAŠIM test domenom!
DB_PATH = 'wettbassis.sqlite'

# --- APSOLUTNE PUTANJE ZA KREDENCIJALE ---
# OVO MORATE PRILAGODITI VAŠEM SISTEMU!
PROJECT_ROOT = Path('/home/mzivkovic/developement/GscAppDevelopement/gsc-api-handler/')
CREDS_PATH = PROJECT_ROOT / 'gsc_credentials' / 'client_secret.json'
TOKEN_PATH = PROJECT_ROOT / 'gsc_credentials' / 'token.pickle'

# --- Provera da li client_secret.json postoji ---
if not CREDS_PATH.exists():
    print(f"ERROR: Client secrets file not found at {CREDS_PATH}.")
    print("Please ensure client_secret.json is located in the 'gsc_credentials' folder")
    print(f"within your project root: {PROJECT_ROOT}")
    exit(1)

# --- PRIPREMA DATUMA (16 meseci unazad) ---
today = datetime.today().date()
end_date_full_period = today - timedelta(days=2) # Ukupni krajnji datum
start_date_full_period = end_date_full_period - relativedelta(months=16) # Ukupni početni datum

# Formatiranje datuma u string za API pozive
start_date_full_period_str = start_date_full_period.strftime('%Y-%m-%d')
end_date_full_period_str = end_date_full_period.strftime('%Y-%m-%d')

print(f"--- Pokreće se test dohvaćanja za domen: {SITE_URL} ---")
print(f"Pokušavam dohvatiti podatke za UKUPAN period od: {start_date_full_period_str} do: {end_date_full_period_str}")
print(f"Podaci će biti sačuvani u: {DB_PATH}")
print(f"Koristeći kredencijale iz: {CREDS_PATH}")

try:
    # --- Čišćenje starog DB fajla pre početka svih fetcheva ---
    if Path(DB_PATH).exists():
        os.remove(DB_PATH)
        print(f"✅ Stari SQLite DB fajl obrisan: {DB_PATH}")

    total_rows_overall = 0
    current_end_date = end_date_full_period

    # --- ITERACIJA KROZ DATUMSKE CHUNKOVE (Mesec po mesec) ---
    # Ova petlja deli ukupan period na manje mesečne "chunkove"
    # kako bi se izbegao timeout i smanjilo opterećenje po jednom API pozivu na Google strani.
    while current_end_date >= start_date_full_period:
        # Određuje početak tekućeg "chunka" (obično početak meseca)
        chunk_start_date_obj = current_end_date - relativedelta(months=1) + timedelta(days=1)
        # Ako je početak "chunka" pre početka punog perioda, prilagodi ga
        if chunk_start_date_obj < start_date_full_period:
            chunk_start_date_obj = start_date_full_period

        chunk_end_date_obj = current_end_date

        chunk_start_date_str = chunk_start_date_obj.strftime('%Y-%m-%d')
        chunk_end_date_str = chunk_end_date_obj.strftime('%Y-%m-%d')

        print(f"\n--- Dohvaćanje chunk-a: {chunk_start_date_str} do {chunk_end_date_str} ---")

        try:
            # Poziva fetch_and_store_gsc_data za tekući datumski chunk
            rows_fetched_chunk = fetch_and_store_gsc_data(
                site_url=SITE_URL,
                db_path=DB_PATH,
                creds_path=str(CREDS_PATH),
                token_path=str(TOKEN_PATH),
                start_date=chunk_start_date_str,
                end_date=chunk_end_date_str,
                dimensions=['country', 'device', 'query', 'page', 'date']
            )
            total_rows_overall += rows_fetched_chunk
            print(f"✅ Dohvaćeno {rows_fetched_chunk} redova za chunk. Ukupno dohvaćeno: {total_rows_overall}")

        except Exception as e:
            print(f"❌ Greška prilikom dohvaćanja chunk-a ({chunk_start_date_str} do {chunk_end_date_str}): {e}")
            if "invalid_grant" in str(e).lower() or "authorization" in str(e).lower():
                print("Savet: Greška autorizacije. Pokušajte obrisati token.pickle fajl i ponovo pokrenuti skriptu.")
            # Nastavi sa sledećim chunkom, možda je privremeni problem
            # Važno: Možete dodati `time.sleep()` ovde da se izbegne prebrzo ponavljanje neuspešnih poziva

        # Pripremi se za sledeći, stariji chunk. Pomeramo se jedan dan unazad od početka obrađenog chunka.
        current_end_date = chunk_start_date_obj - timedelta(days=1)

    print(f"\n--- Globalno dohvaćanje završeno za domen: {SITE_URL} ---")
    print(f"✅ Ukupno svih redova (bez duplikata) dohvaćeno i sačuvano u {DB_PATH}: {total_rows_overall}")

    # --- VERIFIKACIJA PODATAKA U SQLITE BAZI ---
    if not Path(DB_PATH).exists():
        print(f"❌ Greška: SQLite DB fajl nije kreiran na putanji: {DB_PATH}")
        exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM gsc_data")
    count_in_db = cursor.fetchone()[0]
    print(f"📊 Ukupno redova u SQLite DB ({DB_PATH}): {count_in_db}")
    print(f"Očekujemo da ovaj broj bude blizu 'ukupno dohvaćenih redova' ako nije bilo duplikata tokom API fetch-a.")

    cursor.execute("SELECT MIN(date) FROM gsc_data")
    min_date_in_db = cursor.fetchone()[0]
    print(f"🗓️ Najstariji datum u DB: {min_date_in_db} (Očekivano: {start_date_full_period_str})")

    cursor.execute("SELECT MAX(date) FROM gsc_data")
    max_date_in_db = cursor.fetchone()[0]
    print(f"🗓️ Najnoviji datum u DB: {max_date_in_db} (Očekivano: {end_date_full_period_str})")

    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT
                country, device, query, page, date, clicks, impressions, ctr, position
            FROM gsc_data
            GROUP BY
                country, device, query, page, date, clicks, impressions, ctr, position
            HAVING
                COUNT(*) > 1
        ) AS duplicates;
    """)
    duplicates_found = cursor.fetchone()[0]
    print(f"❗ Broj pronađenih duplikata (celih redova): {duplicates_found} (Očekivano: 0)")

    conn.close()

    if min_date_in_db == start_date_full_period_str and \
       max_date_in_db == end_date_full_period_str and \
       duplicates_found == 0:
        print("\n--- Test uspešno završen: Svi datumi su dohvaćeni i nema duplikata! ---")
    else:
        print("\n--- Test završen sa upozorenjima/greškama. Proverite izlaz! ---")

except Exception as e:
    print(f"\n❌ Globalna greška tokom testiranja: {e}")
    if "invalid_grant" in str(e).lower() or "authorization" in str(e).lower():
        print("Savet: Greška autorizacije. Pokušajte obrisati token.pickle fajl i ponovo pokrenuti skriptu.")
