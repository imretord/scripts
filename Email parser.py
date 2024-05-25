import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
import time

popular_pages = [
    "",           # Главная страница
    "career",
    "careers",
    "contact",
    "contacts",
    "about",
    "about-us",
    "team"
]

def get_contact_email(base_url):
    for page in popular_pages:
        url = f"{base_url}/{page}".rstrip('/')
        print(f"Trying URL: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Поиск всех ссылок, содержащих "mailto"
            mailtos = soup.select('a[href^=mailto]')
            emails = [mailto['href'][7:] for mailto in mailtos]
            
            # Если email найден, возвращаем его
            if emails:
                return emails[0]
        except requests.exceptions.RequestException as e:
            print(f"Request error for {url}: {e}")
    
    return "Email not found"

def main(input_file):
    # Загрузка данных из CSV
    data = pd.read_csv(input_file)

    # Проверка наличия необходимых столбцов
    if 'Website' not in data.columns:
        print("CSV file must contain 'Website' column.")
        return

    emails = []
    for index, row in data.iterrows():
        base_url = row['Website'].rstrip('/')
        print(f"Processing {index + 1}/{len(data)}: {base_url}")
        email = get_contact_email(base_url)
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
