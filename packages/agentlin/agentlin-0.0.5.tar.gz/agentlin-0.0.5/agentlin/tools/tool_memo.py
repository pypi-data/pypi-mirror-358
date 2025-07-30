import json

memo: dict[str, str] = {}

def ReadMemo():
    print(json.dumps(memo, indent=2, ensure_ascii=False))
    return memo
