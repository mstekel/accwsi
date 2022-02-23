import json
from oracc import config as oracc_config

config = oracc_config

sentences = config["corpus_ctor"]()

with open(r'output/sentences.json', 'w', encoding="utf-8") as f:
    f.write('[\n')
    for s in sentences:
        json_str = json.dumps({
            'orig': f'{s[0]}:{s[1]}',
            'context': s[2],
            'clean': s[3],
            'sense': s[4],
            'genre': s[5]
        }, indent=2, ensure_ascii=False)
        f.write(json_str)
        f.write(',\n')
    # remove the trailing comma
    f.seek(f.tell() - 1)
    f.write(']\n')