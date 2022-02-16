import json
from oracc import config as oracc_config

config = oracc_config

sentences = config["corpus_ctor"]()

with open(r'output/sentences_111.json', 'w', encoding="utf-8") as f:
    f.write('[\n')
    for s in sentences:
        json_str = json.dumps({
            'orig': f'{s[0]}:{s[1]}',
            'context': s[2],
            'clean': s[3],
            'genre': s[4]
        }, indent=2, ensure_ascii=False)
        f.write(json_str)
        f.write(',\n')
    f.write(']\n')