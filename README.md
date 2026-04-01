# 🧙‍♂️ 魔導士ギルド管理システム

レベルを上げ、魔力を錬成し、伝説の魔導書を集めて世界を救うRPG風管理システムです。

## 🚀 機能
- **ステータス管理**: レベルに応じた最大MPの自動計算
- **アイテムシステム**: 薬草の採取・錬成・使用によるMP回復
- **進化システム**: レベルに応じた称号とオーラの変化
- **エンディング**: 特定条件達成によるクリア演出

## 🛠 使用技術
- **Backend**: Python (FastAPI)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: JSON (ローカル保存)

## 🏃 起動方法
1. 必要ライブラリのインストール: `pip install -r requirements.txt`
2. サーバー起動: `uvicorn main:app --reload`