import wtforms
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, HiddenField, TextAreaField, PasswordField, EmailField
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from wtforms.validators import DataRequired, NumberRange, Email, Length, EqualTo
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
import requests
from flask_migrate import Migrate








login_manager = LoginManager()
login_manager.login_view = '/login'



MOVIE_API_KEY = "dc3eaee5a07613efb39a688a788425bd"
MOVIE_SEARCH_URL = "https://api.themoviedb.org/3/movie/550"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['LOGIN_URL'] = '/login'
db = SQLAlchemy(app)
Bootstrap(app)
bcrypt = Bcrypt()
app.secret_key = "runningupthathill"
login_manager.init_app(app)
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

para = {
    "api_key": MOVIE_API_KEY
}

movie_api_response = requests.get(url=MOVIE_SEARCH_URL, params=para)



def search_movie(title):
    movie = Movie.query.filter_by(title=title).first()
    # print("search function works")
    if movie:
        # Movie exists in the database
        # print("Movie exists from search function")
        return movie
    else:
        # Movie does not exist in the database
        print("Movie not found from search function")
        return None

with app.app_context():

    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        email = db.Column(db.String(20), unique=True, nullable=False)
        password = db.Column(db.String, nullable=False)
        name = db.Column(db.String(1000))

        def set_password(self, password):
            self.password = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password, password)


    class User_reg(FlaskForm):
        id = HiddenField()
        email = StringField("Email:", validators=[DataRequired()], name="email")
        password = PasswordField("Password: ", validators=[
            DataRequired(), Length(min=8, message='Too short'), EqualTo('confirm', 'Password mismatch')], name="password")
        name = StringField("User Name:", validators=[DataRequired()], name="name")
        submit = SubmitField("Done")
        confirm = PasswordField("Confirm Password:", validators=[DataRequired()], name="confirm")

    class RateMovieForm(FlaskForm):
        id = HiddenField()
        rating = DecimalField("Your Rating Out of 10 (e.g. 7.5):",
                              validators=[DataRequired(),
                                          NumberRange(min=0, max=10,
                                                      message="Please input a rating between 0 and 10.")],
                              name="rating", places=1)
        review = TextAreaField("Your Review:", validators=[DataRequired()], name="review")
        submit = SubmitField("Done")

    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        title = db.Column(db.String, unique=True, nullable=False)
        year = db.Column(db.Integer, nullable=True)
        description = db.Column(db.String, nullable=True)
        rating = db.Column(db.Float, nullable=True)
        ranking = db.Column(db.Integer, nullable=True)
        review = db.Column(db.String, nullable=True)
        img_url = db.Column(db.String)
        # movie_list_id = db.Column(db.Integer, db.ForeignKey('movie_list.id'), name='fk_movie_list_id')
        # movie_list = db.relationship("MovieList", backref=db.backref("movies_rel", cascade="all, delete-orphan"))

    # class MovieList(db.Model):
    #     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #     title = db.Column(db.String(50))
    #     description = db.Column(db.Text)
    #     movies = db.relationship('Movie', backref='movie_list_rel', lazy=True)

    class LoginForm(FlaskForm):
        email = StringField('Email', validators=[DataRequired()])
        password = PasswordField(validators=[DataRequired(), Length(min=8, message='Too short')])
        submit = SubmitField('Log In')

        def __repr__(self):
            return f'<Movie {self.title}>'


    db.create_all()

# new_user = User(
#     email="darnell@darnell.com",
#     name="admin",
#     password="Password1234"
# )
#
# db.session.add(new_user)
# db.session.commit()



# CREATE DB
# my_movie_list = MovieList.query.get(1)
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg",
#     movie_list=my_movie_list
# )
# db.session.add(new_movie)
# db.session.commit()

# Create Movielist Database
# new_list = MovieList(user_id=current_user.id, title='My Favorite Movies', description='A list of my all-time favorite movies')
# db.session.add(new_list)
# db.session.commit()



@app.route("/")
def home():
    all_reviews = Movie.query.order_by(Movie.rating.desc()).all()
    return render_template("index.html", reviews=all_reviews)


@app.route("/delete")
@login_required
def delete():
    movie_id = request.args.get("id")
    delete_movie = Movie.query.get(movie_id)
    db.session.delete(delete_movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit")
@login_required
def edit():
    movie_id = request.args.get("id")
    # print(f"Movie Id from Edit route: \n {movie_id}")
    movie = Movie.query.get(movie_id)
    form = RateMovieForm(movie_id)
    # print(f"Data from Form edit route:\n{form.data}")
    return render_template("edit.html", movie=movie, form=form, )


@app.route("/update_movie", methods=["GET", "POST"])
@login_required
def update_movie():
    movie_id = request.args.get("id")
    form = RateMovieForm(id=movie_id)
    movie_id = form.id.data
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        print("VALIDATED")
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    else:
        print(form.errors)
    return render_template("edit.html", movie=movie, form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    user_form = User_reg()
    print(user_form.data)
    if request.method == "POST":
        email = user_form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email is already registered.', 'danger')
            return redirect(url_for('register'))
        if user_form.password.data != user_form.confirm.data:
            flash('Passwords do not match')
            return render_template('register.html', user_form=user_form)
        else:
            new_user = User(
                email=request.form.get('email'),
                name=request.form.get('name'),
                password=request.form.get('password')
            )
            new_user.set_password(new_user.password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("home"))

    return render_template("register.html", user_form=user_form)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        title = request.form["title"]
        url = f"https://api.themoviedb.org/3/search/movie?api_key={MOVIE_API_KEY}&query={title}"
        response = requests.get(url)
        data = response.json()["results"]
        return render_template("select.html", options=data)

    return render_template("add.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if request.method == "POST":
        email = login_form.email.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(login_form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password")
            return redirect(url_for("login"))
    return render_template("login.html", form=login_form)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_API_KEY, "language": "en-US"})
        data = response.json()
        movie_title = data["title"]
        movie = search_movie(movie_title)
        if movie:
            print("Movie already in database")
            movie.year = data["release_date"].split("-")[0]
            movie.img_url = f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}"
            movie.description = data["overview"]
            db.session.commit()
            return redirect(url_for('update_movie', id=movie.id))
        else:
            print("New Movie to be added")
            new_movie = Movie(
                title=data["title"],
                year=data["release_date"].split("-")[0],
                img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
                description=data["overview"]
            )
            db.session.add(new_movie)
            db.session.commit()
            return redirect(url_for('update_movie', id=new_movie.id))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))
if __name__ == '__main__':
    app.run(debug=True, port=5002)
