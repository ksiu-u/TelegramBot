# FunAndStudyBot

Telegram-бот, который умеет предсказывать будущее, угадывать числа и запоминать данные

1. [Формирование базы данных пользователей](#база-данных)
2. [Функция расчета возраста](#функция-predict)
3. [Числовая мини-игра на основе бинарного поиска](#minigame-и-бинарный-поиск)

Функционал бота включает команды:
- /name - добавить имя пользователя в базу
- /age - добавить возраст пользователя в базу
- /start - возврат в главное меню
- /predict - предсказать возраст
- /minigame - игра "Бот угадывает число"
- /all_users - список пользователей бота

### База данных
---
Аналогом работы с СУБД выступает работа с глобальной переменной (словарь users). В базу записыввается id (определяется автоматически), имя и возраст (вводятся пользователем). 
```python
users[answer.from_user.id] = {'user_name': None, 'user_age': None}
```

При вводе имени программа сразу следом запрашивает ввод возраста. Ввод возраста без предварительного ввода имени (при условии, что пользователь новый) невозможен, выводится предупреждение:
```python
bot.send_message(message.from_user.id, 'Кажется, вас нет в базе. Выберите сначала команду /name')
```

Реализована функция all_users, которая позволяет распечатать всех пользователей бота.
```python
for elem in users:
    elem_data = users[elem]
    bot.send_message(message.from_user.id, f'ID {elem}: {elem_data["user_name"]}, {elem_data["user_age"]}')
```

На любом этапе пользователь может ввести команду (которая начинается с '/') и покинуть контекст.
```python
if answer.text.startswith('/'):
    bot.send_message(answer.from_user.id, "Вы ввели команду, работа с базой прервана")
```

### Функция predict
---
Функция извлекает из базы (users) данные об имени и возрасте пользователя (учитывая его id). 
С помощью модуля datetime программа определяет текущий год. 
С помощью метода randomint модуля random генерируется случайное число в диапазоне от сейчас до +100 лет.

```python
current_year = datetime.date.today().year
year = random.randint(current_year, current_year + 100)
age = current_age + (year - current_year)
bot.send_message(message.from_user.id, f"Я вижу, вижу, что Вам, {name}, в {year} будет {age}!")
```

Если в базе нет данных, выводится предупреждение.

### Minigame и бинарный поиск
---
Мини-игра предполагает угадывание загаданного пользователем числа. Бот выводит числа, пользователей отвечает с помощью кнопок Reply-клавиатуры.
```python
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Больше")
    btn2 = telebot.types.KeyboardButton("Меньше")
    btn3 = telebot.types.KeyboardButton("Ответ")
    markup.add(btn1, btn2, btn3)
    react_command_minigame_answer = bot.send_message(message.from_user.id, "Начинаем игру!\nВот мое первое число: 50\nВаше число больше или меньше?", reply_markup=markup)
    bot.register_next_step_handler(react_command_minigame_answer, after_minigame)
```

Игра заканчиватся, если: 
- загаданное число (вычисляется и хранится в переменной num) выходит за пределы диапазона (число меньше 1 и больше 100)
- пользователь нажал на кнопку "Ответ"
- пользователь вызвал команду, которая начинается с "/"
```python
bot.send_message(message.from_user.id, f"Игра окончена", reply_markup=main_menu())
```