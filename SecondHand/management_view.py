from flask import Blueprint
from flaskbb.extensions import allows
from flaskbb.utils.requirements import IsAdmin
from flaskbb.utils.helpers import FlashAndRedirect, render_template
from .helper import exception_process
from flask_babelplus import gettext as _
from flask_login import current_user, login_fresh
SecondHand_management_bp = Blueprint("SecondHand_management_bp", __name__, template_folder="templates", static_folder="static")

@exception_process
@SecondHand_management_bp.before_request
def check_fresh_login():
    """Checks if the login is fresh for the current user, otherwise the user
    has to reauthenticate."""
    if not login_fresh():
        return current_app.login_manager.needs_refresh()


@exception_process
@SecondHand_management_bp.route("/outdated_transaction")
@allows.requires(IsAdmin,
            on_fail=FlashAndRedirect(
                message="您没有权限管理SecondHand后台",
                level="danger",
                endpoint="management.overview"
            ))
def outdated_transaction():
    return render_template("SecondHand_management/SecondHand_mgmt_outdated.html")