from flask_bcrypt import Bcrypt
from library import db, bcrypt
from library.models import User, Librarian, Book, Author, BorrowHistory

db.drop_all()
db.create_all()

password = 'test'
hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
user = User(username='test', email='test@gmail.com', first_name="John", last_name="Smith", password=hash_password)
db.session.add(user)

admin_password = 'test_admin'
hash_admin_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
admin = Librarian(email='test_admin@gmail.com', password=hash_admin_password)
db.session.add(admin)

description = """Lorem ipsum dolor sit amet consectetur adipisicing elit.
               Nesciunt deserunt velit quo in officiis molestias neque rerum suscipit doloremque quis,
               fugit non sequi consequuntur facilis accusantium accusamus est sed nisi ipsam,
               ratione dignissimos repellat ipsa! Quis cumque officiis similique molestiae a maiores cupiditate earum laudantium ipsum,
               doloribus, itaque dolorum nemo."""

book1 = Book(title='automate the boring stuff', category='programming', current_quantity=1, max_quantity=1,
             image="book1.jpg", description=description)
author1 = Author(name='al sweigart')
book1.authors.append(author1)
db.session.add(author1)
db.session.add(book1)

book2 = Book(title='python crash course', category='programming', current_quantity=4, max_quantity=4, 
             image="book2.jpg", description=description)
author2 = Author(name='eric matthes')
book2.authors.append(author2)
db.session.add(author2)
db.session.add(book2)

book3 = Book(title='hands on machine learning', category='artificial intelligence', current_quantity=5, max_quantity=5,
             image="book3.jpg", description=description)
author3 = Author(name='aurelien geron')
book3.authors.append(author3)
db.session.add(author3)
db.session.add(book3)

book4 = Book(title='the pragmatic programmer', category='programming', current_quantity=5, max_quantity=5,
             image="book4.jpg", description=description)
author4 = Author(name='david thomas')
book4.authors.append(author4)
author5 = Author(name='andrew hunt')
book4.authors.append(author5)
db.session.add(author4)
db.session.add(author5)
db.session.add(book4)

db.session.commit()