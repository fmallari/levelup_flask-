import os
from flask import Flask, render_template, redirect, session, flash, g, request, url_for
from werkzeug.utils import secure_filename
from api_client import search_exercises, fetch_gif
from models import connect_db, db, User, Workout, Nutrition
from forms import UserForm, WorkoutForm, NutritionForm
from datetime import datetime, timedelta
import uuid

#  BROOO whats up! Heres some stuff I added: 
# - Profile picture upload logic. I was getting a NoneType error when trying to update the pfp so switched up the routing
#   to use session['user_id']. You already had most of the logic setup for the upload, just needed to add the user_id check
#   and update the user profile image in the database.
# - Username during login was case sensitive so we did a quick little .lower on that bad boy 
# - Also added a default profile image in case the user doesn't upload one, which again you already had but like.. now its generic. 
# - I also added a session timeout feature that logs the user out after 1 minute of inactivity... because im rich. For real deployment 
#   you should change that time to like 15 or 20 minutes but for testing purposes I have it set at 1 min. 
# - I also added a boot_id (Import uuid vibes) to the session to prevent sessions from staying logged int between app initiations. 
#   This part is NOT scalable, but it works for now lol. 
# - Oh I also added a re-route for the LevelUp button. Now when a use is logged in and taps LevelUp it brings them to the search page. Before 
#   it was bringning them to the registration page lol. 
# - The workout and nutrition data is now filtered by logged in user. so I *THINK* all user data is seperated now (PFP, Workout, Nutrishhh, and just all the other vibes)
#   Thats actually it. Thats all I did. Your code is really good btw! Im very impressed! Ill pop lock and drop a branch for you to test and if you like it you can merge. 
# p.s You will see Docker files in the repo now. thats becasue the project is now a container and you can run it anywhere. the ONLY dependency I didnt set up was the db 

CURR_USER_KEY = "curr_user"
BOOT_ID = os.environ.get("BOOT_ID") or str(uuid.uuid4())

app = Flask(__name__)
app.secret_key = 'supersecretkey'

#if __name__ == "__main__":
   # app.run(debug=True, use_reloader=False)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql:///levelup")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "fitness"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "avatars")
app.config['SESSION_PERMANENT'] = False

# Config file upload folder 
app.config['UPLOAD_FOLDER'] = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

connect_db(app)

##########################
### register/login/logout

@app.before_request
def before_every_request():
    if session.get('boot_id') != BOOT_ID:
        print("boot_id mismatch — clearing session")
        session.clear()
        flash("You've been logged out.")
        session['boot_id'] = BOOT_ID

    timeout = timedelta(minutes=1)
    now = datetime.utcnow()

    if CURR_USER_KEY in session:
        last_active = session.get('last_active')

        if last_active:
            try:
                last_active_dt = datetime.fromisoformat(last_active)
                if now - last_active_dt > timeout:
                    session.clear()
                    flash("You've been logged out for inactivity.")
                    return redirect('/login')
            except Exception as e:
                print("Couldn't parse last_active:", e)

        session['last_active'] = now.isoformat()

    g.user = User.query.get(session[CURR_USER_KEY]) if CURR_USER_KEY in session else None

# def home():
#     return "hello world!"

def do_login(user):
    session[CURR_USER_KEY] = user.id
    session['boot_id'] = BOOT_ID
    session['last_active'] = datetime.utcnow().isoformat()
    print(" Logged in, session is:", session)

def do_logout():
    """Logs out the current user by clearing the session."""

    session.clear() 

@app.route('/')
def home_page():
    return render_template('home.html')

#######################################################

# register/login form # 

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()

    # make sure g.user is set 
    if form.validate_on_submit():
        username = form.username.data.lower()
        pwd = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("That username is already taken, Try another one.")
            return render_template("register.html", form=form)

        profile_image = request.files.get("profile_image")

        if profile_image:
            image_filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
        else:
            image_filename = "default.png"

        new_user = User.register(username, pwd, profile_image=image_filename)
        db.session.add(new_user)
        db.session.commit()
        do_login(new_user)
        return redirect('/profile')
    
    return render_template("register.html", form=form)

