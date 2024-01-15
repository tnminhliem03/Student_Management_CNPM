from functools import wraps
from flask import session, url_for, redirect, request
from Project import app


def role_only(role):
    def wrap(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
                print(type(session.get('role')))
                if (session.get('role') and role != session.get('role')) or not session.get('role'):
                    return redirect(url_for("index"))
                else:
                    return f(*args, **kwargs)
        return decorated_function
    return wrap
