from flask import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/bank'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

User_application = db.Table("User_Application",
    db.Column("user_id", db.Integer, db.ForeignKey("User.id")),
    db.Column("account_num", db.Integer, db.ForeignKey("Application_pool.account_num"))
)

class User(db.Model):
    __tablename__ = "User"

    id = db.Column("id", db.Integer, primary_key = True)
    user_name = db.Column("user_name", db.Unicode)
    pw = db.Column("password", db.Unicode)
    ssn = db.Column("ssn", db.Integer)

    user_info = db.relationship("User_info", backref = "user")
    user_login_history = db.relationship("User_login_history", backref = "user")
    userApp = db.relationship("Application_pool", secondary = User_application, backref = db.backref("user", lazy = "dynamic"))


class User_info(db.Model):
    __tablename__ = "User_info"

    ssn = db.Column(db.Integer, db.ForeignKey('User.ssn'), primary_key = True)
    name = db.Column("name", db.Unicode)
    dob = db.Column("dob", db.DateTime)
    sex = db.Column("sex", db.Unicode)
    phone = db.Column("phone", db.Integer)
    address = db.Column("address", db.Unicode)
    email = db.Column("email", db.Unicode)


class User_login_history(db.Model):
    __tablename__ = "User_login_history"

    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), primary_key = True)
    time = db.Column(db.DateTime, primary_key = True)


class Admin(db.Model):
    __tablename__ = "Admin"

    id = db.Column("id", db.Integer, primary_key = True)
    user_name = db.Column("user_name", db.Unicode)
    pw = db.Column("password", db.Unicode)

    maintain_history = db.relationship("Maintain_history", backref = "admin")
    application_pool = db.relationship("Application_pool", backref = "admin")


class Maintain_history(db.Model):
    __tablename__ = "maintain_history"

    admin_id = db.Column(db.Integer, db.ForeignKey("Admin.id"), primary_key = True)
    time = db.Column("time", db.DateTime, primary_key = True)
    action = db.Column("action", db.Unicode)


class Application_pool(db.Model):
    __tablename__ = "Application_pool"

    account_num = db.Column("account_num", db.Integer, primary_key = True)
    type = db.Column("type", db.Unicode)
    apply_date = db.Column("apply_date", db.DateTime)
    approve_date = db.Column("approve_date", db.DateTime)
    deactive_date = db.Column("deactive_date", db.DateTime)
    admin_id = db.Column(db.Integer, db.ForeignKey("Admin.id"))

    account = db.relationship("Account", backref = "ap")
    # userApp = db.relationship("User_application", backref = db.backref("application", lazy = "dynamic"))


class Account(db.Model):
    __tablename__ = "Account"

    account_num = db.Column(db.Integer, db.ForeignKey("Application_pool.account_num"), primary_key = True)
    card_num = db.Column("card_num", db.Integer, primary_key = True)
    credit_balance = db.Column("credit_balance", db.Float, primary_key = True)

    trans_forward = db.relationship("Transaction", backref = "account")


class Transaction(db.Model):
    __tablename__ = "Transaction"

    card_num = db.Column(db.Integer, db.ForeignKey("Account.card_num"), primary_key = True)
    time = db.Column("time", db.DateTime, primary_key = True)
    receive_card_num = db.Column("rec_card_num", db.Integer)
    amount = db.Column("amount", db.Float)
