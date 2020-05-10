from datetime import datetime
from bankEntity import *
import random

class Admin_dao:

    def add_new_admin(self, user_name, password):
        admin = Admin(user_name = user_name, pw = password)
        self.commit(object = admin, action = "add")

    def get_all_admin(self):
        admins = Admin.query.all()
        return admins

    def get_admin_password(self, user_name):
        admin = Admin.query.filter(Admin.user_name == user_name).first()
        return admin.pw

    def get_admin_id(self, user_name):
        admin = Admin.query.filter(Admin.user_name == user_name).first()
        return admin.id

    def delete_admin(self, user_name):
        admin = Admin.query.filter(Admin.user_name == user_name).first()
        if (len(admin.maintain_history) == 0 or len(admin.application_pool) == 0):
            print(admin)
            self.commit(object = admin, action = "delete")
        else:
            print("can not delete admin: " + admin.user_name)

    def reset_password(self, user_name, new_password):
        admin = Admin.query.filter(Admin.user_name == user_name).first()
        admin.pw = new_password
        self.commit(object = admin, action = "update")

    def create_maintain_his(self, user_name, log):
        admin = Admin.query.filter(Admin.user_name == user_name).first()
        maintain_history = Maintain_history(time = datetime.now(), action = log, admin = admin)
        self.commit(object = maintain_history, action = "add")

    def get_maintain_his(self, admin_id):
        history = Maintain_history.query.filter(Maintain_history.admin_id == admin_id)
        return history

    def commit(self, object, action):
        if action == "add":
            db.session.add(object)
        elif action == "delete":
            db.session.delete(object)
        db.session.commit()


class User_dao:

    def add_new_user(self, name, password, ssn):
        user = User(user_name = name, pw = password, ssn = ssn)
        self.commit(user, action = "add")

    def get_user_password(self, user_name):
        user = User.query.filter(User.user_name == user_name).first()
        return user.pw

    def reset_password(self, user_name, new_password):
        user = User.query.filter(User.user_name == user_name).first()
        user.password = new_password
        self.commit(user, "update")

    def update_user_info(self, user_name, name, dob, sex, phone, address, email):
        user = User.query.filter(User.user_name == user_name).first()
        print(user)
        user_info = User_info.query.filter(User_info.ssn == user.ssn).first()
        print(user_info)
        if user_info == None:
            user_info = User_info(name = name, dob = dob, sex = sex, phone = phone, address = address, email = email, user = user)
            self.commit(object = user_info, action = "add")
        else:
            user_info.name = name
            user_info.dob = dob
            user_info.sex = sex
            user_info.phone = phone
            user_info.address = address
            user_info.email = email
            self.commit(object = user_info, action = "update")

    def get_user_info(self, user_name):
        ssn = User.query.filter(User.user_name == user_name).first().ssn
        user_info = User_info.query.filter(User_info.ssn == ssn).first()
        return user_info

    def list_all_user(self):
        users = User.query.all()
        return users  #return a list

    def get_login_history(self, user_name):
        user = User.query.filter(User.user_name == user_name).first()
        history = user.user_login_history
        return history #return a list

    def add_login_history(self, user_name):
        user = User.query.filter(User.user_name == user_name).first()
        history = User_login_history(user_id = user.id, time = datetime.now())
        self.commit(object = history, action = "add")

    def commit(self, object, action):
        if action == "add":
            db.session.add(object)
        elif action == "delete":
            db.session.delete(object)
        db.session.commit()


