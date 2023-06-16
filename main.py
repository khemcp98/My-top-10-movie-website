from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.secret_key = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


class RatingForm(FlaskForm):
    rating = FloatField(label='Your Rating Out Of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Update')


class AddForm(FlaskForm):
    add_movie = StringField(label="Type Movie Name", validators=[DataRequired()])
    submit = SubmitField(label='Search')


@app.route("/")
def home():
    all_movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RatingForm()
    movie_id = request.args.get('id')
    movie_to_update = Movies.query.get(movie_id)
    if form.validate_on_submit():
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=movie_to_update)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_del = Movies.query.get(movie_id)
    db.session.delete(movie_to_del)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddForm()

    if form.validate_on_submit():
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiNjdmZjc2ZDBhMTI3ODA5Mzg4NTNjYTA4Y2NjZDQwMSIsInN1YiI6IjY0ODk2YTEzZDJiMjA5MDEwYzFiNzAyMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.6S_56rXM3fw6R3utJ4pIqMe3I-Xrmn-lV8kc2FFo5aA"
        }
        params = {
            'query': form.add_movie.data,
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", headers=headers, params=params)
        data = response.json()['results']
        return render_template('select.html', movies=data)

    return render_template('add.html', form=form)


@app.route('/db')
def add_db():
    url = 'https://image.tmdb.org/t/p/w500'
    path = request.args.get('path')
    title = request.args.get('title')
    year = request.args.get('year')
    des = request.args.get('overview')
    new_movie = Movies(title=title, year=year, description=des, img_url=f"{url}{path}")
    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
