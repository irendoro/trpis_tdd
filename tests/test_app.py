import pytest
from app.main import app, users, failed_attempts, lockout_time, user_roles
from datetime import datetime, timedelta


# Фикстура для тестирования Flask-приложения
@pytest.fixture
def client():
    app.config['TESTING'] = True  # Включение режима тестирования
    app.config['SECRET_KEY'] = 'your_secret_key'  # Для работы с сессиями
    with app.test_client() as client:
        users.clear()
        failed_attempts.clear()  # Очищаем неудачные попытки
        lockout_time.clear()  # Очищаем время блокировки
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

# Тест на обновление профиля неавторизованного пользователя
def test_update_profile_unauthenticated(client):
    # Попытка обновления профиля без авторизации
    response = client.put('/profile/update', json={'password': 'newpassword123'})
    assert response.status_code == 401
    assert response.json['error'] == 'User not logged in'

# Тест на удаление аккаунта авторизованным пользователем
def test_delete_account_authenticated(client):
    # Регистрация и авторизация пользователя
    client.post('/register', json={'username': 'user1', 'password': 'password123'})
    client.post('/login', json={'username': 'user1', 'password': 'password123'})

    # Удаление аккаунта
    response = client.delete('/delete-account')
    assert response.status_code == 200
    assert response.json['message'] == 'Account deleted successfully'

    # Проверяем, что пользователь удален
    response = client.get('/profile')
    assert response.status_code == 401
    assert response.json['error'] == 'User not logged in'

# Тест на удаление аккаунта неавторизованного пользователя
def test_delete_account_unauthenticated(client):
    # Попытка удалить аккаунт без авторизации
    response = client.delete('/delete-account')
    assert response.status_code == 401
    assert response.json['error'] == 'User not logged in'

# Тест на ограничение количества попыток входа
def test_login_attempts_limit(client):
    # Регистрация пользователя
    client.post('/register', json={'username': 'user1', 'password': 'password123'})

    # Три неудачные попытки входа
    for i in range(2):
        response = client.post('/login', json={'username': 'user1', 'password': 'wrongpassword'})
        assert response.status_code == 400
        assert response.json['error'] == 'Invalid password'

    # Четвертая попытка должна заблокировать аккаунт
    response = client.post('/login', json={'username': 'user1', 'password': 'wrongpassword'})
    assert response.status_code == 403
    assert response.json['error'] == 'Too many failed attempts. Account locked for 10 minutes.'

    # Попытка входа после блокировки
    response = client.post('/login', json={'username': 'user1', 'password': 'password123'})
    assert response.status_code == 403
    assert 'Account is locked. Try again in' in response.json['error']  # Проверка наличия текста блокировки

    # Проверка успешного входа после окончания блокировки
    lockout_time['user1'] = datetime.now() - timedelta(seconds=1)  # Симуляция окончания блокировки
    response = client.post('/login', json={'username': 'user1', 'password': 'password123'})
    assert response.status_code == 200
    assert response.json['message'] == 'Login successful'

def test_admin_registration(client):
    # Первый пользователь должен быть администратором
    response = client.post('/register', json={'username': 'user1', 'password': 'password123'})
    assert response.status_code == 201
    assert response.json['message'] == 'Registration successful'

    # Проверка, что первый пользователь является администратором
    assert user_roles['user1'] == 'admin'

    # Регистрация второго пользователя
    response = client.post('/register', json={'username': 'user2', 'password': 'password123'})
    assert response.status_code == 201
    assert user_roles['user2'] == 'user'  # Второй пользователь обычный
