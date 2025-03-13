import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.loader import ItemLoader

from dell.items import LaptopItem

class LaptopSpider(scrapy.Spider):
    name = "laptop"
    allowed_domains = ["www.dell.com"]
    start_urls = ["https://www.dell.com/ja-jp/shop/dell-laptops/scr/laptops"]

    def start_requests(self):
        # GET request
        yield scrapy.Request(
            url=self.start_urls[0], 
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("screenshot", path="example.png", full_page=True),
                ],
                "current_page": 1
                }
            )
    
    def parse(self, response):
        # screenshot = response.meta["playwright_page_methods"][0]
        
        items = self._extract_items_from_articles(response)
        # parse内からyieldしないと動かない
        for item in items:
            yield item
            
        current_page = response.meta["current_page"]
        total_pages = response.meta.get("total_pages", None)
        if total_pages is None: # 1ページ目だけで取得
            total_pages = self._get_total_pages(response)
        
        if current_page < total_pages:
            next_page = current_page + 1
            yield scrapy.Request(
            url=f"{self.start_urls[0]}?page={next_page}",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("screenshot", path="example.png", full_page=True),
                ],
                "current_page": next_page,
                "total_pages": total_pages,
                "callback": self.parse
                }
            )
        
    def _extract_items_from_articles(self, response):
        """現在のページのarticleタグを処理し、アイテムを生成"""
        items = []
        # TODO: xpathが見つからないとitems = []となり、for文が回らない→エラーが出ない
        for laptop in response.xpath('//article[@class="variant-stack ps-stack"]'):
            try:
                loader = ItemLoader(item=LaptopItem(), selector=laptop)
                loader.add_xpath('order_code', ".//h3/a/@href")
                loader.add_xpath('name', ".//h3/a/text()")
                loader.add_xpath('model', ".//div[@class='ps-model-number']/span[2]/text()")
                loader.add_xpath('price', ".//span[@class='ps-variant-price-amount']/text()")
                loader.add_xpath('url', ".//h3/a/@href")
                items.append(loader.load_item())
            except Exception as e:
                self.logger.error(f"id={laptop.attrib.get('id', 'unknown')}読み込み中にエラーが発生しました: {e}")
        return items
    
    def _get_total_pages(self, response) -> int:
        total_pages_text = response.xpath('//span[@class="dds__pagination__page-range-total"]/text()').get()
        
        if total_pages_text is None:
            self.logger.error("ページ総数の取得に失敗")
            return 1  # デフォルトで1ページに設定

        try:
            return int(total_pages_text.strip())
        except ValueError:
            self.logger.error(f"ページ総数のパースに失敗: {total_pages_text}")
            return 1
