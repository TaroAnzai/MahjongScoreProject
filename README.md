

---

## 📄 `README.md`

```markdown
# MahjongScoreProject

麻雀大会のスコア集計システム  
フロントエンド（React + Vite）とバックエンド（Flask + Smorest + MySQL）を統合した開発用リポジトリです。

---

## 📂 プロジェクト構成

```

MahjongScoreProject/
├── backend/        # Flask + Smorest API
│   ├── app/
│   ├── migrations/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/       # React (Vite)
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml  # 開発用 (backend + MySQL)
├── .gitignore
└── README.md

````

---

## 🚀 開発環境のセットアップ

### 1. リポジトリのクローン
```bash
git clone git@github.com:TaroAnzai/MahjongScoreProject.git
cd MahjongScoreProject
````

### 2. バックエンド (Flask + MySQL)

```bash
docker-compose up --build
```

* API サーバー: [http://localhost:6000](http://localhost:6000)
* DB (MySQL): localhost:3307

### 3. フロントエンド (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

* フロントエンド: [http://localhost:5173](http://localhost:5173)
* API のエンドポイントは `.env` で設定 (例: `VITE_API_URL=http://localhost:6000`)

---

## 🧪 テスト

* バックエンド: pytest (SQLite in-memory を使用)

```bash
cd backend
pytest
```

* フロントエンド: vitest などを導入予定

---

## 📌 備考

* `.env` ファイルは Git 管理外です（各環境で個別に配置してください）。
* 本番環境では Docker を使わず、Ubuntu 上で **gunicorn + systemd + nginx** により常駐運用します。
* GitHub Actions による自動デプロイ（main → 本番サーバー）を導入予定です。

```


