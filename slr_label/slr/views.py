from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_security import current_user
from slr_label.slr.models import Question, Paper, NewPaper, Answer
from slr_label import db

bp = Blueprint("slr", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    if current_user.is_active and current_user.is_authenticated:
        if current_user.has_role('admin'):
            return redirect(url_for('admin.index', next=request.url))
        else:
            my_papers = current_user.papers
            for my_paper in my_papers:
                answers = my_paper.answers
                my_answers = [answer for answer in answers if answer.author_id == current_user.id]
                if len(my_answers) > 0:
                    my_paper.has_review = 1
                else:
                    my_paper.has_review = 0
            return render_template('slr/index.html', my_papers=my_papers)
    else:
        return redirect(url_for('security.login', next=request.url))


@bp.route("/addPaper")
def add_paper():
    """Show all the posts, most recent first."""
    if current_user.is_active and current_user.is_authenticated:
        papers = Paper.query.all()
        new_papers = NewPaper.query.all()
        all_papers = papers + new_papers
        my_papers = [paper.id for paper in current_user.papers]
        my_papers.sort()
        return render_template('slr/addpaper.html', papers=all_papers, my_papers=my_papers)
    else:
        return redirect(url_for('security.login'))


@bp.route("/addNewPaper", methods=['POST'])
def add_new_paper():
    if request.method == 'POST':
        title = request.form['title']
        authors = request.form['authors']
        venue = request.form['venue']
        doi = request.form['doi']
        from_paper = request.form['from_paper']
        new_paper = NewPaper(title=title, authors=authors, venue=venue, doi=doi, labeler_id=current_user.id, paper_id=from_paper)
        db.session.add(new_paper)
        db.session.commit()
        flash('New paper successfully added!')
    return redirect(url_for('slr.add_paper'))


def get_paper_answers(paper_id):
    paper = Paper.query.filter_by(id=paper_id).first()
    answers = paper.answers  # .filter(Answer.author_id == current_user.id).all()
    my_answers = [answer for answer in answers if answer.author_id == current_user.id]
    answers_dict = {}
    for answer in my_answers:
        answers_dict[str(answer.question_id)] = answer
    questions = Question.query.all()
    for question in questions:
        if str(question.id) in answers_dict:
            question.answer = answers_dict[str(question.id)].answer
        else:
            question.answer = None
    return paper, questions


@bp.route("/reviewPaper", methods=['POST'])
def review_paper():
    if request.method == 'POST':
        paper_id = request.form['paper_id']
        paper, questions = get_paper_answers(paper_id)
        return render_template('slr/reviewpaper.html', paper=paper, questions=questions)
    return redirect(url_for('slr.index'))


@bp.route("/displayReview/<int:paper_id>")
def view_review(paper_id):
    try:
        paper, questions = get_paper_answers(paper_id)
        return render_template('slr/displayreview.html', paper=paper, questions=questions)
    except:
        flash('Error when getting the paper, please check if the paper ID is correct!')
        return redirect(url_for('slr.index'))


@bp.route("/saveReview", methods=['POST'])
def save_review():
    if request.method == 'POST':
        paper_id = request.form['paper_id']
        answers = Answer.query.filter_by(author_id=current_user.id, paper_id=paper_id).all()
        answers_dict = {}
        for answer in answers:
            answers_dict[str(answer.question_id)] = answer
        for k, v in request.form.items():
            if 'question' in k:
                q_id = k.replace('question', '')
                if q_id in answers_dict:
                    answers_dict[q_id].answer = v
                else:
                    new_answer = Answer(answer=v, paper_id=paper_id, author_id=current_user.id, question_id=int(q_id))
                    db.session.add(new_answer)
        db.session.commit()
        flash('Review successfully added/updated!')
    return redirect(url_for('slr.index'))
