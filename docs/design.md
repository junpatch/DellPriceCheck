# Dell 製品価格スクレイピングシステム 基本設計書

## 1. システムアーキテクチャ

### 1.1 全体構成
```
[フロントエンド]
    Webブラウザ
        ↓
[バックエンド]
    Flask API (AWS Lambda)
        ↓
[スクレイピング]
    Scrapy + Playwright (ECS Fargate)
        ↓
[データストア]
    PostgreSQL (Render.com)
```

### 1.2 コンポーネント構成
```
DELL_PRICE_CHECK
├── api/                    # Webアプリケーション
│   ├── model/             # データモデル
│   ├── routes/            # APIエンドポイント
│   ├── static/            # 静的ファイル
│   └── app.py             # メインアプリケーション
└── scrapers/              # スクレイピングシステム
    ├── dell/              # Dell用スパイダー
    ├── model/             # スクレイピングモデル
    ├── notification/      # LINE通知機能
    └── app.py             # スクレイピング実行
```

## 2. 技術スタック

### 2.1 フロントエンド
- HTML5/CSS3
- JavaScript (Chart.js)
- Bootstrap

### 2.2 バックエンド
- Python 3.11
- Flask
- SQLAlchemy

### 2.3 スクレイピング
- Scrapy
- Playwright

### 2.4 インフラストラクチャ
- AWS ECS (Fargate)
- AWS Lambda
- AWS EventBridge
- Amazon ECR
- PostgreSQL (Render.com)

### 2.5 CI/CD
- GitHub Actions
- Docker
- Zappa

## 3. データベース設計

### 3.1 テーブル構成
```sql
-- 製品情報テーブル
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 価格履歴テーブル
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    price DECIMAL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通知設定テーブル
CREATE TABLE notification_settings (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    line_user_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. API設計

### 4.1 エンドポイント
```
GET /api/products              # 製品一覧取得
GET /api/products/{id}         # 製品詳細取得
GET /api/price-history/{id}    # 価格履歴取得
POST /api/scrape              # スクレイピング実行
POST /api/notifications       # 通知設定更新
```

### 4.2 レスポンス形式
```json
{
    "status": "success",
    "data": {
        // レスポンスデータ
    },
    "message": "処理結果のメッセージ"
}
```

## 5. スクレイピング設計

### 5.1 スクレイピングフロー
1. Playwrightでブラウザを起動
2. Dell製品ページにアクセス
3. 価格情報を抽出
4. データベースに保存
5. 価格変動を検知
6. LINE通知（変動ありの場合）

### 5.2 エラーハンドリング
- 接続エラー時のリトライ
- データ取得失敗時のログ記録
- 異常検知時の管理者通知

## 6. セキュリティ設計

### 6.1 認証・認可
- APIキーによる認証
- ユーザーセッション管理
- アクセス制御

### 6.2 データ保護
- 環境変数による機密情報管理
- データベース接続の暗号化
- バックアップの暗号化

## 7. 監視設計

### 7.1 ログ管理
- アプリケーションログ
- アクセスログ
- エラーログ

### 7.2 メトリクス
- スクレイピング実行時間
- API応答時間
- エラー率
- データベース接続数

## 8. デプロイメント設計

### 8.1 デプロイフロー
1. GitHubへのコードプッシュ
2. GitHub Actionsによるテスト実行
3. Dockerイメージのビルド
4. ECRへのイメージプッシュ
5. ECSタスクの更新

### 8.2 環境変数
```ini
# API環境変数
POSTGRE_USER_NAME=xxxxx
POSTGRE_PASSWORD=xxxxx
POSTGRE_HOST_NAME=xxxxx
POSTGRE_DB_NAME=xxxxx

# スクレイパー環境変数
LINE_ACCESS_TOKEN=xxxxx
POSTGRE_USER_NAME=xxxxx
POSTGRE_PASSWORD=xxxxx
POSTGRE_HOST_NAME=xxxxx
POSTGRE_DB_NAME=xxxxx
``` 