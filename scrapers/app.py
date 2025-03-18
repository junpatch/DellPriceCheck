import os

from flask import Flask, jsonify
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
    import subprocess
    result = subprocess.run(["scrapy", "crawl", spider_name], capture_output=True, text=True)

    # 成功・失敗に応じたレスポンスを作成
    if result.returncode == 0:
        return jsonify({"status": "success", "output": result.stdout, "error": result.stderr}) # 成功してもstderrに書き込まれる
    else:
        return jsonify({"status": "error", "output": result.stdout, "error": result.stderr}), 500
        
app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
    
    return "Hello World!!! Hit '/run_spider' to run the spider"

@app.route("/run_spider", methods=["GET"])
def run_spider():
    result = execute_spider()
    
    return result

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)