@app.route('/login', methods=['GET','POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
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
    do_logout()
    flash("You’ve been logged out")
    return redirect('/login')

#######################################################

# workout & nutrish view # 

@app.route('/profile', methods=["GET", "POST"])
def show_profile():
    if "user_id" not in session:
        flash("Login required")
        return redirect('/login')

    form = WorkoutForm()
    user_id = session["user_id"]

    workouts = (Workout
                .query
                .filter_by(user_id=user_id)
                .order_by(Workout.date.desc())
                .all())

    nutrition_entries = (Nutrition
                         .query
                         .filter_by(user_id=user_id)
                         .order_by(Nutrition.date.desc())
                         .all())

    user = User.query.get(user_id)
    return render_template(
        'profile.html',
        form=form,
        workouts=workouts,
        nutrition_entries=nutrition_entries,
        user=user
    )

#######################################################

# this is the image upload handler #

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'profile_image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['profile_image']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
       
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        user_id = session.get('user_id')
        if not user_id:
            flash('User not logged in')
            return redirect('/login')
        user = User.query.get(user_id)
        if not user:
            flash('User not found')
            return redirect('/login')
        user.profile_image = filename
        db.session.commit()

        flash('Profile image updated successfully!')
        return redirect('/profile')
    
    flash('Invalid file format')
    return redirect(request.url)

#######################################################

# edit profile name # 

@app.route('/edit_profile_name', methods=["POST"])
def edit_profile_name():
    if "user_id" not in session:
        flash("Login required")
        return redirect('/login')

    user_id = session["user_id"]
    user = User.query.get(user_id)
    
    # Update the username
    user.username = request.form['username']
    db.session.commit()

    flash("Profile name updated successfully!")
    return redirect('/profile')


#######################################################

# add and delete workout # 

@app.route('/workouts')
def workout():
    """ display workouts entered for the current user only """ 
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in.")
        return redirect('/login')
    works = Workout.query.filter_by(user_id=user_id).all()
    return render_template('users/workouts.html', works=works)

@app.route('/add_workout', methods=["GET", "POST"])
def add_workout():
    form = WorkoutForm()

    if form.validate_on_submit():
        exercise = form.exercise.data
        weight = form.weight.data
        reps = form.reps.data
        sets = form.sets.data
        date = form.date.data

        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in.")
            return redirect('/login')

        work = Workout(
            exercise=exercise,
            weight=weight,
            reps=reps,
            sets=sets,
            date=date,
            user_id=user_id  
        )

        db.session.add(work)
        db.session.commit()
        return redirect('/profile')

    return render_template('users/add_workout.html', form=form)


@app.route('/workouts/delete/<int:workout_id>', methods=['POST'])
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    return redirect(url_for('workout')) 


#######################################################

# add and delete nutrition 

@app.route('/nutrition')
def nutrition():
    """Show nutrition entries for the current user only"""
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in.")
        return redirect('/login')
    food = Nutrition.query.filter_by(user_id=user_id).all()
    return render_template('users/nutrition.html', food=food)

@app.route('/add_food', methods=["GET", "POST"])
def add_food():
    form = NutritionForm()

    if form.validate_on_submit():
        food = form.food.data
        protein = form.protein.data
        carbs = form.carbs.data
        fats = form.fats.data
        calories = form.calories.data
        date = form.date.data

        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in.")
            return redirect('/login')

        food = Nutrition(
            food=food,
            protein=protein,
            carbs=carbs,
            fats=fats,
            calories=calories,
            date=date,
            user_id=user_id 
        )

        db.session.add(food)
        db.session.commit()
        return redirect('/profile')

    return render_template('users/add_food.html', form=form)


@app.route('/nutrition/delete/<int:food_id>', methods=['POST'])
def delete_food(food_id):
    food = Nutrition.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()
    return redirect(url_for('nutrition'))

#######################################################

# exercisedb api 

@app.route('/search', methods=['GET', 'POST'])
def search_workouts():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form['query']
        results = search_exercises(query)

        if results:
            app.logger.debug(f"Keys in workout: {list(results[0].keys())}")
            for w in results:
                url = w.get("gifUrl") or ""
                url = url.strip()
                
                # validate URL #
                w["gifUrl"] = url if url.startswith("http") else None
        else:
            app.logger.debug("No results returned")
    return render_template('search.html', query=query, results=results)



# @app.route('/images')
# def show_images():
#     images = fetch_gif()
#     return render_template('images.html', images=images)

# if __name__ == '__main__':
    app.secret_key = "some-secret-key"
    app.run(debug=True)

with app.app_context():
    from models import db
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

    with app.app_context():
        from models import db
        db.create_all()