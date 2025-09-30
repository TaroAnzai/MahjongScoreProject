FROM node:20-slim

WORKDIR /app

# パッケージをインストール
COPY package*.json ./
RUN npm install

# ソースコードをコピー
COPY . .

# 開発サーバー起動
CMD ["npm", "run", "dev"]
