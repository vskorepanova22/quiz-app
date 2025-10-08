# import socket
# from pyngrok import ngrok, conf
# import threading
# from flask import Flask, render_template, request
# from flask_socketio import SocketIO, emit
# import time
#
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'quiz_secret_key_2024'
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
#
# # Вопросы для викторины
# questions = [
#     {
#         'id': 1,
#         'question': 'Столица Франции?',
#         'options': ['Лондон', 'Париж', 'Берлин', 'Мадрид'],
#         'correct_answer': 1
#     },
#     {
#         'id': 2,
#         'question': '2 + 2 = ?',
#         'options': ['3', '4', '5', '6'],
#         'correct_answer': 1
#     },
#     {
#         'id': 3,
#         'question': 'Самая большая планета Солнечной системы?',
#         'options': ['Земля', 'Юпитер', 'Сатурн', 'Марс'],
#         'correct_answer': 1
#     },
#     {
#         'id': 4,
#         'question': 'Автор "Войны и мира"?',
#         'options': ['Достоевский', 'Толстой', 'Чехов', 'Тургенев'],
#         'correct_answer': 1
#     },
#     {
#         'id': 5,
#         'question': 'Химическая формула воды?',
#         'options': ['CO2', 'H2O', 'O2', 'NaCl'],
#         'correct_answer': 1
#     }
# ]
#
#
# class QuizManager:
#     def __init__(self):
#         self.current_question_index = 0
#         self.quiz_active = False
#         self.time_left = 30
#         self.timer_thread = None
#         self.players = {}
#         self.scores = {}
#         self.answers = {}
#         self.timer_active = False
#         self.question_start_time = None
#
#     def start_quiz(self):
#         if not self.quiz_active:
#             self.quiz_active = True
#             self.current_question_index = 0
#             self.players = {}
#             self.scores = {}
#             self.answers = {}
#             print("🎬 Викторина начата!")
#             socketio.emit('quiz_started', broadcast=True)
#             self.start_question()
#
#     def start_question(self):
#         if self.current_question_index < len(questions):
#             self.answers = {}
#             self.time_left = 10  # Уменьшим время для тестирования
#             self.timer_active = True
#             self.question_start_time = time.time()
#
#             question_data = questions[self.current_question_index]
#
#             # Отправляем вопрос всем клиентам
#             socketio.emit('new_question', {
#                 'question_id': question_data['id'],
#                 'question': question_data['question'],
#                 'options': question_data['options'],
#                 'question_number': self.current_question_index + 1,
#                 'total_questions': len(questions),
#                 'time_left': self.time_left
#             })
#
#             print(f"🚀 Вопрос {self.current_question_index + 1} начат: {question_data['question']}")
#             self.start_timer()
#
#     def start_timer(self):
#         def countdown():
#             for i in range(self.time_left, -1, -1):
#                 if not self.timer_active:
#                     break
#                 self.time_left = i
#                 socketio.emit('timer_update', {'time_left': self.time_left})
#                 time.sleep(1)
#
#             if self.timer_active:
#                 print(f"⏰ Время вышло для вопроса {self.current_question_index + 1}")
#                 self.end_question()
#
#         self.timer_thread = threading.Thread(target=countdown)
#         self.timer_thread.daemon = True
#         self.timer_thread.start()
#
#     def end_question(self):
#         self.timer_active = False
#
#         # Подсчет результатов для текущего вопроса
#         question = questions[self.current_question_index]
#         correct_answer = question['correct_answer']
#
#         results = {
#             'total_players': len(self.players),
#             'answered_players': len(self.answers),
#             'correct_answers': sum(1 for answer in self.answers.values()
#                                    if answer == correct_answer),
#             'correct_answer': correct_answer,
#             'correct_answer_text': question['options'][correct_answer],
#             'question_number': self.current_question_index + 1
#         }
#
#         print(f"📊 Результаты вопроса {self.current_question_index + 1}:")
#         print(f"   Игроков ответило: {len(self.answers)}/{len(self.players)}")
#         print(f"   Правильных ответов: {results['correct_answers']}")
#
#         # Отправляем результаты
#         socketio.emit('question_results', results)
#
#         # Ждем 3 секунды перед следующим вопросом
#         print("⏳ Ожидание 3 секунд перед следующим вопросом...")
#         time.sleep(3)
#
#         self.current_question_index += 1
#         if self.current_question_index < len(questions):
#             self.start_question()
#         else:
#             self.end_quiz()
#
#     def end_quiz(self):
#         self.quiz_active = False
#         self.timer_active = False
#
#         # Расчет финальных результатов
#         rankings = []
#         for player_id, player_data in self.players.items():
#             rankings.append({
#                 'name': player_data['name'],
#                 'score': self.scores.get(player_id, 0),
#                 'correct_answers': player_data.get('correct_answers', 0)
#             })
#
#         # Сортировка по убыванию баллов
#         rankings.sort(key=lambda x: x['score'], reverse=True)
#
#         final_results = {
#             'rankings': rankings[:10],
#             'winners': rankings[:3] if len(rankings) >= 3 else rankings,
#             'total_players': len(self.players),
#             'total_questions': len(questions)
#         }
#
#         socketio.emit('quiz_finished', final_results)
#
#         print("🎉 Викторина завершена!")
#         print(f"📈 Участвовало игроков: {len(self.players)}")
#         print("🏆 Победители:")
#         for i, winner in enumerate(final_results['winners']):
#             print(f"   {i + 1}. {winner['name']} - {winner['score']} баллов")
#
#     def add_player(self, player_id, name):
#         if player_id not in self.players:
#             self.players[player_id] = {
#                 'name': name,
#                 'correct_answers': 0
#             }
#             self.scores[player_id] = 0
#             print(f"👤 Новый игрок: {name} (всего игроков: {len(self.players)})")
#
#             # Автоматически запускаем викторину при первом игроке (для тестирования)
#             if len(self.players) == 1 and not self.quiz_active:
#                 print("👑 Первый игрок присоединился - запускаем викторину через 3 секунды...")
#                 threading.Timer(3.0, self.start_quiz).start()
#
#     def submit_answer(self, player_id, question_id, answer_index):
#         if (player_id in self.players and
#                 self.timer_active and
#                 player_id not in self.answers):
#
#             self.answers[player_id] = answer_index
#
#             current_question = questions[self.current_question_index]
#             response_time = time.time() - self.question_start_time
#
#             if answer_index == current_question['correct_answer']:
#                 # Баллы: чем быстрее ответ, тем больше баллов
#                 time_bonus = max(1, 10 - int(response_time))
#                 self.scores[player_id] += time_bonus
#                 self.players[player_id]['correct_answers'] += 1
#                 print(
#                     f"✅ Правильный ответ от {self.players[player_id]['name']} (+{time_bonus} баллов, время: {response_time:.1f}с)")
#             else:
#                 print(f"❌ Неправильный ответ от {self.players[player_id]['name']}")
#
#
# quiz_manager = QuizManager()
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/admin')
# def admin():
#     return render_template('admin.html')
#
#
# @socketio.on('connect')
# def handle_connect():
#     print(f'🔌 Новое подключение: {request.sid}')
#     emit('connected', {'status': 'ok'})
#
#
# @socketio.on('disconnect')
# def handle_disconnect():
#     print(f'🔌 Отключение: {request.sid}')
#
#
# @socketio.on('join_quiz')
# def handle_join(data):
#     name = data.get('name', 'Аноним').strip()
#     if not name:
#         name = 'Аноним'
#
#     quiz_manager.add_player(request.sid, name)
#     emit('joined_success', {'name': name})
#
#     if quiz_manager.quiz_active:
#         quiz_manager.start_question()
#
#
# @socketio.on('submit_answer')
# def handle_answer(data):
#     question_id = data.get('question_id')
#     answer_index = data.get('answer_index')
#
#     quiz_manager.submit_answer(request.sid, question_id, answer_index)
#     emit('answer_received', {'status': 'ok'})
#
#
# @socketio.on('start_quiz')
# def handle_start():
#     quiz_manager.start_quiz()
#     print('🎬 Викторина начата администратором!')
#
#
# @socketio.on('force_next_question')
# def handle_force_next():
#     if quiz_manager.quiz_active:
#         print('⏭️ Принудительный переход к следующему вопросу')
#         quiz_manager.timer_active = False
#         # Используем поток для безопасного завершения вопроса
#         threading.Timer(0.1, quiz_manager.end_question).start()
#
#
# def get_local_ip():
#     """Получает локальный IP-адрес для доступа из сети"""
#     try:
#         # Создаем временное соединение чтобы узнать наш IP
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             s.connect(("8.8.8.8", 80))
#             return s.getsockname()[0]
#     except:
#         return "127.0.0.1"
#
#
# if __name__ == '__main__':
#     local_ip = get_local_ip()
#     port = 8080
#
#     print("=" * 70)
#     print("🎯 ЗАПУСК СЕРВЕРА ВИКТОРИНЫ")
#     print("=" * 70)
#     print("📍 Локальный доступ:")
#     print(f"   📱 http://localhost:{port}")
#     print(f"   ⚙️  http://localhost:{port}/admin")
#     print("")
#     print("📍 Сетевой доступ (для других устройств):")
#     print(f"   📱 http://{local_ip}:{port}")
#     print(f"   ⚙️  http://{local_ip}:{port}/admin")
#     print("")
#     print("💡 Для доступа с других устройств:")
#     print("   1. Убедитесь, что устройства в одной сети Wi-Fi")
#     print("   2. Используйте адрес из раздела 'Сетевой доступ'")
#     print("   3. Разрешите подключение в брандмауэре Windows")
#     print("=" * 70)
#
#     try:
#         socketio.run(
#             app,
#             host='0.0.0.0',  # Принимать подключения со всех интерфейсов
#             port=port,
#             debug=True,
#             allow_unsafe_werkzeug=True
#         )
#     except Exception as e:
#         print(f"❌ Ошибка запуска: {e}")
#         print("💡 Попробуйте другой порт (например, 5000, 8000, 8081)")
#
# Вариант2 с NGROK
# from flask import Flask, render_template, request
# from flask_socketio import SocketIO, emit
# import time
# import threading
# import socket
# import sys
# import requests
# import json
# import os
# import subprocess
#
# try:
#     from pyngrok import ngrok, conf
#     NGROK_AVAILABLE = True
# except ImportError:
#     NGROK_AVAILABLE = False
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'quiz_secret_key_2024'
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
#
# # Вопросы для викторины
# questions = [
#     {
#         'id': 1,
#         'question': 'Столица Франции?',
#         'options': ['Лондон', 'Париж', 'Берлин', 'Мадрид'],
#         'correct_answer': 1
#     },
#     {
#         'id': 2,
#         'question': '2 + 2 = ?',
#         'options': ['3', '4', '5', '6'],
#         'correct_answer': 1
#     },
#     {
#         'id': 3,
#         'question': 'Самая большая планета Солнечной системы?',
#         'options': ['Земля', 'Юпитер', 'Сатурн', 'Марс'],
#         'correct_answer': 1
#     },
#     {
#         'id': 4,
#         'question': 'Автор "Войны и мира"?',
#         'options': ['Достоевский', 'Толстой', 'Чехов', 'Тургенев'],
#         'correct_answer': 1
#     },
#     {
#         'id': 5,
#         'question': 'Химическая формула воды?',
#         'options': ['CO2', 'H2O', 'O2', 'NaCl'],
#         'correct_answer': 1
#     }
# ]
#
#
# class QuizManager:
#     def __init__(self):
#         self.current_question_index = 0
#         self.quiz_active = False
#         self.time_left = 30
#         self.timer_thread = None
#         self.players = {}
#         self.scores = {}
#         self.answers = {}
#         self.timer_active = False
#         self.question_start_time = None
#
#     def start_quiz(self):
#         if not self.quiz_active:
#             self.quiz_active = True
#             self.current_question_index = 0
#             self.players = {}
#             self.scores = {}
#             self.answers = {}
#             print("🎬 Викторина начата!")
#             socketio.emit('quiz_started', broadcast=True)
#             self.start_question()
#
#     def start_question(self):
#         if self.current_question_index < len(questions):
#             self.answers = {}
#             self.time_left = 15  # Увеличим время для удобства
#             self.timer_active = True
#             self.question_start_time = time.time()
#
#             question_data = questions[self.current_question_index]
#
#             socketio.emit('new_question', {
#                 'question_id': question_data['id'],
#                 'question': question_data['question'],
#                 'options': question_data['options'],
#                 'question_number': self.current_question_index + 1,
#                 'total_questions': len(questions),
#                 'time_left': self.time_left
#             })
#
#             print(f"🚀 Вопрос {self.current_question_index + 1} начат: {question_data['question']}")
#             self.start_timer()
#
#     def start_timer(self):
#         def countdown():
#             for i in range(self.time_left, -1, -1):
#                 if not self.timer_active:
#                     break
#                 self.time_left = i
#                 socketio.emit('timer_update', {'time_left': self.time_left})
#                 time.sleep(1)
#
#             if self.timer_active:
#                 print(f"⏰ Время вышло для вопроса {self.current_question_index + 1}")
#                 self.end_question()
#
#         self.timer_thread = threading.Thread(target=countdown)
#         self.timer_thread.daemon = True
#         self.timer_thread.start()
#
#     def end_question(self):
#         self.timer_active = False
#
#         question = questions[self.current_question_index]
#         correct_answer = question['correct_answer']
#
#         results = {
#             'total_players': len(self.players),
#             'answered_players': len(self.answers),
#             'correct_answers': sum(1 for answer in self.answers.values()
#                                    if answer == correct_answer),
#             'correct_answer': correct_answer,
#             'correct_answer_text': question['options'][correct_answer],
#             'question_number': self.current_question_index + 1
#         }
#
#         print(f"📊 Результаты вопроса {self.current_question_index + 1}:")
#         print(f"   Игроков ответило: {len(self.answers)}/{len(self.players)}")
#         print(f"   Правильных ответов: {results['correct_answers']}")
#
#         socketio.emit('question_results', results)
#
#         print("⏳ Ожидание 5 секунд перед следующим вопросом...")
#         time.sleep(5)
#
#         self.current_question_index += 1
#         if self.current_question_index < len(questions):
#             self.start_question()
#         else:
#             self.end_quiz()
#
#     def end_quiz(self):
#         self.quiz_active = False
#         self.timer_active = False
#
#         rankings = []
#         for player_id, player_data in self.players.items():
#             rankings.append({
#                 'name': player_data['name'],
#                 'score': self.scores.get(player_id, 0),
#                 'correct_answers': player_data.get('correct_answers', 0)
#             })
#
#         rankings.sort(key=lambda x: x['score'], reverse=True)
#
#         final_results = {
#             'rankings': rankings[:10],
#             'winners': rankings[:3] if len(rankings) >= 3 else rankings,
#             'total_players': len(self.players),
#             'total_questions': len(questions)
#         }
#
#         socketio.emit('quiz_finished', final_results)
#
#         print("🎉 Викторина завершена!")
#         print(f"📈 Участвовало игроков: {len(self.players)}")
#         print("🏆 Победители:")
#         for i, winner in enumerate(final_results['winners']):
#             print(f"   {i + 1}. {winner['name']} - {winner['score']} баллов")
#
#     def add_player(self, player_id, name):
#         if player_id not in self.players:
#             self.players[player_id] = {
#                 'name': name,
#                 'correct_answers': 0
#             }
#             self.scores[player_id] = 0
#             print(f"👤 Новый игрок: {name} (всего игроков: {len(self.players)})")
#
#             if len(self.players) == 1 and not self.quiz_active:
#                 print("👑 Первый игрок присоединился - запускаем викторину через 5 секунд...")
#                 threading.Timer(5.0, self.start_quiz).start()
#
#     def submit_answer(self, player_id, question_id, answer_index):
#         if (player_id in self.players and
#                 self.timer_active and
#                 player_id not in self.answers):
#
#             self.answers[player_id] = answer_index
#
#             current_question = questions[self.current_question_index]
#             response_time = time.time() - self.question_start_time
#
#             if answer_index == current_question['correct_answer']:
#                 time_bonus = max(1, 10 - int(response_time))
#                 self.scores[player_id] += time_bonus
#                 self.players[player_id]['correct_answers'] += 1
#                 print(f"✅ Правильный ответ от {self.players[player_id]['name']} (+{time_bonus} баллов)")
#
#
# quiz_manager = QuizManager()
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/admin')
# def admin():
#     return render_template('admin.html')
#
#
# @socketio.on('connect')
# def handle_connect():
#     print(f'🔌 Новое подключение: {request.sid}')
#     emit('connected', {'status': 'ok'})
#
#
# @socketio.on('disconnect')
# def handle_disconnect():
#     print(f'🔌 Отключение: {request.sid}')
#
#
# @socketio.on('join_quiz')
# def handle_join(data):
#     name = data.get('name', 'Аноним').strip()
#     if not name:
#         name = 'Аноним'
#
#     quiz_manager.add_player(request.sid, name)
#     emit('joined_success', {'name': name})
#
#     if quiz_manager.quiz_active:
#         quiz_manager.start_question()
#
#
# @socketio.on('submit_answer')
# def handle_answer(data):
#     question_id = data.get('question_id')
#     answer_index = data.get('answer_index')
#
#     quiz_manager.submit_answer(request.sid, question_id, answer_index)
#     emit('answer_received', {'status': 'ok'})
#
#
# @socketio.on('start_quiz')
# def handle_start():
#     quiz_manager.start_quiz()
#     print('🎬 Викторина начата администратором!')
#
#
# @socketio.on('force_next_question')
# def handle_force_next():
#     if quiz_manager.quiz_active:
#         print('⏭️ Принудительный переход к следующему вопросу')
#         quiz_manager.timer_active = False
#         threading.Timer(0.1, quiz_manager.end_question).start()


