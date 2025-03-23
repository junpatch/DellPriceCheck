# Dell 製品価格スクレイピングシステム 詳細設計書

## 1. コンポーネント詳細設計

### 1.1 APIサーバー（Flask）
#### クラス構成
```python
class ProductController:
    def get_products()      # 製品一覧取得
    def get_product(id)     # 製品詳細取得
    def get_price_history(id) # 価格履歴取得
    
class ScrapingController:
    def trigger_scraping()  # スクレイピング実行
    def get_status()       # 実行状況取得
    
class NotificationController:
    def update_settings()   # 通知設定更新
    def send_notification() # LINE通知送信
```

#### データモデル
```python
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    price_history = db.relationship('PriceHistory', backref='product')

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    price = db.Column(db.Decimal)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 1.2 スクレイピングシステム
#### クラス構成
```python
class DellSpider(scrapy.Spider):
    def parse()           # メインページ解析
    def parse_product()   # 製品ページ解析
    
class PriceExtractor:
    def extract_price()   # 価格情報抽出
    def validate_price()  # 価格データ検証
    
class DatabaseManager:
    def save_price()      # 価格保存
    def check_changes()   # 価格変動確認
```

## 2. シーケンス図

### 2.1 スクレイピング実行フロー
```
[API] → [ECS Task] → [Spider] → [Price Extractor] → [DB] → [Notification]
  ↑          |           |            |               |          |
  |          |           |            |               |          |
  └──────────┴───────────┴────────────┴───────────────┴──────────┘
```

### 2.2 通知処理フロー
```
[DB] → [Price Change Detection] → [Notification Service] → [LINE API]
  ↑              |                         |                    |
  |              |                         |                    |
  └──────────────┴─────────────────────────┴────────────────────┘
```

## 3. データベース詳細設計

### 3.1 インデックス設定
```sql
-- 価格履歴の検索効率化
CREATE INDEX idx_price_history_product_id ON price_history(product_id);
CREATE INDEX idx_price_history_recorded_at ON price_history(recorded_at);

-- 製品検索の効率化
CREATE INDEX idx_products_name ON products(name);
```

### 3.2 パーティション設計
```sql
-- 価格履歴テーブルの月次パーティション
CREATE TABLE price_history_partitioned (
    LIKE price_history INCLUDING ALL
) PARTITION BY RANGE (recorded_at);

-- 月次パーティションの作成
CREATE TABLE price_history_y2024m01 
    PARTITION OF price_history_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## 4. エラーハンドリング

### 4.1 スクレイピングエラー
```python
class ScrapingError(Exception):
    def __init__(self, message, retry_count=0):
        self.message = message
        self.retry_count = retry_count

def handle_scraping_error(error):
    if error.retry_count < MAX_RETRIES:
        time.sleep(RETRY_DELAY)
        return retry_scraping()
    else:
        notify_admin(error)
        log_error(error)
```

### 4.2 データベースエラー
```python
class DatabaseError(Exception):
    def __init__(self, operation, details):
        self.operation = operation
        self.details = details

def handle_db_error(error):
    log_error(error)
    rollback_transaction()
    notify_admin(error)
```

## 5. パフォーマンス最適化

### 5.1 キャッシュ戦略
- Redisを使用した価格データのキャッシュ
- キャッシュ有効期限：1時間
- キャッシュ更新トリガー：価格変動時

### 5.2 データベース最適化
- 定期的なVACUUM実行
- 統計情報の更新
- クエリの最適化

### 5.3 スクレイピング最適化
- 並列処理による複数製品の同時スクレイピング
- リクエスト間隔の最適化
- プロキシの活用 