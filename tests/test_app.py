import pytest
from app.main import app, users

# Фикстура для тестирования Flask-приложения
@pytest.fixture
def client():
    app.config['TESTING'] = True  # Включение режима тестирования
    with app.test_client() as client:
        users.clear()
        yield client

# Тест на успешную регистрацию
def test_registration_success(client):
    response = client.post('/register', json={'username': 'user1', 'password': 'password123'})
    print(response.json)  # Добавим вывод для диагностики
    assert response.status_code == 201
    assert response.json['message'] == 'Registration successful'

# Тест на проверку уникальности логина
def test_registration_duplicate_username(client):
    # Первая регистрация
    response = client.post('/register', json={'username': 'user1', 'password': 'password123'})
    print(response.json)  # Добавим вывод для диагностики
    assert response.status_code == 201
    assert response.json['message'] == 'Registration successful'

    # Повторная регистрация с тем же логином
    response = client.post('/register', json={'username': 'user1', 'password': 'password456'})
    print(response.json)  # Добавим вывод для диагностики
    assert response.status_code == 400
    assert response.json['error'] == 'Username already exists'

# Тест на успешную авторизацию
def test_login_success(client):
    # Регистрация пользователя
    client.post('/register', json={'username': 'user1', 'password': 'password123'})

    # Авторизация с правильными данными
    response = client.post('/login', json={'username': 'user1', 'password': 'password123'})
    assert response.status_code == 200
    assert response.json['message'] == 'Login successful'