# def get_local_ip():
#     """Получает локальный IP-адрес"""
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             s.connect(("8.8.8.8", 80))
#             return s.getsockname()[0]
#     except:
#         return "127.0.0.1"
#
#
# def find_ngrok():
#     """Ищет ngrok.exe в разных местах"""
#     # Возможные пути к ngrok
#     possible_paths = [
#         "ngrok.exe",  # В папке с проектом
#         "D:\\NGROK\\ngrok.exe",  # Ваша папка
#         "D:\\NGROK\\ngrok-stable-windows-amd64\\ngrok.exe",  # Если в архиве
#         os.path.join(os.getcwd(), "ngrok.exe"),  # Текущая папка
#     ]
#
#     for path in possible_paths:
#         if os.path.exists(path):
#             print(f"✅ Найден ngrok: {path}")
#             return path
#
#     print("❌ ngrok.exe не найден!")
#     print("💡 Разместите ngrok.exe в одной из этих папок:")
#     for path in possible_paths:
#         print(f"   - {path}")
#     return None
#
#
# def start_ngrok_manual(port):
#     """Запускает ngrok вручную"""
#     try:
#         print("🌐 Поиск ngrok...")
#
#         # Ищем ngrok
#         ngrok_path = find_ngrok()
#         if not ngrok_path:
#             return None
#
#         print(f"🚀 Запуск ngrok: {ngrok_path}")
#
#         # Завершаем предыдущие процессы ngrok
#         try:
#             subprocess.run(['taskkill', '/f', '/im', 'ngrok.exe'],
#                            capture_output=True, timeout=5)
#             time.sleep(2)
#         except:
#             pass
#
#         # Запускаем ngrok
#         ngrok_process = subprocess.Popen(
#             [ngrok_path, 'http', str(port), '--log=stdout'],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             bufsize=1,
#             universal_newlines=True
#         )
#
#         # Ждем запуска и пытаемся получить URL несколько раз
#         print("⏳ Ожидание запуска ngrok...")
#
#         public_url = None
#         for attempt in range(10):  # 10 попыток с интервалом 2 секунды
#             time.sleep(2)
#             print(f"   Попытка {attempt + 1}/10 получить URL...")
#
#             try:
#                 response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
#                 if response.status_code == 200:
#                     data = response.json()
#                     tunnels = data.get('tunnels', [])
#                     for tunnel in tunnels:
#                         if tunnel.get('proto') == 'https':
#                             public_url = tunnel.get('public_url')
#                             break
#
#                     if public_url:
#                         break
#             except:
#                 pass
#
#         if public_url:
#             print("=" * 70)
#             print("🌐 ДОСТУП ИЗ ЛЮБОЙ СЕТИ ИНТЕРНЕТ:")
#             print(f"   📱 ДЛЯ ИГРОКОВ: {public_url}")
#             print(f"   ⚙️  ДЛЯ АДМИНА: {public_url}/admin")
#             print("=" * 70)
#             print("💡 Отправьте эту ссылку игрокам!")
#             print("   Работает из любой точки мира 🌍")
#             print("=" * 70)
#             return public_url
#         else:
#             print("⚠️ Не удалось автоматически получить ngrok URL")
#             print("💡 Откройте в браузере: http://localhost:4040")
#             print("   чтобы увидеть ваш публичный URL")
#             return None
#
#     except Exception as e:
#         print(f"❌ Ошибка запуска ngrok: {e}")
#         return None
#
#
# if __name__ == '__main__':
#     port = 8080
#     local_ip = get_local_ip()
#
#     print("=" * 70)
#     print("🎯 ЗАПУСК СЕРВЕРА ВИКТОРИНЫ")
#     print("=" * 70)
#
#     # Запускаем ngrok
#     ngrok_url = start_ngrok_manual(port)
#
#     print("")
#     print("📍 ЛОКАЛЬНЫЙ ДОСТУП:")
#     print(f"   📱 http://localhost:{port}")
#     print(f"   🌐 http://{local_ip}:{port}")
#     print("")
#     print("⚙️  ПАНЕЛЬ УПРАВЛЕНИЯ:")
#     print(f"   http://localhost:{port}/admin")
#     print("")
#
#     if ngrok_url:
#         print("✅ Ngrok успешно запущен!")
#     else:
#         print("💡 Для доступа из интернета убедитесь, что ngrok.exe доступен")
#
#     print("=" * 70)
#     print("🚀 Запуск сервера...")
#     print("=" * 70)
#
#     try:
#         socketio.run(
#             app,
#             host='0.0.0.0',
#             port=port,
#             debug=True,
#             allow_unsafe_werkzeug=True
#         )
#     except Exception as e:
#         print(f"❌ Ошибка запуска: {e}")
#


