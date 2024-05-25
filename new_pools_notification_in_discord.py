import toloka.client as toloka
from datetime import datetime, timedelta
import logging
import discord
import asyncio
import time
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

#File config
base_dir = os.path.dirname(__file__)
config_path = os.path.join(base_dir, 'config.json')
with open(config_path, 'r') as file:
    config = json.load(file)
api_key = config.get('api_key')
project_id = config.get('project_ids')
discord_token_id = config.get('discord_token_id')
discord_channel_id = config.get('discord_channel_id')

# Ваш токен доступа Толоки
toloka_access_token = api_key

# Список ID проектов, для которых нужно проверять пулы
project_ids = project_id

# Токен доступа для Discord бота
discord_token = discord_token_id

# ID канала, куда бот будет отправлять сообщения
channel_id = discord_channel_id

# Инициализация клиента Толоки
logger.info('Initializing Toloka client.')
toloka_client = toloka.TolokaClient(toloka_access_token, 'PRODUCTION')

# Инициализация клиента Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Функция для получения названия проекта по его ID
def get_project_name(project_id):
    project = toloka_client.get_project(project_id)
    return project.public_name

# Функция для проверки новых пулов для одного проекта
async def check_new_pools(project_id):
    project_name = get_project_name(project_id)
    logger.info('Fetching pools for project ID: %s (%s)', project_id, project_name)
    
    # Поиск пулов с фильтрацией по статусу "OPEN" и project_id
    pools = toloka_client.find_pools(project_id=project_id, status='OPEN')
    new_pools = []

    logger.info('Total open pools found for project %s (%s): %d', project_id, project_name, len(pools.items))

    # Время отсечения - 10 минут назад от текущего времени
    cutoff_time = datetime.utcnow() - timedelta(minutes=5)
    logger.info('Cutoff time for new pools: %s', cutoff_time)

    for pool in pools.items:
        pool_created = pool.created.replace(tzinfo=None)  # Удаление информации о временной зоне
        logger.info('Checking pool ID: %s, created at: %s', pool.id, pool_created)

        # Проверяем, был ли пул создан за последние 10 минут
        if pool_created > cutoff_time:
            logger.info('New pool found: %s', pool.id)
            new_pools.append(pool)
        else:
            logger.info('Pool ID: %s is not new.', pool.id)

    # Оповещение о новых пулах в Discord
    channel = client.get_channel(channel_id)
    if new_pools:
        logger.info('New pools found for project %s (%s):', project_id, project_name)
        for pool in new_pools:
            message = f"Project: {project_name}, New Pool ID: {pool.id}, Pool Name: {pool.private_name}, Created: {pool.created}"
            logger.info(message)
            await channel.send(message)
    else:
        message = f"No new pools found for project {project_name} (ID: {project_id}) in the last 5 minutes."
        logger.info(message)
        # await channel.send(message)

@client.event
async def on_ready():
    logger.info('Logged in as %s', client.user)
    while True:
        for project_id in project_ids:
            await check_new_pools(project_id)
        logger.info('Sleeping for 5 minutes...')
        await asyncio.sleep(300)  # Ждать 5 минут перед следующей проверкой

# Запуск клиента Discord
logger.info('Starting Discord client.')
client.run(discord_token)
logger.info('Pool check completed.')
