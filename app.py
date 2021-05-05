#import pymysql
from flask import Flask,render_template,redirect,url_for,request,flash,session
from model import RegistrationForm,UserLoginForm
#from flaskext.mysql import MySQL
import mysql.connector

app=Flask(__name__)
app.config['SECRET_KEY']='This'
#mysql = MySQL()

# MySQL configurations
'''app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'kitchen2'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'''


@app.route('/login',methods=['GET','POST'])
def login():
    #if request.method =='POST'and 'email' in request.form and 'password' in request.form:
    form=UserLoginForm()
    if request.method == 'POST':    # Create variables for easy access
        email = form.username.data
        password = form.password.data
        print(form.username.data,password)
        # Check if account exists using MySQL
        conn = mysql.connector.connect(host='localhost', user='root', password='ViruVikky123', database='kitchen2')
        # cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM customers WHERE email = %s AND password = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()


        # If account exists in accounts table in out database
        if account:
            if account[3]== "admin@cloudkitchen.com":
                return redirect(url_for('Adminpage'))
            else:
                session['loggedin'] = True
                session['email'] = account[3]
                session['cusid'] = account[0]
                session['customername'] = account[1]+" "+account[2]
                return redirect(url_for('products'))
        else:
            return 'Incorrect username/password!'
    return render_template("login.html", form=form)
@app.route('/Adminpage')
def Adminpage():
    conn = mysql.connector.connect(host='localhost', user='root', password='ViruVikky123', database='kitchen2')
    # cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM customers where email!="admin@cloudkitchen.com"')
    data = cursor.fetchall()
    return render_template("Adminpage.html",value=data)
@app.route('/orders')
def orders():
    conn = mysql.connector.connect(host='localhost', user='root', password='ViruVikky123', database='kitchen2')
    # cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    cursor.execute('select * from orders,customers where orders.cusid=customers.cusid')
    data = cursor.fetchall()
    return render_template("orders.html",value=data)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/about')
def about():
    return  render_template("about.html")

@app.route('/home')
def home():
    return render_template("home.html")



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():
        #return f'We confirm your registration!,{form.fname.data}, {form.lname.data},{form.email.data},{form.password.data},{form.confirm.data}'
        conn = mysql.connector.connect(host='localhost',user='root',password='ViruVikky123',database='kitchen2')
        #cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor=conn.cursor()
        sql="insert into Customers(firstname,lastname ,email,password)values(%s,%s,%s,%s)"
        val=(form.fname.data,form.lname.data,form.email.data,form.password.data)
        cursor.execute(sql,val)
        conn.commit()

        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    global conn
    cursor = None
    try:
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        # validate the received values
        if _quantity and _code and request.method == 'POST':
            conn =  conn = mysql.connector.connect(host='localhost',user='root',password='ViruVikky123',database='kitchen2')
            cursor = conn.cursor()
            sql="SELECT * FROM product WHERE code='{}'".format(_code)
            cursor.execute(sql)
            row = cursor.fetchone()

           # itemArray = {
            #    row['code']: {'name': row['name'], 'code': row['code'], 'quantity': _quantity, 'price': row['price'],
             #                 'image': row['image'], 'total_price': _quantity * row['price']}}
            itemArray = {row[2]: {'name': row[1], 'code': row[2], 'quantity': _quantity, 'price': row[4],
                              'image': row[3], 'total_price': _quantity * row[4]}}
            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:
                if row[2] in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if row[2] == key:
                            # session.modified = True
                            # if session['cart_item'][key]['quantity'] is not None:
                            #	session['cart_item'][key]['quantity'] = 0
                            old_quantity = session['cart_item'][key]['quantity']
                            total_quantity = old_quantity + _quantity
                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * row[4]
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                all_total_price = all_total_price + _quantity * row[4]

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            return redirect(url_for('.products'))
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/products')
def products():

    global cursor, conn
    try:
        conn = conn = mysql.connector.connect(host='localhost', user='root', password='ViruVikky123', database='kitchen2')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")
        rows = cursor.fetchall()

        return render_template('products.html', products=rows)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        # return redirect('/')
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False

@app.route('/order', methods=['GET','POST'])
def order():
    cursor = None
    try:
        # validate the received values
        if 'cart_item' in session:
            if request.method == 'POST':
                for key, value in session['cart_item'].items():
                    cusid=session['cusid']
                    orderitemcode=session['cart_item'][key]['code']
                    orderitemname=session['cart_item'][key]['name']
                    orderitemprice = float(session['cart_item'][key]['total_price'])
                    orderitemquantity = int(session['cart_item'][key]['quantity'])

                    print(cusid," ",orderitemcode," ",orderitemname," ",orderitemquantity," ",orderitemprice)
                    conn = conn = mysql.connector.connect(host='localhost', user='root', password='ViruVikky123',
                                                          database='kitchen2')
                    cursor = conn.cursor()
                    sql1 = "insert into orders(cusid,order_item_code,order_item_name ,order_item_quantity,order_item_price , order_status)values(%s,%s,%s,%s,%s,%s)"
                    val1 = (cusid,orderitemcode, orderitemname, orderitemquantity, orderitemprice,1)
                    cursor.execute(sql1, val1)
                    conn.commit()
            flash("Your order placed successfuly..!")
            return redirect(url_for('.products'))
        else:
            return redirect(url_for('.products'))

    except Exception as e:
        print(e)






if __name__ == '__main__':

   app.run(debug=True)