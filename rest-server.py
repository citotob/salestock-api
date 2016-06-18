#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for, Response, g
from flask.ext.httpauth import HTTPBasicAuth
import MySQLdb

app = Flask(__name__, static_url_path = "")
auth = HTTPBasicAuth()

# set the secret key.  keep this really secret:
app.secret_key = '1$bc*salestock876)#mok'

@auth.get_password
def get_password(username):
    if username == 'christo':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    resp = make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    return resp
    #return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    


@app.before_request
def db_connect():
    g.conn = MySQLdb.connect(host='127.0.0.1',
                              user='root',
                              passwd='dell3dbelipatungan',
                              db='salestock')
    g.cursor = g.conn.cursor()

@app.after_request
def db_disconnect(response):
    g.cursor.close()
    g.conn.close()
    return response

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ) , 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ) , 404)

def make_public_data(categories):
    new_user = {}
    for field in user:
        if field == 'id':
            new_user['uri'] = url_for('get_user', user_email = user['email'], _external = True)
        else:
            #print field
            new_user[field] = user[field]
    return new_user

@app.route('/salestock/categories', methods = ['GET'])
@auth.login_required
def get_categories_all():
    query = """SELECT c.* FROM category c """

    
    category = g.cursor.execute(query)
    
    if category == 0:
        abort(404)
    categories = []

    categories = [dict((g.cursor.description[idx][0], value)
               for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
    
    return jsonify( { 'data': categories } )

@app.route('/salestock/category/<string:name>', methods = ['GET'])
@auth.login_required
def get_categories(name):
    query = """SELECT c.* FROM category c WHERE c.name REGEXP '%s' """ % (name)

    category = g.cursor.execute(query)

    if category == 0:
        abort(404)
    categories = []

    categories = [dict((g.cursor.description[idx][0], value)
               for idx, value in enumerate(row)) for row in g.cursor.fetchall()]

    return jsonify( { 'data': categories } )

@app.route('/salestock/category/create', methods = ['POST'])
@auth.login_required
def create():
    if not request.json or not 'name' in request.json:
        abort(400)
    req_json = request.get_json()
    name = request.json['name']
    
    query = """INSERT INTO category(name) values ('%s') """ % (name)

    category = g.cursor.execute(query)
    g.conn.commit()
    resp = Response("CREATED", status=201, mimetype='application/json')
    return resp

@app.route('/salestock/category/remove/<int:category_id>', methods = ['DELETE'])
@auth.login_required
def remove(category_id):
    query = """DELETE FROM category WHERE id = %i """ % (category_id)
    print query
    category = g.cursor.execute(query)
    g.conn.commit()

    return jsonify( { 'result': True } )

#======Products=================================
    
@app.route('/salestock/products', methods = ['GET'])
@auth.login_required
def get_products_all():
    query = """SELECT p.* FROM product p """


    product = g.cursor.execute(query)

    if product == 0:
        abort(404)
    products = []

    products = [dict((g.cursor.description[idx][0], value)
               for idx, value in enumerate(row)) for row in g.cursor.fetchall()]

    return jsonify( { 'data': products } )

@app.route('/salestock/product/<string:name>', methods = ['GET'])
@auth.login_required
def get_products(name):
    query = """SELECT p.* FROM product p WHERE p.name REGEXP '%s' """ % (name)

    product = g.cursor.execute(query)

    if product == 0:
        abort(404)
    products = []

    products = [dict((g.cursor.description[idx][0], value)
               for idx, value in enumerate(row)) for row in g.cursor.fetchall()]

    return jsonify( { 'data': products } )

@app.route('/salestock/product/filter', methods = ['GET'])
@auth.login_required
def filter():
    if not request.json:
        abort(400)
    #where_loop = len(request.json)

    query = """SELECT p.* FROM product p WHERE 1"""

    for field in request.json:
	if field == 'range_price':
	    rangeprice = request.json['range_price'].split(":")
	    query += " AND p.price between %s and %s" % (rangeprice[0], rangeprice[1])
	else:
	    query += " AND p.%s = '%s'" % (field, request.json[field])
    
    product = g.cursor.execute(query)

    if product == 0:
        abort(404)
    products = []

    products = [dict((g.cursor.description[idx][0], value)
               for idx, value in enumerate(row)) for row in g.cursor.fetchall()]

    return jsonify( { 'result': products } )

@app.route('/salestock/product/create', methods = ['POST'])
@auth.login_required
def create_product():
    if not request.json or not 'name' in request.json:
        abort(400)
    req_json = request.get_json()
    name = request.json['name']
    price = request.json['price']
    category_id = request.json['category_id']
    size = request.json['size']
    color = request.json['color']

    query = """INSERT INTO product(name, price, category_id, size, color) values ('%s', '%s', '%s', '%s', '%s') """ % (name, price, category_id, size, color)

    product = g.cursor.execute(query)
    g.conn.commit()
    resp = Response("CREATED", status=201, mimetype='application/json')
    return resp

@app.route('/salestock/product/remove/<int:product_id>', methods = ['DELETE'])
@auth.login_required
def remove_product(product_id):
    query = """DELETE FROM product WHERE id = %i """ % (product_id)

    product = g.cursor.execute(query)
    g.conn.commit()

    return jsonify( { 'result': True })

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug = True)
citotob
