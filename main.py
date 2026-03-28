from fastapi import FastAPI

app = FastAPI()

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