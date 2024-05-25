import gspread
from google.oauth2.service_account import Credentials
import toloka.client as toloka
import pandas as pd
import numpy as np
import logging
import time
from config_agi_pref import API_KEY
from config_agi_pref import DOC_NAME
from config_agi_pref import SKILL_LIST

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройка доступа к Google Sheets
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Имя Google Sheets и листа
spreadsheet_name = DOC_NAME  # Замените на имя вашей таблицы
sheet_name = "New script"  # Замените на имя вашего листа

# Инициализация клиента Толоки
toloka_client = toloka.TolokaClient(
    API_KEY,  # Замените на ваш API ключ
    'PRODUCTION'
)

# Словарь с идентификаторами навыков
skill_ids = SKILL_LIST

def get_and_update_user_skills(df, toloka_client, skill_ids):
    """
    Получает и обновляет навыки пользователей в DataFrame.

    Args:
        df (pd.DataFrame): DataFrame с данными пользователей.
        toloka_client (toloka.TolokaClient): Клиент для взаимодействия с API Толоки.
        skill_ids (dict): Словарь с идентификаторами навыков.

    Returns:
        pd.DataFrame: Обновленный DataFrame.
    """
    logging.info('Updating user skills in DataFrame.')
    updates = {column: [] for column in skill_ids.keys()}

    for i, worker_id in enumerate(df['id']):
        logging.info(f'Fetching skills for user ID: {worker_id}')
        try:
            skills = toloka_client.get_user_skills(user_id=worker_id)
        except toloka.client.exceptions.AccessDeniedApiError as e:
            logging.error(f'Access denied for user ID: {worker_id} - {e}')
            continue
        
        skill_values = {key: None for key in skill_ids.keys()}

        for skill in skills:
            for key, skill_id in skill_ids.items():
                if skill.skill_id == skill_id:
                    skill_values[key] = skill.value

        for key in skill_ids.keys():
            updates[key].append(skill_values[key])

    for key in skill_ids.keys():
        df[key] = updates[key]

    return df

def main():
    try:
        logging.info('Starting the update process.')

        # Настройка доступа к Google Sheets
        logging.info('Setting up Google Sheets access.')
        creds = Credentials.from_service_account_file(r'C:\Users\I\Documents\VS Studio\my project\scripts\All experts skills\credentials.json', scopes=scopes)
        client = gspread.authorize(creds)

        # Открываем Google Sheet по имени
        logging.info(f'Opening Google Sheet with name: {spreadsheet_name}')
        spreadsheet = client.open(spreadsheet_name)

        # Чтение данных из первой вкладки по имени
        logging.info(f'Opening worksheet: {sheet_name}')
        sheet = spreadsheet.worksheet(sheet_name)

        # Чтение данных в DataFrame
        logging.info('Reading data from Google Sheet into DataFrame.')
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Обновление данных в DataFrame
        logging.info('Updating DataFrame with user skills.')
        df = get_and_update_user_skills(df, toloka_client, skill_ids)

        # Обработка значений NaN и бесконечностей
        logging.info('Handling NaN and infinite values in DataFrame.')
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna('', inplace=True)

        # Запись обновленных данных обратно в Google Sheets
        logging.info('Writing updated data back to Google Sheet.')
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

        logging.info('Update process completed successfully.')

    except Exception as e:
        logging.error(f'An error occurred: {e}')

# Вызов функции main для запуска скрипта вручную
if __name__ == "__main__":
    main()
