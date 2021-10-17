# encoding: utf-8
from pathlib import Path

import pandas as pd
import json
import urllib.request

json_path = '../files/resources'
lmd_by_tier = {5: 400, 4: 300, 3: 200, 2: 100, 1: 0}


def dict_to_recipe_list(recipe: dict, tier: int):
    return [{"name": name, "quantity": quantity} for name, quantity in recipe.items()]


with urllib.request.urlopen("https://raw.githubusercontent.com/Aceship/AN-EN-Tags/master/json/akmaterial.json") as url:
    data = json.loads(url.read().decode())


df = pd.DataFrame.from_dict(data)
df = df[['name_cn', 'name_en', 'level', 'madeof', 'source']]
translation_table = df.set_index('name_cn')['name_en'].to_dict()
translation_table['晶体电子单元'] = 'Crystalline Electronic Unit'
df['lmd'] = df.apply(lambda row: lmd_by_tier[row['level']], axis=1)
df['droppable'] = df.apply(lambda row: True if len(row.source) > 0 else False, axis=1)
df['name'] = df.apply(lambda row: translation_table[row.name_cn], axis=1)
df.madeof = df.apply(lambda row: {translation_table[key]: value for key, value in row.madeof.items()}, axis=1)
df.madeof = df.apply(lambda row: dict_to_recipe_list(row.madeof, row.level), axis=1)
df = df[['name', 'level', 'droppable', 'lmd', 'madeof']]
df.rename(columns={'madeof': 'recipe', 'level': 'tier'}, inplace=True)

for resource in df.to_dict('records'):
    path = f"{json_path}/tier{resource['tier']}/{resource['name']}.json"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing Resources data: {resource['name']}.")
    with open(path, 'w+', encoding='utf-8') as f:
        json.dump(resource, f, indent=4)

print("Done.")
