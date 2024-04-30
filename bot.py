import telebot
import random 
import datetime

bot = telebot.TeleBot('token')

users = {}
record = {}
hide_markup = telebot.types.ReplyKeyboardRemove()

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Поздороваться c ботом")
    btn2 = telebot.types.KeyboardButton("Что ты умеешь?")
    markup.add(btn1, btn2)
    return markup

# обработка команды start
@bot.message_handler(commands=['start'])
def react_command_start(message):
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}! Я бот, я готов к работе', reply_markup=main_menu())

def all_commands(answer):
    if answer.text == "/start":
        react_command_start(answer)
    elif answer.text == "/help":
        react_command_help(answer)
    elif answer.text == "/minigame":
        react_command_minigame(answer)
    elif answer.text == "/age":
        react_command_age(answer)
    elif answer.text == "/name":
        react_command_name(answer)
    elif answer.text == "/predict":
        react_command_predict(answer)
    elif answer.text == "/all_users":
        react_command_all_users(answer)
    elif answer.text == "/dairy":
        react_command_dairy(answer)
    elif answer.text == "возврат в меню":
        react_command_start(answer)
    else:
        bot.send_message(answer.from_user.id, "Команда не существует")

# обработка команды name, внесение в базу данных о пользователях
@bot.message_handler(commands=['name'])
def react_command_name(message):
    react_command_name_answer = bot.send_message(message.from_user.id, "Введите ваше имя", reply_markup=hide_markup)
    bot.register_next_step_handler(react_command_name_answer, after_name)     

def after_name(answer):
    global users
    if answer.text.startswith('/'):
        bot.send_message(answer.from_user.id, "Вы ввели команду, работа с базой прервана")
        all_commands(answer)
    else:
        try:
            data = users[answer.from_user.id]
        except:
            users[answer.from_user.id] = {'user_name': None, 'user_age': None, 'user_dairy': []}
        finally:
            name = answer.text
            users[answer.from_user.id]['user_name'] = name
            bot.send_message(answer.from_user.id, "Данные успешно внесены")
            after_age_answer = bot.send_message(answer.from_user.id, "Введите ваш возраст")
            bot.register_next_step_handler(after_age_answer, after_age)

# обработка команды age (которая связана с name и идет строго после), внесение в базу данных о пользователях
@bot.message_handler(commands=['age'])
def react_command_age(message):
    try:
        data = users[message.from_user.id]
        react_command_age_answer = bot.send_message(message.from_user.id, "Введите ваш возраст")
        bot.register_next_step_handler(react_command_age_answer, after_age)
    except:
        bot.send_message(message.from_user.id, 'Кажется, вас нет в базе. Выберите сначала команду /name')

def after_age(answer):
    global users
    if answer.text.startswith('/'):
        bot.send_message(answer.from_user.id, "Вы ввели команду, работа с базой прервана")
        all_commands(answer)
    else:
        if answer.text.isdigit():
            age = int(answer.text)
            users[answer.from_user.id]['user_age'] = age
            bot.send_message(answer.from_user.id, "Данные успешно внесены", reply_markup=main_menu())
        else:
            after_age_answer = bot.send_message(answer.from_user.id, 'Пожалуйста, введите ваш возраст числом')
            if after_age_answer.text.startswith('/'):
                all_commands(after_age_answer)
            else:
                bot.register_next_step_handler(after_age_answer, after_age)

