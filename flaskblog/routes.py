import os  
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, session
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, ChooseForm, ReviewfillForm, ProductForm, AdminForm, SearchForm, SortForm, ForgotForm, ChangeForm, DeleteForm, ScoreForm
from flaskblog.models import User, Post, Product, Review, Admin
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.dictionary import *
import socket
from sqlalchemy import func
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
import re
import string



posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

df_manual_testing = pd.read_csv("review.csv")
df_manual_testing.head(10)
df_manual_testing.shape
df_manual_testing.columns
df=df_manual_testing.drop(["_id/$oid","reviewerID","asin","reviewerName","helpful/0","overall","summary","unixReviewTime","reviewTime","category"], axis = 1)
df.head(5)
df.reset_index(inplace = True)
df.drop(["index"], axis = 1, inplace = True)
df.columns
def wordopt(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W"," ",text) 
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)    
    return text


df["reviewText"] = df["reviewText"].apply(wordopt)
x = df["reviewText"]
y = df["class"]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)

from sklearn.feature_extraction.text import TfidfVectorizer
vectorization = TfidfVectorizer()
xv_train = vectorization.fit_transform(x_train)
xv_test = vectorization.transform(x_test)

from sklearn.linear_model import LogisticRegression
LR = LogisticRegression(max_iter=50000)
LR.fit(xv_train,y_train)
pred_lr=LR.predict(xv_test)
LR.score(xv_test, y_test)


from sklearn.tree import DecisionTreeClassifier
DT = DecisionTreeClassifier()
DT.fit(xv_train, y_train)
pred_dt = DT.predict(xv_test)
DT.score(xv_test, y_test)


from sklearn.ensemble import GradientBoostingClassifier
GBC = GradientBoostingClassifier(random_state=0)
GBC.fit(xv_train, y_train)
pred_gbc = GBC.predict(xv_test)
GBC.score(xv_test, y_test)


from sklearn.ensemble import RandomForestClassifier
RFC = RandomForestClassifier(random_state=0)
RFC.fit(xv_train, y_train)
pred_rfc = RFC.predict(xv_test)
RFC.score(xv_test, y_test)


