from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

# Создание Flask-приложения
app = Flask(__name__)

# Настройки сессий
app.secret_key = 'your_secret_key'

# Временное хранилище пользователей
users = {}

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

    # Сохранение нового пользователя
    # Хешируем пароль перед сохранением
    users[username] = generate_password_hash(password)
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

    # Проверка пароля
    if not check_password_hash(users[username], password):
        return jsonify({'error': 'Invalid password'}), 400
    
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

# Запуск приложения (необходим для отладки)
if __name__ == "__main__":
    app.run(debug=True)
