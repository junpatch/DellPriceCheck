# ベースイメージとして公式のPythonイメージを使用
FROM python:3.11-slim AS base

# 作業ディレクトリを設定
WORKDIR /scrapers

# 必要なパッケージをインストールして、python仮想環境をセットアップ
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    build-essential \
    bash \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# RUN python -m venv /scrapers/.venv \
#     && /scrapers/.venv/bin/pip install --upgrade pip

# `pwuser` を追加（スクレイピング用のセキュリティ対策）
# RUN adduser --disabled-password --gecos "" pwuser

RUN python -m venv ./venv \
    && ./venv/bin/pip install --upgrade pip

# Scrapyとその他必要なライブラリをインストール
COPY requirements.txt .
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt
    # && source ./venv/bin/activate 
    # && playwright install --with-deps

# アプリケーションのソースコードをコンテナにコピー
# COPY . .

# ユーザーを切り替え
# USER pwuser

ENV DOCKER_ENV=true

# コンテナのポート5000を公開
EXPOSE 5001

# デフォルトのコマンドを指定
CMD ["/bin/bash", "-c", "source /scrapers/venv/bin/activate && playwright install --with-deps && bash"]