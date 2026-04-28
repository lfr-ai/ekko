from pathlib import Path
for p in Path('.').rglob('*.toml'):
    try:
        txt = p.read_text(encoding='utf8')
    except Exception:
        continue
    if 'commitizen' in txt:
        print(p)
        print('----')
        print(txt)
        print('====')