# обработка команды all_users
@bot.message_handler(commands=['all_users'])
def react_command_all_users(message):
    if len(users) > 0:
        try:
            user_name = users[message.from_user.id]["user_name"]
            user_age = users[message.from_user.id]["user_age"]
            user_dairy = users[message.from_user.id]["user_dairy"]
            bot.send_message(message.from_user.id, f'Ваши данныe: {user_name}, {user_age}')
            if len(users[message.from_user.id]['user_dairy']) > 0:
                dairy_data = pd.DataFrame(user_dairy)
                bot.send_message(message.from_user.id, ' '.join(dairy_data.columns.to_list()))
                bot.send_message(message.from_user.id, dairy_data.to_string(header=False, index=False))
            else:
                bot.send_message(message.from_user.id, 'Ваш дневник пуст', reply_markup=main_menu())
        except:
            bot.send_message(message.from_user.id, f'Ваши данные отсутствуют в базе.\nВыберите сначала команду /name')
        # finally:
        #     bot.send_message(message.from_user.id, 'Все пользователи')
        #     for elem in users:
        #         elem_data = users[elem]
        #         bot.send_message(message.from_user.id, f'ID {elem}: {elem_data["user_name"]}, {elem_data["user_age"]}')
    else:
        bot.send_message(message.from_user.id, f'В базе нет данных')

# обработка команды dairy
@bot.message_handler(commands=['dairy'])
def react_command_dairy(message):
    global record
    try:
        data = users[message.from_user.id] 
    except:
        bot.send_message(message.from_user.id, 'Кажется, вас нет в базе. Выберите сначала команду /name')   
    else:
        bot.send_message(message.from_user.id, "Давайте запишем ваши данные в дневник", reply_markup=hide_markup)
        record = {'date': None, 'pressure': None, 'temperature': None}
        date = bot.send_message(message.from_user.id, "Введите дату записи в формате 'dd.mm.yyyy'")
        bot.register_next_step_handler(date, after_dairy_date)

def after_dairy_date(answer):
    global users
    global record
    if answer.text.startswith('/'):
        bot.send_message(answer.from_user.id, "Некорректный формат ввода, повторите ввод")
        date = bot.send_message(answer.from_user.id, "Введите дату записи в формате 'dd.mm.yyyy'")
        bot.register_next_step_handler(date, after_dairy_date)
    else:
        record['date'] = answer.text
        pressure = bot.send_message(answer.from_user.id, "Введите показатели вашего давления (через слэш и без пробела, пример: 120/80)'")
        bot.register_next_step_handler(pressure, after_dairy_pressure)

def after_dairy_pressure(answer):
    global users
    global record
    if answer.text.startswith('/'):
        bot.send_message(answer.from_user.id, "Некорректный формат ввода, повторите ввод")
        pressure = bot.send_message(answer.from_user.id, "Введите показатели вашего давления (через слэш и без пробела, пример: 120/80)'")
        bot.register_next_step_handler(pressure, after_dairy_pressure)
    else:
        record['pressure'] = answer.text
        temperature = bot.send_message(answer.from_user.id, "Введите вашу температуру (пример: 36.5)")
        bot.register_next_step_handler(temperature, after_dairy_temperature)

def after_dairy_temperature(answer):
    global users
    global record
    if answer.text.startswith('/'):
        bot.send_message(answer.from_user.id, "Некорректный формат ввода, повторите ввод")
        temperature = bot.send_message(answer.from_user.id, "Введите вашу температуру (пример: 36.5)")
        bot.register_next_step_handler(temperature, after_dairy_temperature)
    else:
        record['temperature'] = answer.text
        users[answer.from_user.id]['user_dairy'].append(record)
        record = {}
        bot.send_message(answer.from_user.id, "Данные успешно внесены", reply_markup=main_menu())

# обработка команды help
@bot.message_handler(commands=['help'])
def react_command_help(message):
    text = ['Доступные команды:\n', 
            '/name - добавить имя пользователя в базу,\n',
            '/age - добавить возраст пользователя в базу\n',
            '/start - возврат в главное меню\n',
            '/predict - предсказать возраст\n',
            '/minigame - игра "Бот угадывает число"\n',
            '/all_users - список пользователей бота\n',
            '/dairy - добавить запись в дневник']
    bot.send_message(message.from_user.id, ''.join(text))

