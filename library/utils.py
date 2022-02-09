from functools import wraps
from flask import session
from flask_login import current_user
from library import login_manager
from library.models import User, Librarian


def role_required(role):
    """ Wrapper to disallow users from access routes if unauthorized or incorrect account type"""
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return login_manager.unauthorized()
            if session['account_type'] != role:
                return login_manager.unauthorized()      
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


@login_manager.user_loader
def load_user(user_id):
    """ Load user from database function """
    if session.get('account_type') == 'user':
        return User.query.get(int(user_id))
    elif session.get('account_type') == 'librarian':
        return Librarian.query.get(int(user_id))