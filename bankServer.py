from bankDao import *


@app.route("/")
def customer_welcome():
    return render_template("customer_welcome.html")


@app.route("/user/login", methods = ['POST'])
def user_login():
    udao = User_dao()

    users = udao.list_all_user()
    user_names = []
    for u in users:
        user_names.append(u.user_name)

    user_name = request.form['username']
    password = request.form['password']

    if user_name in user_names:
        session['user_name'] = user_name
        if password == udao.get_user_password(user_name = user_name):
            user_info = udao.get_user_info(user_name = user_name)
            udao.add_login_history(session['user_name'])
            name = user_info.name
            session['username'] = name
            return render_template("customer_login_page.html", user_info = user_info)
        else:
            return "Please provide correct password!"
    else:
        return "user doesn't exist!!!"


@app.route("/user/application", methods = ['GET', 'POST'])
def user_application():
    if 'user_name' in session:
        adao = Application_dao()
        # print(session['user_name'])
        if request.method == 'POST':
            adao.add_new_application(user_name = session['user_name'], type = request.form['type'])
        application_history = adao.get_user_application(session['user_name'])
        # print(application_history)
        return render_template("application.html", history = application_history, user_name = session['username'])


@app.route("/user/info", methods = ['GET', 'POST'])
def update_info():
    if 'user_name' in session:
        udao = User_dao()
        message = None
        if request.method == 'POST':
            udao.update_user_info(user_name = session['user_name'], name = request.form['name'], dob = request.form['dob'], sex = request.form['sex'], phone = request.form['phone'], address = request.form['address'], email = request.form['email'])
            message = "You have successfully updated your persional information."
            # flash("You have successfully updated your persional information.")
        user_info = udao.get_user_info(user_name = session['user_name'])
        return render_template("updating_info.html", user_info = user_info, message = message)


@app.route("/user/signup", methods = ["GET"])
def goto_user_signup():
    return render_template("user_signup.html")


@app.route("/user/signup", methods = ["POST"])
def user_signup():
    udao = User_dao()

    users = udao.list_all_user()
    user_names = []
    for u in users:
        user_names.append(u.user_name)

    user_name = request.form['user_name']
    if user_name not in user_names:
        password = request.form['password']
        name = request.form['name']
        ssn = request.form['ssn']
        dob = request.form['dob']
        sex = request.form['sex']
        phone = request.form['phone']
        address = request.form['address']
        email = request.form['email']

        udao.add_new_user(user_name, password, ssn)
        udao.update_user_info(user_name, name, dob, sex, phone, address, email)
        return redirect(url_for('customer_welcome'))
    else:
        return "user_name already exist!!!"


@app.route("/user/account", methods = ['GET'])
def user_account():
    if 'user_name' in session:
        adao = Application_dao()
        accounts_info = adao.get_user_account_info(user_name = session['user_name'])
        return render_template("account_info.html", accounts_info = accounts_info, username = session['username'])


@app.route("/user/transaction", methods = ['POST'])
def user_transaction():
    if 'user_name' in session:
        card_num = request.form['card_num']
        tdao = Transaction_dao()
        if request.form.get('amount', None):
            receive_card_num = request.form.get('receive_card_num', None)
            if receive_card_num != "":
                receive_card_num = int(receive_card_num)
            else:
                print("receive_card_num is None!!!")
                receive_card_num = None
            tdao.new_transaction(card_num = card_num, receive_card_num = receive_card_num, amount = int(request.form['amount']))
        transactions = tdao.get_transactions_card_num(card_num = card_num)
        return render_template("user_transaction.html", username = session['username'], trans = transactions, card_num = card_num)


@app.route("/user/login_history", methods = ['GET'])
def user_login_history():
    if 'user_name' in session:
        udao = User_dao()
        history = udao.get_login_history(user_name = session['user_name'])
        return render_template("login_history.html", history = history, username = session['username'], user_name = session['user_name'])


@app.route("/user/logout")
def logout():
    if 'user_name' in session:
        session.pop('user_name', None)
        session.pop('username', None)
    return redirect(url_for('customer_welcome'))


##########################################################################################################################################


@app.route("/admin")
def admin_page():
    return render_template("admin_welcome.html")

@app.route("/admin/login", methods = ['POST'])
def admin_login():
    user_name = request.form['user_name']
    password = request.form['password']
    adao = Admin_dao()
    admins = adao.get_all_admin()
    usernames = []
    for a in admins:
        usernames.append(a.user_name)
    if user_name in usernames:
        if password == adao.get_admin_password(user_name = user_name):
            session['admin_name'] = user_name
            session['admin_id'] = adao.get_admin_id(user_name = user_name)
            return render_template("admin_login_page.html", user_name = session['admin_name'], id = session['admin_id'])
        else:
            return "Please provide correct password!"
    else:
        return "This admin doesn't exist!"


@app.route("/admin/transactions", methods = ['GET'])
def transactions():
    if 'admin_name' in session:
        tdao = Transaction_dao()
        transactions = tdao.get_all_transactions()
        return render_template("all_transactions.html", transactions = transactions, user_name = session['admin_name'])
    else:
        return "time out"


@app.route("/admin/application", methods = ['GET'])
def application():
    if 'admin_name' in session:
        adao = Application_dao()
        applications = adao.get_all_application()
        return render_template("all_applications.html", applications = applications, user_name = session['admin_name'])


@app.route("/admin/active", methods = ['POST'])
def active_account():
    if 'admin_name' in session:
        adao = Application_dao()
        num = request.form['account_num']
        app = adao.get_application_by_account(account_num = int(num))
        if app != None and app.approve_date == None:
            adao.approve_application(account_num = num, admin_id = session['admin_id'])
            adminDao = Admin_dao()
            log = "approve the new application with account number = " + str(num)
            adminDao.create_maintain_his(user_name = session['admin_name'], log = log)
        else:
            return "This application was already approved or the application doesn't exist."
        return redirect(url_for('application'))


@app.route("/admin/deactive", methods = ['POST'])
def deactive_account():
    if 'admin_name' in session:
        adao = Application_dao()
        num = request.form['account_num']
        app = adao.get_application_by_account(account_num = int(num))
        if app != None and app.deactive_date == None:
            adao.deactive_account(account_num = int(num))
            adminDao = Admin_dao()
            log = "deactive the account with account number = " + str(num)
            adminDao.create_maintain_his(user_name = session['admin_name'], log = log)
        else:
            return "This account was already deactived or the account doesn't exist."
        return redirect(url_for('application'))


@app.route("/admin/m_history", methods = ['GET'])
def maintain_history():
    if 'admin_name' in session:
        adminDao = Admin_dao()
        history = adminDao.get_maintain_his(admin_id = session['admin_id'])
        return render_template("maintain_history.html", history = history, user_name = session['admin_name'])


@app.route("/admin/logout")
def admin_logout():
    if 'admin_name' in session:
        session.pop('admin_name', None)
        session.pop('admin_id', None)
    return render_template("admin_welcome.html")


if __name__ == "__main__":
    app.run(debug = True)
