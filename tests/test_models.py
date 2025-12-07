from models import User, Workout

def test_create_user(db_session):
    u = User(email="test@test.com", password="hashedpass", username="testuser")  # include required fields
    db_session.session.add(u)
    db_session.session.commit()

    got = User.query.first()
    assert got is not None
    assert got.email == "test@test.com"
    assert got.username == "tester100" 

def test_workout_relationship(db_session):
    u = User(email="a@a.com", password="pass", username="alpha")  # include required fields
    db_session.session.add(u)
    db_session.session.commit()

    w = Workout(name="Bench Press", reps=10, weight=135, user_id=u.id)
    db_session.session.add(w)
    db_session.session.commit()

    got = Workout.query.first()
    assert got is not None
    assert got.user.email == "a@a.com"
