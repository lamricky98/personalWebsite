from flask import session, redirect, render_template, flash, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import RegisterForm, LoginForm, UpdateInfoForm, CommentForm, PasswordResetRequestForm, PasswordResetForm
from app.models import User, Post
from app import app, db, bcrypt, login_manager, mail, session, Base, Pages
import os
import secrets
from PIL import Image
from flask_mail import Message


@app.route('/')
def index():
    return redirect('home')


@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/biography')
def biography():
    return render_template("biography.html")


@app.route('/education')
def education():
    return render_template("education.html")


@app.route('/projects')
def projects():
    return render_template("projects.html")


@app.route('/other')
def other():
    return render_template("other.html")


@app.route('/comments', methods=['GET', 'POST'])
def comments():
    comments = Post.query.all()
    form = CommentForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Comment created successfully.', 'success')
        return redirect(url_for('comments'))
    return render_template("comments.html", form=form, comments=comments)


@app.route("/comments/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('You have deleted the comment.', 'success')
    return redirect(url_for('comments'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('profile'))
        else:
            flash('The username and password combination was not found or incorrect.', 'warning')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash(str(session))
    return redirect('/')


@app.route('/profile')
@login_required
def profile():
    profilePic = url_for('static', filename='profilepics/' + current_user.prof_pic)
    return render_template("profile.html", profilePic=profilePic)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_fn)

    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    form = UpdateInfoForm()
    if form.validate_on_submit():
        if current_user and bcrypt.check_password_hash(current_user.password, form.currentpassword.data):
            if form.username.data:
                current_user.username = form.username.data
            if form.email.data:
                current_user.email = form.email.data
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.prof_pic = picture_file
            if form.password.data:
                hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                current_user.password = hashed_pw
            db.session.commit()
            flash('Changes saved successfully.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('You entered a wrong current password. Please try again.', 'warning')
    profilePic = url_for('static', filename='profilepics/' + current_user.prof_pic)
    return render_template("update.html", profilePic=profilePic, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You may now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''Please follow this link to reset your password:
    {url_for('reset_token', token=token, _external=True)}
    
    If you believe this email has been mistakenly sent, please ignore it or delete it.
    '''
    mail.send(msg)


@app.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Please check your email for instructions on resetting your password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('There is no such account with that email. Please try again.', 'warning')
            return redirect(url_for('resetpassword'))
    return render_template('resetpassword.html', form=form)


@app.route('/setnewpassword/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('The link you followed is invalid or expired.', 'warning')
        return redirect(url_for('login'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('You have successfully changed your password. You may log in using your new password.', 'success')
        return redirect(url_for('login'))
    return render_template('setnewpassword.html', form=form)


@app.route('/restful')
def restful():
    pages = session.query(Pages).all()
    return render_template('restful.html', pages=pages)


# This will let us Create a new page and save it in our database
@app.route('/pages/new/', methods=['GET', 'POST'])
def newPage():
    if request.method == 'POST':
        newPage = Pages(title=request.form['name'])
        session.add(newPage)
        session.commit()
        return redirect(url_for('restful'))
    else:
        return render_template('addnew.html')


@app.route("/pages/<int:page_id>/edit/", methods=['GET', 'POST'])
def editPage(page_id):
    editedPage = session.query(Pages).filter_by(id=page_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedPage.title = request.form['name']
            return redirect(url_for('restful'))
    else:
        return render_template('editPage.html', page=editedPage)


# This will let us Delete our page
@app.route('/pages/<int:page_id>/delete/', methods=['GET', 'POST'])
def deletePage(page_id):
    pageToDelete = session.query(Pages).filter_by(id=page_id).one()
    if request.method == 'POST':
        session.delete(pageToDelete)
        session.commit()
        return redirect(url_for('restful', page_id=page_id))
    else:
        return render_template('deletePage.html', page=pageToDelete)


from flask import jsonify


def get_pages():
    pages = session.query(Pages).all()
    return jsonify(pages=[p.serialize for p in pages])


def get_page(page_id):
    pages = session.query(Pages).filter_by(id=page_id).one()
    return jsonify(pages=pages.serialize)


def makeANewPage(title, author, genre):
    addedpage = Pages(title=title)
    session.add(addedpage)
    session.commit()
    return jsonify(Page=addedpage.serialize)


def updatePage(id, title):
    updatedPage = session.query(Pages).filter_by(id=id).one()
    if not title:
        updatedPage.title = title
    session.add(updatedPage)
    session.commit()
    return 'Updated the Page with id %s' % id


def deleteAPage(id):
    pageToDelete = session.query(Pages).filter_by(id=id).one()
    session.delete(pageToDelete)
    session.commit()
    return 'Removed Page with id %s' % id

@app.route('/pagesApi', methods=['GET', 'POST'])
def pagesFunction():
    if request.method == 'GET':
        return get_pages()
    elif request.method == 'POST':
        title = request.args.get('title', '')
        return makeANewPage(title)

@app.route('/pagesApi/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def pageFunctionId(id):
    if request.method == 'GET':
        return get_page(id)

    elif request.method == 'PUT':
        title = request.args.get('title', '')
        return updatePage(id, title)

    elif request.method == 'DELETE':
        return deleteAPage(id)
