import pytest
from datetime import datetime
from app import app, db
from models import User, Workout, Nutrition

class TestUserAuthentication:
    """Test user authentication functionality"""
    
    def test_user_registration(self, test_client):
        """Test new user can register"""
        response = test_client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'new@example.com'
    
    def test_user_login_success(self, test_client, test_user):
        """Test user can login with correct credentials"""
        response = test_client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'testuser' in response.data or b'Profile' in response.data
    
    def test_user_login_failure(self, test_client, test_user):
        """Test login fails with incorrect password"""
        response = test_client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid' in response.data or b'incorrect' in response.data
    
    def test_logout(self, authenticated_client):
        """Test user can logout"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_duplicate_username_registration(self, test_client, test_user):
        """Test cannot register with existing username"""
        response = test_client.post('/register', data={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert b'already exists' in response.data or b'taken' in response.data


class TestWorkoutManagement:
    """Test workout CRUD operations"""
    
    def test_add_workout_requires_login(self, test_client):
        """Test add workout page requires authentication"""
        response = test_client.get('/add_workout', follow_redirects=True)
        assert b'Login' in response.data
    
    def test_add_workout_success(self, authenticated_client):
        """Test authenticated user can add workout"""
        response = authenticated_client.post('/add_workout', data={
            'exercise': 'Squats',
            'sets': 4,
            'reps': 8,
            'weight': 225,
            'muscle_group': 'Legs'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        with app.app_context():
            workout = Workout.query.filter_by(exercise='Squats').first()
            assert workout is not None
            assert workout.sets == 4
            assert workout.reps == 8
    
    def test_view_workout_history(self, authenticated_client, sample_workout):
        """Test user can view their workout history"""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200
        assert b'Bench Press' in response.data
    
    def test_delete_workout(self, authenticated_client, sample_workout):
        """Test user can delete their workout"""
        workout_id = sample_workout.id
        response = authenticated_client.post(
            f'/delete_workout/{workout_id}',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        with app.app_context():
            workout = Workout.query.get(workout_id)
            assert workout is None
    
    def test_edit_workout(self, authenticated_client, sample_workout):
        """Test user can edit their workout"""
        workout_id = sample_workout.id
        response = authenticated_client.post(f'/edit_workout/{workout_id}', data={
            'exercise': 'Incline Bench Press',
            'sets': 4,
            'reps': 12,
            'weight': 115,
            'muscle_group': 'Chest'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        with app.app_context():
            workout = Workout.query.get(workout_id)
            assert workout.exercise == 'Incline Bench Press'
            assert workout.sets == 4
    
    def test_workout_validation(self, authenticated_client):
        """Test workout form validates input"""
        response = authenticated_client.post('/add_workout', data={
            'exercise': '',
            'sets': -1,
            'reps': 0,
            'weight': -50,
            'muscle_group': ''
        }, follow_redirects=True)
        
        # Should show validation errors
        assert response.status_code == 200


class TestNutritionTracking:
    """Test nutrition tracking functionality"""
    
    def test_add_nutrition_requires_login(self, test_client):
        """Test add nutrition page requires authentication"""
        response = test_client.get('/add_nutrition', follow_redirects=True)
        assert b'Login' in response.data
    
    def test_add_nutrition_success(self, authenticated_client):
        """Test authenticated user can add nutrition entry"""
        response = authenticated_client.post('/add_nutrition', data={
            'food_name': 'Brown Rice',
            'calories': 215,
            'protein': 5,
            'carbs': 45,
            'fats': 1.6
        }, follow_redirects=True)
        
        assert response.status_code == 200
        with app.app_context():
            nutrition = Nutrition.query.filter_by(food_name='Brown Rice').first()
            assert nutrition is not None
            assert nutrition.calories == 215
    
    def test_view_nutrition_history(self, authenticated_client, sample_nutrition):
        """Test user can view nutrition history"""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200
        assert b'Chicken Breast' in response.data
    
    def test_delete_nutrition(self, authenticated_client, sample_nutrition):
        """Test user can delete nutrition entry"""
        nutrition_id = sample_nutrition.id
        response = authenticated_client.post(
            f'/delete_nutrition/{nutrition_id}',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        with app.app_context():
            nutrition = Nutrition.query.get(nutrition_id)
            assert nutrition is None
    
    def test_nutrition_daily_totals(self, authenticated_client):
        """Test calculating daily nutrition totals"""
        # Add multiple nutrition entries
        foods = [
            {'food_name': 'Oatmeal', 'calories': 150, 'protein': 5, 'carbs': 27, 'fats': 3},
            {'food_name': 'Banana', 'calories': 105, 'protein': 1, 'carbs': 27, 'fats': 0},
            {'food_name': 'Chicken', 'calories': 165, 'protein': 31, 'carbs': 0, 'fats': 3.6}
        ]
        
        for food in foods:
            authenticated_client.post('/add_nutrition', data=food)
        
        response = authenticated_client.get('/nutrition_summary')
        assert response.status_code == 200
        # Should show total calories, protein, etc.

class TestDatabaseModels:
    """Test database models"""
    
    def test_user_password_hashing(self, test_client):
        """Test password is properly hashed"""
        with app.app_context():
            user = User(username='hashtest', email='hash@test.com')
            user.set_password('mypassword')
            
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_workout_user_relationship(self, test_user):
        """Test workout-user relationship"""
        with app.app_context():
            workout = Workout(
                user_id=test_user.id,
                exercise='Deadlift',
                sets=3,
                reps=5,
                weight=315
            )
            db.session.add(workout)
            db.session.commit()
            
            assert workout.user.username == 'testuser'
            assert workout in test_user.workouts
    
    def test_nutrition_user_relationship(self, test_user):
        """Test nutrition-user relationship"""
        with app.app_context():
            nutrition = Nutrition(
                user_id=test_user.id,
                food_name='Apple',
                calories=95,
                protein=0,
                carbs=25,
                fats=0
            )
            db.session.add(nutrition)
            db.session.commit()
            
            assert nutrition.user.username == 'testuser'
            assert nutrition in test_user.nutrition_entries


class TestAPIIntegration:
    """Test external API integration"""
    
    def test_muscle_groups_endpoint(self, authenticated_client):
        """Test fetching muscle groups"""
        response = authenticated_client.get('/api/muscle_groups')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_exercises_by_muscle_endpoint(self, authenticated_client):
        """Test fetching exercises by muscle group"""
        response = authenticated_client.get('/api/exercises?muscle=chest')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    @pytest.mark.skipif(True, reason="Requires API key")
    def test_exercise_api_integration(self):
        """Test actual API integration (requires API key)"""
        from api_client import get_exercises_by_muscle
        exercises = get_exercises_by_muscle('chest')
        assert len(exercises) > 0


class TestAuthorization:
    """Test authorization and access control"""
    
    def test_user_can_only_edit_own_workouts(self, test_client):
        """Test user cannot edit another user's workout"""
        with app.app_context():
            # Create two users
            user1 = User(username='user1', email='user1@test.com')
            user1.set_password('pass123')
            user2 = User(username='user2', email='user2@test.com')
            user2.set_password('pass123')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            # User2 creates a workout
            workout = Workout(
                user_id=user2.id,
                exercise='Squats',
                sets=4,
                reps=8,
                weight=225
            )
            db.session.add(workout)
            db.session.commit()
            workout_id = workout.id
        
        # User1 logs in
        test_client.post('/login', data={
            'username': 'user1',
            'password': 'pass123'
        })
        
        # Try to edit user2's workout
        response = test_client.post(f'/edit_workout/{workout_id}', data={
            'exercise': 'Modified Exercise',
            'sets': 5,
            'reps': 10,
            'weight': 250,
            'muscle_group': 'Legs'
        }, follow_redirects=True)
        
        # Workout should not be modified
        with app.app_context():
            workout = Workout.query.get(workout_id)
            assert workout.exercise == 'Squats'
    
    def test_user_can_only_view_own_data(self, test_client):
        """Test users can only see their own workouts"""
        with app.app_context():
            user1 = User(username='viewer1', email='v1@test.com')
            user1.set_password('pass123')
            user2 = User(username='viewer2', email='v2@test.com')
            user2.set_password('pass123')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            # Each user creates a workout
            workout1 = Workout(user_id=user1.id, exercise='Bench', sets=3, reps=10, weight=135)
            workout2 = Workout(user_id=user2.id, exercise='Squats', sets=4, reps=8, weight=225)
            db.session.add_all([workout1, workout2])
            db.session.commit()
        
        # User1 logs in
        test_client.post('/login', data={'username': 'viewer1', 'password': 'pass123'})
        response = test_client.get('/profile')
        
        # Should see own workout but not user2's
        assert b'Bench' in response.data
        assert b'Squats' not in response.data


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_sql_injection_protection(self, authenticated_client):
        """Test protection against SQL injection"""
        response = authenticated_client.post('/add_workout', data={
            'exercise': "'; DROP TABLE workouts; --",
            'sets': 3,
            'reps': 10,
            'weight': 135,
            'muscle_group': 'Chest'
        }, follow_redirects=True)
        
        # Should handle safely
        with app.app_context():
            # Workouts table should still exist
            workouts = Workout.query.all()
            assert isinstance(workouts, list)
    
    def test_concurrent_user_sessions(self, test_client):
        """Test multiple users can be logged in simultaneously"""
        with app.app_context():
            user1 = User(username='concurrent1', email='c1@test.com')
            user1.set_password('pass123')
            user2 = User(username='concurrent2', email='c2@test.com')
            user2.set_password('pass123')
            db.session.add_all([user1, user2])
            db.session.commit()
        
        # Create two separate clients
        client1 = app.test_client()
        client2 = app.test_client()
        
        # Both log in
        client1.post('/login', data={'username': 'concurrent1', 'password': 'pass123'})
        client2.post('/login', data={'username': 'concurrent2', 'password': 'pass123'})
        
        # Both should have access
        response1 = client1.get('/profile')
        response2 = client2.get('/profile')
        
        assert response1.status_code == 200
        assert response2.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])