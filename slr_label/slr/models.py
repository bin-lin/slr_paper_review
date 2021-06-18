from slr_label import db

assignments = db.Table('assignment',
    db.Column('paper_id', db.Integer, db.ForeignKey('paper.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    type = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return self.question


class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    authors = db.Column(db.String)
    venue = db.Column(db.String)
    doi = db.Column(db.String)
    labelers = db.relationship('User', secondary=assignments, lazy='subquery',
                               backref=db.backref('papers', lazy=True, order_by=id))

    def __str__(self):
        return self.title


class NewPaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    authors = db.Column(db.String)
    venue = db.Column(db.String)
    doi = db.Column(db.String)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    paper = db.relationship('Paper', backref=db.backref('new_papers', lazy=True))
    labeler_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    labeler = db.relationship('User', backref=db.backref('new_papers', lazy=True))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __str__(self):
        return self.title


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    paper = db.relationship('Paper', backref=db.backref('answers', lazy=True))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('answers', lazy=True))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question = db.relationship('Question', backref=db.backref('answers', lazy=True))
    answer = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_on = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __str__(self):
        return self.answer
