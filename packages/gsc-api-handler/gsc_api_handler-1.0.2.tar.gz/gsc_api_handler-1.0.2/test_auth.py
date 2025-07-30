# test_auth.py (privremeni fajl u root-u projekta)
from gsc_api_handler import authorize_creds

# Poziv bez argumenata — koristi putanje iz .env fajla
service = authorize_creds()

# Ako je autentikacija uspešna, ovo će ispisati <Resource ...>
print(service)


