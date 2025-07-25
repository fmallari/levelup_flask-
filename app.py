from flask import Flask, render_template, redirect, session, flash, g, request
from api_client import search_exercises, fetch_gif
from models import connect_db, db, User, Workout, Nutrition
from forms import UserForm, WorkoutForm, NutritionForm


CURR_USER_KEY = "curr_user"
    
app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///levelup"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "fitness"

connect_db(app)

##########################
### register/login/logout

@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def home():
    return "hello world!"

def do_login(user):
    """Log in user"""

    session[CURR_USER_KEY] = user.id
    return render_template('login.html')

def do_logout():
    """Logout user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/profile', methods=["GET", "POST"])
def show_profile():
    if "user_id" not in session:
        flash("Login required")
        return redirect('/login')
    form = WorkoutForm()

    return render_template('profile.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # check if user already exists
        existing_user = User.query.filter_by(username=name).first()
        if existing_user:
            flash("Username already taken. Please choose another one.")
            return render_template('register.html', form=form)

        new_user = User.register(name, pwd)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id

        flash("Welcome! You have successfully created your profile")
        return redirect('/profile')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['user_id'] = user.id
            return redirect('/profile')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('/login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Successfully logged out")
    return redirect('/login')    

#######################################################

# add and edit workout form # 

@app.route('/workouts')
def workout():
    """ display workouts entered """ 

    works = Workout.query.all()

    return render_template('users/workouts.html', works=works)

@app.route('/add_workout', methods=["GET", "POST"])
def add_workout():
    """Add workout form"""

    form = WorkoutForm()

    if form.validate_on_submit():
        exercise = form.exercise.data
        weight = form.weight.data
        reps = form.reps.data
        sets = form.sets.data
        date = form.date.data
        work = Workout(exercise=exercise, weight=weight, reps=reps, sets=sets, date=date)

        db.session.add(work)
        db.session.commit()
        return redirect('/workouts')

    else:
        return render_template('users/add_workout.html', form=form)

#######################################################

# add nutrition / add food #

@app.route('/nutrition')
def nutrition():
    """Show workouts entered"""

    food = Nutrition.query.all()
    
    return render_template('users/nutrition.html', food=food)

@app.route('/add_food', methods=["GET", "POST"])
def add_food():
    """Add workout form"""

    form = NutritionForm()

    if form.validate_on_submit():
        food = form.food.data
        protein = form.protein.data
        carbs = form.carbs.data
        fats = form.fats.data
        calories = form.calories.data
        date = form.date.data
            

        food = Nutrition(food=food, protein=protein, carbs=carbs, fats=fats, calories=calories, date=date)

        db.session.add(food)
        db.session.commit()
        return redirect('/nutrition')
    else:
        return render_template('users/add_food.html', form=form) 

#######################################################

# add exercisedb api #

@app.route('/search', methods=['GET', 'POST'])
def search_workouts():
    results = []
    query = ""
    
    if request.method == 'POST':
        query = request.form['query']
        results = search_exercises(query)

        if results:
            app.logger.debug(f"Keys in workout: {list(results[0].keys())}")
            # ⬇️ Clean up the gifUrl for each result
            for w in results:
                url = w.get("gifUrl", "")
                w["gifUrl"] = url.strip()  # Remove extra spaces
        else:
            app.logger.debug("No results returned")

    return render_template('search.html', query=query, results=results)


@app.route('/images')
def show_images():
    images = fetch_gif()
    return render_template('images.html', images=images)


if __name__ == '__main__':
    app.secret_key = "some-secret-key"
    app.run(debug=True)


