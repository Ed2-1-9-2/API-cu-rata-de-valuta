import requests

with open("api_key.txt", "r") as file:
    api_key = file.read().strip()

base_currency = input("Introduceți moneda de bază (ex: USD): ").upper()
target_currency = input("Introduceți moneda de conversie (ex: EUR): ").upper()

url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"

response = requests.get(url)

print("Response text:", response.text)

try:
    data = response.json()
except requests.exceptions.JSONDecodeError:
    print("Error: The response is not a valid JSON format.")
    data = None

if data and data.get('result') == 'success':
    exchange_rate = data['conversion_rate']
    print(f"1 {base_currency} = {exchange_rate} {target_currency}")
else:
    print("Error fetching exchange rate.")
