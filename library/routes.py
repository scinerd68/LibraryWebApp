import os
import secrets
from collections import Counter
from unicodedata import category
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, logout_user, current_user
from datetime import datetime, timedelta
from library import app, db, bcrypt
from library.forms import RegistrationForm, LoginForm, InsertBookForm, ReturnBookForm
from library.models import BorrowHistory, Librarian, User, Book, Author
from library.utils import role_required, load_user


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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
            return redirect(url_for("home"))
        else:
            session.clear()
            flash("Login unsuccessful. Check email and password", "danger")
            return redirect(url_for("login"))
    
    return render_template("login2.html", form=form, title="Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data,
                    last_name=form.last_name.data, password=hash_password)
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


@app.route("/account")
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


@app.route("/search", methods=["GET", "POST"])
def search():
    table = []
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

    return render_template("search.html", table=table)


def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_image.filename)
    image_file = random_hex + file_ext
    image_path = os.path.join(app.root_path, 'static/image', image_file)

    output_size = (450, 300)
    output_image = Image.open(form_image)
    output_image.thumbnail = output_size
    output_image.save(image_path)
    return image_file


@app.route("/insert", methods=["GET", "POST"])
@role_required("librarian")
def insert():
    form = InsertBookForm()
    
    if form.validate_on_submit():
        book = Book(title=form.title.data, category=form.category.data, current_quantity=form.added_quantity.data,
            max_quantity=form.added_quantity.data, description=form.description.data)
        
        existed_authors_name = [author.name for author in Author.query.all()]
        for author in form.authors:
            author_name = author.data.strip().lower()
            if author_name != '':
                if author_name not in existed_authors_name:
                    author = Author(name=author.data)
                    book.authors.append(author)
                else:
                    author = Author.query.filter_by(name=author_name)
                    book.authors.append(author)
        if form.image.data:
            image_file = save_image(form.image.data)
            book.image = image_file

        db.session.add(book)
        db.session.commit()
        flash(f"Book added to database!", "success")
        return redirect(url_for("home"))
    return render_template("insert.html", title="Insert Book", form=form, legend="New Book")


@app.route("/book/<book_id>")
def book(book_id):
    book = Book.query.get_or_404(book_id)
    authors = [author.name for author in book.authors]
    image_file = url_for('static', filename='image/' + book.image)
    return render_template("book.html", book=book, image_file=image_file, authors=authors)


@app.route("/book/<book_id>/update", methods=["GET", "POST"])
@role_required("librarian")
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = InsertBookForm()
    
    if form.validate_on_submit():
        if book.max_quantity - form.remove_quantity.data < 0:
            flash("Too many book to be removed", "danger")
            return redirect(url_for("update_book", book_id=book_id))
        else:
            book.current_quantity -= form.remove_quantity.data
            book.max_quantity -= form.remove_quantity.data

        book.title = form.title.data
        book.category = form.category.data
        book.description = form.description.data
        book.current_quantity += form.added_quantity.data
        book.max_quantity += form.added_quantity.data

        book.authors = []
        existed_authors_name = [author.name for author in Author.query.all()]
        for author in form.authors:
            author_name = author.data.strip().lower()
            if author_name != '':
                if author_name not in existed_authors_name:
                    author = Author(name=author.data)
                    book.authors.append(author)
                else:
                    author = Author.query.filter_by(name=author_name)
                    book.authors.append(author)
        if form.image.data:
            image_file = save_image(form.image.data)
            book.image = image_file
        
        db.session.commit()
        flash(f"Book updated!", "success")
        return redirect(url_for("book", book_id=book.id))
        
    form.title.data = book.title
    form.category.data = book.category
    form.description.data = book.description
    for author_field, author in zip(form.authors, book.authors):
        author_field.data = author.name.strip().title()
    form.added_quantity.data = 0
    form.remove_quantity.data = 0

    return render_template("update_book.html", title="Update Book", form=form, legend="Update Book")


