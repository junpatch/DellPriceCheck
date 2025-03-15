ARG WORK_DIR="/var/task"

# ====== ビルドステージ ======
FROM python:3.11-slim AS builder

ARG WORK_DIR
# # 環境変数を設定（Playwright が Chromium を認識できるように）
ENV PLAYWRIGHT_BROWSERS_PATH="/playwright"

# 作業ディレクトリを設定
WORKDIR ${WORK_DIR}

# # AWS Lambdaランタイムインターフェースエミュレータのinstall
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh ${WORK_DIR}/entry.sh
RUN chmod 755 /usr/bin/aws-lambda-rie ${WORK_DIR}/entry.sh

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

# Scrapyとその他必要なライブラリをインストール
COPY requirements.txt ${WORK_DIR}
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps

COPY . ${WORK_DIR}

# ====== 実行ステージ ======
FROM python:3.11-slim AS final

ARG WORK_DIR

# 作業ディレクトリを設定
WORKDIR ${WORK_DIR}

# 環境変数を設定（Playwright が Chromium を認識できるように）
ENV PLAYWRIGHT_BROWSERS_PATH="/playwright"

# AWS Lambdaランタイムインターフェースエミュレータのinstall
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh ${WORK_DIR}/entry.sh
RUN chmod 755 /usr/bin/aws-lambda-rie ${WORK_DIR}/entry.sh

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

# 作業フォルダ配下をコピー
COPY . ${WORK_DIR}

# Playwright の Chromium バイナリのみコピー
COPY --from=builder /playwright/ /playwright/

# builderでインストールしたパッケージ類をコピー
COPY --from=builder /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/bin/ /usr/bin/
COPY --from=builder /usr/include/ /usr/include/
# COPY --from=builder /etc/ /etc/
# COPY --from=builder /usr/lib64 /usr/lib64

# pipでインストールしたフォルダをコピー
# COPY --from=builder /opt/extensions /opt/extensions
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

ENTRYPOINT [ "/bin/bash", "./entry.sh" ]
CMD [ "lambda_function.handler" ]