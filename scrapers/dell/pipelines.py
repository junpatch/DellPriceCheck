# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

from datetime import datetime
from dotenv import load_dotenv
import pytz
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import models
from notification.line_notifier import LineNotifier


# 定数
load_dotenv()

if os.environ.get("ENV") == "local":
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.getcwd(), 'instance', 'dell_laptop.db')}"
else:
    USER_NAME = os.environ.get('POSTGRE_USER_NAME')
    PASSWORD = os.environ.get('POSTGRE_PASSWORD')
    HOST_NAME = os.environ.get('POSTGRE_HOST_NAME')
    DB_NAME = os.environ.get('POSTGRE_DB_NAME')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{USER_NAME}:{PASSWORD}@{HOST_NAME}.oregon-postgres.render.com/{DB_NAME}?sslmode=require"
DEFAULT_PRICE = 0  # 既存価格がない場合のデフォルト値


class SQLAlchemyPipeline:
    def __init__(self):
        self.updated_count = 0

    def open_spider(self, spider) -> None:
        """データベース接続を初期化し、テーブルを作成する。"""
        self.engine = create_engine(SQLALCHEMY_DATABASE_URI)
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.notifier = LineNotifier()

    def process_item(self, item: dict, spider) -> dict:
        """アイテムを処理してデータベースに保存する。"""
        current_time = datetime.now(pytz.timezone('Asia/Tokyo'))
        old_price = self._get_price_last_scraped(item)
        new_price = item.get('price')

        # データベースに商品と価格履歴を保存
        self._save_product_and_history(item, current_time, spider)

        # 価格が変更された場合、かつ通知設定ONの場合、LINE通知を送信
        if new_price != old_price and self._get_line_notification_status(item):
            self._send_notification(item, old_price, new_price)

        return item

    def close_spider(self, spider) -> None:
        """データベースセッションと接続を終了する。"""
        self.session.close()
        print(self.updated_count, end="")

    def _save_product_and_history(self, item: dict, current_time: datetime, spider) -> None:
        """データベースに商品データと価格履歴を保存する。"""
        try:
            product = self._create_product(item, current_time)
            self.session.merge(product)
            self.session.commit() # PriceHistoryでForeign Keyが見つからないのでそれぞれcommit

            price_history = self._create_price_history(item, current_time)
            self.session.add(price_history)
            self.session.commit()

            spider.logger.info(f"DB登録成功: {product.order_code}")
            self.updated_count += 1
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"DB登録失敗: {item.get('order_code')}): {e}", exc_info=True)
            raise DropItem(f"{item.get('order_code')}の処理を中止します: {e}")

    def _create_product(self, item: dict, current_time: datetime) -> models.Products:
        """アイテムから Product オブジェクトを作成する。"""
        return models.Products(
            order_code=item.get('order_code'),
            name=item.get('name'),
            model=item.get('model'),
            url=item.get('url'),
            price=item.get('price'),
            scraped_at=current_time,
            # TODO: 既存の設定を上書きしてFalseにしてしまう。一旦定義なしにするが、既存の設定を保持する仕組みにしたい
            # is_line_notification=False
        )

    def _create_price_history(self, item: dict, current_time: datetime) -> models.PriceHistory:
        """アイテムから PriceHistory オブジェクトを作成する。"""
        return models.PriceHistory(
            order_code=item.get('order_code'),
            price=item.get('price'),
            scraped_at=current_time
        )

    def _get_price_last_scraped(self, item: dict) -> int:
        """指定されたアイテムの以前の価格を取得する。"""
        existing_product = self.session.query(models.Products).filter_by(
            order_code=item.get('order_code')
        ).first()
        return existing_product.price if existing_product else DEFAULT_PRICE

    def _send_notification(self, item: dict, old_price: int, new_price: int) -> None:
        """価格変更に関する通知を送信する。"""
        self.notifier.send_notifications(
            name=item.get('name'),
            model=item.get('model'),
            old_price=old_price,
            new_price=new_price,
            url=item.get('url')
        )

    def _get_line_notification_status(self, item: dict) -> bool:
        product = self.session.query(models.Products).filter_by(
            order_code=item.get('order_code')
        ).first()
        return product.is_line_notification if product else False
