from fastapi import FastAPI

# FastAPIの本体を作ります
app = FastAPI()

# 「/」（トップページ）にアクセスしたときの処理
@app.get("/")
def read_root():
    return {"status": "success", "message": "Pythonエンジニアへの第一歩！"}

# 「/items/1」のようにアクセスしたときの処理
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

@app.get("/add")
def add_numbers(a: int, b: int):
    # ここにAtCoderで使うようなロジックを書けます
    result = a + b
    return {"formula": f"{a} + {b}", "result": result}