# EЩЕ ОДНА ЧАСТЬ с IP
# def get_local_ip():
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             s.connect(("8.8.8.8", 80))
#             return s.getsockname()[0]
#     except:
#         return "127.0.0.1"
#
#
# def start_ngrok_with_auth(port, auth_token):
#     """Запускает ngrok с авторизацией"""
#     try:
#         ngrok_path = "ngrok.exe"
#
#         if not os.path.exists(ngrok_path):
#             print("❌ ngrok.exe не найден в папке проекта")
#             return None
#
#         print("🔑 Настройка ngrok с вашим токеном...")
#
#         # Сначала устанавливаем authtoken
#         auth_process = subprocess.Popen(
#             [ngrok_path, 'authtoken', auth_token],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
#         auth_process.wait()
#         print("✅ Токен установлен!")
#
#         # Теперь запускаем туннель
#         print("🌐 Запуск ngrok туннеля...")
#         process = subprocess.Popen(
#             [ngrok_path, 'http', str(port)],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             bufsize=1
#         )
#
#         # Ждем запуска
#         print("⏳ Ожидание запуска ngrok...")
#         ngrok_url = None
#
#         for i in range(20):
#             time.sleep(1)
#
#             # Пытаемся прочитать вывод
#             try:
#                 line = process.stdout.readline()
#                 if line:
#                     line = line.strip()
#                     print(f"   Ngrok: {line}")
#
#                     # Ищем URL в выводе
#                     if '.ngrok.io' in line and 'Forwarding' in line:
#                         import re
#                         # Ищем URL в строке вида: "Forwarding https://abc123.ngrok.io -> http://localhost:8080"
#                         urls = re.findall(r'https://[a-zA-Z0-9-]+\.ngrok\.io', line)
#                         if urls:
#                             ngrok_url = urls[0]
#                             print(f"✅ Ngrok URL: {ngrok_url}")
#                             break
#             except:
#                 pass
#
#             if i % 5 == 0 and i > 0:
#                 print(f"   ...ожидание ({i}/20 секунд)")
#
#         if ngrok_url:
#             return ngrok_url
#         else:
#             print("⚠️ Ngrok запущен, но URL не получен автоматически")
#             return "ОЖИДАНИЕ_URL"
#
#     except Exception as e:
#         print(f"❌ Ошибка ngrok: {e}")
#         return None
#
#
# def manual_ngrok_instructions(auth_token):
#     """Инструкция для ручного запуска ngrok"""
#     print(f"\n🔧 ДЛЯ ВНЕШНЕГО ДОСТУПА (Ngrok):")
#     print("1. Откройте новое окно командной строки")
#     print("2. Перейдите в папку с проектом:")
#     print("   cd D:\\Python\\Project\\pythonProject2")
#     print("3. Установите токен:")
#     print(f"   ngrok.exe authtoken {auth_token}")
#     print("4. Запустите туннель:")
#     print("   ngrok.exe http 8080")
#     print("5. Скопируйте URL с .ngrok.io и отправьте игрокам")
#
#
# if __name__ == '__main__':
#     port = 8080
#     local_ip = get_local_ip()
#
#     # ВСТАВЬТЕ ВАШ ТОКЕН ЗДЕСЬ ↓
#     NGROK_AUTH_TOKEN = "33jcNwjvdTIkHXRLCRvjUyak3xh_6u2TGqMph5sAVSyW22prV"  # ЗАМЕНИТЕ НА ВАШ ТОКЕН
#
#     print("=" * 70)
#     print("🎯 ЗАПУСК СЕРВЕРА ВИКТОРИНЫ С NGROK")
#     print("=" * 70)
#
#     # Пробуем автоматический запуск ngrok
#     print("🌐 Попытка запуска Ngrok с авторизацией...")
#     ngrok_url = start_ngrok_with_auth(port, NGROK_AUTH_TOKEN)
#
#     print("")
#     if ngrok_url and ngrok_url != "ОЖИДАНИЕ_URL":
#         print("🌐 ДОСТУП ИЗ ЛЮБОЙ СЕТИ ИНТЕРНЕТ:")
#         print(f"   📱 ДЛЯ ИГРОКОВ: {ngrok_url}")
#         print(f"   ⚙️  ДЛЯ АДМИНА: {ngrok_url}/admin")
#         print("=" * 70)
#         print("💡 Отправьте эту ссылку игрокам!")
#         print("   Работает из любой точки мира 🌍")
#         print("=" * 70)
#     else:
#         print("📍 ЛОКАЛЬНЫЙ ДОСТУП (работает в вашей Wi-Fi сети):")
#         print(f"   📱 http://{local_ip}:{port}")
#         print("")
#         print("🌐 ДЛЯ ДОСТУПА ИЗ ИНТЕРНЕТА:")
#         manual_ngrok_instructions(NGROK_AUTH_TOKEN)
#
#     print("")
#     print("⚙️  ПАНЕЛЬ УПРАВЛЕНИЯ:")
#     print(f"   http://localhost:{port}/admin")
#     print("=" * 70)
#     print("🚀 Запуск сервера...")
#     print("=" * 70)
#
#     try:
#         socketio.run(
#             app,
#             host='0.0.0.0',
#             port=port,
#             debug=True,
#             allow_unsafe_werkzeug=True
#         )
#     except Exception as e:
#         print(f"❌ Ошибка запуска: {e}")


