from flask_login import UserMixin
from library import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=800000)
    borrower = db.relationship('BorrowHistory', backref='borrower', lazy=True)
    activated = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Librarian(db.Model, UserMixin):
    __tablename__ = 'librarian'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    lender = db.relationship('BorrowHistory', backref='lender', lazy=True, foreign_keys='BorrowHistory.lender_id')
    receiver = db.relationship('BorrowHistory', backref='receiver', lazy=True, foreign_keys='BorrowHistory.receiver_id')

    def __repr__(self):
        return f"Librarian('{self.id}', '{self.email}')"


book_author = db.Table('association', db.Model.metadata,
    db.Column('book_id', db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.ForeignKey('author.id'), primary_key=True)
)


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    current_quantity = db.Column(db.Integer, nullable=False, default=1)
    max_quantity = db.Column(db.Integer, nullable=False, default=1)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False, default='placeholder.jpg')
    description = db.Column(db.String(500))
    authors = db.relationship('Author', secondary=book_author, backref='books', lazy=True)
    borrow = db.relationship('BorrowHistory', backref='borrowed_books', lazy=True)
    
    def __repr__(self):
        return f"Book('{self.title}')"


class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Author('{self.id}', '{self.name}')"


class BorrowHistory(db.Model):
    __tablename__ = 'borrow_history'
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    register_date = db.Column(db.DateTime, primary_key=True)
    borrow_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String)
    lender_id = db.Column(db.Integer, db.ForeignKey('librarian.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('librarian.id'))

    def __repr__(self):
        return f"Borrow('({self.book_id}, {self.user_id}, {self.register_date})"




