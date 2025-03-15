ARG WORK_DIR="/var/task"

# ====== ビルドステージ ======
FROM python:3.11-slim AS builder

ARG WORK_DIR

# 作業ディレクトリを設定
WORKDIR ${WORK_DIR}

# # AWS Lambdaランタイムインターフェースエミュレータのinstall
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entry.sh ${WORK_DIR}
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
# FROM python:3.11-slim AS final

# # 作業ディレクトリを設定
# WORKDIR /var/task

# # AWS Lambdaランタイムインターフェースエミュレータのinstall
# ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
# COPY entry.sh "/entry.sh"
# RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh

# # RUN yum update -y && yum install -y \
# #     gcc \
# #     libffi-devel \
# #     openssl-devel \
# #     postgresql-devel \
# #     make \
# #     bash \
# #     curl \
# #     && yum clean all

# # 仮想環境の必要なファイルだけコピー
# COPY --from=builder /var/task/venv /var/task/venv

# # Playwright の Chromium バイナリのみコピー
# COPY --from=builder /root/.cache/ms-playwright/ /root/.cache/ms-playwright/
# # 環境変数を設定（Playwright が Chromium を認識できるように）
# ENV PLAYWRIGHT_BROWSERS_PATH="/root/.cache/ms-playwright"

# # builderでインストールしたパッケージ類をコピー
# COPY --from=builder /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
# COPY --from=builder /usr/bin/ /usr/bin/
# COPY --from=builder /usr/include/ /usr/include/
# # COPY --from=builder /etc/ /etc/
# # COPY --from=builder /usr/lib64 /usr/lib64

# ENV DOCKER_ENV=true

# # コンテナのポート5000を公開
# EXPOSE 5001

# # デフォルトのコマンドを指定
# # CMD ["/bin/bash", "-c", "source /scrapers/venv/bin/activate && playwright install --with-deps && bash"]
# # CMD ["/bin/bash"]

# # Set runtime interface client as default command for the container runtime
# ENTRYPOINT [ "/var/task/venv/bin/python", "-m", "awslambdaric" ]
# # Lambdaハンドラーを指定
# CMD ["app.lambda_handler"]

ENTRYPOINT [ "/bin/bash", "./entry.sh" ]
CMD [ "lambda_function.handler" ]