# from flask import Flask, render_template, request
# from flask_socketio import SocketIO, emit
# import time
# import threading
# import socket
# import sys
# import os
# import subprocess
#
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'quiz_secret_key_2024'
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
#
# # Вопросы для викторины
# questions = [
#     {
#         'id': 1,
#         'question': 'Столица Франции?',
#         'options': ['Лондон', 'Париж', 'Берлин', 'Мадрид'],
#         'correct_answer': 1
#     },
#     {
#         'id': 2,
#         'question': '2 + 2 = ?',
#         'options': ['3', '4', '5', '6'],
#         'correct_answer': 1
#     },
#     {
#         'id': 3,
#         'question': 'Самая большая планета Солнечной системы?',
#         'options': ['Земля', 'Юпитер', 'Сатурн', 'Марс'],
#         'correct_answer': 1
#     },
#     {
#         'id': 4,
#         'question': 'Автор "Войны и мира"?',
#         'options': ['Достоевский', 'Толстой', 'Чехов', 'Тургенев'],
#         'correct_answer': 1
#     },
#     {
#         'id': 5,
#         'question': 'Химическая формула воды?',
#         'options': ['CO2', 'H2O', 'O2', 'NaCl'],
#         'correct_answer': 1
#     }
# ]
#
#
# class QuizManager:
#     def __init__(self):
#         self.current_question_index = 0
#         self.quiz_active = False
#         self.time_left = 30
#         self.timer_thread = None
#         self.players = {}
#         self.scores = {}
#         self.answers = {}
#         self.timer_active = False
#         self.question_start_time = None
#
#     def start_quiz(self):
#         if not self.quiz_active:
#             self.quiz_active = True
#             self.current_question_index = 0
#             self.players = {}
#             self.scores = {}
#             self.answers = {}
#             print("🎬 Викторина начата!")
#             socketio.emit('quiz_started', namespace='/')
#             self.start_question()
#
#     def start_question(self):
#         if self.current_question_index < len(questions):
#             self.answers = {}
#             self.time_left = 15
#             self.timer_active = True
#             self.question_start_time = time.time()
#
#             question_data = questions[self.current_question_index]
#
#             socketio.emit('new_question', {
#                 'question_id': question_data['id'],
#                 'question': question_data['question'],
#                 'options': question_data['options'],
#                 'question_number': self.current_question_index + 1,
#                 'total_questions': len(questions),
#                 'time_left': self.time_left
#             }, namespace='/')
#
#             print(f"🚀 Вопрос {self.current_question_index + 1} начат: {question_data['question']}")
#             self.start_timer()
#
#     def start_timer(self):
#         def countdown():
#             for i in range(self.time_left, -1, -1):
#                 if not self.timer_active:
#                     break
#                 self.time_left = i
#                 socketio.emit('timer_update', {'time_left': self.time_left}, namespace='/')
#                 time.sleep(1)
#
#             if self.timer_active:
#                 print(f"⏰ Время вышло для вопроса {self.current_question_index + 1}")
#                 self.end_question()
#
#         self.timer_thread = threading.Thread(target=countdown)
#         self.timer_thread.daemon = True
#         self.timer_thread.start()
#
#     def end_question(self):
#         self.timer_active = False
#
#         question = questions[self.current_question_index]
#         correct_answer = question['correct_answer']
#
#         results = {
#             'total_players': len(self.players),
#             'answered_players': len(self.answers),
#             'correct_answers': sum(1 for answer in self.answers.values()
#                                    if answer == correct_answer),
#             'correct_answer': correct_answer,
#             'correct_answer_text': question['options'][correct_answer],
#             'question_number': self.current_question_index + 1
#         }
#
#         print(f"📊 Результаты вопроса {self.current_question_index + 1}:")
#         print(f"   Игроков ответило: {len(self.answers)}/{len(self.players)}")
#
#         socketio.emit('question_results', results, namespace='/')
#
#         print("⏳ Ожидание 5 секунд перед следующим вопросом...")
#         time.sleep(5)
#
#         self.current_question_index += 1
#         if self.current_question_index < len(questions):
#             self.start_question()
#         else:
#             self.end_quiz()
#
#     def end_quiz(self):
#         self.quiz_active = False
#         self.timer_active = False
#
#         rankings = []
#         for player_id, player_data in self.players.items():
#             rankings.append({
#                 'name': player_data['name'],
#                 'score': self.scores.get(player_id, 0),
#                 'correct_answers': player_data.get('correct_answers', 0)
#             })
#
#         rankings.sort(key=lambda x: x['score'], reverse=True)
#
#         final_results = {
#             'rankings': rankings[:10],
#             'winners': rankings[:3] if len(rankings) >= 3 else rankings,
#             'total_players': len(self.players),
#             'total_questions': len(questions)
#         }
#
#         socketio.emit('quiz_finished', final_results, namespace='/')
#
#         print("🎉 Викторина завершена!")
#         print(f"📈 Участвовало игроков: {len(self.players)}")
#
#     def add_player(self, player_id, name):
#         if player_id not in self.players:
#             self.players[player_id] = {
#                 'name': name,
#                 'correct_answers': 0
#             }
#             self.scores[player_id] = 0
#             print(f"👤 Новый игрок: {name} (всего игроков: {len(self.players)})")
#
#             if len(self.players) == 1 and not self.quiz_active:
#                 print("👑 Первый игрок присоединился - запускаем викторину через 5 секунд...")
#                 threading.Timer(5.0, self.start_quiz).start()
#
#     def submit_answer(self, player_id, question_id, answer_index):
#         if (player_id in self.players and
#                 self.timer_active and
#                 player_id not in self.answers):
#
#             self.answers[player_id] = answer_index
#
#             current_question = questions[self.current_question_index]
#             response_time = time.time() - self.question_start_time
#
#             if answer_index == current_question['correct_answer']:
#                 time_bonus = max(1, 10 - int(response_time))
#                 self.scores[player_id] += time_bonus
#                 self.players[player_id]['correct_answers'] += 1
#                 print(f"✅ Правильный ответ от {self.players[player_id]['name']} (+{time_bonus} баллов)")
#
#
# quiz_manager = QuizManager()
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/admin')
# def admin():
#     return render_template('admin.html')
#
#
# @socketio.on('connect')
# def handle_connect():
#     print(f'🔌 Новое подключение: {request.sid}')
#     emit('connected', {'status': 'ok'})
#
#
# @socketio.on('disconnect')
# def handle_disconnect():
#     print(f'🔌 Отключение: {request.sid}')
#
#
# @socketio.on('join_quiz')
# def handle_join(data):
#     name = data.get('name', 'Аноним').strip()
#     if not name:
#         name = 'Аноним'
#
#     quiz_manager.add_player(request.sid, name)
#     emit('joined_success', {'name': name})
#
#     if quiz_manager.quiz_active:
#         quiz_manager.start_question()
#
#
# @socketio.on('submit_answer')
# def handle_answer(data):
#     question_id = data.get('question_id')
#     answer_index = data.get('answer_index')
#
#     quiz_manager.submit_answer(request.sid, question_id, answer_index)
#     emit('answer_received', {'status': 'ok'})
#
#
# @socketio.on('start_quiz')
# def handle_start():
#     quiz_manager.start_quiz()
#     print('🎬 Викторина начата администратором!')
#
#
# @socketio.on('force_next_question')
# def handle_force_next():
#     if quiz_manager.quiz_active:
#         print('⏭️ Принудительный переход к следующему вопросу')
#         quiz_manager.timer_active = False
#         threading.Timer(0.1, quiz_manager.end_question).start()
#
#
# def get_local_ip():
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             s.connect(("8.8.8.8", 80))
#             return s.getsockname()[0]
#     except:
#         return "127.0.0.1"
#
#
# def start_serveo_manual(port):
#     """Инструкция для ручного запуска Serveo"""
#     print("🌐 ДЛЯ ВНЕШНЕГО ДОСТУПА:")
#     print("1. Откройте НОВОЕ окно командной строки")
#     print("2. Выполните команду:")
#     print(f"   ssh -o StrictHostKeyChecking=no -R 80:localhost:{port} serveo.net")
#     print("3. Дождитесь появления URL с 'serveo.net'")
#     print("4. Скопируйте этот URL и отправьте игрокам")
#     print("5. НЕ ЗАКРЫВАЙТЕ окно с Serveo!")
#     return None
#
#
# if __name__ == '__main__':
#     port = 8080
#     local_ip = get_local_ip()
#
#     print("=" * 70)
#     print("🎯 ЗАПУСК СЕРВЕРА ВИКТОРИНЫ")
#     print("=" * 70)
#
#     print("📍 ЛОКАЛЬНЫЙ ДОСТУП (работает в вашей Wi-Fi сети):")
#     print(f"   📱 http://{local_ip}:{port}")
#     print("")
#
#     # Показываем инструкцию для Serveo
#     serveo_url = start_serveo_manual(port)
#
#     print("")
#     print("⚙️  ПАНЕЛЬ УПРАВЛЕНИЯ:")
#     print(f"   http://localhost:{port}/admin")
#     print("=" * 70)
#     print("🚀 Запуск сервера...")
#     print("=" * 70)
#
#     try:
#         socketio.run(
#             app,
#             host='0.0.0.0',
#             port=port,
#             debug=True,
#             allow_unsafe_werkzeug=True
#         )
#     except Exception as e:
#         print(f"❌ Ошибка запуска: {e}")


