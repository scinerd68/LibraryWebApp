from flask_bcrypt import Bcrypt
from library import db, bcrypt
from library.models import User, Librarian, Book, Author, BorrowHistory

password = 'test'
hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
user = User(username='test', email='test@gmail.com', password=hash_password)
db.session.add(user)

admin_password = 'test_admin'
hash_admin_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
admin = Librarian(username='test_admin', email='test_admin@gmail.com', password=hash_admin_password)
db.session.add(admin)

book1 = Book(title='test1', category='test1', current_quantity=1, max_quantity=1)
author1 = Author(name='test1')
book1.authors.append(author1)
db.session.add(author1)
db.session.add(book1)

book2 = Book(title='test2', category='test2', current_quantity=1, max_quantity=1)
author2 = Author(name='test2')
book2.authors.append(author2)
db.session.add(author2)
db.session.add(book2)

book3 = Book(title='test3', category='test3', current_quantity=1, max_quantity=1)
author3 = Author(name='test3')
book3.authors.append(author3)
db.session.add(author3)
db.session.add(book3)

db.session.commit()