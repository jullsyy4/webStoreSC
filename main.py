import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
load_dotenv()

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from cloudipsp import Api, Checkout

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sc-store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):  #name titles
        return self.title


admin = Admin(app)
admin.add_view(ModelView(Item, db.session))


with app.app_context():
    db.create_all()
    db.session.close()


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', items=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']

        item = Item(title=title, price=price, description=description)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an error when adding an item!"
    else:
        return render_template('create.html')


@app.route('/<int:id>/delete')
def delete(id):
    item = Item.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/')
    except:
        return "There was an error when deleting an item"


@app.route('/<int:id>/update', methods=['POST', 'GET'])
def update(id):
    item = Item.query.get(id)
    if request.method == "POST":
        item.title = request.form['title']
        item.price = request.form['price']
        item.description = request.form['description']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "An error occurred while trying to update the product!"
    else:
        return render_template('update.html', item=item)


@app.route('/buy/<int:id>')
def buy(id):
    item = db.session.get(Item, id)

    secret_key_buy = os.getenv('SECRET_KEY_BUY')
    merchant_id = os.getenv('MERCHANT_ID')
    api = Api(merchant_id=merchant_id,
              secret_key=secret_key_buy)
    checkout = Checkout(api=api)
    data = {
        "currency": "UAH",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


if __name__ == "__main__":
    app.secret_key = os.getenv('SECRET_KEY')
    app.run()