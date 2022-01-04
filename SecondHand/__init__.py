# -*- coding: utf-8 -*-
"""
    flaskbb.plugins.SecondHand
    ~~~~~~~~~~~~~~~~~~~~~~

    A SecondHand Plugin for FlaskBB.
"""
import os
from pluggy import HookimplMarker
from flask_babelplus import gettext as _
from flaskbb.display.navigation import NavigationLink
from flaskbb.forum.models import Forum
from flaskbb.utils.forms import SettingValueType
from .views import SecondHand_bp
from .management_view import SecondHand_management_bp
from .database import connect_database
from itertools import chain
from flask_allows import Permission
from flask_login import current_user
from .model import orderStatus
from sqlalchemy.orm import sessionmaker

__version__ = "0.1.0"
hookimpl = HookimplMarker("flaskbb")
Session = None


def available_forums():
    forums = Forum.query.order_by(Forum.id.asc()).all()
    return [(forum.id, forum.title) for forum in forums]

@hookimpl
def flaskbb_extensions(app):
    global Session, upload_path
    Session = connect_database(app)


@hookimpl
def flaskbb_load_blueprints(app):
    app.register_blueprint(
        SecondHand_bp, url_prefix=app.config.get("PLUGIN_SECONDHAND_URL_PREFIX", "/SecondHand")
    )
    app.register_blueprint(
        SecondHand_management_bp, url_prefix="/SecondHand_management"
    )



@hookimpl
def flaskbb_tpl_navigation_after():
    return NavigationLink(
        endpoint="SecondHand_bp.SecondHand_index",
        name=_("二手交易"),
        icon="fas fa-hand-holding-usd",
    )

@hookimpl
def flaskbb_tpl_profile_links(user):
    if user == current_user:
        return [
            NavigationLink(
                endpoint="SecondHand_bp.SecondHand_userRecord",
                name=_("二手交易"),
                icon="fas fa-hand-holding-usd",
                urlforkwargs={"username": user.username},
            ),
        ]


@hookimpl(trylast=True)
def flaskbb_tpl_admin_settings_menu():
    # only add this item if the user is an admin
    from flaskbb.utils.requirements import IsAdmin  # noqa: circular dependency
    if Permission(IsAdmin, identity=current_user):
        return [
            ("SecondHand_management_bp.outdated_transaction", "二手交易管理", "fas fa-hand-holding-usd")
        ]


SETTINGS = {
    "outdated_range": {
        "value": 10,
        "value_type": SettingValueType.integer,
        "name": "交易超时天数",
        "description": (
            "设置这个订单从开始交易到今天的天数大于多少算作交易超时"
        ),
        "extra": {"coerce": int},
    }
}
