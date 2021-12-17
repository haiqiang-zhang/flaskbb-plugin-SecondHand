# -*- coding: utf-8 -*-
"""
    flaskbb.plugins.SecondHand.views
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains the SecondHand view.

"""
import json

from flask import Blueprint, current_app, flash, request, g, redirect, url_for, jsonify
from flask_babelplus import gettext as _
from flask_login import current_user, login_fresh

from flaskbb.utils.helpers import render_template
from flaskbb.forum.models import Topic, Post, Forum
from flaskbb.user.models import User, Group
from flaskbb.plugins.models import PluginRegistry
from flaskbb.utils.helpers import time_diff, get_online_users
from flaskbb.utils.settings import flaskbb_config
import SecondHand
import datetime
from .form import ReleaseItemsForm, PurchaseItemsForm

from .model import Items, Items_del

SecondHand_bp = Blueprint("SecondHand_bp", __name__, template_folder="templates", static_folder="static")


@SecondHand_bp.before_request
def check_fresh_login():
    """Checks if the login is fresh for the current user, otherwise the user
    has to reauthenticate."""
    if not login_fresh():
        return current_app.login_manager.needs_refresh()


@SecondHand_bp.route("/", methods=['GET', 'POST'])
def SecondHand_index():
    session = SecondHand.Session()
    items = session.query(Items).all()
    user_id = current_user.id
    form = ReleaseItemsForm()
    if request.method == 'GET':
        return render_template(
            "SecondHand_index.html",
            items=items,
            handler_url=url_for("SecondHand_bp.SecondHand_index"),
            form=form
        )
    if form.validate_on_submit():
        item = Items(items_name=form.items_name.data,
                     price=float(form.price.data),
                     sellerID=user_id,
                     description=form.desc.data,
                     main_picture_url=form.main_picture_url.data,
                     post_date=datetime.datetime.now())
        session = SecondHand.Session()
        session.add(item)
        session.commit()
        return json.dumps({"validate":"success"})
    else:
        error = dict({"validate" : "error"}, **form.errors)
        print(error)
        return json.dumps(error)




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
    i: Items = session.query(Items).filter(Items.id == item).one()
    item_del = Items_del(
        prev_id=i.id,
        items_name=i.items_name,
        price=i.price,
        sellerID=i.sellerID,
        buyerID=i.buyerID,
        post_date=i.post_date,
        transaction_date=i.transaction_date,
        main_picture_url=i.main_picture_url,
        description=i.description,
        del_date=datetime.datetime.now())
    session.add(item_del)
    session.delete(i)
    session.commit()
    url = request.args.get("next_url")
    return redirect(url)


@SecondHand_bp.route("/SecondHand_mgmt")
def SecondHand_mgmt():
    return render_template(
        "SecondHand_mgmt.html"
    )


@SecondHand_bp.route("/SecondHand_desc/<item>")
def SecondHand_desc(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    user = User.query.filter(i.sellerID == User.id).one()
    form = PurchaseItemsForm()
    return render_template(
        "SecondHand_itemsDesc.html",
        item=i,
        user=user,
        request=request,
        form=form
    )