def output_lable(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
        
        

        
def manual_testing(news):
    testing_news = {"text":[news]}
    new_def_test = pd.DataFrame(testing_news)
    new_def_test["text"] = new_def_test["text"].apply(wordopt) 
    new_x_test = new_def_test["text"]
    new_xv_test = vectorization.transform(new_x_test)
    pred_LR = LR.predict(new_xv_test)
    pred_DT = DT.predict(new_xv_test)
    pred_GBC = GBC.predict(new_xv_test)
    pred_RFC = RFC.predict(new_xv_test)
    l = pred_LR[0] + pred_DT[0] + pred_GBC[0] + pred_RFC[0]
    analysis = [output_lable(pred_LR[0]), output_lable(pred_DT[0]), output_lable(pred_GBC[0]), output_lable(pred_RFC[0])]
    return analysis
    #return output_lable(pred_LR[0]) + output_lable(pred_DT[0]) + output_lable(pred_GBC[0]) +  output_lable(pred_RFC[0])


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    result = 1
    form = SearchForm()
    form1 = SortForm()
    form2 = ScoreForm()

    if form1.identifier.data == 'FORM1' and form1.validate_on_submit():
        if session['res'] == 'n':
            product_all = Product.query.order_by(Product.item_name.asc()).all()
            return render_template('home.html', posts=posts, product=product_all, form=form, form1=form1, form2=form2)
    
    if form2.identifier.data == 'FORM2' and form2.validate_on_submit():
        if session['res'] == 'n':
            product_all = Product.query.order_by(Product.rate.desc()).all()
            return render_template('home.html', posts=posts, product=product_all, form=form, form1=form1, form2=form2)

    product_all = Product.query.all()
    if form.identifier.data == 'FORM' and form.validate_on_submit():
        result = form.productname.data
        u_result = Product.query.filter(func.lower(Product.item_name) == func.lower(result)).all()
        if u_result:
            return render_template('home.html', posts=posts, product=u_result, form=form, form1=form1, form2=form2, result=result)
        product_all = Product.query.filter_by(item_name = result).all()
    session['res']='n'
    return render_template('home.html', posts=posts, product=product_all, form=form, form1=form1, form2=form2, result=result)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/detail/<item>", methods=['GET', 'POST'])
def detail(item):
    form = ReviewfillForm()
    item1 = item
    session['item']=item
        
    
    if 'item' in session:
        product_1 = Product.query.filter_by(id = item).first()
        item = session['item']
        review = Review.query.filter_by(item_id = item).order_by(Review.date.desc()).all()
        if current_user.is_authenticated:
            c_name = current_user.username
            r_check = Review.query.filter_by(item_id = item, rev_name = c_name).first()
            if r_check is None:
                hide = 0
            else:
                hide = 1
        else:
            hide = 1
        
        if request.method == 'POST':
            if current_user.is_authenticated:
                rev_text = str(request.form['review'])
                analysis = manual_testing(rev_text)
                lr = analysis[0]
                dt = analysis[1]
                gbc = analysis[2]
                rfc = analysis[3]
                staus = lr + dt + gbc + rfc
                if staus >= 2:
                    status_value = 1
                else:
                    status_value = 0
                username = current_user.username
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
                rev_chk = Review.query.filter_by(ip = ip_address, item_id = item).all()
                if rev_chk is None:
                    i_mark = 0
                else:
                    i_mark = 1

                text = rev_text.lower()
                rate = rating(text)
                rev_1 = Review(rev_name =username, item_id =item, rev_text =rev_text, staus =status_value, lr =lr, dt = dt, gbc =gbc, rfc =rfc, rate =rate, mark =0, contra =1, c_ignore =0, ip =ip_address, i_mark =i_mark, i_ignore =0)
                db.session.add(rev_1)
                db.session.commit()
                score = Review.query.filter_by(item_id = item).all()
                
                a_score = 0.0
                count = 0
                for n in score:
                    a_score = a_score + n.rate
                    count = count + 1

                if a_score == 0:
                    t_score = a_score
                else:
                    t_score = a_score/count

                rows_changed = Product.query.filter_by(id=item).update(dict(rate=t_score))
                db.session.commit()
                flash('Your review has been provided!', 'success')
                return redirect(url_for('detail', item = item))
            else:
                flash('Login to give review!', 'success')
                return redirect(url_for('login'))
        return render_template('detail.html', title='Product', item=item, product=product_1, form=form, review=review, hide=hide)
    return render_template('detail.html', title='About')





@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/product", methods=['GET', 'POST'])
def product():
    form = ProductForm()
    form1 = DeleteForm()
    title = 'Admin'
    usr = current_user.username
    if usr == title:
        if form.validate_on_submit():
            picture_file = save_picture(form.image.data)
            image_file = picture_file
            item = form.productname.data
            detail = form.detail.data
            platform = form.platform.data
            category = form.category.data
            product = Product(item_name =item, details=detail, image=image_file, category=category, platform=platform)
            db.session.add(product)
            db.session.commit()
            flash('New product has been uploded!', 'success')
            return redirect(url_for('product'))
    else:
        flash('Admin autherization required!', 'success')
        return redirect(url_for('admin'))
    return render_template('product.html', title=title, form=form, usr=usr, form1=form1)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AdminForm()
    if form.validate_on_submit():
        if form.username.data == 'Admin':
            admin = User.query.filter_by(username=form.username.data).first()
            if admin and bcrypt.check_password_hash(admin.password, form.password.data):
                login_user(admin, remember=form.remember.data)
                
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')  
    return render_template('admin.html', title='Admin', form=form)


@app.route("/admreview", methods=['GET', 'POST'])
def admreview():
    rev_1 = Review.query.filter_by(staus =0, mark =0).all()
    rev_2= Review.query.filter_by(i_mark =1, i_ignore =0).all()
    return render_template('admreview.html',review1=rev_1, review2=rev_2)

   
@app.route("/delete/<rid>", methods=['GET', 'POST'])
def delete(rid):
    rev = Review.query.filter_by(id=rid).first()
    db.session.delete(rev)
    db.session.commit()
    return redirect(url_for('admreview'))

@app.route("/ignore/<rid>", methods=['GET', 'POST'])
def ignore(rid):
    ign = Review.query.get(rid)
    ign.mark = 1
    db.session.commit()
    return redirect(url_for('admreview'))

@app.route("/ignoreip/<rid>", methods=['GET', 'POST'])
def ignoreip(rid):
    ign = Review.query.get(rid)
    ign.i_ignore = 1
    db.session.commit()
    return redirect(url_for('admreview'))

@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    form = ForgotForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, username=form.username.data).all()
        if user is None:
            flash('Wrong Email or Username', 'danger') 
        else:
            session['username'] = form.username.data
            return redirect(url_for('change'))
    return render_template('forgot.html', form=form)

@app.route("/change", methods=['GET', 'POST'])
def change():
    form = ChangeForm()
    if form.validate_on_submit():
        user = session['username']
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        rows_changed = User.query.filter_by(username = user).update(dict(password = hashed_password))
        db.session.commit()
        flash('Login with new password', 'success')
        return redirect(url_for('login'))
    return render_template('change.html', form=form)


@app.route("/pdelete", methods=['GET', 'POST'])
def pdelete():
    form = DeleteForm()    
    if form.validate_on_submit():
        name = form.productname.data
        pdt = Product.query.filter_by(item_name=name).first()
        db.session.delete(pdt)
        db.session.commit()
        flash('Product Removed', 'success')
    return redirect(url_for('product'))    