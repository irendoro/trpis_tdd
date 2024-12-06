from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re

# Создание Flask-приложения
app = Flask(__name__)

# Настройки сессий
app.secret_key = 'your_secret_key'

# Временное хранилище пользователей
users = {}
user_roles = {}

# Словарь для хранения паролей
passwords = {}

# Хранилище для отслеживания неудачных попыток входа
failed_attempts = {}
lockout_time = {}

# Максимальное количество попыток
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION = timedelta(minutes=10)

# Валидация логина и пароля
def validate_username(username):
    return len(username) >= 3 and re.match(r'^[a-zA-Z0-9_]+$', username) is not None

def validate_password(password):
    return len(password) >= 6 and re.match(r'^[a-zA-Z0-9_]+$', password) is not None

# Маршрут регистрации
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Проверка, что данные заполнены
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Проверка уникальности логина
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

     # Валидация логина и пароля
    if not validate_username(username):
        return jsonify({'error': 'Username must be at least 3 characters long and can only contain letters, numbers, and underscores'}), 400
    if not validate_password(password):
        return jsonify({'error': 'Password must be at least 6 characters long and can only contain letters, numbers, and underscores'}), 400

    # Регистрируем первого пользователя как администратора
    if not users:
        user_roles[username] = 'admin'  # Назначаем роль администратор для первого пользователя
    else:
        user_roles[username] = 'user'  # По умолчанию обычный пользователь для остальных

    # Сохранение нового пользователя
    # Хешируем пароль перед сохранением
    users[username] = generate_password_hash(password)
    passwords[username] = password
    return jsonify({'message': 'Registration successful'}), 201

# Маршрут авторизации
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Проверка, что данные заполнены
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Проверка существования пользователя
    if username not in users:
        return jsonify({'error': 'Invalid username'}), 400
    
    # Проверка блокировки аккаунта
    if username in lockout_time:
        time_left = lockout_time[username] - datetime.now()
        if time_left > timedelta(seconds=0):
            return jsonify({'error': f'Account is locked. Try again in {time_left}'}), 403
        else:
            del lockout_time[username]  # Снимаем блокировку, если время прошло

    # Проверка пароля
    if not check_password_hash(users[username], password):
         # Увеличиваем количество неудачных попыток
        failed_attempts[username] = failed_attempts.get(username, 0) + 1
        if failed_attempts[username] >= MAX_FAILED_ATTEMPTS:
            lockout_time[username] = datetime.now() + LOCKOUT_DURATION
            failed_attempts[username] = 0  # Сбрасываем счетчик неудачных попыток
            return jsonify({'error': 'Too many failed attempts. Account locked for 10 minutes.'}), 403
        return jsonify({'error': 'Invalid password'}), 400  # Вернуть статус 400 на 3-й неудачной попытке
    
    # Сбрасываем неудачные попытки, если вход успешен
    failed_attempts[username] = 0

    # Сохраняем информацию о пользователе в сессии
    session['username'] = username

    return jsonify({'message': 'Login successful'}), 200


# Маршрут получения профиля
@app.route('/profile', methods=['GET'])
def profile():
    # Проверка, авторизован ли пользователь
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Возвращаем информацию о текущем пользователе
    username = session['username']
    return jsonify({'username': username, 'message': 'Profile data'}), 200

# Маршрут для обновления профиля
@app.route('/profile/update', methods=['PUT'])
def update_profile():
    username = session.get('username')
    # Проверка, авторизован ли пользователь
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    new_username = data.get('username')
    password = data.get('password')

    # Проверка, что пароль передан
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    
    # Проверка, что username передан в запросе
    if not new_username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Проверка роли
    if user_roles[username] != 'admin' and new_username != username:
        return jsonify({'error': 'Permission denied'}), 403

    # Хешируем новый пароль и сохраняем его
    users[session['username']] = generate_password_hash(password)

    return jsonify({'message': 'Profile updated successfully'}), 200

# Маршрут для удаления аккаунта
@app.route('/delete-account', methods=['DELETE'])
def delete_account():
    # Проверка, авторизован ли пользователь
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Удаляем пользователя из хранилища
    username = session['username']
    del users[username]

    # Очищаем сессию
    session.pop('username', None)

    return jsonify({'message': 'Account deleted successfully'}), 200


# Запуск приложения (необходим для отладки)
if __name__ == "__main__":
    app.run(debug=True)