############################################################
# if __name__ == '__main__':
#     port = 8080
#     local_ip = get_local_ip()
#
#     print("=" * 70)
#     print("🎯 ЗАПУСК СЕРВЕРА ВИКТОРИНЫ")
#     print("=" * 70)
#
#     print("📍 ЛОКАЛЬНЫЙ ДОСТУП:")
#     print(f"   📱 http://{local_ip}:{port}")
#     print("")
#     print("🌐 Serveo URL для внешнего доступа:")
#     print("https://26ac27cf3b427c98febb717a9688685b.serveo.net/")
#     print("")
#     print("⚙️  ПАНЕЛЬ УПРАВЛЕНИЯ:")
#     print(f"   http://localhost:{port}/admin")
#     print("=" * 70)
#
#     # Принудительно запускаем на всех интерфейсах
#     print("🚀 Запуск сервера на всех сетевых интерфейсах...")
#     print("=" * 70)
#
#     try:
#         socketio.run(
#             app,
#             host='0.0.0.0',  # Важно: принимать подключения со всех интерфейсов
#             port=port,
#             debug=True,
#             use_reloader=False,  # Важно отключить автоперезагрузку,
#             allow_unsafe_werkzeug = True
#         )
#     except Exception as e:
#         print(f"❌ Ошибка запуска: {e}")



