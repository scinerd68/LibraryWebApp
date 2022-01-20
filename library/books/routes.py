from flask import Blueprint, flash, redirect, render_template, url_for
from library import db
from library.models import Author, Book
from library.books.forms import InsertBookForm
from library.utils import role_required, load_user
from library.books.utils import save_image


books = Blueprint('books', __name__)

@books.route("/insert", methods=["GET", "POST"])
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
        return redirect(url_for("main.home"))
    return render_template("insert.html", title="Insert Book", form=form, legend="New Book")


@books.route("/book/<book_id>")
def book(book_id):
    book = Book.query.get_or_404(book_id)
    authors = [author.name for author in book.authors]
    image_file = url_for('static', filename='image/' + book.image)
    return render_template("book.html", book=book, image_file=image_file, authors=authors)


@books.route("/book/<book_id>/update", methods=["GET", "POST"])
@role_required("librarian")
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = InsertBookForm()
    
    if form.validate_on_submit():
        if book.max_quantity - form.remove_quantity.data < 0:
            flash("Too many book to be removed", "danger")
            return redirect(url_for("books.update_book", book_id=book_id))
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
        return redirect(url_for("books.book", book_id=book.id))
        
    form.title.data = book.title
    form.category.data = book.category
    form.description.data = book.description
    for author_field, author in zip(form.authors, book.authors):
        author_field.data = author.name.strip().title()
    form.added_quantity.data = 0
    form.remove_quantity.data = 0

    return render_template("update_book.html", title="Update Book", form=form, legend="Update Book")