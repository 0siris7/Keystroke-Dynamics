from flask import Flask,render_template,request,redirect,url_for,flash,session
import database as db
import demjson
import urllib
import numpy
import sklearn
from core import *

app=Flask(__name__)
app.secret_key = "sdfghjkl"

def get_data_from(url):
	data = urllib.request.urlopen(url)

	return demjson.decode(data.read())

@app.route('/',methods=['get','post'])
def home():
	return render_template('user_app/public_home.html')


@app.route('/login_action/',methods=['get','post'])
def login_action():
	data = {}
	if 'login' in request.form:
		name=request.form['username']
		#pas=request.form['password']
		features=request.form['features']
		s="select * from user_login where username='%s'"%(name)
		sel=db.select(s)
		if len(sel)>0:
			bool = get_login_id(features)
			print(bool)
			if bool != -1: 
				session['login_id'] = sel[0]['login_id']
				data['status'] = 'success'
				data['data'] = sel
			else:
				data['status'] = 'failed'
				data['reason'] = 'Time difference'
		else:
			data['status'] = 'failed'
			data['reason'] = 'Username or password is incorrect'
	return demjson.encode(data)

@app.route('/register_action/',methods=['get','post'])
def register_action():
	if 'register' in request.form:
		fnam=request.form['fname']
		lnam=request.form['lname']
		ag=request.form['age']
		d=request.form['dob']
		plac=request.form['place']
		ci=request.form['city']
		st=request.form['state']
		eml=request.form['email']
		phn=request.form['phone']
		user=request.form['user']
		passw=request.form['pass']
		features=request.form['features']
		lo="insert into user_login(username,password,login_type,features)values('%s','%s','user','%s')"%(user,passw,features)
		log=db.insert(lo)
		q="insert into users(login_id,f_name,l_name,age,dob,place,city,state,email,phone)values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(log,fnam,lnam,ag,d,plac,ci,st,eml,phn)
		res=db.insert(q)
		train()
		return "ok"

@app.route('/logout/')
def logout():
	session.clear()
	return redirect(url_for('home'))


@app.route('/user_home',methods=['get','post'])
def user_home():
	login_id = session['login_id']
	q = db.select("select f_name from users where login_id = '%s' " %(login_id))[0]['f_name']
	print(q)
	return render_template('user_app/user_home.html',data=q)


@app.route('/add_bank_account',methods=['get','post'])
def add_bank_account():
	data = ""
	if "submit" in request.form:
		login_id = session['login_id']
		dob=request.form['dob']
		account_no=request.form['account_no']
		url = "http://127.0.0.1:5001/api/add_bank_account?dob=%s&bank_account_no=%s" % (dob,account_no)
		data = get_data_from(url)
		if data['status'] == 'success':
			print(login_id)
			q = "insert into user_account(user_id,account_id,user_account_status)values((select user_id from users where login_id='%s'),'%s','pending')" % (login_id,account_no)
			db.insert(q)
			return redirect(url_for('enter_otp'))
		else:
			flash(data['reason'])
	q = "select * from user_account where user_id=(select user_id from users where login_id='%s')" % session['login_id'] 
	res = db.select(q)
	return render_template('user_app/user_add_bank_account.html',data=res)


@app.route('/enter_otp',methods=['get','post'])
def enter_otp():
	login_id = session['login_id']
	if "submit" in request.form:
		otp=request.form['otp']
		q="select * from user_account where user_id=(select user_id from users where login_id='%s') and user_account_status='pending'" % login_id
		res = db.select(q)
		if res:
			account_no=res[0]['account_id']
			url = "http://127.0.0.1:5001/api/enter_otp?otp=%s&account_no=%s" % (otp,account_no)
			data = get_data_from(url)
			if data['status'] == 'success':
				q = "update user_account set user_account_status='active' where user_id=(select user_id from users where login_id='%s') and account_id='%s'" % (login_id,account_no)
				db.update(q)
				return redirect(url_for('user_home'))
	return render_template('user_app/user_enter_otp.html')


@app.route('/transfer',methods=['get','post'])
def transfer():
	if "submit" in request.form:
		to_account_no=request.form['to_account_no']
		from_account_no=request.form['from_account_no']
		amount=request.form['amount']
		url = "http://127.0.0.1:5001/api/transfer?to_account_no=%s&from_account_no=%s&amount=%s" % (to_account_no,from_account_no,amount)
		data = get_data_from(url)
		if data['status'] == 'success':
			return redirect(url_for('user_home'))
		else:
			flash(data['reason'])
	q = "select * from user_account where user_id=(select user_id from users where login_id='%s')" % session['login_id']
	res = db.select(q)
	return render_template('user_app/user_transfer.html',data=res)


