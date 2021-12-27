# -*- coding: utf-8 -*-
"""
    flaskbb.plugins.SecondHand.views
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains the SecondHand view.

"""
import json
import os
from flask import Blueprint, current_app, flash, request, g, redirect, url_for, jsonify, send_from_directory
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
from conversations.models import Conversation, Message
import uuid
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
    items = session.query(Items).filter(Items.orderStatusId == 1)
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
        f = form.main_picture.data
        filename = "{}-{}-{}.{}".format(current_user.id, form.items_name.data,datetime.datetime.now(), f.filename.rsplit('.', 1)[1])
        f.save(os.path.join(os.path.dirname(__file__), "static/upload_file/image/item_main_picture",filename))
        file_path = os.path.join('upload_file/image/item_main_picture', filename)
        item = Items(items_name=form.items_name.data,
                     price=float(form.price.data),
                     sellerID=user_id,
                     description=form.desc.data,
                     main_picture_url=file_path,
                     post_date=datetime.datetime.now(),
                     orderStatusId=1)
        session = SecondHand.Session()
        session.add(item)
        session.commit()
        return json.dumps({"validate": "success"})
    else:
        error = dict({"validate": "error"}, **form.errors)
        print(error)
        return json.dumps(error)


@SecondHand_bp.route("/userRecord")
def SecondHand_userRecord():
    session = SecondHand.Session()
    onSalse = session.query(Items).filter(Items.sellerID == current_user.id, Items.orderStatusId == 1)
    onTransaction = session.query(Items).filter(Items.sellerID == current_user.id, Items.orderStatusId.in_([2, 3, 5]))
    success = session.query(Items).filter(Items.sellerID == current_user.id, Items.orderStatusId.in_([4, 6]))
    buyer_onTransaction = session.query(Items).filter(Items.buyerID == current_user.id,
                                                      Items.orderStatusId.in_([2, 3, 5]))
    buyer_success = session.query(Items).filter(Items.buyerID == current_user.id, Items.orderStatusId.in_([4, 6]))
    tabTarget = request.args.get("tabTarget")
    return render_template(
        "SecondHand_userRecord.html",
        myRelease=onSalse,
        user=current_user,
        onTransaction=onTransaction,
        success=success,
        buyer_onTransaction=buyer_onTransaction,
        buyer_success=buyer_success,
        tabTarget=tabTarget,
        id=id
    )


@SecondHand_bp.route("/SecondHand_mgmt")
def SecondHand_mgmt():
    return render_template(
        "SecondHand_mgmt.html"
    )


@SecondHand_bp.route("/SecondHand_desc/<item>", methods=['GET', 'POST'])
def SecondHand_desc(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    user = User.query.filter(i.sellerID == User.id).one()
    form = PurchaseItemsForm()
    if request.method == 'GET':
        return render_template(
            "SecondHand_itemsDesc.html",
            item=i,
            user=user,
            request=request,
            form=form
        )
    if form.validate_on_submit():
        i.buyerID = current_user.id
        i.start_transaction_date = datetime.datetime.now()
        i.orderStatusId = 2
        i.buyer_phone = form.phone.data
        i.buyer_email = form.email.data
        i.buyer_location = form.location.data
        i.buyer_comment = form.comment.data
        session.commit()
        # send message to seller
        purchase_message = "系统自动发送\n{} 已下单 {} 商品\n&#128230;买方的联系方式:\n手机: {}\nEmail: {}\n地址: {}\n留言: {}" \
            .format(current_user.username, i.items_name, form.phone.data, form.email.data, form.location.data,
                    form.comment.data)
        message_seller = Message(
            message=purchase_message,
            user_id=current_user.id
        )
        conversation_seller = Conversation(
            subject=current_user.username + " 已下单 " + i.items_name,
            draft=False,
            shared_id=uuid.uuid4(),
            from_user_id=current_user.id,
            to_user_id=i.sellerID,
            user_id=i.sellerID,
            unread=True,
        )
        conversation_seller.save(message=message_seller)
        message_buyer = Message(
            message=purchase_message,
            user_id=current_user.id
        )
        conversation_buyer = Conversation(
            subject=current_user.username + " 已下单 " + i.items_name,
            draft=False,
            shared_id=uuid.uuid4(),
            from_user_id=current_user.id,
            to_user_id=i.sellerID,
            user_id=current_user.id,
            unread=False,
        )
        conversation_buyer.save(message=message_buyer)
        return json.dumps({"validate": "success"})
    else:
        error = dict({"validate": "error"}, **form.errors)
        print(error)
        return json.dumps(error)


# -----------------------------------
#   change items status or del
# -----------------------------------
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
        start_transaction_date=i.start_transaction_date,
        success_transaction_date=i.success_transaction_date,
        main_picture_url=i.main_picture_url,
        description=i.description,
        orderStatusId=i.orderStatusId,
        buyer_phone=i.buyer_phone,
        buyer_email=i.buyer_email,
        buyer_location=i.buyer_location,
        buyer_comment=i.buyer_comment,
        del_date=datetime.datetime.now())
    session.add(item_del)
    session.delete(i)
    session.commit()
    url = request.args.get("next_url")
    return redirect(url)


