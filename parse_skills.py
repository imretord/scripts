import toloka.client as toloka
import pandas as pd

def get_skill_value(skills, skill_id):
    skill = next((s for s in skills if s.skill_id == skill_id), None)
    return skill.value if skill else None

def update_skills(row, toloka_client, skill_ids):
    skills = toloka_client.get_user_skills(user_id=row['ID'])
    for skill_name, skill_id in skill_ids.items():
        row[skill_name] = get_skill_value(skills, skill_id)
    return row

def main():
    
    toloka_client = toloka.TolokaClient('API_KEY', 'PRODUCTION')
    skill_ids = {
        'gp-agi-validations-last-hidden': '131416',
        'web-query-rel-exp-exam': '128781',
        'web-query-rel-exp-train': '125757',
        'choose-best-answer': '116284',
        'delivery-hero-exam': '123270'
    }
    
    # Чтение данных
    df = pd.read_excel('for scripts.xlsx')

    # Обновление навыков
    df = df.apply(update_skills, axis=1, args=(toloka_client, skill_ids))

    # Сохранение данных
    df.to_excel('for scripts.xlsx', index=False)

if __name__ == "__main__":
    main()