#########################################LOCALTUNNEL
# from flask import Flask, render_template, request
# from flask_socketio import SocketIO, emit
# import time
# import threading
# import socket
# import sys
# import requests
# import json
# import os
# import subprocess
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'quiz_secret_key_2024'
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
#
# # Вопросы для викторины
# questions = [
#     {
#         'id': 1,
#         'question': 'Столица Франции?',
#         'options': ['Лондон', 'Париж', 'Берлин', 'Мадрид'],
#         'correct_answer': 1
#     },
#     {
#         'id': 2,
#         'question': '2 + 2 = ?',
#         'options': ['3', '4', '5', '6'],
#         'correct_answer': 1
#     },
#     {
#         'id': 3,
#         'question': 'Самая большая планета Солнечной системы?',
#         'options': ['Земля', 'Юпитер', 'Сатурн', 'Марс'],
#         'correct_answer': 1
#     },
#     {
#         'id': 4,
#         'question': 'Автор "Войны и мира"?',
#         'options': ['Достоевский', 'Толстой', 'Чехов', 'Тургенев'],
#         'correct_answer': 1
#     },
#     {
#         'id': 5,
#         'question': 'Химическая формула воды?',
#         'options': ['CO2', 'H2O', 'O2', 'NaCl'],
#         'correct_answer': 1
#     }
# ]
#
#
# class QuizManager:
#     def __init__(self):
#         self.current_question_index = 0
#         self.quiz_active = False
#         self.time_left = 30
#         self.timer_thread = None
#         self.players = {}
#         self.scores = {}
#         self.answers = {}
#         self.timer_active = False
#         self.question_start_time = None
#
#     def start_quiz(self):
#         if not self.quiz_active:
#             self.quiz_active = True
#             self.current_question_index = 0
#             self.players = {}
#             self.scores = {}
#             self.answers = {}
#             print("🎬 Викторина начата!")
#             socketio.emit('quiz_started', broadcast=True)
#             self.start_question()
#
#     def start_question(self):
#         if self.current_question_index < len(questions):
#             self.answers = {}
#             self.time_left = 15  # Увеличим время для удобства
#             self.timer_active = True
#             self.question_start_time = time.time()
#
#             question_data = questions[self.current_question_index]
#
#             socketio.emit('new_question', {
#                 'question_id': question_data['id'],
#                 'question': question_data['question'],
#                 'options': question_data['options'],
#                 'question_number': self.current_question_index + 1,
#                 'total_questions': len(questions),
#                 'time_left': self.time_left
#             })
#
#             print(f"🚀 Вопрос {self.current_question_index + 1} начат: {question_data['question']}")
#             self.start_timer()
#
#     def start_timer(self):
#         def countdown():
#             for i in range(self.time_left, -1, -1):
#                 if not self.timer_active:
#                     break
#                 self.time_left = i
#                 socketio.emit('timer_update', {'time_left': self.time_left})
#                 time.sleep(1)
#
#             if self.timer_active:
#                 print(f"⏰ Время вышло для вопроса {self.current_question_index + 1}")
#                 self.end_question()
#
#         self.timer_thread = threading.Thread(target=countdown)
#         self.timer_thread.daemon = True
#         self.timer_thread.start()
#
#     def end_question(self):
#         self.timer_active = False
#
#         question = questions[self.current_question_index]
#         correct_answer = question['correct_answer']
#
#         results = {
#             'total_players': len(self.players),
#             'answered_players': len(self.answers),
#             'correct_answers': sum(1 for answer in self.answers.values()
#                                    if answer == correct_answer),
#             'correct_answer': correct_answer,
#             'correct_answer_text': question['options'][correct_answer],
#             'question_number': self.current_question_index + 1
#         }
#
#         print(f"📊 Результаты вопроса {self.current_question_index + 1}:")
#         print(f"   Игроков ответило: {len(self.answers)}/{len(self.players)}")
#         print(f"   Правильных ответов: {results['correct_answers']}")
#
#         socketio.emit('question_results', results)
#
#         print("⏳ Ожидание 5 секунд перед следующим вопросом...")
#         time.sleep(5)
#
#         self.current_question_index += 1
#         if self.current_question_index < len(questions):
#             self.start_question()
#         else:
#             self.end_quiz()
#
#     def end_quiz(self):
#         self.quiz_active = False
#         self.timer_active = False
#
#         rankings = []
#         for player_id, player_data in self.players.items():
#             rankings.append({
#                 'name': player_data['name'],
#                 'score': self.scores.get(player_id, 0),
#                 'correct_answers': player_data.get('correct_answers', 0)
#             })
#
#         rankings.sort(key=lambda x: x['score'], reverse=True)
#
#         final_results = {
#             'rankings': rankings[:10],
#             'winners': rankings[:3] if len(rankings) >= 3 else rankings,
#             'total_players': len(self.players),
#             'total_questions': len(questions)
#         }
#
#         socketio.emit('quiz_finished', final_results)
#
#         print("🎉 Викторина завершена!")
#         print(f"📈 Участвовало игроков: {len(self.players)}")
#         print("🏆 Победители:")
#         for i, winner in enumerate(final_results['winners']):
#             print(f"   {i + 1}. {winner['name']} - {winner['score']} баллов")
#
#     def add_player(self, player_id, name):
#         if player_id not in self.players:
#             self.players[player_id] = {
#                 'name': name,
#                 'correct_answers': 0
#             }
#             self.scores[player_id] = 0
#             print(f"👤 Новый игрок: {name} (всего игроков: {len(self.players)})")
#
#             if len(self.players) == 1 and not self.quiz_active:
#                 print("👑 Первый игрок присоединился - запускаем викторину через 5 секунд...")
#                 threading.Timer(5.0, self.start_quiz).start()
#
#     def submit_answer(self, player_id, question_id, answer_index):
#         if (player_id in self.players and
#                 self.timer_active and
#                 player_id not in self.answers):
#
#             self.answers[player_id] = answer_index
#
#             current_question = questions[self.current_question_index]
#             response_time = time.time() - self.question_start_time
#
#             if answer_index == current_question['correct_answer']:
#                 time_bonus = max(1, 10 - int(response_time))
#                 self.scores[player_id] += time_bonus
#                 self.players[player_id]['correct_answers'] += 1
#                 print(f"✅ Правильный ответ от {self.players[player_id]['name']} (+{time_bonus} баллов)")
#
#
# quiz_manager = QuizManager()
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/admin')
# def admin():
#     return render_template('admin.html')
#
#
# @socketio.on('connect')
# def handle_connect():
#     print(f'🔌 Новое подключение: {request.sid}')
#     emit('connected', {'status': 'ok'})
#
#
# @socketio.on('disconnect')
# def handle_disconnect():
#     print(f'🔌 Отключение: {request.sid}')
#
#
# @socketio.on('join_quiz')
# def handle_join(data):
#     name = data.get('name', 'Аноним').strip()
#     if not name:
#         name = 'Аноним'
#
#     quiz_manager.add_player(request.sid, name)
#     emit('joined_success', {'name': name})
#
#     if quiz_manager.quiz_active:
#         quiz_manager.start_question()
#
#
# @socketio.on('submit_answer')
# def handle_answer(data):
#     question_id = data.get('question_id')
#     answer_index = data.get('answer_index')
#
#     quiz_manager.submit_answer(request.sid, question_id, answer_index)
#     emit('answer_received', {'status': 'ok'})
#
#
# @socketio.on('start_quiz')
# def handle_start():
#     quiz_manager.start_quiz()
#     print('🎬 Викторина начата администратором!')
#
#
# @socketio.on('force_next_question')
# def handle_force_next():
#     if quiz_manager.quiz_active:
#         print('⏭️ Принудительный переход к следующему вопросу')
#         quiz_manager.timer_active = False
#         threading.Timer(0.1, quiz_manager.end_question).start()
#
#
# def get_local_ip():
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             s.connect(("8.8.8.8", 80))
#             return s.getsockname()[0]
#     except:
#         return "127.0.0.1"
#
#
# def install_and_start_localtunnel(port):
#     """Устанавливает и запускает localtunnel"""
#     try:
#         print("📦 Проверка наличия localtunnel...")
#
#         # Проверяем, установлен ли localtunnel
#         result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
#         if result.returncode != 0:
#             print("❌ npx не найден. Убедитесь, что Node.js установлен на вашем компьютере.")
#             print("   Скачайте с: https://nodejs.org/")
#             return None
#
#         print("🌐 Запуск localtunnel...")
#
#         # Запускаем localtunnel
#         process = subprocess.Popen(
#             ['npx', 'localtunnel', '--port', str(port)],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             bufsize=1
#         )
#
#         # Ждем запуска и получаем URL
#         print("⏳ Ожидание запуска localtunnel...")
#         lt_url = None
#
#         for i in range(15):
#             time.sleep(1)
#
#             try:
#                 line = process.stdout.readline()
#                 if line:
#                     line = line.strip()
#                     print(f"   Localtunnel: {line}")
#
#                     # Ищем URL в выводе
#                     if 'your url is:' in line.lower():
#                         lt_url = line.split('your url is:')[-1].strip()
#                         print(f"✅ Localtunnel URL: {lt_url}")
#                         break
#                     elif 'https://' in line and '.loca.lt' in line:
#                         lt_url = line.strip()
#                         print(f"✅ Localtunnel URL: {lt_url}")
#                         break
#             except:
#                 pass
#
#             if i % 5 == 0 and i > 0:
#                 print(f"   ...ожидание ({i}/15 секунд)")
#
#         if lt_url:
#             return lt_url, process
#         else:
#             print("⚠️ Localtunnel запущен, но URL не получен автоматически")
#             return None, process
#
#     except Exception as e:
#         print(f"❌ Ошибка localtunnel: {e}")
#         return None, None
#
#
# def manual_localtunnel_instructions(port):
#     """Инструкция для ручного запуска localtunnel"""
#     print(f"\n🔧 ДЛЯ ВНЕШНЕГО ДОСТУПА (Localtunnel):")
#     print("1. Убедитесь, что у вас установлен Node.js")
#     print("2. Откройте новое окно командной строки")
#     print("3. Запустите команду:")
#     print(f"   npx localtunnel --port {port}")
#     print("4. Скопируйте URL с .loca.lt и отправьте игрокам")
#
#
# if __name__ == '__main__':
#     port = 8080
#     local_ip = get_local_ip()
#
#     print("=" * 70)
#     print("🎯 ЗАПУСК СЕРВЕРА ВИКТОРИНЫ С LOCALTUNNEL")
#     print("=" * 70)
#
#     # Пробуем автоматический запуск localtunnel
#     print("🌐 Попытка запуска Localtunnel...")
#     lt_result = install_and_start_localtunnel(port)
#     lt_url, lt_process = lt_result if lt_result else (None, None)
#
#     print("")
#     if lt_url:
#         print("🌐 ДОСТУП ИЗ ЛЮБОЙ СЕТИ ИНТЕРНЕТ:")
#         print(f"   📱 ДЛЯ ИГРОКОВ: {lt_url}")
#         print(f"   ⚙️  ДЛЯ АДМИНА: {lt_url}/admin")
#         print("=" * 70)
#         print("💡 Отправьте эту ссылку игрокам!")
#         print("   Работает из любой точки мира 🌍")
#         print("=" * 70)
#         print("⚠️  Внимание: Localtunnel туннель закроется при остановке программы")
#     else:
#         print("📍 ЛОКАЛЬНЫЙ ДОСТУП (работает в вашей Wi-Fi сети):")
#         print(f"   📱 http://{local_ip}:{port}")
#         print("")
#         print("🌐 ДЛЯ ДОСТУПА ИЗ ИНТЕРНЕТА:")
#         manual_localtunnel_instructions(port)
#
#     print("")
#     print("⚙️  ПАНЕЛЬ УПРАВЛЕНИЯ:")
#     print(f"   http://localhost:{port}/admin")
#     print("=" * 70)
#     print("🚀 Запуск сервера...")
#     print("=" * 70)
#
#     try:
#         socketio.run(
#             app,
#             host='0.0.0.0',
#             port=port,
#             debug=True,
#             allow_unsafe_werkzeug=True
#         )
#     except Exception as e:
#         print(f"❌ Ошибка запуска: {e}")
#     finally:
#         # Завершаем процесс localtunnel при остановке сервера
#         if lt_process:
#             lt_process.terminate()
#             print("🔒 Localtunnel туннель закрыт")

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import time
import threading
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'quiz_secret_key_2024')

