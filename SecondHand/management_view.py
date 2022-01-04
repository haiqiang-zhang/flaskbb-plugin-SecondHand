import datetime
from flask import Blueprint, current_app, flash
from flaskbb.extensions import allows
from flaskbb.utils.requirements import IsAdmin
from flaskbb.utils.helpers import FlashAndRedirect, render_template
import SecondHand
from .helper import exception_process, count_outdated_items
from flask_login import login_fresh
from flaskbb.user.models import User
from flaskbb.plugins.models import PluginRegistry

from .model import Items

SecondHand_management_bp = Blueprint("SecondHand_management_bp", __name__, template_folder="templates",
                                     static_folder="static")


@SecondHand_management_bp.before_request
def check_fresh_login():
    """Checks if the login is fresh for the current user, otherwise the user
    has to reauthenticate."""
    if not login_fresh():
        return current_app.login_manager.needs_refresh()


@SecondHand_management_bp.route("/outdated_transaction")
@allows.requires(IsAdmin,
                 on_fail=FlashAndRedirect(
                     message="您没有权限管理SecondHand后台",
                     level="danger",
                     endpoint="management.overview"))
@exception_process
def outdated_transaction():
    plugin = PluginRegistry.query.filter_by(name="SecondHand").first()
    outdated_range = -1
    if plugin and not plugin.settings:
        flash(
            "SecondHand未被安装，请在后台管理的插件窗口安装SecondHand",
            "warning",
        )
    else:
        outdated_range = plugin.settings["outdated_range"]
    session = SecondHand.Session()
    before_date = datetime.datetime.now() - datetime.timedelta(days=outdated_range)
    outdated_items = session.query(Items) \
        .filter(Items.orderStatusId.in_([2, 3, 5]), Items.start_transaction_date < before_date).all()
    return render_template("SecondHand_management/SecondHand_mgmt_outdated.html",
                           outdated_items=outdated_items,
                           User=User)  # It is model of user


@SecondHand_management_bp.route("/onTransaction")
@allows.requires(IsAdmin,
                 on_fail=FlashAndRedirect(
                     message="您没有权限管理SecondHand后台",
                     level="danger",
                     endpoint="management.overview"))
@exception_process
def onTransaction():
    session = SecondHand.Session()
    items = session.query(Items) \
        .filter(Items.orderStatusId.in_([2, 3, 5])).all()
    return render_template("SecondHand_management/SecondHand_mgmt_onTransaction.html",
                           items=items,
                           count_outdated_items=count_outdated_items(),
                           User=User)  # It is model of user


@SecondHand_management_bp.route("/onSale")
@allows.requires(IsAdmin,
                 on_fail=FlashAndRedirect(
                     message="您没有权限管理SecondHand后台",
                     level="danger",
                     endpoint="management.overview"))
@exception_process
def onSale():
    session = SecondHand.Session()
    items = session.query(Items) \
        .filter(Items.orderStatusId == 1).all()
    return render_template("SecondHand_management/SecondHand_mgmt_onSale.html",
                           items=items,
                           User=User,  # It is model of user
                           count_outdated_items=count_outdated_items())


@SecondHand_management_bp.route("/success")
@allows.requires(IsAdmin,
                 on_fail=FlashAndRedirect(
                     message="您没有权限管理SecondHand后台",
                     level="danger",
                     endpoint="management.overview"))
@exception_process
def success():
    session = SecondHand.Session()
    items = session.query(Items) \
        .filter(Items.orderStatusId.in_([4, 6])).all()
    return render_template("SecondHand_management/SecondHand_mgmt_success.html",
                           items=items,
                           User=User,  # It is model of user
                           count_outdated_items=count_outdated_items())


@SecondHand_management_bp.route("/mgmt_item_desc/<item>")
@allows.requires(IsAdmin,
                 on_fail=FlashAndRedirect(
                     message="您没有权限管理SecondHand后台",
                     level="danger",
                     endpoint="management.overview"
                 ))
@exception_process
def mgmt_item_desc(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    return render_template("SecondHand_management/SecondHand_mgmt_desc.html",
                           i=i)
