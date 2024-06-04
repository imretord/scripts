import pandas as pd
import requests
import sys
import time


API_KEY = 'your_hunter_io_api_key'

def get_contact_email(domain):
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        emails = [email['value'] for email in data.get('data', {}).get('emails', [])]
        
        # Если email найден, возвращаем его
        return emails[0] if emails else "Email not found"
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"

def main(input_file):
    # Загрузка данных из CSV
    data = pd.read_csv(input_file)

    # Проверка наличия необходимых столбцов
    if 'Website' not in data.columns:
        print("CSV file must contain 'Website' column.")
        return

    emails = []
    for index, row in data.iterrows():
        website = row['Website'].rstrip('/')
        domain = website.replace('http://', '').replace('https://', '').split('/')[0]
        print(f"Processing {index + 1}/{len(data)}: {domain}")
        email = get_contact_email(domain)
        emails.append(email)
        print(f"Found email: {email}")
        time.sleep(1)  # Задержка между запросами для предотвращения блокировки

    # Добавление email-адресов в DataFrame
    data['Contact Email'] = emails

    # Сохранение обновленного DataFrame в новый CSV файл
    output_file = input_file.replace(".csv", "_with_emails.csv")
    data.to_csv(output_file, index=False)
    print(f"Updated file saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_csv_file>")
    else:
        input_file = sys.argv[1]
        main(input_file)