# Используем threading вместо eventlet для Render
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Вопросы для викторины
questions = [
    {
        'id': 1,
        'question': 'Столица Франции?',
        'options': ['Лондон', 'Париж', 'Берлин', 'Мадрид'],
        'correct_answer': 1
    },
    {
        'id': 2,
        'question': '2 + 2 = ?',
        'options': ['3', '4', '5', '6'],
        'correct_answer': 1
    },
    {
        'id': 3,
        'question': 'Самая большая планета Солнечной системы?',
        'options': ['Земля', 'Юпитер', 'Сатурн', 'Марс'],
        'correct_answer': 1
    },
    {
        'id': 4,
        'question': 'Автор "Войны и мира"?',
        'options': ['Достоевский', 'Толстой', 'Чехов', 'Тургенев'],
        'correct_answer': 1
    },
    {
        'id': 5,
        'question': 'Химическая формула воды?',
        'options': ['CO2', 'H2O', 'O2', 'NaCl'],
        'correct_answer': 1
    }
]


class QuizManager:
    def __init__(self):
        self.current_question_index = 0
        self.quiz_active = False
        self.time_left = 30
        self.timer_thread = None
        self.players = {}
        self.scores = {}
        self.answers = {}
        self.timer_active = False
        self.question_start_time = None

    def start_quiz(self):
        if not self.quiz_active:
            self.quiz_active = True
            self.current_question_index = 0
            self.players = {}
            self.scores = {}
            self.answers = {}
            print("🎬 Викторина от Вероника начата!")
            socketio.emit('quiz_started', broadcast=True)
            self.start_question()

    def start_question(self):
        if self.current_question_index < len(questions):
            self.answers = {}
            self.time_left = 15
            self.timer_active = True
            self.question_start_time = time.time()

            question_data = questions[self.current_question_index]

            socketio.emit('new_question', {
                'question_id': question_data['id'],
                'question': question_data['question'],
                'options': question_data['options'],
                'question_number': self.current_question_index + 1,
                'total_questions': len(questions),
                'time_left': self.time_left
            })

            print(f"🚀 Вопрос {self.current_question_index + 1} начат: {question_data['question']}")
            self.start_timer()

    def start_timer(self):
        def countdown():
            for i in range(self.time_left, -1, -1):
                if not self.timer_active:
                    break
                self.time_left = i
                socketio.emit('timer_update', {'time_left': self.time_left})
                time.sleep(1)

            if self.timer_active:
                print(f"⏰ Время вышло для вопроса {self.current_question_index + 1}")
                self.end_question()

        self.timer_thread = threading.Thread(target=countdown)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def end_question(self):
        self.timer_active = False

        question = questions[self.current_question_index]
        correct_answer = question['correct_answer']

        results = {
            'total_players': len(self.players),
            'answered_players': len(self.answers),
            'correct_answers': sum(1 for answer in self.answers.values()
                                   if answer == correct_answer),
            'correct_answer': correct_answer,
            'correct_answer_text': question['options'][correct_answer],
            'question_number': self.current_question_index + 1
        }

        print(f"📊 Результаты вопроса {self.current_question_index + 1}:")
        print(f"   Игроков ответило: {len(self.answers)}/{len(self.players)}")
        print(f"   Правильных ответов: {results['correct_answers']}")

        socketio.emit('question_results', results)

        print("⏳ Ожидание 5 секунд перед следующим вопросом...")
        time.sleep(5)

        self.current_question_index += 1
        if self.current_question_index < len(questions):
            self.start_question()
        else:
            self.end_quiz()

    def end_quiz(self):
        self.quiz_active = False
        self.timer_active = False

        rankings = []
        for player_id, player_data in self.players.items():
            rankings.append({
                'name': player_data['name'],
                'score': self.scores.get(player_id, 0),
                'correct_answers': player_data.get('correct_answers', 0)
            })

        rankings.sort(key=lambda x: x['score'], reverse=True)

        final_results = {
            'rankings': rankings[:10],
            'winners': rankings[:3] if len(rankings) >= 3 else rankings,
            'total_players': len(self.players),
            'total_questions': len(questions)
        }

        socketio.emit('quiz_finished', final_results)

        print("🎉 Викторина завершена!")
        print(f"📈 Участвовало игроков: {len(self.players)}")
        print("🏆 Победители:")
        for i, winner in enumerate(final_results['winners']):
            print(f"   {i + 1}. {winner['name']} - {winner['score']} баллов")

    def add_player(self, player_id, name):
        if player_id not in self.players:
            self.players[player_id] = {
                'name': name,
                'correct_answers': 0
            }
            self.scores[player_id] = 0
            print(f"👤 Новый игрок: {name} (всего игроков: {len(self.players)})")

            if len(self.players) == 1 and not self.quiz_active:
                print("👑 Первый игрок присоединился - запускаем викторину через 5 секунд...")
                threading.Timer(5.0, self.start_quiz).start()

    def submit_answer(self, player_id, question_id, answer_index):
        if (player_id in self.players and
                self.timer_active and
                player_id not in self.answers):

            self.answers[player_id] = answer_index

            current_question = questions[self.current_question_index]
            response_time = time.time() - self.question_start_time

            if answer_index == current_question['correct_answer']:
                time_bonus = max(1, 10 - int(response_time))
                self.scores[player_id] += time_bonus
                self.players[player_id]['correct_answers'] += 1
                print(f"✅ Правильный ответ от {self.players[player_id]['name']} (+{time_bonus} баллов)")