@app.route("/borrow", methods=["GET", "POST"])
@role_required("user")
def borrow():
    user = current_user
    
    if request.method == "POST":
        requesting_id = [book.book_id for book in BorrowHistory.query.all() if book.status=="requesting" or book.status=="borrowing"]
        register_book_id = request.form.get('book_id')
        if register_book_id != None:
            register_book_id = int(register_book_id)
            if register_book_id not in requesting_id:
                book = Book.query.get(register_book_id)
                if book.current_quantity == 0:
                    flash(f"No book available at the moment.", "danger")
                else:
                    borrow = BorrowHistory(book_id=register_book_id, user_id=user.id, 
                                        register_date=datetime.now(), status="requesting")
                    db.session.add(borrow)
                    book.current_quantity -= 1
                    db.session.commit()
                    flash(f"Book has been requested successfully.", "success")
            else:
                flash(f"Book has already been requested or borrowed.", "danger")
        else:
            remove_book_id = request.form.get('remove_book_id')
            num_book_delete = BorrowHistory.query.filter_by(book_id=remove_book_id).filter_by(status="requesting").delete()
            if num_book_delete > 0:
                book = Book.query.get(remove_book_id)
                book.current_quantity += 1
            db.session.commit()
            flash(f"Undo request successfully", "success")

        borrow_entries = BorrowHistory.query.filter_by(user_id=user.id).all()
        table = []
        for entry in borrow_entries:
            if entry.status == "requesting":
                book_id = entry.book_id
                book = Book.query.get(book_id)
                register_date_str = entry.register_date.strftime("%d/%m/%Y %H:%M")
                table.append((book_id, book.title, register_date_str))
        return render_template("borrow.html", table=table, title="Borrow")

    borrow_entries = BorrowHistory.query.filter_by(user_id=user.id).all()
    table = []
    for entry in borrow_entries:
        if entry.status == "requesting":
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
        book_id = entry.book_id
        book = Book.query.get(book_id)

        borrow_date_str = None
        return_date_str = None
        register_date_str = entry.register_date.strftime("%d/%m/%Y %H:%M")
        if entry.borrow_date is not None:
            borrow_date_str = entry.borrow_date.strftime("%d/%m/%Y %H:%M")
        if entry.return_date is not None:
            return_date_str = entry.return_date.strftime("%d/%m/%Y %H:%M")
        table.append((book_id, book.title, register_date_str, borrow_date_str, return_date_str, entry.status))

    SORT_ORDER = {"requesting" : 2, "borrowing" : 1, "returned" : 0}
    table.sort(key=lambda entry: (SORT_ORDER[entry[5]], entry[2]), reverse=True)
    return render_template("history.html", table=table, title="Borrow History")


@app.route("/lend", methods=["GET", "POST"])
@role_required("librarian")
def lend():
    SORT_ORDER = {"requesting" : 2, "borrowing" : 1, "returned" : 0}
    table = []
    user_id = None
    if request.method == "POST":
        if 'search_form' in request.form:
            user_id = request.form.get('user_id')
            borrow_entries = BorrowHistory.query.filter_by(user_id=user_id)
            for entry in borrow_entries:
                book_id = entry.book_id
                book = Book.query.get(book_id)

                borrow_date_str = None
                return_date_str = None
                register_date_str = entry.register_date.strftime("%d/%m/%Y %H:%M")
                if entry.borrow_date is not None:
                    borrow_date_str = entry.borrow_date.strftime("%d/%m/%Y %H:%M")
                if entry.return_date is not None:
                    return_date_str = entry.return_date.strftime("%d/%m/%Y %H:%M")
                table.append((book_id, book.title, register_date_str, borrow_date_str, return_date_str, entry.status))
            
            table.sort(key=lambda entry: (SORT_ORDER[entry[5]], entry[2]), reverse=True)
            return render_template("lend.html", table=table, user=user_id, title="Lend Books")

        elif 'accept_form' in request.form:
            accept_book_id = request.form.get('accept_book_id')
            user_id = request.form.get('user_id')
            borrow_history = BorrowHistory.query.filter_by(user_id=user_id).filter_by(book_id=accept_book_id).filter_by(status="requesting").first()
            if borrow_history is None:
                return redirect(url_for("home"))
            borrow_history.lender_id = current_user.id
            borrow_history.borrow_date = datetime.now()
            borrow_history.status = "borrowing"
            db.session.commit()
            
            borrow_entries = BorrowHistory.query.filter_by(user_id=user_id).all()
            for entry in borrow_entries:
                book_id = entry.book_id
                book = Book.query.get(book_id)
                borrow_date_str = None
                return_date_str = None
                register_date_str = entry.register_date.strftime("%d/%m/%Y %H:%M")
                if entry.borrow_date is not None:
                    borrow_date_str = entry.borrow_date.strftime("%d/%m/%Y %H:%M")
                if entry.return_date is not None:
                    return_date_str = entry.return_date.strftime("%d/%m/%Y %H:%M")
                table.append((book_id, book.title, register_date_str, borrow_date_str, return_date_str, entry.status))
            table.sort(key=lambda entry: (SORT_ORDER[entry[5]], entry[2]), reverse=True)
            return render_template("lend.html", table=table, user=user_id, title="Lend Books")
    
    return render_template("lend.html", table=table, user=user_id, title="Lend Books")


