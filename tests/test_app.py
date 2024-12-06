import pytest
from app.main import app, users

# Фикстура для тестирования Flask-приложения
@pytest.fixture
def client():
    app.config['TESTING'] = True  # Включение режима тестирования
    app.config['SECRET_KEY'] = 'your_secret_key'  # Для работы с сессиями
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

# Тест на авторизацию с неправильным паролем
def test_login_invalid_password(client):
    # Регистрация пользователя
    client.post('/register', json={'username': 'user1', 'password': 'password123'})

    # Попытка авторизоваться с неверным паролем
    response = client.post('/login', json={'username': 'user1', 'password': 'wrongpassword'})
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid password'

# Тест на авторизацию с неправильным логином
def test_login_invalid_username(client):
    # Попытка авторизоваться с несуществующим логином
    response = client.post('/login', json={'username': 'nonexistent', 'password': 'password123'})
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid username'

# Тест на получение профиля авторизованного пользователя
def test_profile_authenticated(client):
    # Регистрация и авторизация пользователя
    client.post('/register', json={'username': 'user1', 'password': 'password123'})
    client.post('/login', json={'username': 'user1', 'password': 'password123'})

    # Запрос к маршруту профиля
    response = client.get('/profile')
    assert response.status_code == 200
    assert response.json['username'] == 'user1'
    assert response.json['message'] == 'Profile data'

# Тест на получение профиля неавторизованного пользователя
def test_profile_unauthenticated(client):
    # Запрос к маршруту профиля без авторизации
    response = client.get('/profile')
    assert response.status_code == 401
    assert response.json['error'] == 'User not logged in'

# Тест на обновление профиля (пароля)
def test_update_profile_authenticated(client):
    # Регистрация и авторизация пользователя
    client.post('/register', json={'username': 'user1', 'password': 'password123'})
    client.post('/login', json={'username': 'user1', 'password': 'password123'})

    # Обновление пароля
    response = client.put('/profile/update', json={'password': 'newpassword123'})
    assert response.status_code == 200
    assert response.json['message'] == 'Profile updated successfully'

    # Проверяем, что новый пароль правильно сохранен
    # Попробуем войти с новым паролем
    response = client.post('/login', json={'username': 'user1', 'password': 'newpassword123'})
    assert response.status_code == 200
    assert response.json['message'] == 'Login successful'