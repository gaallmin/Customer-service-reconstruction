# app.py
from flask import Flask, render_template, request, redirect, url_for
from models import SessionLocal, UserFeedback, init_db
from dash_app import create_dash_app

app = Flask(__name__)
init_db()

# Attach Dash app to Flask
dash_app = create_dash_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        reservation_opinion = request.form.get('reservation_opinion')
        health_issues = request.form.get('health_issues')
        ankh_help = request.form.get('ankh_help')

        db = SessionLocal()
        new_feedback = UserFeedback(
            reservation_opinion=reservation_opinion,
            health_issues=health_issues,
            ankh_help=ankh_help
        )
        db.add(new_feedback)
        db.commit()
        db.close()

        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

