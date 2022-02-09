from datetime import datetime, timedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from library import db
from library.borrows.forms import ReturnBookForm
from library.models import Book, BorrowHistory, User
from library.utils import role_required, load_user


borrows = Blueprint('borrows', __name__)

@borrows.route("/borrow", methods=["GET", "POST"])
@role_required("user")
def borrow():
    """ Route to handle request book by user """
    user = current_user
    
    if request.method == "POST":
        if not user.activated:
            flash("Need to activate account to borrow books. Come to library to request activation.")
            return redirect(url_for("main.home"))
        requesting_id = [book.book_id for book in BorrowHistory.query.filter_by(user_id=user.id).all() if book.status=="requesting" or book.status=="borrowing"]
        register_book_id = request.form.get('book_id')
        if register_book_id != None:
            if len(requesting_id) == 3:
                flash("Can only borrow maximum 3 books a time.", "info")
                return redirect(url_for("main.home"))
            register_book_id = int(register_book_id)
            if register_book_id not in requesting_id:
                book = Book.query.get(register_book_id)
                if book.current_quantity == 0:
                    flash(f"No book available at the moment.", "danger")
                else:
                    borrow = BorrowHistory(book_id=register_book_id, user_id=user.id, 
                                        register_date=datetime.now(), status="requesting")
                    db.session.add(borrow)
                    db.session.commit()
                    flash(f"Book has been requested successfully. Please return book after 14 days.", "success")
            else:
                flash(f"Book has already been requested or borrowed.", "danger")
        else:
            remove_book_id = request.form.get('remove_book_id')
            num_book_delete = BorrowHistory.query.filter_by(user_id=user.id).filter_by(book_id=remove_book_id).filter_by(status="requesting").delete()
            if num_book_delete > 0:
                book = Book.query.get(remove_book_id)
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


@borrows.route("/lend", methods=["GET", "POST"])
@role_required("librarian")
def lend():
    """ Route to lend book to user """
    SORT_ORDER = {"requesting" : 3, "borrowing" : 2, "returned" : 1, "declined" : 0}
    table = []
    user_id = None
    if request.method == "POST":
        if 'search_form' in request.form:
            user_id = request.form.get('user_id')
            try:
                user_id = int(user_id)
            except ValueError:
                flash("User ID must be an integer", "info")
                return render_template("lend.html", table=table, user=None, title="Lend Books")

        elif 'accept_form' in request.form:
            accept_book_id = request.form.get('accept_book_id')
            user_id = request.form.get('user_id')
            borrow_history = BorrowHistory.query.filter_by(user_id=user_id).filter_by(book_id=accept_book_id).filter_by(status="requesting").first()
            if borrow_history is None:
                return redirect(url_for("main.home"))
            borrow_history.lender_id = current_user.id
            borrow_history.borrow_date = datetime.now()
            borrow_history.status = "borrowing"
            db.session.commit()

        elif 'decline_form' in request.form:
            decline_book_id = request.form.get('decline_book_id')
            user_id = request.form.get('user_id')
            borrow_history = BorrowHistory.query.filter_by(user_id=user_id).filter_by(book_id=decline_book_id).filter_by(status="requesting").first()
            if borrow_history is None:
                return redirect(url_for("main.home"))
            borrow_history.lender_id = current_user.id
            borrow_history.borrow_date = datetime.now()
            borrow_history.status = "declined"
            book = Book.query.get(decline_book_id)
            book.current_quantity += 1
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


@borrows.route("/history")
@role_required("user")
def borrow_history():
    """ Route to display user' borrow history """
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

    SORT_ORDER = {"requesting" : 3, "borrowing" : 2, "returned" : 1, "declined" : 0}
    table.sort(key=lambda entry: (SORT_ORDER[entry[5]], entry[2]), reverse=True)
    return render_template("history.html", table=table, title="Borrow History")


@borrows.route("/return", methods=["POST"])
@role_required("librarian")
def return_book():
    """ Route to return book to user """
    form = ReturnBookForm()
    if request.method == "POST":
        if 'return_form' in request.form:
            return_book_id = request.form.get('return_book_id')
            book = Book.query.get(return_book_id)
            user_id = request.form.get('user_id')
            history = BorrowHistory.query.filter_by(user_id=user_id).filter_by(book_id=return_book_id).filter_by(status="borrowing").first()
            if history is None:
                return redirect(url_for("main.home"))
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
            return redirect(url_for("borrows.lend"))

        else:
            return redirect(url_for("borrows.lend"))