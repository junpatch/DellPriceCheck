# ベースイメージとして公式のPythonイメージを使用
FROM python:3.13 AS base

# 作業ディレクトリを設定
WORKDIR /api

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ローカルのrequirements.txtをコンテナにコピー
COPY requirements.txt .

# Pythonの依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコンテナにコピー
COPY . .

# 環境変数の設定（Flaskアプリを起動するため）
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# コンテナのポート5000を公開
EXPOSE 5000

# Flaskアプリケーションを起動
# CMD ["flask", "run"]
CMD ["/bin/bash"]
# Flaskアプリケーションを起動（本番用）
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]