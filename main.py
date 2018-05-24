from flask import Flask, request, render_template, jsonify, redirect, abort, send_from_directory
from flask_login import LoginManager, login_user, login_required, current_user
from peewee import *
from db import User, Item, TYPE_NAME
import hashlib
import decimal
import urllib.parse
import urllib.request
import re
import json
import html
import base64
import math

def sha256(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

admins = [1]
app = Flask(__name__, static_url_path='/static')
app.secret_key = '5EHQlxuTOfynD/8q9ktqrvK4Qo6/XDoIFcTLCAXF'
app.config['JSON_AS_ASCII'] = False
login_manager = LoginManager()
login_manager.login_view = '/cas'
login_manager.setup_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.get(User.id_ == int(user_id))
        return user
    except DoesNotExist:
        return None

@app.route('/cas')
def cas_handler():
    service = request.args.get('service')
    ticket = request.args.get('ticket')
    if service == None or ticket == None:
        return redirect('http://home.ustc.edu.cn/~pengdinglan/cas_market/', code=302)
    service = urllib.parse.quote(service, safe='')
    ticket = urllib.parse.quote(ticket, safe='')
    request_url = 'https://passport.ustc.edu.cn/serviceValidate?ticket=%s&service=%s' % (ticket, service)
    validate_res = str(urllib.request.urlopen(request_url).read())
    if validate_res.find('not recognized') != -1:
        return render_template('cas_failed.html', msg='登陆失败，请稍后再试', active='cas')
    re_user = re.compile('<cas:user>(.*)</cas:user>')
    m = re_user.search(validate_res)
    if not m:
        return render_template('cas_failed.html', msg='登陆失败，请稍后再试', active='cas')
    student_id = m.group(1)
    if student_id[0] not in ['p', 'P']:
        return render_template('cas_failed.html', msg='请使用学号登陆', active='cas')
    student_id = student_id.upper()
    try:
        user = User.get(User.student_id == student_id)
        login_user(user)
        if not user.has_registered:
            return redirect('/register', code=302)
        else:
            return redirect('/myitems', code=302)
    except DoesNotExist:
        user = User.create(name='', student_id=student_id, phone='', is_admin=False, has_registered=False)
        user.save()
        login_user(user)
        return redirect('/register', code=302)

@app.route('/items')
def items_handler():
    page = request.args.get('page')
    if page == None:
        page = 1
    else:
        try:
            page = int(page)
        except:
            page = 1
    keywords = request.args.get('keywords')
    type_ = request.args.get('type')
    condition = (Item.is_deleted == False) & (Item.has_saled == False)
    if keywords != None and keywords != '':
        keywords = keywords.split(' ')
        for k in keywords:
            condition = condition & (Item.name.contains(k) | Item.detail.contains(k))
    if type_ != None and type_ != 'all':
        try:
            type_ = int(type_)
            if type_ in [0, 1, 2, 3]:
                condition = condition & (Item.type_ == type_)
        except:
            pass
    query = Item.select().where(condition)
    pages = int(math.ceil(query.count() / 10))
    if pages == 0:
        return render_template('items.html', items=[], page=0, pages=0, active='items')
    if page > pages:
        abort(404)
    items = query.order_by(Item.id_.desc()).paginate(page, 10)
    return render_template('items.html', items=items, page=page, pages=pages, active='items')

@app.route('/myitems')
@login_required
def myitems_handler():
    if not current_user.has_registered:
        return redirect('/register', code=302)
    items = Item.select().where((Item.user == current_user.id_) & (Item.is_deleted == False))
    return render_template('myitems.html', items=json.dumps([{
            'id' : item.id_,
            'type' : item.type_,
            'name' : item.name,
            'detail' : item.detail,
            'price' : format(item.price, 'f'),
            'has_saled' : item.has_saled,
            'sale_self' : item.sale_self,
            'will_take_back' : item.will_take_back,
            'has_given_staff' : item.has_given_staff
            } for item in items], ensure_ascii=False), active='myitems')

@app.route('/item/<int:item_id>', methods=['GET', 'DELETE', 'PUT'])
@login_required
def item_handler(item_id):
    if not current_user.has_registered:
        return jsonify({'status':'unauthorized'}), 401
    try:
        item = Item.get((Item.id_ == item_id) & (Item.is_deleted == False))
    except DoesNotExist:
        return jsonify({'status':'itemnotexist'}), 404
    if item.user.id_ != current_user.id_:
        return jsonify({'status':'unauthorized'}), 401
    if request.method == 'GET':
        return jsonify({
            'status' : 'ok',
            'type' : item.type_,
            'name' : item.name,
            'detail' : item.detail,
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
        return jsonify({'status' : 'ok'})
    elif request.method == 'PUT':
        try:
            req_data = request.get_json(force=True)
            name = html.escape(req_data['name'])
            detail = html.escape(req_data['detail'])
            img_type = req_data['img']['type']
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
        if img_type not in ['png', 'jpg', 'gif', 'null']:
            return jsonify({'status' : 'badrequest'}), 400
        item.name = name
        item.detail = detail
        if img_type == 'null':
            item.img_filename = ''
        else:
            img = base64.b64decode(req_data['img']['data'])
            item.img_filename = '%d.%s' % (item.id_, img_type)
            with open('imgs/' + item.img_filename, 'wb') as f:
                f.write(img)
        item.type_ = type_
        item.sale_self = sale_self
        item.will_take_back = will_take_back
        item.price = price
        item.save()
        return jsonify({'status' : 'ok'})

@app.route('/item', methods=['POST'])
@login_required
def item_post_handler():
    if not current_user.has_registered:
        return jsonify({'status':'unauthorized'}), 401
    try:
        req_data = request.get_json(force=True)
        name = html.escape(req_data['name'])
        detail = html.escape(req_data['detail'])
        img_type = req_data['img']['type']
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
    if img_type not in ['png', 'jpg', 'gif', 'null']:
        return jsonify({'status' : 'badrequest'}), 400
    if img_type == 'null':
        id_ = Item.insert(name=name, price=price, type_=type_, sale_self=sale_self,
            will_take_back=will_take_back, user=current_user.id_, has_saled=False,
            is_deleted=False, has_given_staff=False, detail=detail, img_filename='').execute()
    else:
        img = base64.b64decode(req_data['img']['data'])
        if len(img) > 102400:
            return jsonify({'status' : 'badrequest'}), 400
        item = Item.create(name=name, price=price, type_=type_, sale_self=sale_self,
            will_take_back=will_take_back, user=current_user.id_, has_saled=False,
            is_deleted=False, has_given_staff=False, detail=detail, img_filename='')
        item.save()
        item.img_filename = '%d.%s' % (item.id_, img_type)
        with open('imgs/' + item.img_filename, 'wb') as f:
            f.write(img)
        item.save()
        id_ = item.id_
    return jsonify({'status' : 'ok', 'id' : id_})

@app.route('/img/<int:item_id>')
def img_handler(item_id):
    try:
        item = Item.get((Item.id_ == item_id) & (Item.is_deleted == False))
    except DoesNotExist:
        abort(404)
    if item.img_filename == '':
        abort(404)
    return send_from_directory('imgs', item.img_filename)

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register_handler():
    if current_user.has_registered:
        return redirect('/myitems', code=302)
    if request.method == 'GET':
        return render_template('register.html', active='register')
    elif request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        if name == None or phone == None:
            return render_template('register.html', failed=True, active='register')
        current_user.name = name
        current_user.phone = phone
        current_user.has_registered = True
        current_user.save()
        return redirect('/myitems', code=302)

@app.route('/eula')
def eula_handler():
    return render_template('eula.html', active='eula')

@app.route('/')
def index_handler():
    return render_template('home.html', active='home')

@app.route('/rule')
def rule_handler():
    return render_template('rule.html', active='rule')

@app.route('/detail/<int:item_id>')
def detail_handler(item_id):
    try:
        item = Item.get((Item.id_ == item_id) & (Item.is_deleted == False))
    except DoesNotExist:
        abort(404)
    return render_template('detail.html', active='detail', item=item)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_checkout_handler():
    if not current_user.is_admin:
        abort(401)
    if request.method == 'GET':
        users = User.select()
        return render_template('admin.html', active='admin', users=users)
    elif request.method == 'POST':
        req_data = request.get_json(force=True)
        try:
            action = req_data['action']
            id_ = int(req_data['id'])
            if action == 'newadmin':
                user = User.get(User.id_ == id_)
            else:
                item = Item.get((Item.id_ == id_) & (Item.is_deleted == False))
        except DoesNotExist:
            return jsonify({'status' : 'notfound'}), 404
        except:
            return jsonify({'status' : 'badrequest'}), 400
        if action == 'checkout':
            if item.has_saled:
                return jsonify({'status' : 'hassaled'}), 404
            item.has_saled = True
            item.save()
        elif action == 'receive':
            if item.sale_self:
                return jsonify({'status' : 'saleself'}), 400
            if item.has_given_staff:
                return jsonify({'status' : 'hasgiven'}), 404
            item.has_given_staff = True
            item.save()
        elif action == 'newadmin':
            user.is_admin = True
            user.save()
        else:
            return jsonify({'status' : 'badrequest'}), 400
        return jsonify({'status' : 'ok'})


if __name__ == '__main__':
    app.run(port=8080, threaded=True, host='0.0.0.0')