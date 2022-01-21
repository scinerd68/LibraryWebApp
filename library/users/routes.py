from collections import Counter
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from library import db, bcrypt
from library.models import Book, BorrowHistory, Librarian, User
from library.users.forms import LoginForm, RegistrationForm
from library.utils import role_required, load_user


users = Blueprint('users', __name__)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        if form.librarian.data == True:
            print("librarian")
            user = Librarian.query.filter_by(email=form.email.data).first()
            session['account_type'] = 'librarian'
        else:
            user = User.query.filter_by(email=form.email.data).first()
            session['account_type'] = 'user'
        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            print("User's status:", user.is_authenticated)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("main.home"))
        else:
            session.clear()
            flash("Login unsuccessful. Check email and password", "danger")
            return redirect(url_for("users.login"))
    
    return render_template("login2.html", form=form, title="Login")


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                    last_name=form.last_name.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You can now login.", "success")
        return redirect(url_for("users.login"))

    return render_template("register2.html", form=form, title="Register")


@users.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.home"))


@users.route("/account")
@role_required("user")
def account():
    borrow_history = BorrowHistory.query.with_entities(BorrowHistory.book_id).\
                    filter_by(user_id=current_user.id).all()
    if len(borrow_history) != 0:
        count_book = Counter(borrow_history)
        most_borrowed_book_id = max(count_book, key=count_book.get)[0]
        book = Book.query.get(most_borrowed_book_id)
        authors = [author.name for author in book.authors]
    else: 
        book = None
        authors = None

    return render_template("account.html", book=book, authors=authors, current_user=current_user)


@users.route("/user", methods={"GET", "POST"})
@role_required("librarian")
def user_account():
    book = None
    user = None
    if request.method == "POST":
        if 'search_form' in request.form:
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            borrow_history = BorrowHistory.query.with_entities(BorrowHistory.book_id).\
                    filter_by(user_id=user_id).all()
            if len(borrow_history) != 0:
                count_book = Counter(borrow_history)
                most_borrowed_book_id = max(count_book, key=count_book.get)[0]
                book = Book.query.get(most_borrowed_book_id)
                authors = [author.name for author in book.authors]
            else: 
                book = None
                authors = None
            return render_template('user.html', user=user, book=book, authors=authors)

        elif 'recharge' in request.form:
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            user.balance = 800000
            db.session.commit()
            user = User.query.get(user_id)
            borrow_history = BorrowHistory.query.with_entities(BorrowHistory.book_id).\
                    filter_by(user_id=user_id).all()
            if len(borrow_history) != 0:
                count_book = Counter(borrow_history)
                most_borrowed_book_id = max(count_book, key=count_book.get)[0]
                book = Book.query.get(most_borrowed_book_id)
                authors = [author.name for author in book.authors]
            else: 
                book = None
                authors = None
            return render_template('user.html', user=user, book=book, authors=authors)

        elif 'activate' in request.form:
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            user.activated = True
            db.session.commit()
            borrow_history = BorrowHistory.query.with_entities(BorrowHistory.book_id).\
                    filter_by(user_id=user_id).all()
            if len(borrow_history) != 0:
                count_book = Counter(borrow_history)
                most_borrowed_book_id = max(count_book, key=count_book.get)[0]
                book = Book.query.get(most_borrowed_book_id)
                authors = [author.name for author in book.authors]
            else: 
                book = None
                authors = None
            return render_template('user.html', user=user, book=book, authors=authors)

        elif 'deactivate' in request.form:
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            user.activated = False
            db.session.commit()
            borrow_history = BorrowHistory.query.with_entities(BorrowHistory.book_id).\
                    filter_by(user_id=user_id).all()
            if len(borrow_history) != 0:
                count_book = Counter(borrow_history)
                most_borrowed_book_id = max(count_book, key=count_book.get)[0]
                book = Book.query.get(most_borrowed_book_id)
                authors = [author.name for author in book.authors]
            else: 
                book = None
                authors = None
            return render_template('user.html', user=user, book=book, authors=authors)

    return render_template('user.html', book=book, user=user)