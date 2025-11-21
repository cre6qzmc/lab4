import pytest
import sys
import os
from fastapi.testclient import TestClient
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app
from database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_successful_registration(test_db):
    response = client.post(
        "/api/register",
        json={"login": "testuser", "password": "Test123!@#"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "user создан"
    assert "user_id" in response.json()

def test_duplicate_login(test_db):
    # Первая регистрация
    client.post(
        "/api/register",
        json={"login": "testuser", "password": "Test123!@#"}
    )
    
    # Вторая регистрация с тем же логином
    response = client.post(
        "/api/register",
        json={"login": "testuser", "password": "Test123!@#"}
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_weak_password(test_db):
    response = client.post(
        "/api/register",
        json={"login": "newuser", "password": "weak"}
    )
    assert response.status_code == 422
    response_data = response.json()
    
    # Проверяем структуру ошибки валидации FastAPI
    assert "detail" in response_data
    detail = response_data["detail"]
    
    # Ошибка приходит в виде списка объектов
    assert isinstance(detail, list)
    assert len(detail) > 0
    
    # Проверяем что есть ошибка связанная с password
    password_errors = [error for error in detail if "password" in error.get("loc", [])]
    assert len(password_errors) > 0
    
    # Проверяем сообщение об ошибке
    error_msg = password_errors[0].get("msg", "")
    assert "Must be at least 8 characters long" in error_msg
    assert "uppercase" in error_msg
    assert "digit" in error_msg
    assert "special character" in error_msg

def test_successful_login(test_db):
    # Сначала регистрируем пользователя
    client.post(
        "/api/register",
        json={"login": "testuser", "password": "Test123!@#"}
    )
    
    # Пытаемся войти
    response = client.post(
        "/api/login",
        json={"login": "testuser", "password": "Test123!@#"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"

def test_login_invalid_credentials(test_db):
    response = client.post(
        "/api/login",
        json={"login": "nonexistent", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert "Invalid login or password" in response.json()["detail"]