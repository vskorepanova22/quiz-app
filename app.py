from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import time
import threading
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'quiz_secret_key_2024')

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Вопросы для викторины с разным временем на ответ
questions = [
    {
        'id': 1,
        'question': 'Столица Франции?',
        'options': ['Лондон', 'Париж', 'Берлин', 'Мадрид'],
        'correct_answer': 1,
        'time_limit': 10  # секунд
    },
    {
        'id': 2,
        'question': '2 * 3 = ?',
        'options': ['3', '2', '5', '6'],
        'correct_answer': 3,
        'time_limit': 10  # секунд
    },
    {
        'id': 3,
        'question': 'Самая большая планета Солнечной системы?',
        'options': ['Юпитер', 'Земля', 'Сатурн', 'Марс'],
        'correct_answer': 0,
        'time_limit': 10  # секунд
    },
    {
        'id': 4,
        'question': 'Автор "Войны и мира"?',
        'options': ['Достоевский', 'Толстой', 'Чехов', 'Тургенев'],
        'correct_answer': 1,
        'time_limit': 10  # секунд
    },
    {
        'id': 5,
        'question': 'Что выведет код: print("5" * 3)?',
        'options': ['[5,5,5]', 'Error', '555', '15'],
        'correct_answer': 2,
        'time_limit': 12  # секунд
    },
    {
        'id': 5,
        'question': 'Что делает модель регрессии?',
        'options': ['Классифицирует объекты', 'Предсказывает непрерывные величины', 'Сортирует данные', 'В некоторых задачах сортирует данные, а в некоторых - строит дерево решений'],
        'correct_answer': 1,
        'time_limit': 12  # секунд
    }

]


