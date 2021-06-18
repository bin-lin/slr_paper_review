import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
from flask_admin.contrib import sqla
from flask_security import current_user


bp = Blueprint("auth", __name__, url_prefix="/auth")


class AuthModelView(sqla.ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('admin'))

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))
