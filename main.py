import requests
import sys
import os
import csv
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict

exchange_rate_cache = defaultdict(dict)
def write_api_key_to_binary_file(api_key, file_path):
    """Scrie cheia API într-un fișier binar (de fapt, text în format binar)."""
    with open(file_path, 'wb') as binary_file:
        binary_file.write(api_key.encode('utf-8'))
    print(f"API key a fost scrisă în {file_path} ca fișier binar.")

def read_api_key_from_binary_file(file_path):
    """Citește cheia API dintr-un fișier binar (de fapt, text în format binar)."""
    try:
        with open(file_path, 'rb') as binary_file:
            api_key = binary_file.read().decode('utf-8')
        print("API key a fost citită din fișierul binar.")
        return api_key
    except FileNotFoundError:
        return None

def read_api_key_from_text_file(file_path):
    """Citește cheia API dintr-un fișier text și o convertește într-un fișier binar dacă este necesar."""
    try:
        with open(file_path, 'r') as text_file:
            api_key = text_file.read().strip()
        print("API key a fost citită din fișierul text.")
        # Convertește cheia API din text într-un fișier binar pentru utilizări viitoare
        write_api_key_to_binary_file(api_key, "api_key.bin")
        return api_key
    except FileNotFoundError:
        return None

def get_api_key():
    """Obține cheia API, verificând atât fișierele binare cât și cele text."""
    binary_file_path = "api_key.bin"
    text_file_path = "api_key.txt"

    # Încercăm să citim mai întâi din fișierul binar
    api_key = read_api_key_from_binary_file(binary_file_path)
    if api_key:
        return api_key

    # Dacă fișierul binar nu este găsit, încercăm să citim din fișierul text
    api_key = read_api_key_from_text_file(text_file_path)
    if api_key:
        return api_key

    # Dacă niciun fișier nu este găsit, returnăm None
    print("Nu s-a putut găsi API key-ul. Asigură-te că fișierul text sau binar este disponibil și corect.")
    return None
def get_exchange_rate(api_key, base_currency, target_currency):
    """Fetch exchange rate from ExchangeRate-API with caching."""
    current_time = datetime.now()

    if (target_currency in exchange_rate_cache[base_currency] and
            current_time - exchange_rate_cache[base_currency][target_currency]['timestamp'] < timedelta(hours=1)):
        return exchange_rate_cache[base_currency][target_currency]['rate']

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
        return None
    except requests.exceptions.JSONDecodeError:
        print("Error: The response is not a valid JSON format.")
        return None

    if data.get('result') == 'success':
        rate = data['conversion_rate']
        exchange_rate_cache[base_currency][target_currency] = {'rate': rate, 'timestamp': current_time}
        return rate
    else:
        print(f"Error fetching exchange rate: {data.get('error-type', 'Unknown error')}")
        return None


def is_valid_currency(currency):
    return len(currency) == 3 and currency.isalpha()


def save_to_csv(data, filename="conversion_results.csv"):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Amount", "Base Currency", "Target Currency", "Converted Amount", "Rate"])
            writer.writerows(data)
        print(f"Results have been saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


def plot_exchange_rate_history(api_key, base_currency, target_currency, days=7):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')


    url = f"http://data.fixer.io/api/timeseries"
    params = {
        "access_key": api_key,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "base": base_currency,
        "symbols": target_currency
    }

    response = requests.get(url, params=params)

    try:
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
        return
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
        print(f"Response content: {response.text}")
        return
    except ValueError:
        print("Error: The response is not a valid JSON format.")
        print(f"Response content: {response.text}")
        return

    if data.get('success'):
        rates = data['rates']
        dates = sorted(rates.keys())
        values = [rates[date][target_currency] for date in dates]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, values, marker='o')
        plt.title(f'Exchange Rate History: {base_currency} to {target_currency}')
        plt.xlabel('Date')
        plt.ylabel('Exchange Rate')
        plt.grid(True)
        plt.show()
    else:
        print(f"Error fetching exchange rate history: {data.get('error', 'Unknown error')}")

def currency_conversion(api_key):
    base_currency = input("Introduceți moneda de bază (ex: USD): ").upper()
    if not is_valid_currency(base_currency):
        print("Error: Invalid currency code. Please enter a valid 3-letter currency code.")
        return

    target_currency = input("Introduceți moneda de conversie (ex: EUR): ").upper()
    if not is_valid_currency(target_currency):
        print("Error: Invalid currency code. Please enter a valid 3-letter currency code.")
        return

    try:
        amount = float(input(f"Introduceți suma în {base_currency}: "))
    except ValueError:
        print("Error: Please enter a valid numeric value for the amount.")
        return

    exchange_rate = get_exchange_rate(api_key, base_currency, target_currency)

    if exchange_rate:
        converted_amount = amount * exchange_rate
        print(f"{amount:.2f} {base_currency} = {converted_amount:.2f} {target_currency}")
        return amount, base_currency, target_currency, converted_amount, exchange_rate


def main():
    # Get the API key from either binary or text file
    api_key = get_api_key()
    if not api_key:
        print("Nu s-a putut citi API key-ul. Asigură-te că fișierul binar este disponibil și corect.")
        return

    conversion_results = []

    while True:
        print("\nMeniu principal:")
        print("1. Conversie valutară între două monede")
        print("2. Vizualizare istoricul ratei de schimb")
        print("3. Salvarea rezultatelor într-un fișier CSV")
        print("4. Ieșire din program")

        choice = input("Alegeți o opțiune (1-4): ")

        if choice == '1':
            result = currency_conversion(api_key)
            if result:
                conversion_results.append(result)
                # Log the transaction to a file
                with open("conversion_log.txt", "a") as log_file:
                    log_file.write(
                        f"{result[0]:.2f} {result[1]} to {result[2]}: {result[3]:.2f} (Rate: {result[4]:.4f})\n")

        elif choice == '2':
            base_currency = input("Introduceți moneda de bază pentru istoricul ratei (ex: USD): ").upper()
            if not is_valid_currency(base_currency):
                print("Error: Invalid currency code. Please enter a valid 3-letter currency code.")
                continue

            target_currency = input("Introduceți moneda de conversie pentru istoricul ratei (ex: EUR): ").upper()
            if not is_valid_currency(target_currency):
                print("Error: Invalid currency code. Please enter a valid 3-letter currency code.")
                continue

            plot_exchange_rate_history(api_key, base_currency, target_currency)

        elif choice == '3':
            if conversion_results:
                save_to_csv(conversion_results)
            else:
                print("Nu există rezultate de salvat.")

        elif choice == '4':
            print("Ieșire din program. La revedere!")
            break

        else:
            print("Alegere invalidă. Vă rugăm să selectați o opțiune din meniul principal.")


if __name__ == "__main__":
    main()
