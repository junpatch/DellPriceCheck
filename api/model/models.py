from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Products(db.Model):
    __tablename__ = "Products"
    order_code = db.Column(db.String, primary_key=True, nullable=False)
    name = db.Column(db.String)
    model = db.Column(db.String)
    url = db.Column(db.String)
    price = db.Column(db.Integer)
    scraped_at = db.Column(db.DateTime)
    is_line_notification = db.Column(db.Boolean)

class PriceHistory(db.Model):
    __tablename__ = 'PriceHistory'
    id = db.Column(db.Integer, primary_key=True)  # 主キー
    order_code = db.Column(db.String(50), nullable=False)  # 注文コード
    price = db.Column(db.Float, nullable=False)  # 価格
    scraped_at = db.Column(db.DateTime, nullable=False)  # スクレイプ日時
