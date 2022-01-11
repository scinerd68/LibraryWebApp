from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, logout_user, current_user
from datetime import datetime
from library import app, db, bcrypt
from library.forms import RegistrationForm, LoginForm, InsertBookForm
from library.models import BorrowHistory, Librarian, User, Book, Author
from library.utils import role_required, load_user


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    book_name = None
    if request.method == "POST":
        book_name = request.form.get('book_name')

    books = []
    if book_name is not None:
        books = Book.query.filter(Book.title.contains(book_name)).all()
    authors_all_books = []
    for book in books:
        authors = [author.name for author in book.authors]
        authors_all_books.append(authors)
    table = [(book, authors) for book, authors in zip(books, authors_all_books)]
    return render_template("search.html", table=table)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        if form.librarian.data == True:
            user = Librarian.query.filter_by(email=form.email.data).first()
            session['account_type'] = 'librarian'
        else:
            user = User.query.filter_by(email=form.email.data).first()
            session['account_type'] = 'user'
        print(session)
        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            print("User's status:", user.is_authenticated)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("home"))
        else:
            flash("Login unsuccessful. Check email and password", "danger")
    
    return render_template("login2.html", form=form, title="Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You can now login.", "success")
        return redirect(url_for("login"))

    return render_template("register2.html", form=form, title="Register")


@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("home"))


@app.route("/insert", methods=["GET", "POST"])
@role_required("librarian")
def insert():
    form = InsertBookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data, category=form.category.data, current_quantity=form.added_quantity.data,
            max_quantity=form.added_quantity.data)
        author = Author(name=form.author.data)
        book.authors.append(author)
        db.session.add(book)
        db.session.commit()
        flash(f"Book added to database!", "success")
        return redirect(url_for("home"))
    return render_template("insert.html", form=form)


@app.route("/borrow", methods=["GET", "POST"])
@role_required("user")
def borrow():
    user = current_user
    if request.method == "POST":
        register_book_id = request.form.get('book_id')
        if register_book_id != None:
            borrow = BorrowHistory(book_id=register_book_id, user_id=user.id, register_date=datetime.now())
            db.session.add(borrow)
            db.session.commit()
        else:
            remove_book_id = request.form.get('remove_book_id')
            BorrowHistory.query.filter_by(book_id=remove_book_id).delete()
            db.session.commit()

    borrow_entries = BorrowHistory.query.filter_by(user_id=user.id).all()
    table = []
    for entry in borrow_entries:
        if entry.borrow_date == None:
            book_id = entry.book_id
            book = Book.query.get(book_id)
            register_date_str = entry.register_date.strftime("%d/%m/%Y %H:%M")
            table.append((book_id, book.title, register_date_str))

    return render_template("borrow.html", table=table, title="Borrow")


@app.route("/history")
@role_required("user")
def borrow_history():
    user = current_user
    borrow_entries = BorrowHistory.query.filter_by(user_id=user.id).all()
    table = []
    for entry in borrow_entries:
        if entry.borrow_date != None:
            book_id = entry.book_id
            book = Book.query.get(book_id)
            register_date_str = entry.register_date.strftime("%d/%m/%Y %H:%M")
            table.append((book_id, book.title, register_date_str, entry.borrow_date, entry.return_date))
    return render_template("history.html", table=table, title="Borrow History")


@app.route("/lend", methods=["GET", "POST"])
@role_required("librarian")
def lend():
    table = []
    if request.method == "POST":
        if 'search_form' in request.form:
            borrow_entries = BorrowHistory.query.filter_by(user_id=request.form.get('user_id'))
            for entry in borrow_entries:
                if entry.borrow_date == None:
                    book_id = entry.book_id
                    book = Book.query.get(book_id)
                    register_date_str = entry.register_date.strftime("%d/%m/%Y %H:%M")
                    table.append((book_id, book.title, register_date_str))

        elif 'accept_form' in request.form:
            accept_book_id = request.form.get('accept_book_id')
            borrow_history = BorrowHistory.query.filter_by(book_id=accept_book_id).first()
            borrow_history.lender_id = current_user.id
            borrow_history.borrow_date = datetime.now()
            db.session.commit()
            
            # TODO: Need to fix user_id
            borrow_entries = BorrowHistory.query.filter_by(user_id=1)
            for entry in borrow_entries:
                print(entry.borrow_date)
                if entry.lender_id == None:
                    book_id = entry.book_id
                    book = Book.query.get(book_id)
                    register_date_str = entry.register_date.strftime("%d/%m/%Y %H:%M")
                    table.append((book_id, book.title, register_date_str))
    return render_template("lend.html", table=table, title="Lend Books")


@app.route("/admin")
@role_required("librarian")
def admin():
    return "admin"
