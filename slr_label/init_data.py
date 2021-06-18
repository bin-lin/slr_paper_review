import random

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from slr_label.auth.models import Role, User
from slr_label.slr.models import Paper, Question
import csv


def insert_users(db):
    user_role = Role(name='user')
    admin_role = Role(name='admin')
    db.session.add(user_role)
    db.session.add(admin_role)
    db.session.commit()

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.create_user(
            username='Admin',
            password=hash_password('adminPass'),
            roles=[user_role, admin_role]
        )
    users = [('Bob', 'BobPass'), ('Alice', 'AlicePass')]
    for user in users:
        user_datastore.create_user(
            username=user[0],
            password=hash_password(user[1]),
            roles=[user_role, ]
        )
    db.session.commit()


def insert_papers(db):
    f = open('sample_data/papers.csv')
    reader = csv.DictReader(f)
    for row in reader:
        if 'http' in row['doi']:
            link = row['doi']
        else:
            link = 'https://www.doi.org/'+row['doi']
        paper = Paper(title=row['title'], authors=row['authors'], venue=row['venue'], doi=link)
        db.session.add(paper)
    db.session.commit()


def insert_questions(db):
    questions = [
        ('Does the paper propose a new opinion mining approach?', 0),
        ('Which opinion mining techniques are used (list all of them, clearly stating their name/reference)?', 1),
        ('Write down any other comments/notes here.', 1)
    ]
    for question in questions:
        q = Question(question=question[0], type=question[1])
        db.session.add(q)
    db.session.commit()


def insert_assignments(db):
    papers = [paper for paper in Paper.query.all()]
    admin_role = Role.query.filter_by(name='admin').first()
    users = [user for user in User.query.filter(~User.roles.contains(admin_role))]
    print(len(papers), len(users))
    random.shuffle(papers)
    assignments = [papers[i::len(users)] for i in range(len(users))]
    for ind, user in enumerate(users):
        for paper in assignments[ind]:
            user.papers.append(paper)
    db.session.commit()