class Application_dao:

    def get_application_by_account(self, account_num):
        app = Application_pool.query.filter(Application_pool.account_num == account_num).first()
        return app

    def add_new_application(self, user_name, type):
        user = User.query.filter(User.user_name == user_name)
        application = Application_pool(user = user, type = type, apply_date = datetime.now())
        self.commit(object = application, action = "add")

    def approve_application(self, account_num, admin_id):
        application = Application_pool.query.filter(Application_pool.account_num == account_num).first()
        application.approve_date = datetime.now()
        application.admin_id = admin_id

        accounts = Account.query.all()
        cardNums = []
        for a in accounts:
            cardNums.append(a.card_num)
        generateNewCard = True
        while generateNewCard:
            newCardNum = random.randint(1, 1000000000)
            if newCardNum in cardNums:
                generateNewCard = True
            else:
                generateNewCard = False
        if application.type == "credit":
            newAccount = Account(ap = application, card_num = newCardNum, credit_balance = 1000)
        else:
            newAccount = Account(ap = application, card_num = newCardNum, credit_balance = 0)
        # self.commit(object = application, action = "update")
        self.commit(object = newAccount, action = "add")

    def deactive_account(self, account_num):
        application = Application_pool.query.filter(Application_pool.account_num == account_num).first()
        application.deactive_date = datetime.now()
        self.commit(object = application, action = "update")

    def get_user_application(self, user_name):
        application = db.engine.execute("select a.account_num, a.type, a.apply_date, a.approve_date, a.deactive_date " +
                                        "from Application_pool as a join User_Application as ua on a.account_num = ua.account_num " +
                                        "join User as u on u.id = ua.user_id " +
                                        "where u.user_name = '%s'" % user_name)
        # print(application.first())
        return application

    def get_all_application(self):
        applications = db.engine.execute("select u.user_name, a.account_num, a.type, a.apply_date, a.approve_date, a.deactive_date " +
                                        "from Application_pool as a join User_Application as ua on a.account_num = ua.account_num " +
                                        "join User as u on u.id = ua.user_id ")
        return applications

    def get_all_active_account(self):
        # active_accounts = db.session.query(Application_pool, Account).outerjoin(Account, Application_pool.account_num == Account.account_num).filter(Application_pool.deactive_date == None).all()
        active_accounts = db.engine.execute("select u.name, a.account_num, a.card_num, ap.type, a.credit_balance " +
                                            "from User_info as u join User as ur on u.ssn = ur.ssn " +
                                            "join User_Application as ua on ur.id = ua.user_id " +
                                            "join Application_pool as ap on ua.account_num = ap.account_num " +
                                            "join Account as a on a.account_num = ap.account_num where ap.deactive_date is Null")
        return active_accounts

    def get_user_account_info(self, user_name):
        accounts = db.engine.execute("select a.account_num, a.card_num, ap.type, a.credit_balance " +
                                         "from User_info as u join User as ur on u.ssn = ur.ssn " +
                                         "join User_Application as ua on ur.id = ua.user_id " +
                                         "join Application_pool as ap on ua.account_num = ap.account_num " +
                                         "join Account as a on a.account_num = ap.account_num where ap.approve_date is not Null " +
                                         "and ap.deactive_date is Null " +
                                         "and ur.user_name = '%s'" % user_name)
        return accounts

    def commit(self, object, action):
        if action == "add":
            db.session.add(object)
        elif action == "delete":
            db.session.delete(object)
        db.session.commit()


class Transaction_dao:

    def get_transactions_account_num(self, account_num):
        transactions = db.session.query(Account, Transaction).outerjoin(Transaction, Account.card_num == Transaction.card_num).filter(Account.account_num == account_num).all()
        return transactions

    def get_transactions_card_num(self, card_num):
        transactions = Transaction.query.filter(Transaction.card_num == card_num)
        return transactions

    def new_transaction(self, card_num, receive_card_num, amount):
        if receive_card_num == None:
            new_trans = Transaction(card_num = card_num, time = datetime.now(), amount = amount)
            account = Account.query.filter(Account.card_num == card_num).first()
            account.credit_balance -= int(amount)
            self.commit(object = new_trans, action = "add")
        else:
            new_trans = Transaction(card_num = card_num, time = datetime.now(), amount = amount, receive_card_num = receive_card_num)
            account_rec = Account.query.filter(Account.card_num == receive_card_num).first()
            account_rec.credit_balance += amount
            account = Account.query.filter(Account.card_num == card_num).first()
            account.credit_balance -= int(amount)
            self.commit(object = new_trans, action = "add")

    def get_all_transactions(self):
        transactions = Transaction.query.all()
        return transactions

    def commit(self, object, action):
        if action == "add":
            db.session.add(object)
        elif action == "delete":
            db.session.delete(object)
        db.session.commit()
