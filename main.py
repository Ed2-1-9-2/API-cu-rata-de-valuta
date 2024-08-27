import requests
import sys


def read_api_key(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: 'api_key.txt' not found. Please provide a valid API key file.")
        sys.exit(1)


def get_exchange_rate(api_key, base_currency, target_currency):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"
    response = requests.get(url)

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error: The response is not a valid JSON format.")
        return None

    if data.get('result') == 'success':
        return data['conversion_rate']
    else:
        print(f"Error fetching exchange rate: {data.get('error-type', 'Unknown error')}")
        return None


def is_valid_currency(currency):
    return len(currency) == 3 and currency.isalpha()


def main():
    api_key = read_api_key("api_key.txt")

    while True:
        base_currency = input("Introduceți moneda de bază (ex: USD): ").upper()
        if not is_valid_currency(base_currency):
            print("Error: Invalid currency code. Please enter a valid 3-letter currency code.")
            continue

        target_currency = input("Introduceți moneda de conversie (ex: EUR): ").upper()
        if not is_valid_currency(target_currency):
            print("Error: Invalid currency code. Please enter a valid 3-letter currency code.")
            continue

        try:
            amount = float(input(f"Introduceți suma în {base_currency}: "))
        except ValueError:
            print("Error: Please enter a valid numeric value for the amount.")
            continue

        exchange_rate = get_exchange_rate(api_key, base_currency, target_currency)

        if exchange_rate:
            converted_amount = amount * exchange_rate
            print(f"{amount:.2f} {base_currency} = {converted_amount:.2f} {target_currency}")
            with open("conversion_log.txt", "a") as log_file:
                log_file.write(
                    f"{amount:.2f} {base_currency} to {target_currency}: {converted_amount:.2f} (Rate: {exchange_rate:.4f})\n")

        if input("Doriți să efectuați o altă conversie? (y/n): ").lower() != 'y':
            break


if __name__ == "__main__":
    main()
