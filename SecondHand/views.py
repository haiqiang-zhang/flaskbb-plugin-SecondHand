# -*- coding: utf-8 -*-
"""
    flaskbb.plugins.SecondHand.views
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains the SecondHand view.

"""
from flask import Blueprint, current_app, flash, request, g, redirect, url_for
from flask_babelplus import gettext as _
from flask_login import current_user

from flaskbb.utils.helpers import render_template
from flaskbb.forum.models import Topic, Post, Forum
from flaskbb.user.models import User, Group
from flaskbb.plugins.models import PluginRegistry
from flaskbb.utils.helpers import time_diff, get_online_users
from flaskbb.utils.settings import flaskbb_config
import SecondHand
import datetime
from .form import ReleaseItemsForm

from .model import Items

SecondHand_bp = Blueprint("SecondHand_bp", __name__, template_folder="templates")


@SecondHand_bp.route("/", methods=['GET', 'POST'])
def SecondHand_index():
    # page = request.args.get("page", 1, type=int)
    # forum_ids = []
    #
    # plugin = PluginRegistry.query.filter_by(name="SecondHand").first()
    # if plugin and not plugin.settings:
    #     flash(
    #         _(
    #             "Please install the plugin first to configure the forums "
    #             "which should be displayed."
    #         ),
    #         "warning",
    #     )
    # else:
    #     forum_ids = plugin.settings["forum_ids"]
    # group_ids = [group.id for group in current_user.groups]
    # forums = Forum.query.filter(Forum.groups.any(Group.id.in_(group_ids)))
    #
    # # get the news forums - check for permissions
    # news_ids = [f.id for f in forums.filter(Forum.id.in_(forum_ids)).all()]
    # news = (
    #     Topic.query.filter(Topic.forum_id.in_(news_ids))
    #     .order_by(Topic.id.desc())
    #     .paginate(page, flaskbb_config["TOPICS_PER_PAGE"], True)
    # )
    #
    # # get the recent topics from all to the user available forums (not just the
    # # configured ones)
    # all_ids = [f.id for f in forums.all()]
    # recent_topics = (
    #     Topic.query.filter(Topic.forum_id.in_(all_ids))
    #     .order_by(Topic.last_updated.desc())
    #     .limit(plugin.settings.get("recent_topics", 10))
    # )
    #
    # user_count = User.query.count()
    # topic_count = Topic.query.count()
    # post_count = Post.query.count()
    # newest_user = User.query.order_by(User.id.desc()).first()
    #
    # # Check if we use redis or not
    # if not current_app.config["REDIS_ENABLED"]:
    #     online_users = User.query.filter(User.lastseen >= time_diff()).count()
    #     online_guests = None
    # else:
    #     online_users = len(get_online_users())
    #     online_guests = len(get_online_users(guest=True))
    session = SecondHand.Session()
    items = session.query(Items).all()
    user_id = current_user.id
    form = ReleaseItemsForm()
    print([i.id for i in items])
    if form.validate_on_submit():
        item = Items(items_name=form.items_name.data,
                     price=float(form.price.data),
                     sellerID=user_id,
                     description=form.desc.data,
                     main_picture_url=form.main_picture_url.data,
                     post_date=datetime.datetime.now())
        print(item)
        session = SecondHand.Session()
        session.add(item)
        session.commit()
        return redirect(url_for("SecondHand_bp.SecondHand_index"))
    return render_template(
        "SecondHand_index.html",
        items=items,
        handler_url=url_for("SecondHand_bp.SecondHand_index"),
        form=form
    )


@SecondHand_bp.route("/userRecord")
def SecondHand_userRecord():
    session = SecondHand.Session()
    myRelease = session.query(Items).filter(Items.sellerID == current_user.id)

    return render_template(
        "SecondHand_userRecord.html",
        myRelease=myRelease,
        user=current_user,
        id=id
    )



@SecondHand_bp.route("/del_myRelease/<item>")
def SecondHand_del_myRelease(item):
    session = SecondHand.Session()
    i = session.query(Items).filter(Items.id == item).one()
    session.delete(i)
    session.commit()
    return redirect(url_for("SecondHand_bp.SecondHand_userRecord"))