class QuizManager:
    def __init__(self):
        self.current_question_index = -1 # чтобы первый вопрос был
        self.quiz_active = False
        self.time_left = 0
        self.timer_thread = None
        self.players = {}
        self.scores = {}
        self.answers = {}
        self.timer_active = False
        self.question_start_time = None
        self.waiting_for_admin = True  # Ожидание старта от администратора
        self.player_positions = {}  # Позиции игроков в облаке

    def start_quiz(self):
        if not self.quiz_active and self.waiting_for_admin:
            self.quiz_active = True
            self.waiting_for_admin = False
            self.current_question_index = 0 # начинаем с первого вопроса
            # self.players = {}
            # self.scores = {}
            self.answers = {} # Очищаем ответы для нового вопроса
            print("🎬 Хакатон от Вероники начата администратором!")
            socketio.emit('quiz_started')
            # Переходим к первому вопросу
            self.current_question_index = 0
            self.start_question()


    def start_question(self):
        if self.current_question_index < len(questions):
            self.answers = {}
            question_data = questions[self.current_question_index]
            self.time_left = question_data['time_limit']
            self.timer_active = True
            self.question_start_time = time.time()

            socketio.emit('new_question', {
                'question_id': question_data['id'],
                'question': question_data['question'],
                'options': question_data['options'],
                'question_number': self.current_question_index + 1,
                'total_questions': len(questions),
                'time_left': self.time_left,
                'time_limit': question_data['time_limit']
            })

            print(
                f"🚀 Вопрос {self.current_question_index + 1} начат: {question_data['question']} (время: {self.time_left}с)")
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

        # ДЕТАЛЬНАЯ статистика по ответам
        correct_answers_count = 0
        incorrect_answers_count = 0
        answer_details = []

        for player_id, answer in self.answers.items():
            player_name = self.players[player_id]['name']
            is_correct = (answer == correct_answer)

            if is_correct:
                correct_answers_count += 1
            else:
                incorrect_answers_count += 1

            answer_details.append({
                'name': player_name,
                'answer': answer,
                'correct': is_correct,
                'score': self.scores.get(player_id, 0)
            })

        # Сортируем по скорости ответа (если нужно) или по правильности
        answer_details.sort(key=lambda x: (x['correct'], x['score']), reverse=True)

        results = {
            'total_players': len(self.players),
            'answered_players': len(self.answers),
            'correct_answers': correct_answers_count,
            'incorrect_answers': incorrect_answers_count,
            'correct_answer': correct_answer,
            'correct_answer_text': question['options'][correct_answer],
            'question_number': self.current_question_index + 1,
            'answer_details': answer_details[:10],  # Топ 10 ответов
            'current_rankings': self.get_current_rankings()  # Текущий рейтинг
        }

        print(f"📊 Результаты вопроса {self.current_question_index + 1}:")
        print(f"   Игроков ответило: {len(self.answers)}/{len(self.players)}")
        print(f"   Правильных ответов: {correct_answers_count}")
        print(f"   Неправильных ответов: {incorrect_answers_count}")

        # Печатаем топ игроков
        print("   Топ игроков на данный момент:")
        for i, player in enumerate(results['current_rankings'][:3]):
            print(f"      {i + 1}. {player['name']} - {player['score']} баллов")

        socketio.emit('question_results', results)

        print("⏳ Ожидание 3 секунд перед следующим вопросом...")
        time.sleep(3)

        self.current_question_index += 1
        if self.current_question_index < len(questions):
            self.start_question()
        else:
            self.end_quiz()

    def get_current_rankings(self): # Метод для получения текущего рейтинга
        """Возвращает текущий рейтинг игроков"""
        rankings = []
        for player_id, player_data in self.players.items():
            rankings.append({
                'name': player_data['name'],
                'score': self.scores.get(player_id, 0),
                'correct_answers': player_data.get('correct_answers', 0)
            })

        # Сортируем по убыванию баллов
        rankings.sort(key=lambda x: x['score'], reverse=True)
        return rankings

    def end_quiz(self):
        self.quiz_active = False
        self.timer_active = False
        self.waiting_for_admin = True  # Сбрасываем для следующей игры

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
            # Генерируем случайную позицию для облака имен
            position = {
                'x': random.randint(10, 90),  # Проценты от ширины
                'y': random.randint(10, 90),  # Проценты от высоты
                'size': random.randint(14, 24)  # Размер шрифта
            }

            self.players[player_id] = {
                'name': name,
                'correct_answers': 0,
                'position': position
            }
            self.scores[player_id] = 0
            self.player_positions[player_id] = position

            print(f"👤 Новый игрок: {name} (всего игроков: {len(self.players)})")

            # Отправляем обновленное облако имен всем клиентам
            self.update_name_cloud()

    def update_name_cloud(self):
        """Отправляет обновленное облако имен всем клиентам"""
        name_cloud = []
        for player_id, player_data in self.players.items():
            name_cloud.append({
                'name': player_data['name'],
                'x': player_data['position']['x'],
                'y': player_data['position']['y'],
                'size': player_data['position']['size']
            })

        socketio.emit('name_cloud_update', {'players': name_cloud})

    def submit_answer(self, player_id, question_id, answer_index): #ответы участников
        if (player_id in self.players and
                self.timer_active and
                player_id not in self.answers):

            self.answers[player_id] = answer_index

            current_question = questions[self.current_question_index]
            response_time = time.time() - self.question_start_time

            # ВАЖНО: Сохраняем инфомацию о правильности ответа
            correct = (answer_index == current_question['correct_answer'])

            if correct:
                # Бонус за скорость: чем быстрее ответ, тем больше баллов
                max_bonus = 10
                time_bonus = max(1, max_bonus - int(response_time))
                self.scores[player_id] += time_bonus
                self.players[player_id]['correct_answers'] += 1
                print(
                    f"✅ Правильный ответ от {self.players[player_id]['name']} (+{time_bonus} баллов, время: {response_time:.1f}с)")
            else:
                print(f"❌ Неправильный ответ от {self.players[player_id]['name']}")

            # Сохраняем детали ответа для статистики
            self.players[player_id]['last_answer_correct'] = correct
            self.players[player_id]['last_response_time'] = response_time

            # Немедленно отправляем подтверждение ответа игроку
            socketio.emit('answer_processed', {
                'correct': correct,
                'player_score': self.scores[player_id]
            }, room=player_id)


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
    # Удаляем игрока из облака имен при отключении
    if request.sid in quiz_manager.players:
        del quiz_manager.players[request.sid]
        del quiz_manager.player_positions[request.sid]
        quiz_manager.update_name_cloud()


@socketio.on('join_quiz')
def handle_join(data):
    name = data.get('name', 'Аноним').strip()
    if not name:
        name = 'Аноним'

    quiz_manager.add_player(request.sid, name)
    emit('joined_success', {'name': name})

    # Отправляем текущее состояние викторины
    if quiz_manager.waiting_for_admin:
        emit('waiting_for_start', room=request.sid)
    elif quiz_manager.quiz_active:
        # Если викторина уже идет, отправляем текущий вопрос
        quiz_manager.start_question()


@socketio.on('submit_answer')
def handle_answer(data):
    question_id = data.get('question_id')
    answer_index = data.get('answer_index')

    print(f"📨 Получен ответ от {request.sid}: вопрос {question_id}, ответ {answer_index}")

    quiz_manager.submit_answer(request.sid, question_id, answer_index)
    # emit('answer_received', {'status': 'ok'})


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


