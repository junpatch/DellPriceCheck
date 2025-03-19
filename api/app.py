from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from model.models import db
from routes import main_routes, api_routes
from config import config


app = Flask(__name__)
# 設定を読み込み
app.config.from_object(config["development"])

# toolbar = DebugToolbarExtension(app)

db.init_app(app)

# ルーティングの登録（Blueprintを利用）
app.register_blueprint(main_routes.bp)
app.register_blueprint(api_routes.bp)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)