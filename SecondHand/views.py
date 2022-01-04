# -*- coding: utf-8 -*-
"""
    flaskbb.plugins.SecondHand.views
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains the SecondHand view.

"""
import json
import os
from flask_allows import Permission

from flask import Blueprint, current_app, request, redirect, url_for
from flask_login import current_user, login_fresh
from flaskbb.utils.requirements import IsAdmin
from flaskbb.utils.helpers import render_template, FlashAndRedirect
from flaskbb.user.models import User
import SecondHand
import datetime
from .form import ReleaseItemsForm, PurchaseItemsForm, ChangeItemsForm
from conversations.models import Conversation, Message
import uuid
from .model import Items, Items_del
from .helper import upload_item_picture, no_right, exception_process, check_seller_existing
from flask_wtf.file import FileStorage

SecondHand_bp = Blueprint("SecondHand_bp", __name__, template_folder="templates", static_folder="static")


@SecondHand_bp.before_request
def check_before_request():
    """Checks if the login is fresh for the current user, otherwise the user
            has to reauthenticate."""
    if not login_fresh():
        return current_app.login_manager.needs_refresh()
    if current_user.primary_group.banned:
        f_r = FlashAndRedirect(
            message="您被禁止访问SecondHand平台，请联系论坛管理团队",
            level="danger",
            endpoint="forum.index"
        )
        return f_r()


@SecondHand_bp.route("/", methods=['GET', 'POST'])
@exception_process
def SecondHand_index():
    session = SecondHand.Session()
    items = session.query(Items).filter(Items.orderStatusId == 1).all()
    items = filter(check_seller_existing, items)
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
        path = os.path.join(os.path.dirname(__file__), "static/upload_file/image/item_main_picture")
        file_path = upload_item_picture(
            path,
            form.main_picture.data,
            current_user.id,
            form.items_name.data)
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
@exception_process
def SecondHand_userRecord():
    session = SecondHand.Session()
    onSalse = session.query(Items).filter(Items.sellerID == current_user.id, Items.orderStatusId == 1).all()
    onTransaction = session.query(Items).filter(Items.sellerID == current_user.id,
                                                Items.orderStatusId.in_([2, 3, 5])).all()
    success = session.query(Items).filter(Items.sellerID == current_user.id, Items.orderStatusId.in_([4, 6])).all()
    buyer_onTransaction = session.query(Items).filter(Items.buyerID == current_user.id,
                                                      Items.orderStatusId.in_([2, 3, 5])).all()
    buyer_success = session.query(Items).filter(Items.buyerID == current_user.id, Items.orderStatusId.in_([4, 6])).all()
    tabTarget = request.args.get("tabTarget")
    form_change = ChangeItemsForm()
    return render_template(
        "SecondHand_userRecord.html",
        myRelease=onSalse,
        user=current_user,
        onTransaction=onTransaction,
        success=success,
        buyer_onTransaction=buyer_onTransaction,
        buyer_success=buyer_success,
        tabTarget=tabTarget,
        form_change=form_change,
        id=id,  # It is a function
        User=User  # it is a class
    )


@SecondHand_bp.route("/SecondHand_desc/<item>", methods=['GET', 'POST'])
@exception_process
def SecondHand_desc(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    user = User.query.filter(i.sellerID == User.id).one()
    form = PurchaseItemsForm()
    form_change = ChangeItemsForm()
    if request.method == 'GET':
        return render_template(
            "SecondHand_itemsDesc.html",
            item=i,
            user=user,
            request=request,
            form=form,
            form_change=form_change,
            User=User  # It is Model of user
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
#   change items or del
# -----------------------------------

@SecondHand_bp.route("/del_myRelease/<item>")
@exception_process
def SecondHand_del_myRelease(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    url = request.args.get("next_url")
    if i.orderStatusId in [6, 4] and current_user.id == i.sellerID:
        i.sellerID = None
        session.commit()
        return redirect(url)
    elif i.orderStatusId in [6, 4] and current_user.id == i.buyerID:
        i.buyerID = None
        session.commit()
        return redirect(url)
    elif (i.orderStatusId == 1 and current_user.id == i.sellerID) or Permission(IsAdmin, identity=current_user):
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
        return redirect(url)
    else:
        return no_right()


@SecondHand_bp.route("/buyer_success/<item>")
@exception_process
def SecondHand_buyer_success(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    if current_user.id == i.buyerID:
        i.orderStatusId = 3
        session.commit()
        url = request.args.get("next_url")
        return redirect(url)
    else:
        session.close()
        return no_right()


@SecondHand_bp.route("/seller_success/<item>")
@exception_process
def SecondHand_seller_success(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    if current_user.id == i.sellerID:
        i.orderStatusId = 4
        i.success_transaction_date = datetime.datetime.now()
        session.commit()
    url = request.args.get("next_url")
    return redirect(url)


@SecondHand_bp.route("/buyer_cancel/<item>")
@exception_process
def SecondHand_buyer_cancel(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    i.orderStatusId = 5
    session.commit()
    # send message to seller
    purchase_message = "系统自动发送\n&#10071;{} 已取消购买 {} 商品\n请尽快与买家联系，如有争议请联系论坛管理团队" \
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
@exception_process
def SecondHand_seller_cancel(item):
    session = SecondHand.Session()
    i: Items = session.query(Items).filter(Items.id == item).one()
    i.orderStatusId = 6
    i.success_transaction_date = datetime.datetime.now()
    session.commit()
    # send message to seller
    purchase_message = "系统自动发送\n&#9989;您取消购买的 {} 商品，卖家已确认取消，交易完成" \
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
        subject="卖家已确认取消 " + i.items_name,
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


@SecondHand_bp.route("/change_item/<item>", methods=['GET', 'POST'])
@exception_process
def SecondHand_change_item(item):
    session = SecondHand.Session()
    form = ChangeItemsForm()
    i: Items = session.query(Items).filter(Items.id == item).one()

    if all([form.items_name.data == "",
            form.price.data == "",
            form.desc.data == "",
            not (isinstance(form.main_picture.data, FileStorage) and form.main_picture.data)]):
        error = dict({"validate": "error", "notChange": "请输入需要修改的对应项"})
        print(error)
        return json.dumps(error)
    elif form.validate_on_submit():
        if form.items_name.data != "":
            i.items_name = form.items_name.data
        if form.price.data != "":
            i.price = float(form.price.data)
        if form.desc.data != "":
            i.description = form.desc.data
        if isinstance(form.main_picture.data, FileStorage) and form.main_picture.data:
            file_path = upload_item_picture(
                os.path.join(os.path.dirname(__file__), "static/upload_file/image/item_main_picture"),
                form.main_picture.data,
                current_user.id,
                form.items_name.data)
            i.main_picture_url = file_path
        session.commit()
        return json.dumps({"validate": "success"})
    else:
        error = dict({"validate": "error"}, **form.errors)
        print(error)
        return json.dumps(error)
