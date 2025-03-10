import os

from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")

# 消す
@bp.route("/test")
def test():
    os.getcwd()
    return f"cwd: {os.getcwd()}, file: {os.path.dirname(__file__)}"