quiz_manager = QuizManager()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@socketio.on('connect')
def handle_connect():
    print(f'🔌 Новое подключение: {request.sid}')
    emit('connected', {'status': 'ok'})


@socketio.on('disconnect')
def handle_disconnect():
    print(f'🔌 Отключение: {request.sid}')


@socketio.on('join_quiz')
def handle_join(data):
    name = data.get('name', 'Аноним').strip()
    if not name:
        name = 'Аноним'

    quiz_manager.add_player(request.sid, name)
    emit('joined_success', {'name': name})

    if quiz_manager.quiz_active:
        quiz_manager.start_question()


@socketio.on('submit_answer')
def handle_answer(data):
    question_id = data.get('question_id')
    answer_index = data.get('answer_index')

    quiz_manager.submit_answer(request.sid, question_id, answer_index)
    emit('answer_received', {'status': 'ok'})


@socketio.on('start_quiz')
def handle_start():
    quiz_manager.start_quiz()
    print('🎬 Викторина начата администратором!')


@socketio.on('force_next_question')
def handle_force_next():
    if quiz_manager.quiz_active:
        print('⏭️ Принудительный переход к следующему вопросу')
        quiz_manager.timer_active = False
        threading.Timer(0.1, quiz_manager.end_question).start()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Запуск сервера на порту {port}")
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )

