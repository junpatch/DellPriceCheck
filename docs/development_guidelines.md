# Dell 製品価格スクレイピングシステム 開発ガイドライン

## 1. コーディング規約

### 1.1 Python コーディング規約
- PEP 8に準拠
- 行の最大長は100文字
- インデントは4スペース
- クラス名はPascalCase
- メソッド名と変数名はsnake_case
- 定数は大文字のSNAKE_CASE

### 1.2 コメント規約
```python
class PriceExtractor:
    """価格情報を抽出するクラス
    
    Attributes:
        retry_count (int): リトライ回数
        timeout (int): タイムアウト秒数
    """
    
    def extract_price(self, html: str) -> float:
        """HTMLから価格情報を抽出する
        
        Args:
            html (str): 解析対象のHTML
            
        Returns:
            float: 抽出された価格
            
        Raises:
            PriceExtractionError: 価格抽出に失敗した場合
        """
        pass
```

## 2. Gitブランチモデル

### 2.1 ブランチ命名規則
- メインブランチ: `main`
- 開発ブランチ: `develop`
- 機能ブランチ: `feature/機能名`
- バグ修正: `fix/バグ内容`
- リリース: `release/バージョン番号`

### 2.2 コミットメッセージ規約
```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
style: コードスタイル修正
refactor: リファクタリング
test: テストコード追加・修正
chore: ビルド・補助ツール更新
```

## 3. PRレビュー基準

### 3.1 レビュー項目
- [ ] コーディング規約に準拠しているか
- [ ] 適切なテストが追加されているか
- [ ] セキュリティ上の問題がないか
- [ ] パフォーマンスへの影響は考慮されているか
- [ ] ドキュメントが更新されているか

### 3.2 PRテンプレート
```markdown
## 変更内容
- 変更点1
- 変更点2

## テスト内容
- [ ] テスト項目1
- [ ] テスト項目2

## レビューポイント
- レビューして欲しい点1
- レビューして欲しい点2
```

## 4. 環境構築手順

### 4.1 ローカル開発環境
```bash
# リポジトリのクローン
git clone https://github.com/your-repo/dell-price-check.git
cd dell-price-check

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な値を設定

# データベースのセットアップ
flask db upgrade

# 開発サーバーの起動
flask run
```

### 4.2 Dockerを使用した開発
```bash
# コンテナのビルドと起動
docker-compose up --build

# テストの実行
docker-compose run api pytest

# データベースマイグレーション
docker-compose run api flask db upgrade
```

## 5. デプロイメントフロー

### 5.1 本番環境へのデプロイ手順
1. developブランチの最新コードをpull
2. releaseブランチを作成
3. バージョン番号を更新
4. テストを実行
5. mainブランチにマージ
6. タグを作成
7. GitHub Actionsによる自動デプロイ

### 5.2 デプロイ後の確認項目
- [ ] アプリケーションが正常に起動しているか
- [ ] データベースマイグレーションが成功しているか
- [ ] ログが正常に出力されているか
- [ ] 監視システムが正常に動作しているか

## 6. テストガイドライン

### 6.1 単体テスト
- テストファイル名: `test_*.py`
- テストクラス名: `Test*`
- テストメソッド名: `test_*`
- テストカバレッジ: 80%以上

### 6.2 テストデータ
- テストデータは`tests/fixtures`に配置
- 機密情報は環境変数で管理
- テストデータは最小限に抑える

### 6.3 テスト実行
```bash
# 全テストの実行
pytest

# 特定のテストファイルの実行
pytest tests/test_price_extractor.py

# カバレッジレポートの生成
pytest --cov=app tests/
``` 