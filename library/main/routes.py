from collections import Counter
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from library.models import Book, BorrowHistory
from library.utils import role_required, load_user


main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
@main.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@main.route("/search", methods=["GET", "POST"])
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

@main.route("/statistics")
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