@SecondHand_bp.route("/buyer_success/<item>")
def SecondHand_buyer_success(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    i.orderStatusId = 3
    session.commit()
    url = request.args.get("next_url")
    return redirect(url)


@SecondHand_bp.route("/seller_success/<item>")
def SecondHand_seller_success(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    i.orderStatusId = 4
    session.commit()
    url = request.args.get("next_url")
    return redirect(url)


@SecondHand_bp.route("/buyer_cancel/<item>")
def SecondHand_buyer_cancel(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    i.orderStatusId = 5
    session.commit()
    # send message to seller
    purchase_message = "系统自动发送\n&#10071;{} 已取消购买 {} 商品\n请尽快与买家联系，如有争议请联系论坛管理团队"\
        .format(current_user.username, i.items_name)
    message_seller = Message(
        message=purchase_message,
        user_id=current_user.id
    )
    conversation_seller = Conversation(
        subject=current_user.username + " 已取消购买 " + i.items_name,
        draft=False,
        shared_id=uuid.uuid4(),
        from_user_id=current_user.id,
        to_user_id=i.sellerID,
        user_id=i.sellerID,
        unread=True,
    )
    conversation_seller.save(message=message_seller)
    message_buyer = Message(
        message=purchase_message,
        user_id=current_user.id
    )
    conversation_buyer = Conversation(
        subject=current_user.username + " 已取消购买 " + i.items_name,
        draft=False,
        shared_id=uuid.uuid4(),
        from_user_id=current_user.id,
        to_user_id=i.sellerID,
        user_id=current_user.id,
        unread=False,
    )
    conversation_buyer.save(message=message_buyer)
    url = request.args.get("next_url")
    return redirect(url)


@SecondHand_bp.route("/seller_cancel/<item>")
def SecondHand_seller_cancel(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    i.orderStatusId = 6
    session.commit()
    # send message to seller
    purchase_message = "系统自动发送\n&#9989;您取消购买的 {} 商品，卖家已确认取消，交易完成"\
        .format(i.items_name)
    message_seller = Message(
        message=purchase_message,
        user_id=current_user.id
    )
    conversation_seller = Conversation(
        subject="卖家已确认取消 " + i.items_name,
        draft=False,
        shared_id=uuid.uuid4(),
        from_user_id=current_user.id,
        to_user_id=i.buyerID,
        user_id=i.buyerID,
        unread=True,
    )
    conversation_seller.save(message=message_seller)
    message_buyer = Message(
        message=purchase_message,
        user_id=current_user.id
    )
    conversation_buyer = Conversation(
        subject="买家已确认取消 " + i.items_name,
        draft=False,
        shared_id=uuid.uuid4(),
        from_user_id=current_user.id,
        to_user_id=i.buyerID,
        user_id=current_user.id,
        unread=False,
    )
    conversation_buyer.save(message=message_buyer)
    url = request.args.get("next_url")
    return redirect(url)