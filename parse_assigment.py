import toloka.client as toloka
import requests
import json
import pandas as pd

def get_api_key():
    return 'api_key'

def get_toloka_client():
    api_key = get_api_key()
    return toloka.TolokaClient(api_key, 'PRODUCTION')

def get_headers(api_key):
    return {'Authorization': f'ApiKey {api_key}'}

def get_assignment_details(assignment_id, headers):
    url = f"https://toloka.dev/api/v1/assignments/{assignment_id}"
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

def safe_extract(data, path):
    try:
        for key in path:
            data = data[key]
        return data
    except KeyError:
        return ''

def process_assignments(assignments, headers):
    results = []
    for assignment in assignments:
        details = get_assignment_details(assignment.id, headers)
        new_row = {f'INPUT:{key}': safe_extract(details, ['tasks', 0, 'input_values', key]) for key in 
                   ['id', 'log', 'chat', 'skip', 'domain', 'length', 'source', 'comment', 'prompts', 'seed_id', 'ambiguity', 
                    'iteration', 'structure', 'subdomain', 'worker_id', 'assignment_id', 'technical_info', 'prompt_category']}
        new_row['GOLDEN:result'] = safe_extract(details, ['solutions', 0, 'output_values', 'verdict'])
        results.append(new_row)
    return results

def main():
    client = get_toloka_client()
    api_key = get_api_key()
    headers = get_headers(api_key)
    assignments = client.get_assignments(pool_id='42900748')
    results = process_assignments(assignments, headers)
    results_df = pd.DataFrame(results)
    existing_df = pd.read_excel('results.xlsx')
    updated_df = pd.concat([existing_df, results_df], ignore_index=True)
    updated_df.to_excel('results.xlsx', index=False)

if __name__ == "__main__":
    main()