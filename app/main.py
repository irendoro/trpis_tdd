from flask import Flask, request, jsonify


# Создание Flask-приложения
app = Flask(__name__)

# Временное хранилище пользователей
users = {}

# Маршрут регистрации
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Логирование данных
    print(f"Received data: {data}")

    # Проверка, что данные заполнены
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Проверка уникальности логина
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

    # Сохранение нового пользователя
    users[username] = password
    return jsonify({'message': 'Registration successful'}), 201

# Маршрут авторизации
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Логирование данных
    print(f"Received data: {data}")

    # Проверка, что данные заполнены
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Проверка существования пользователя
    if username not in users:
        return jsonify({'error': 'Invalid username'}), 400

    # Проверка пароля
    if users[username] != password:
        return jsonify({'error': 'Invalid password'}), 400

    return jsonify({'message': 'Login successful'}), 200


# Запуск приложения (необходим для отладки)
if __name__ == "__main__":
    app.run(debug=True)
