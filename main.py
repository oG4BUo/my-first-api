from fastapi import FastAPI
from datetime import datetime

import json
import os
import random
import asyncio
import time

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

@app.get("/battle/{name}/{enemy}")
def battle(name: str, enemy: str):
    user = users_db.get(name)
    # ★魔導書を持っているかチェック
    has_grimoire = "✨伝説の魔導書" in user["items"]

    if has_grimoire:
        #魔導書の力で絶対勝つ
        win = True
        message = f"【覚醒】{name}は伝説の魔導書を開いた！圧倒的な魔力が{enemy}を包み込む！"
    else:
        win = random.choice([True, False])
        message = f"{name}は{enemy}と戦った！"

    if win:
        user["level"] += 5
        result = f"{message}\n勝利! レベルが５上がった！"
    else:
        user["level"] -= 1
        result = f"{message}\n敗北...レベルが１下がった。"

    save_db() #★ここでセーブ
    return {"result": result}

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

@app.get("/ranking")
def get_ranking():
    #1. 辞書からユーザーのリストを取り出す
    users_list = list(users_db.values())

    #2. レベルが高い順に並び変える
    #lambdaを使ってlevelを基準にソートする
    sorted_users = sorted(users_list, key=lambda x: x["level"], reverse=True)

    return sorted_users

@app.get("/quest/{name}")
async def start_quest(name: str):
    if name not in users_db:
        return {"error": "登録されていません"}
    
    user = users_db[name] # 短く書くために変数に入れます

    # --- ✨【修行ポイント】魔力チェックの門番 ---
    # まだMPが登録されていない場合や、20未満の場合はここで終了
    if user.get("mp", 0) < 20:
        return {
            "message": f"魔力が足りません！現在【{user.get('mp', 0)}】です。最低20必要です。",
            "new_data": user
        }

    # 条件をクリアしたら、先にMPを20消費して保存する
    user["mp"] -= 20
    save_db() 
    # ------------------------------------------

    if "luck_stack" not in user:
        user["luck_stack"] = 0

    # ここから先の5秒待ちやアイテム抽選は、MPがある人だけが通れる聖域
    await asyncio.sleep(5)
    
    found_item = "なし" 
    luck = random.randint(1, 100)
    bonus = user["luck_stack"]
    
    if (luck + bonus) > 95:
        found_item = "✨伝説の魔導書"
        user["luck_stack"] = 0 
    elif (luck + bonus) > 70:
        found_item = "銀の鍵"
        user["luck_stack"] = 0
    else:
        user["luck_stack"] += 5 
        message = f"何も見つからなかった...（現在、徳が {user['luck_stack']} 溜まっている）"

    if found_item != "なし":
        user["items"].append(found_item)
        message = f"探索完了！【{found_item}】を見つけた！（運ボーナス {bonus} 使用）"

    user["level"] += 1
    save_db()
    
    return {"message": message, "new_data": user}

@app.get("/craft/{name}")
def craft_item(name: str):
    user = users_db.get(name)
    items = user["items"]

    # 錬成のレシピ：　薬草　＋　銀の鍵
    if "薬草" in items and "銀の鍵" in items:
        #アイテムを消費する
        items.remove("薬草")
        items.remove("銀の鍵")
        
        #新しい強力なアイテムを付与
        new_item = "💎賢者の石"
        items.append(new_item)

        user["level"] += 10
        save_db()
        return {"message": f"錬成成功! 【{new_item}】が誕生し、レベルが10上がった!"}
    else:
        return{"message": "材料（薬草と銀の鍵）が足りません..."}
    
@app.get("/user/{name}")
def get_user(name: str):
    if name not in users_db:
        return {"error": "NotFound"}
    
    user = users_db[name]
    now = time.time()
    
    # --- ✨ ここで最大MPを再計算！ ---
    # レベルを取り出して計算（レベルがなければ1とする）
    level = user.get("level", 1)
    # --- ✨【称号進化システム】レベルに応じてジョブを書き換える ---
    lvl = user.get("level", 1)
    if lvl >= 30:
        user["job"] = "伝説の賢者"
    elif lvl >= 20:
        user["job"] = "大魔導士"
    elif lvl >= 10:
        user["job"] = "熟練魔導士"
    elif lvl >= 5:
        user["job"] = "一人前の魔導士"
    else:
        user["job"] = "魔導士の見習い"
    max_mp = 100 + (level * 10)
    
    # 計算した最大値をデータに覚えさせる
    user["max_mp"] = max_mp
    # -------------------------------

    last_seen = user.get("last_seen", now)
    wait_time = int(now - last_seen)
    items = user.get("items", [])
    book_count = items.count("✨伝説の魔導書")
    level = user.get("level", 1)

    if level >= 10 and book_count >= 3:
        user["is_clear"] = True
    else:
        user["is_clear"] = False
    
    if "mp" not in user:
        user["mp"] = 0
    
    # 回復処理（100固定ではなく max_mp を使う）
    recovery = wait_time // 10
    if recovery > 0:
        user["mp"] = min(max_mp, user["mp"] + recovery)
        user["last_seen"] = now
        save_db() # 変更を保存！
        
    return user

@app.get("/ultimate/{name}")
def ultimate_magic(name: str):

    if name not in users_db:
        return {"error": "NotFound"}
    
    user = users_db[name]

    #魔力が満タンの時だけ発動できる
    if user.get("mp", 0) < 100:
        return {"message": "魔力が足りません! 極限までためてください！"}
    
    #魔力をすべて解き放つ！
    user["mp"] = 0
    user["level"] += 3
    save_db()

    return {
        "message": "【極・究極魔法】を発動! レベルが3上がった!",
        "new_data": user
    }

@app.get("/create_item/{name}")
def create_item(name: str):
    if name not in users_db:
        return {"error": "NotFound"}
    
    user = users_db[name]
    
    # 【チェック】MPが30以上あるか？
    if user.get("mp", 0) < 30:
        return {"message": "魔力が足りません！(30必要です)", "new_data": user}
    
    # 【代償】MPを30消費
    user["mp"] -= 30
    
    # 【錬成】ランダムでアイテムを1つ生成
    new_item = random.choice(["薬草", "銀の鍵", "不思議な粉"])
    user["items"].append(new_item)
    
    save_db() # 忘れずにセーブ！
    
    return {
        "message": f"魔力を練り上げ、新たに【{new_item}】を錬成した！",
        "new_data": user
    }

@app.get("/use_item/{name}")
def use_item(name: str):
    if name not in users_db:
        return {"error": "NotFound"}
    
    user = users_db[name]
    items = user.get("items", [])

    # 【チェック】薬草を持っているか？
    if "薬草" not in items:
        return {"message": "薬草を持っていません！", "new_data": user}

    # 【最大MPの確認】
    max_mp = user.get("max_mp", 100)
    if user["mp"] >= max_mp:
        return {"message": "魔力はすでに満タンです！", "new_data": user}

    # 【使用処理】薬草をリストから1つ消す
    items.remove("薬草")
    
    # 【回復】MPを30回復（最大値を超えないように）
    user["mp"] = min(max_mp, user["mp"] + 30)
    
    save_db()
    
    return {
        "message": "薬草を煎じて飲んだ！魔力が30回復したぞ！",
        "new_data": user
    }

