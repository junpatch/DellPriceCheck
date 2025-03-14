# ベースイメージとして公式のPythonイメージを使用
FROM python:3.12-slim AS base

# 作業ディレクトリを設定
WORKDIR /workspace

# 必要なパッケージをインストールして、python仮想環境をセットアップ
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    bash \
    curl \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws
    

RUN python -m venv /workspace/.venv \
    && /workspace/.venv/bin/pip install --upgrade pip

# ローカルのrequirements.txtをコンテナにコピー
COPY requirements.txt .

# Pythonの依存関係をインストール
RUN /workspace/.venv/bin/pip install --no-cache-dir -r /workspace/requirements.txt

# アプリケーションのソースコードをコンテナにコピー
COPY . .

# 環境変数の設定（Flaskアプリを起動するため）
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PATH="/workspace/.venv/bin:$PATH"

# コンテナのポート5000を公開
EXPOSE 5000

# Flaskアプリケーションを起動
# CMD ["flask", "run"]
CMD ["/bin/bash", "-c", "source /workspace/.venv/bin/activate && bash"]
# CMD ["/bin/bash", "-c", "source /workspace/.venv/bin/activate && flask run --host=0.0.0.0 --port=5000"]
# Flaskアプリケーションを起動（本番用）
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]