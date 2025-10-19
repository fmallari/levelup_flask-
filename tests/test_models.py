from models import User, Workout

def test_create_user(db_session):
    u = User(username="testuser", password="another1")
    db_session.session.add(u)
    db_session.session.commit()
    got = User.query.first()
    assert.got.username == "testuser"

def test_workout_relationship(db_session):
    u = User(username="workoutuser", password="workout1")
    db_session.session.add(u)
    db_session.session.commit()

    w = Workout(
        user_id=u.id,
        exercise_name="Push Up",
        sets=3,
        reps=15,
        date="2024-01-01"
    )
    db_session.session.add(w)
    db_session.session.commit()

    got_user = User.query.filter_by(username="workoutuser").first()
    assert len(got_user.workouts) == 1
    assert got_user.workouts[0].exercise_name == "Push Up"

