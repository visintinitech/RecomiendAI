import pytest
from app import create_app
from app.models import db as _db
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-key'
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        from app.models import User
        user = User(name='testuser')
        user.set_password('testpass')
        _db.session.add(user)
        _db.session.commit()
        token = create_access_token(str(user.id))
        return {'Authorization': f'Bearer {token}'}
