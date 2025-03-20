from __future__ import annotations

from datetime import datetime

import boto3
from flask import Blueprint, jsonify, request, render_template, Response

from model.models import Products, PriceHistory, db


bp = Blueprint("api", __name__, url_prefix="/api")

ecs_client = boto3.client("ecs", region_name="ap-northeast-1") 

# 定数定義
NOTIFICATION_UPDATED_MSG = "通知設定を更新しました order_code: {}"
PRODUCT_NOT_FOUND_MSG = "商品が見つかりません order_code: {}"
CLUSTER_NAME = "fargate-demo-cluster"
TASK_FAMILY = "fargate-demo-task-definition_git"
SUBNETS = ["subnet-036e9c273c248c659", "subnet-022e1a8dee3ffabb0", "subnet-050ec254319674193", "subnet-06fa6266584317e5b"]
SECURITY_GROUPS =["sg-0f985e8b85e007092"]

# ヘルパー関数
def fetch_product_by_order_code(order_code: str) -> Products | None:
    """order_code で該当する商品を取得"""
    return db.session.query(Products).filter_by(order_code=order_code).first()


def fetch_price_trends(order_code: str) -> list[dict]:
    """order_code に対応する価格推移を取得"""
    trends = PriceHistory.query.filter_by(order_code=order_code).all()
    return [
        {"date": trend.scraped_at.isoformat() if isinstance(trend.scraped_at, datetime) else trend.scraped_at,
         "price": trend.price}
        for trend in trends
    ]


def fetch_order_code(name: str, model: str) -> str | None:
    """商品の name と model を用いて order_code を取得"""
    product = db.session.query(Products.order_code).filter_by(name=name, model=model).first()
    return product[0] if product else None


def fetch_model_by_name(name: str, ) -> str | None:
    """商品の name と model を用いて model を取得"""
    models = db.session.query(Products.model).filter_by(name=name).all()
    return models if models else None


def get_latest_task_definition(task_family):
    """タスク定義の最新リビジョンを取得"""
    response = ecs_client.list_task_definitions(
        familyPrefix=task_family,
        sort="DESC",
        status="ACTIVE",
        maxResults=1
    )
    if response["taskDefinitionArns"]:
        return response["taskDefinitionArns"][0]  # 最新のリビジョン ARN を取得
    else:
        raise ValueError("No active task definition found.")


# ルート定義
@bp.route("/")
def index():
    """ホーム画面表示"""
    try:
        products = Products.query.all()
        # TODO: DELL HP上で表記揺らぎあり「inspiron 14ノートパソコン」と「inspiron14ノートパソコン」など。
        #       スペースを詰めて重複削除が必要。その後、モデル名を選択するときにさらなる工夫が必要・・・
        product_names_list = sorted(set([product.name for product in products]))
    except Exception as e:
        from app import app
        app.logger.info(f"DBからのデータ取得エラー: {e}")
        product_names_list = []
    return render_template("api.html", product_names_list=product_names_list)


@bp.route("/line_notification_setting")
def line_notification_setting():
    """Line通知設定画面表示"""
    sorted_products = Products.query.order_by(Products.name.asc()).all()

    return render_template("api_line_notification_setting.html", products=sorted_products)


@bp.route("/register_line_notification")
def register_line_notification():
    return render_template("api_register_line_notification.html")


@bp.route("/get_price_trend/<string:name>/<string:model>", methods=["GET"])
def price_trends(name, model) -> Response:
    """価格推移データを取得"""
    order_code = fetch_order_code(name, model)
    if not order_code:
        return jsonify({"error": "商品の注文コードが見つかりません"}), 404

    price_data = fetch_price_trends(order_code)

    product = fetch_product_by_order_code(order_code)
    url = product.url

    return jsonify({"prices": price_data, "url": url})


@bp.route("/get_notification_setting", methods=["GET"])
def notification_setting() -> Response:
    """通知設定を取得"""
    products = db.session.query(Products.order_code, Products.is_line_notification).all()
    toggle_values = {}
    if products:
        for product in products:
            toggle_values[product.order_code] = product.is_line_notification
        return jsonify({"success": True, "toggleValues": toggle_values})
    return jsonify({"success": False, "toggleValues": None})


@bp.route("/update_notification_setting", methods=["POST"])
def update_notification_setting() -> Response:
    """通知設定を更新"""
    data = request.get_json()
    order_code = data.get("order_code")
    is_checked = data.get("is_checked")
    product = fetch_product_by_order_code(order_code)
    if product:
        product.is_line_notification = 1 if is_checked else 0
        db.session.commit()
        return jsonify({"message": NOTIFICATION_UPDATED_MSG.format(order_code)}), 200
    return jsonify({"error": PRODUCT_NOT_FOUND_MSG.format(order_code)}), 404


@bp.route('/get_model/<string:name>', methods=['GET'])
def get_subcategories(name) -> Response:
    models = fetch_model_by_name(name)
    return jsonify([{"model": row[0]} for row in models])


@bp.route("/check_price", methods=["GET"])
def price_check() -> Response:
    """現在の価格を取得"""
    response = ecs_client.run_task(
        cluster=CLUSTER_NAME,
        taskDefinition=get_latest_task_definition(TASK_FAMILY),
        capacityProviderStrategy=[
            {"capacityProvider": "FARGATE_SPOT", "weight": 1}
        ],
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": SUBNETS,
                "securityGroups": SECURITY_GROUPS,
                "assignPublicIp": "ENABLED",
            }
        },
    )
    # 起動されたタスクの ARN を取得
    task_arn = response["tasks"][0]["taskArn"]
    
    return jsonify({"taskArn": task_arn}) 

@bp.route("/get_scraping_status/<path:task_arn>", methods=["GET"])
def check_task_status(task_arn):
    # タスクの状態を取得
    response = ecs_client.describe_tasks(
        cluster=CLUSTER_NAME,
        tasks=[task_arn]
    )

    # タスクの状態を確認
    tasks = response.get("tasks", [])
    if not tasks:
        return {"error": "Task not found"}, 404
    task = tasks[0]
    status = task.get("lastStatus", "UNKNOWN")# タスクの状態 (PROVISIONING, PENDING, RUNNING, STOPPED)
    
    # タスクが STOPPED の場合、追加情報を取得
    result = {
        "status": status,
        "stoppedAt": task.get("stoppedAt"),
        "stopReason": task.get("stoppedReason", "No reason provided"),
        "exitCode": task.get("containers", [{}])[0].get("exitCode", "Unknown"),
        "taskArn": task_arn,
    } if status == "STOPPED" else {
        "status": status,
        "stoppedAt": None,
        "stopReason": None,
        "exitCode": None,
        "taskArn": task_arn,
    }
    
    return jsonify(result)
       
@bp.route("/notification_test", methods=["GET"])
def notification_test() -> Response:
    """すべての価格を0円に変更後、最新価格を取得"""
    
    try:
        # すべての価格を0円に変更
        products = Products.query.all()
        for product in products:
            product.price = 0

        db.session.commit()  # データベースに変更を反映

        # 現在の価格を取得
        return price_check()

    except Exception as e:
        db.session.rollback()  # 失敗時にロールバック
        return jsonify({"result": 0, "error": str(e)})
