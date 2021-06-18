import os
import click
import flask_admin
from flask import Flask, url_for
from flask.cli import with_appcontext
from flask_security import SQLAlchemyUserDatastore, Security, LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from flask_admin import helpers as admin_helpers
from wtforms import StringField
from wtforms.validators import InputRequired

db = SQLAlchemy()


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # some deploy systems set the database url in the environ
    db_url = os.environ.get("DATABASE_URL")

    if db_url is None:
        # default to a sqlite database in the instance folder
        db_url = "sqlite:///" + os.path.join(app.instance_path, "slr_label.sqlite")
        # ensure the instance folder exists
        os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        # default secret that should be overridden in environ or config
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        FLASK_ADMIN_SWATCH='superhero',
        SECURITY_PASSWORD_SALT='security_secret',
        # SECURITY_POST_LOGIN_VIEW='/login/',
        # SECURITY_POST_LOGOUT_VIEW='/logout/',
        # SECURITY_POST_REGISTER_VIEW='/register/',
        SECURITY_REGISTERABLE=False,
        SECURITY_CHANGEABLE=True,
        SECURITY_SEND_PASSWORD_CHANGE_EMAIL=False,
        SECURITY_SEND_REGISTER_EMAIL=False,
        SECURITY_USER_IDENTITY_ATTRIBUTES='username'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # initialize Flask-SQLAlchemy and the init-db command
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(insert_db_data_command)

    # apply the blueprints to the app
    from slr_label import slr, auth

    app.register_blueprint(slr.bp)
    app.register_blueprint(auth.bp)
    # make "index" point at "/", which is handled by "blog.index"
    app.add_url_rule("/", endpoint="index")

    # Setup Flask-Security
    from slr_label.auth.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    class ExtendedLoginForm(LoginForm):
        email = StringField('Username', [InputRequired()])

    class ExtendedRegisterForm(RegisterForm):
        email = StringField('Username', [InputRequired()])

    security = Security(app, user_datastore, login_form=ExtendedLoginForm, register_form=ExtendedRegisterForm)

    # This processor is added to only the register view
    @security.register_context_processor
    def change_password_context_processor():
        return dict(title='Change Password')

    admin = flask_admin.Admin(
        app, 'SLR Web App',
        base_template='master.html',
        template_mode='bootstrap3',
    )

    from slr_label.auth.views import AuthModelView
    admin.add_view(AuthModelView(Role, db.session))
    admin.add_view(AuthModelView(User, db.session))

    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
        )

    from slr_label.slr.models import Question, Paper, Answer, NewPaper
    admin.add_view(AuthModelView(Question, db.session))
    admin.add_view(AuthModelView(Paper, db.session))
    admin.add_view(AuthModelView(Answer, db.session))
    admin.add_view(AuthModelView(NewPaper, db.session))
    return app


def init_db():
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("insert-data")
@with_appcontext
def insert_db_data_command():
    """Insert user and role sample data."""
    from slr_label.init_data import insert_users, insert_papers, insert_questions, insert_assignments
    insert_users(db)
    click.echo("Inserted the users to database.")
    insert_papers(db)
    click.echo("Inserted the papers to database.")
    insert_questions(db)
    click.echo("Inserted the questions to database.")
    insert_assignments(db)
    click.echo("Inserted the assignments to database.")
