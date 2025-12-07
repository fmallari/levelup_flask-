def test_home_page_loads(client):
    """GET / should load successfully."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"LevelUp" in resp.data  # checks for keyword in rendered HTML

def test_redirect_when_not_logged_in(client):
    """Protected routes should redirect unauthenticated users."""
    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code in (301, 302)

def test_register_login_logout_flow(client, db_session):
    """Full auth flow: register -> login -> logout."""
    # Register
    resp = client.post("/register", data={
        "email": "test@test.com",
        "password": "secret123"
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Login
    resp = client.post("/login", data={
        "email": "test@test.com",
        "password": "secret123"
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Logout
    resp = client.get("/logout", follow_redirects=True)
    assert resp.status_code == 200

