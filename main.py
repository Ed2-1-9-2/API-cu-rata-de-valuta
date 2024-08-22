import requests

# Introduceți cheia API obținută de la ExchangeRate-API
api_key = "9670edd9a40d0d3c7106769f"

# Solicităm utilizatorului să introducă moneda de bază și cea de conversie
base_currency = input("Introduceți moneda de bază (ex: USD): ").upper()
target_currency = input("Introduceți moneda de conversie (ex: EUR): ").upper()

# URL-ul API-ului ExchangeRate-API
url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"

# Faceți solicitarea GET către API
response = requests.get(url)

# Afișăm răspunsul text pentru debugging
print("Response text:", response.text)

try:
    # Convertim răspunsul în format JSON
    data = response.json()
except requests.exceptions.JSONDecodeError:
    print("Error: The response is not a valid JSON format.")
    data = None

# Continuăm doar dacă datele sunt valide
if data and data.get('result') == 'success':
    # Extragem rata de schimb
    exchange_rate = data['conversion_rate']
    print(f"1 {base_currency} = {exchange_rate} {target_currency}")
else:
    print("Error fetching exchange rate.")
