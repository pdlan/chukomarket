from flask import Flask, request, render_template, jsonify
from flask_login import LoginManager, login_user, login_required, current_user
from peewee import *
from db import User, Item, TYPE_NAME
import hashlib
import decimal

def sha256(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

admins = [1]
app = Flask(__name__, static_url_path='/static')
app.secret_key = '5EHQlxuTOfynD/8q9ktqrvK4Qo6/XDoIFcTLCAXF'
app.config['JSON_AS_ASCII'] = False
login_manager = LoginManager()
login_manager.setup_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.get(User.id_ == int(user_id))
        return user
    except DoesNotExist:
        return None

@app.route('/cas', methods=['GET'])
def cas_handler():
    #service = request.form['service']
    #ticket = request.form['ticket']
    student_id = 'PB17111607'
    try:
        user = User.get(User.student_id == student_id)
        login_user(user)
        print(user)
        return 'test'
    except DoesNotExist:
        return render_template('register.html', failed=True)

@app.route('/items')
def items_handler():
    items = Item.select().where(Item.user == current_user.id_)
    return render_template('items.html', items=[{
            'id' : item.id_,
            'type' : item.type_,
            'type_name' : TYPE_NAME[item.type_],
            'name' : item.name,
            'price' : item.price,
            'has_saled' : item.has_saled,
            'sale_self' : item.sale_self,
            'will_take_back' : item.will_take_back,
            'has_given_staff' : item.has_given_staff
            } for item in items])

@app.route('/item/<int:item_id>', methods=['GET', 'DELETE', 'PUT'])
@login_required
def item_handler(item_id):
    try:
        item = Item.get(Item.id_ == item_id & Item.is_deleted == False)
    except DoesNotExist:
        return jsonify({'status':'itemnotexist'}), 404
    if item.user.id_ != current_user.id_:
        return jsonify({'status':'forbidden'}), 403
    if request.method == 'GET':
        return jsonify({
            'status' : 'ok',
            'type' : item.type_,
            'type_name' : TYPE_NAME[item.type_],
            'name' : item.name,
            'price' : format(item.price, 'f'),
            'has_saled' : item.has_saled,
            'sale_self' : item.sale_self,
            'will_take_back' : item.will_take_back,
            'has_given_staff' : item.has_given_staff
            })
    if item.has_saled or item.has_given_staff:
        return jsonify({'status' : 'cannotmodify'}), 403
    if request.method == 'DELETE':
        item.is_deleted = True
        item.save()
    elif request.method == 'PUT':
        try:
            req_data = request.get_json(force=True)
            name = req_data['name']
            type_ = int(req_data['type'])
            sale_self = req_data['sale_self']
            will_take_back = req_data['will_take_back']
            price = decimal.Decimal(req_data['price'])
        except:
            return jsonify({'status' : 'badrequest'}), 400
        if type_ >= len(TYPE_NAME) or type_ < 0:
            return jsonify({'status' : 'badrequest'}), 400
        item.name = name
        item.type_ = type_
        item.sale_self = sale_self
        item.will_take_back = will_take_back
        item.price = price
        return jsonify({'status' : 'ok'})
        

@app.route('/item', methods=['POST'])
@login_required
def item_post_handler():
    try:
        req_data = request.get_json(force=True)
        name = req_data['name']
        type_ = int(req_data['type'])
        sale_self = req_data['sale_self']
        will_take_back = req_data['will_take_back']
        price = decimal.Decimal(req_data['price'])
    except:
        return jsonify({'status' : 'badrequest'}), 400
    if name == '' or price < 0 or price > 100000000:
        return jsonify({'status' : 'badrequest'}), 400
    if type_ >= len(TYPE_NAME) or type_ < 0:
        return jsonify({'status' : 'badrequest'}), 400
    id_ = Item.insert(name=name, price=price, type_=type_, sale_self=sale_self,
        will_take_back=will_take_back, user=current_user.id_, has_saled=False,
        is_deleted=False, has_given_staff=False).execute()
    return jsonify({'status' : 'ok', 'id' : id_})

@app.route('/admin/checkout')
@login_required
def admin_checkout_handler():
    if not current_user.is_admin:
        return 403


if __name__ == '__main__':
    app.run()