@app.route("/return", methods=["POST"])
@role_required("librarian")
def return_book():
    form = ReturnBookForm()
    if request.method == "POST":
        if 'return_form' in request.form:
            return_book_id = request.form.get('return_book_id')
            book = Book.query.get(return_book_id)
            user_id = request.form.get('user_id')
            history = BorrowHistory.query.filter_by(user_id=user_id).filter_by(book_id=return_book_id).filter_by(status="borrowing").first()
            if history is None:
                return redirect(url_for("home"))
            form.book_id.data = return_book_id
            form.user_id.data = user_id
            form.title.data = book.title.title()
            form.borrow_date.data = history.borrow_date
            form.damage_fine.data = 0

            expected_return_date = history.borrow_date + timedelta(days=14)
            time_difference = (datetime.now() - expected_return_date).days
            if time_difference <= 0:
                form.late_status.data = "Not Late"
                form.late_fine.data = 0
            else:
                num_late_date = time_difference
                form.late_status.data = "Late " + str(num_late_date) + " days"
                form.late_fine.data = 10000 * num_late_date

            return render_template("return.html", form=form, title="Return Book")
        
        elif form.validate_on_submit:
            book_id = form.book_id.data
            user_id = form.user_id.data
            book = Book.query.get(book_id)
            user = User.query.get(user_id)
            
            history = BorrowHistory.query.filter_by(user_id=user_id).filter_by(book_id=book_id).filter_by(status="borrowing").first()
            history.receiver_id = current_user.id
            history.return_date = datetime.now()
            history.status = "returned"
             
            user.balance -= (form.damage_fine.data + form.late_fine.data)
            if form.return_status.data == "Normal" or form.return_status.data == "Light Damage":
                book.current_quantity += 1
            else:
                book.max_quanitity -= 1
            
            db.session.commit()
            flash("Book returned succesfully", "success")
            return redirect(url_for("lend"))

        else:
            return redirect(url_for("lend"))



@app.route("/user", methods={"GET", "POST"})
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

    return render_template('user.html', book=book, user=user)


@app.route("/statistics")
@role_required("librarian")
def statistics():
    all_books = Book.query.with_entities(Book.id).all() 
    all_books_borrowed = BorrowHistory.query.with_entities(BorrowHistory.book_id)\
              .filter(BorrowHistory.register_date > (datetime.now() - timedelta(days=30))).all()

    # Query most and least popular books
    total_borrowed_turns = len(all_books_borrowed)
    book_counter = Counter(all_books_borrowed)
    sorted_book_counter = sorted(book_counter, key=book_counter.get, reverse=True)
    most_borrowed_books = [(Book.query.get(id[0]), book_counter[id]) for id in sorted_book_counter[:4]]

    not_bororwed_books = list(set(all_books) - set(all_books_borrowed))
    least_borrowed_books = [(Book.query.get(id[0]), 0) for id in not_bororwed_books]
    if len(least_borrowed_books) < 4:
        num_missing_item = 4 - len(least_borrowed_books)
        least_borrowed_books += [(Book.query.get(id[0]), book_counter[id]) for id in sorted_book_counter[::-1][:num_missing_item]]

    # Query category
    all_category = [Book.query.filter_by(id=id[0]).with_entities(Book.category).first()[0] for id in all_books_borrowed]
    category_counter = Counter(all_category)
    category = list(category_counter.keys())
    category_count = list(category_counter.values())
    colors = ["green"] * len(category)
    return render_template('statistics.html', most_borrowed_books=most_borrowed_books, total_borrowed_turns=total_borrowed_turns,
                            least_borrowed_books=least_borrowed_books, category=category,
                            category_count=category_count, colors=colors, title="Library Statistics")


"""
TODO:
- Handle logic when return book late [x]
- Add fine field to return form [x]
- Add route for user account contain username, email, balance, info [x]
- Add favorite book to account gui [x]
- Handle error in insert form [x]
- Send email when balance < 300000
- Add route to allow librarian recharge balance for user [x]
- Statistics [x]
- Handle request book expire after 2 days (optional)
- Activate user account (optional)
- Improve GUI
- Reorganize using Blueprint
- Consider add decline function when borrow book

"""
