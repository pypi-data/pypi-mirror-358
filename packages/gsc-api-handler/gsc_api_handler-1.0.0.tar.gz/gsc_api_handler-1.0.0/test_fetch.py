# test_fetch.py

import os
from gsc_api_handler.fetcher import fetch_and_store_gsc_data
from gsc_api_handler.auth import DEFAULT_CREDS_PATH, DEFAULT_TOKEN_PATH

# Osnovna konfiguracija — može biti hardkodovana ili preuzeta iz .env fajla
SITE_URL = 'sc-domain:worldsoccertalk.com'
DB_PATH = 'gsc_worldsoccertalk.sqlite'

# Ove vrednosti već preuzima `authorize_creds` iz .env fajla
CREDS_PATH = DEFAULT_CREDS_PATH
TOKEN_PATH = DEFAULT_TOKEN_PATH

# Testiranje za jedan dan — najnoviji dan dostupan (pre 2 dana)
from datetime import date, timedelta
today = date.today()
end_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
start_date = end_date  # isti dan

# Pokretanje fetch procesa
rows = fetch_and_store_gsc_data(
    site_url=SITE_URL,
    db_path=DB_PATH,
    creds_path=CREDS_PATH,
    token_path=TOKEN_PATH,
    start_date=start_date,
    end_date=end_date
)

print(f"✅ Fetch complete. Total rows inserted: {rows}")