# обработка команды predict
@bot.message_handler(commands=['predict'])
def react_command_predict(message):
    user = users.get(message.from_user.id)
    if user and (user['user_age'] != None) and (user['user_name'] != None):
        current_age, name = user['user_age'], user['user_name']
        current_year = datetime.date.today().year
        year = random.randint(current_year, current_year + 100)
        age = current_age + (year - current_year)
        bot.send_message(message.from_user.id, f"Я вижу, вижу, что Вам, {name}, в {year} будет {age}!")
    else:
        bot.send_message(message.from_user.id, f"Кажется, вас нет в базе! Выберите команду /name, введите имя и возраст")
    
# обработка команды minigame
max_num = 100
min_num = 1
num = 50
@bot.message_handler(commands=['minigame'])
def react_command_minigame(message):
    bot.send_message(message.from_user.id, "Сыграем в игру!\nЗагадайте число от 1 до 100 включительно\nЯ буду угадывать, а вы отвечайте: ваше число больше моего или меньше\nНажмите кнонку 'Ответ', когда число будет угадано", reply_markup=hide_markup)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Больше")
    btn2 = telebot.types.KeyboardButton("Меньше")
    btn3 = telebot.types.KeyboardButton("Ответ")
    markup.add(btn1, btn2, btn3)
    react_command_minigame_answer = bot.send_message(message.from_user.id, "Начинаем игру!\nВот мое первое число: 50\nВаше число больше или меньше?", reply_markup=markup)
    bot.register_next_step_handler(react_command_minigame_answer, after_minigame)

def after_minigame(message):
    global max_num, min_num, num

    if message.text == 'Больше':
        min_num = num + 1
        num = min_num + (max_num - min_num) // 2
        if max_num >= 1 and (min_num <= 100):
            after_minigame_answer = bot.send_message(message.from_user.id, f"Вы загадали число {num}?")
            bot.register_next_step_handler(after_minigame_answer, after_minigame)
        else:
            bot.send_message(message.from_user.id, f"Загаданное число вне диапазона")
            bot.send_message(message.from_user.id, f"Игра окончена", reply_markup=main_menu())
            max_num = 100
            min_num = 1
            num = 50

    elif message.text == 'Меньше':
        max_num = num - 1
        num = min_num + (max_num - min_num) // 2
        if max_num >= 1 and (min_num <= 100):
            after_minigame_answer = bot.send_message(message.from_user.id, f"Вы загадали число {num}?")
            bot.register_next_step_handler(after_minigame_answer, after_minigame)
        else:
            bot.send_message(message.from_user.id, f"Загаданное число вне диапазона")
            bot.send_message(message.from_user.id, f"Игра окончена", reply_markup=main_menu())
            max_num = 100
            min_num = 1
            num = 50

    elif message.text == 'Ответ':
        bot.send_message(message.from_user.id, f"Вы загадали число {num}!\nЯ угадал!", reply_markup=hide_markup)
        bot.send_message(message.from_user.id, f"Игра окончена", reply_markup=main_menu())
        max_num = 100
        min_num = 1
        num = 50

    else:
        bot.send_message(message.from_user.id, f"Вы покинули игру", reply_markup=main_menu())
        all_commands(message)

# обработка кнопок главного меню
@bot.message_handler(content_types=['text'])
def after_start(answer):
    if answer.text == "Поздороваться c ботом":
        bot.send_message(answer.from_user.id, "У вас хорошие манеры!")

    elif answer.text == "Что ты умеешь?":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = telebot.types.KeyboardButton("/start")
        btn2 = telebot.types.KeyboardButton("/help")
        btn3 = telebot.types.KeyboardButton("/minigame")
        btn4 = telebot.types.KeyboardButton("/age")
        btn5 = telebot.types.KeyboardButton("/name")
        btn6 = telebot.types.KeyboardButton("/predict")
        btn7 = telebot.types.KeyboardButton("/all_users")
        btn8 = telebot.types.KeyboardButton("/dairy")
        back = telebot.types.KeyboardButton("возврат в меню")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, back)
        bot.send_message(answer.from_user.id, "Вот весь список функций", reply_markup=markup)
    
    elif answer.text == "возврат в меню":
        react_command_start(answer)
    
    else:
        bot.send_message(answer.from_user.id, answer.text)

bot.polling()