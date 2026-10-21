from flask import Blueprint

bp: Blueprint = Blueprint("flavour", __name__)


@bp.get("/flavours", endpoint="flavours_list")
def flavours_list():
    return "lel"