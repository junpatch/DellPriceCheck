# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join

# 定数の定義
PRICE_SUFFIX = '円'


# order_codeを抽出するための関数
def extract_order_code(url):
    """URLの中から注文コードを抽出する"""
    match = re.search(r'/([^/]+)\?ref', url)
    if match:
        return match.group(1)  # 抽出した注文コードを返す
    return url  # マッチしなかった場合はそのまま返す

# 価格をパースするユーティリティ関数
def parse_price(price):
    """価格から通貨記号とカンマを除去し、整数型に変換する"""
    return int(price.replace(PRICE_SUFFIX, '').replace(',', ''))

# モデル情報をパースするユーティリティ関数
def parse_model(model):
    """モデル名から 'モデル: ' プレフィックスを除去する"""
    return model.replace('モデル: ', '')

def add_https_to_url(url):
    """URLの先頭に 'https:' を付け足す"""
    if not url.startswith("https:"):
        return f"https:{url}"
    return url

class LaptopItem(scrapy.Item):
    """ノートパソコン情報を表すアイテムクラス"""
    order_code = scrapy.Field(
        input_processor=MapCompose(extract_order_code),
        output_processor=TakeFirst()  # 最初の値を取得
    )
    name = scrapy.Field(
        output_processor=TakeFirst()  # 最初の値を取得
    )
    model = scrapy.Field(
        input_processor=MapCompose(parse_model),  # モデル名をクリーンアップ
        output_processor=TakeFirst()
    )
    url = scrapy.Field(
        input_processor=MapCompose(add_https_to_url),
        output_processor=TakeFirst()
    )
    price = scrapy.Field(
        input_processor=MapCompose(parse_price),  # 価格をパース
        output_processor=TakeFirst()
    )
    scraped_at = scrapy.Field(
        output_processor=TakeFirst()
    )
