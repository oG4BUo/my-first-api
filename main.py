from fastapi import FastAPI

import json
import os

# --- 記憶の石（ファイル名） ---
DB_FILE = "users_db.json"

# --- 起動時にファイルを読み込む魔法 ---
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        users_db = json.load(f)
else:
    users_db = {}

# --- データを保存する魔法（関数化しておくと便利） ---
def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users_db, f, indent=4, ensure_ascii=False)

app = FastAPI()
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

#staticフォルダを、ブラウザから見えるように公開する.
app.mount("/static", StaticFiles(directory="static"), name="static") 

@app.get("/panel", response_class=HTMLResponse)
def read_panel():
    #index.htmlの中身を読み取ってブラウザに返す
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/")
def read_root():
    return {"message": "Python修行中! API進化中!"}

#ここからが改善ポイント！
@app.get("/judge/{score}")
def judge_score(score: int):
    #practice.pyで学んだ[if-elif-else]をここに流し込む
    if score >= 80:
        evaluation = "Aランク:天才か！？"
    elif score >= 60:
        evaluation = "Bランク:合格！やるね！"
    else:
        evaluation = "Cランク:不合格。伸びしろしかない！"

    return {
        "score_input": score,
        "result": evaluation,
        "status": "APIが自分で考えて返事をしたぞ！"
    }

# 既存のコードの下に追記
@app.get("/friends")
def get_friends():
    member_list = ["田中", "佐藤", "鈴木", "小田"]
    return {
        "count": len(member_list),
        "all_members": member_list,
        "leader": member_list[0]
    }

db_members = ["田中", "佐藤", "鈴木"]

@app.get("/add/{name}")
def add_member(name: str):
    #名簿に、URLで送られてきた名前を追加する
    db_members.append(name)
    return{
        "message": name + "さんを名簿に追加しました！",
        "current_members": db_members
    }

@app.get("/calc/{mode}/{a}/{b}")
def universal_calculator(mode: str, a: int, b: int):
    #モードによって計算方法を変える
    if mode == "plus":
        result = a + b
        sign = "+"
    elif mode == "minus":
        result = a - b
        sign = "-"
    else:
        #足し算でも引き算でもないとき
        return {"error": "plus か minus を選んでね!"}
    
    return {
        "operation": f"{a} {sign} {b}",
        "answer": result,
        "message": f"{mode}モードで計算しました！"
    }

my_status = {
    "name": "小田",
    "job": "Python見習い魔導士",
    "level": 12,
    "hp": 150,
    "mp": 80,
    "items": ["薬草", "古い杖", "デバッグの書"]
}

@app.get("/levelup")
def level_up():
    my_status["level"] = my_status["level"] + 1
    my_status["hp"] = my_status["hp"] + 10

    #レベル３０になったら、伝説のアイテムをご褒美にあげる
    if my_status["level"] == 30:
        my_status["items"].append("★最強のキーボード")
        message = "レベル30到達! ご褒美をもらったぞ！"
    elif my_status["level"] >= 20:
        my_status["job"] = "Python上級魔導士(プロ)"
        message = "おめでとう！ジョブチェンジしました！"
    else:
        message = "レベルアップしました！"

    return { 
        "message": message,
        "new_level": my_status["level"],
        "current_items": my_status["items"]
    }

@app.get("/register/{name}")
def register_user(name: str):
    #名簿に、その名前を追加する
   new_user = {"name": name, "level": 1, "hp": 100, "job": "見習い", "items": []}
   users_db[name] = new_user #準備した箱に入れる
   save_db() #★ここでセーブ
   return {"message": "登録完了", "user": new_user}

@app.get("/user/{name}")
def get_user_status(name: str):
    #名簿の中に、その名前に人がいるかどうかチェック
    if name in users_db:
        return users_db[name]
    else:
        return {"error": f"{name}さんはまだ登録されていません！ /register/{name}で登録してね"}

@app.get("/getitem/{item_name}")
def get_item(item_name: str):
    #my_status の中の"items"に、新しいアイテムを追加する
    my_status["items"].append(item_name)

    return {
        "message": f"新しいアイテム{item_name}を手に入れた！",
        "all_items": my_status["items"]
    }

@app.get("/levelup/{name}")
def level_up_user(name: str):
    #1,名簿にその人がいるか確認
    if name in users_db:
        #2,レベルを1上げる
        users_db[name]["level"] += 1
        users_db[name]["hp"] += 10 #レベルが上がるとHPも10増える仕様にする
        save_db() #★ここでセーブ
        return {
            "message": f"{name}さんのレベルが上がった！",
            "new_data": users_db[name]
        }
    else:
        return {"error": f"{name}さんはまだ登録されていません！"}

import random

@app.get("/battle/{name1}/{name2}")
def battle(name1: str, name2: str):
    if name1 not in users_db or name2 not in users_db:
        return {"error": "対戦相手が見つかりません"}

    p1_power = (users_db[name1]["level"] * 3) + random.randint(1, 10)
    p2_power = (users_db[name2]["level"] * 3) + random.randint(1, 10)

    if p1_power > p2_power:
        winner, loser = name1, name2
    elif p2_power > p1_power:
        winner, loser = name2, name1
    else:
        return {"result": "互角の戦い！", "p1": name1, "p2": name2}

    # 勝敗が決まった後の処理
    if "薬草" in users_db[loser]["items"]:
        users_db[loser]["items"].remove("薬草")
        message = f"{winner}の勝利！しかし{loser}は「薬草」でレベル減少を防いだ！"
        users_db[winner]["level"] += 1 # 勝者はレベルアップ
    else:
        message = f"{winner}の勝利！{loser}はレベルが下がってしまった..."
        users_db[winner]["level"] += 1
        if users_db[loser]["level"] > 1:
            users_db[loser]["level"] -= 1

    save_db() # 忘れずにセーブ

    return {
        "result": message,
        "p1_status": users_db[name1],
        "p2_status": users_db[name2]
    }

@app.get("/reset/{name}")
def reset_user(name: str):
    if name in users_db:
        users_db[name]["level"] = 1
        users_db[name]["hp"] = 100
        save_db() #忘れずにセーブ
        return {"message": f"{name}を初期状態に戻しました。修行しなおしだ！", "data": users_db[name]}
    return {"error": "ユーザーが見つかりません"}

@app.get("/getitem/{name}/{item_name}")
def get_item(name: str, item_name: str):
    #1, 名簿にその人がいるか確認
    if name in users_db:
        #２．指定された人のitemsに追加する
        users_db[name]["items"].append(item_name)
        save_db() #★ここでセーブ
        return {
            "message": f"{name}が新しいアイテム【{item_name}】を手に入れた！",
            "all_items": users_db[name]["items"]
        }
    return {"error": f"{name}さんはまだ登録されていません!"}