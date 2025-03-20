import json
import subprocess


DEFAULT_SPIDER = 'laptop'  # 意図をより明確にする定数名へリネーム


def execute_spider(spider_name=DEFAULT_SPIDER):  # より直感的な関数名にリネーム
    """
    Execute a Scrapy spider by its name.

    The function sets the current working directory to the script's directory (for proper execution),
    initializes a Scrapy CrawlerProcess with project settings, and starts the specified spider.

    :param spider_name: Name of the spider to execute. Defaults to 'laptop'.
    :type spider_name: str
    """
    result = subprocess.run(["scrapy", "crawl", spider_name])

    # 成功・失敗に応じたレスポンスを作成
    if result.returncode == 0:
        return json.dumps({"status": "success", "output": "output", "error": "error"}) # printの出力がstdoutに書かれる
    else:
        return json.dumps({"status": "error", "output": "output", "error": "error"}), 500


if __name__ == "__main__":
    execute_spider()