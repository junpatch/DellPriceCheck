import os

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

DEFAULT_SPIDER = 'laptop'  # 意図をより明確にする定数名へリネーム


def execute_spider(spider_name=DEFAULT_SPIDER):  # より直感的な関数名にリネーム
    """
    Execute a Scrapy spider by its name.

    The function sets the current working directory to the script's directory (for proper execution),
    initializes a Scrapy CrawlerProcess with project settings, and starts the specified spider.

    :param spider_name: Name of the spider to execute. Defaults to 'laptop'.
    :type spider_name: str
    """
    # スクリプトの現在の作業ディレクトリを動的に取得して設定
    # current_directory = os.path.abspath(os.path.dirname(__file__))  # os.chdirの補助変数を導入
    # os.chdir(current_directory)

    try:
        # スパイダーを初期化して実行
        process = CrawlerProcess(get_project_settings())
        process.crawl(spider_name)
        process.start()
    except Exception as e:
        print(f"エラー: {e}")    
        
        
if __name__ == "__main__":
    execute_spider()