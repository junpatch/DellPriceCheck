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

# Scrapyとその他必要なライブラリをインストール
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps

# アプリケーションのソースコードをコンテナにコピー
# COPY . .

# ユーザーを切り替え
# USER pwuser

ENV DOCKER_ENV=true

# デフォルトのコマンドを指定
CMD ["/bin/bash"]