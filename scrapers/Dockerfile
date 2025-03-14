# ====== ビルドステージ ======
FROM python:3.11-slim AS builder

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

RUN python -m venv ./venv \
    && ./venv/bin/pip install --upgrade pip

# Scrapyとその他必要なライブラリをインストール
COPY requirements.txt .
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt
RUN ./venv/bin/playwright install chromium --with-deps


# ====== 実行ステージ ======
FROM python:3.11-slim AS final

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

# 仮想環境の必要なファイルだけコピー
COPY --from=builder /scrapers/venv /scrapers/venv

# Playwright の Chromium バイナリのみコピー
COPY --from=builder /root/.cache/ms-playwright/ /root/.cache/ms-playwright/
# 環境変数を設定（Playwright が Chromium を認識できるように）
ENV PLAYWRIGHT_BROWSERS_PATH="/root/.cache/ms-playwright"

# builderでインストールしたパッケージ類をコピー
COPY --from=builder /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/bin/ /usr/bin/
COPY --from=builder /usr/include/ /usr/include/
COPY --from=builder /etc/ /etc/

ENV DOCKER_ENV=true

# コンテナのポート5000を公開
EXPOSE 5001

# デフォルトのコマンドを指定
# CMD ["/bin/bash", "-c", "source /scrapers/venv/bin/activate && playwright install --with-deps && bash"]
CMD ["/bin/bash"]