@app.route('/user_view_trasaction',methods=['get','post'])
def user_view_trasaction():
	login_id = session['login_id']
	q = "select * from user_account where user_id=(select user_id from user_login where login_id='%s')" % login_id
	res = db.select(q)
	if res:
		from_account_no = res[0]['account_id']
	url = "http://127.0.0.1:5001/api/transaction?from_account_no=%s" % from_account_no
	data = get_data_from(url)
	return render_template('user_app/user_view_trasaction.html',data=data['data'])
	return render_template('user_app/user_view_trasaction.html')

@app.route('/user_view_balance',methods=['get','post'])
def user_view_balance():
	login_id = session['login_id']
	data = {}
	q="select * from user_account where user_id=(select user_id from users where login_id='%s')" % login_id
	res = db.select(q)
	print(res)
	if res:
		account_no=res[0]['account_id']
		url = "http://127.0.0.1:5001/api/view_account_balance?acc_no=%s" % account_no
		data = get_data_from(url)
	else:
		flash("Account not available.Try again")
	return render_template('user_app/view_accbaal.html',data=data)



















# @app.route('/bank_trans',methods=['get','post'])
# def bank_trans():
# 	if 'start transaction' in request.form:
# 		dt=request.form['datetime']
# 		fc=request.form['fromaccount']
# 		tc=request.form['toaccount']
# 		amt=request.form['amount']
# 		t="insert into bank_transaction(datetime,from_id,to_id,amount)values('%s','%s','%s','%s')"%(dt,fc,tc,amt)
# 		trans=dbs.insert(t)
# 	return render_template('bank_app/bank_trans.html')

# @app.route('/adminpage',methods=['get','post'])
# def adminpage():
	
# 	return render_template('user_app/adminpage.html')


# @app.route('/view_transaction',methods=['get','post'])
# def view_transaction():
# 	data=""
# 	if 'submit' in request.form:
# 		ac_id=request.form['account_id']
# 		url="http://127.0.0.1:5001/api/add_view_transaction?ac_id='%s'"%(ac_id)
# 		data=get_data_from(url)
# 	return render_template('user_app/view_transaction.html',data=data)

# @app.route('/view_transaction1',methods=['get','post'])
# def view_transaction1():
# 	data=""
# 	if 'submit' in request.form:
# 		acc_id=request.form['account_id']
# 		balance=request_form['balance']
# 		url="http://127.0.0.1:5001/api/add_view_transaction1?ac_id='%s'"%(acc_id)
# 		data=get_data_from(url)
# 	return render_template('user_app/view_transaction1.html',data=data)


# @app.route('/view_accbal',methods=['get','post'])
# def view_accbal():
# 	data=""
# 	if 'submit' in request.form:
# 		acbal=request.form['accbal']
# 		s="select account_id from bank_account where balance='%s'" %(acbal)
# 		sel=db1.select(s)
# 		account_id=sel[0]['account_id']
# 		url="http://127.0.0.1:5001/api/add_view_accbal?account_id='%s'" %(account_id)
# 		data=get_data_from(url)
# 	return render_template('user_app/view_accbal.html',data=data)


# @app.route('/request_fund',methods=['get','post'])
# def request_fund():
# 	data=""
# 	if 'submit' in request.form:
# 		acno=request.form['accno']
# 		url="http://127.0.0.1:5001/api/add_request_fund?acno=%s" %(acno)
# 		data=get_data_from(url)
# 	return render_template('user_app/request_fund.html',data=data)


# @app.route('/transfer_fund',methods=['get','post'])
# def transfer_fund():
# 	data=""
# 	if 'submit' in request.form:
# 		acc_no = request.form['accno']
# 		url="http://127.0.0.1:5001/api/add_transfer_fund?acc_no=%s" %(acc_no)
# 		data=get_data_from(url)
# 	return render_template('user_app/transfer_fund.html',data=data)



# @app.route('/view_user',methods=['get','post'])
# def view_user():
# 	v="select * from users"
# 	view=db.select(v)
# 	return render_template('user_app/view_user.html',data=view)



# @app.route('/view_accbaal',methods=['get','post'])
# def view_accbaal():
# 	data=""
# 	account_id=request.form['account_id']
# 	print(account_id)
# 	balance=request.form['balance']
# 	url="http://127.0.0.1:5001/api/add_view_accbaal"
# 	data=get_data_from(url)
# 	return render_template('bank_app/view_accbaal.html',data=data)



app.run(debug=True,port=5004)

