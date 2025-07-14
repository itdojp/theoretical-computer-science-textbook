# Jekyll 開発環境用 Dockerfile
FROM ruby:3.1-alpine

# 必要なパッケージをインストール
RUN apk add --no-cache \
    build-base \
    git \
    nodejs \
    npm \
    tzdata

# 作業ディレクトリを作成
WORKDIR /app

# Gemfile をコピーして依存関係をインストール
COPY Gemfile Gemfile.lock* ./
RUN bundle install

# package.json をコピーしてNode.js依存関係をインストール
COPY package.json package-lock.json* ./
RUN npm install

# アプリケーションファイルをコピー
COPY . .

# ポート4000を公開
EXPOSE 4000

# 開発サーバーを起動
CMD ["npm", "run", "dev"]