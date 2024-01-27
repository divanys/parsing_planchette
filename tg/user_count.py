import json

def count_unique_keys(json_data):
    unique_keys = set(json_data.keys())
    return len(unique_keys)

file_path = 'pattern_for_user.json'

with open(file_path, 'r') as file:
    json_data = json.load(file)

unique_keys_count = count_unique_keys(json_data)
print(f"Количество уникальных записей: {unique_keys_count}")

