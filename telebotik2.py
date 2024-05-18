import telebot
from telebot import types
from threading import Timer
import random
from datetime import datetime

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the token you received from BotFather
bot = telebot.TeleBot('6920406775:AAE9rAtGpOkPNR9Xsoi1RPj9h8UKXBuP4')

# This dictionary will store the user's personal data
user_data = {}
user_timers = {}

# State management
user_states = {}


# Define user states
class UserState:
    CHOOSING_LANGUAGE = 0
    ASKING_NAME = 1
    ASKING_AGE = 2
    ASKING_SEX = 3
    ASKING_HEIGHT = 4
    ASKING_WEIGHT = 5
    ASKING_GYM_NEWBIE = 6
    ASKING_GYM_YEARS = 7
    SHOWING_STATS = 8
    SETTING_TIMER = 9
    UPDATING_WEIGHT = 10
    SHOWING_SPLITS = 11


# List of advices
advices = [
    "Remember to stay hydrated!",
    "Consistency is key to success.",
    "Don't forget to warm up before your workout.",
    "Proper form is more important than heavy weights.",
    "Rest and recovery are crucial for muscle growth.",
    "Balanced nutrition is essential for a healthy body.",
    "Set realistic goals and track your progress.",
    "Mix up your routine to avoid plateaus.",
    "Consistency is the key. It's not about being perfect every day, but showing up and giving your best effort consistently.",
    "Strength isn't just about lifting heavy weights; it's about overcoming challenges and pushing your limits.",
    "Success in fitness and life comes down to hard work, dedication, and a positive mindset.",
    "Every rep, every set, every workout – it all adds up. Stay focused on your goals and never give up.",
    "Progress isn't always visible immediately, but every step forward, no matter how small, brings you closer to your goals.",
    "Embrace the journey, enjoy the process, and celebrate every victory, no matter how small.",
    "It's not about being the best. It's about being better than you were yesterday.",
    "Fitness is not just a hobby; it's a lifestyle. Commit to it fully, and the results will follow.",
    "The only limits that exist are the ones you place on yourself. Break free from them and reach your full potential.",
    "Believe in yourself, stay disciplined, and trust the process. The results will come."
]


# Function to start the bot and ask for the user's language
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('English', 'Українська')
    bot.send_message(message.chat.id,
                     "Welcome to Coach Sam! Please choose your language.\nЛаскаво просимо до Coach Sam! Будь ласка, оберіть мову.",
                     reply_markup=markup)
    user_states[message.chat.id] = UserState.CHOOSING_LANGUAGE


# Function to handle state transitions and user messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    state = user_states.get(message.chat.id, None)

    if state == UserState.CHOOSING_LANGUAGE:
        if message.text in ['English', 'Українська']:
            user_data[message.chat.id] = {'language': message.text}
            if message.text == 'English':
                bot.send_message(message.chat.id, "What's your name?")
            else:
                bot.send_message(message.chat.id, "Як вас звати?")
            user_states[message.chat.id] = UserState.ASKING_NAME
        else:
            bot.send_message(message.chat.id, "Please choose a valid language.\nБудь ласка, оберіть дійсну мову.")

    elif state == UserState.ASKING_NAME:
        user_data[message.chat.id].update({'name': message.text})
        if user_data[message.chat.id]['language'] == 'English':
            bot.send_message(message.chat.id, "How old are you?")
        else:
            bot.send_message(message.chat.id, "Скільки вам років?")
        user_states[message.chat.id] = UserState.ASKING_AGE

    elif state == UserState.ASKING_AGE:
        if message.text.isdigit() and int(message.text) > 0:
            user_data[message.chat.id]['age'] = int(message.text)
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "What is your sex? (Male/Female)")
            else:
                bot.send_message(message.chat.id, "Яка ваша стать? (Чоловіча/Жіноча)")
            user_states[message.chat.id] = UserState.ASKING_SEX
        else:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please enter a valid age.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, введіть дійсний вік.")

    elif state == UserState.ASKING_SEX:
        sex = message.text.lower()
        if sex in ['male', 'female', 'чоловіча', 'жіноча']:
            user_data[message.chat.id]['sex'] = sex.capitalize()
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "What is your height in cm?")
            else:
                bot.send_message(message.chat.id, "Який ваш зріст у см?")
            user_states[message.chat.id] = UserState.ASKING_HEIGHT
        else:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please enter either Male or Female.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, введіть або Чоловіча, або Жіноча.")

    elif state == UserState.ASKING_HEIGHT:
        if message.text.isdigit() and int(message.text) > 0:
            user_data[message.chat.id]['height'] = int(message.text)
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "What is your weight in kg?")
            else:
                bot.send_message(message.chat.id, "Яка ваша вага у кг?")
            user_states[message.chat.id] = UserState.ASKING_WEIGHT
        else:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please enter a valid height in cm.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, введіть дійсний зріст у см.")

    elif state == UserState.ASKING_WEIGHT:
        if message.text.isdigit() and int(message.text) > 0:
            user_data[message.chat.id]['weight'] = int(message.text)
            calculate_bmi(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add('Yes', 'No') if user_data[message.chat.id]['language'] == 'English' else markup.add('Так', 'Ні')
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Are you a newbie to the gym? (Yes/No)", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Ви новачок у тренажерному залі? (Так/Ні)", reply_markup=markup)
            user_states[message.chat.id] = UserState.ASKING_GYM_NEWBIE
        else:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please enter a valid weight in kg.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, введіть дійсну вагу у кг.")

    elif state == UserState.ASKING_GYM_NEWBIE:
        if message.text.lower() in ['yes', 'так']:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "That's awesome! Everyone starts somewhere. Keep it up!")
                user_data[message.chat.id]['gym_years'] = 0
                bot.send_message(message.chat.id, "Thank you for providing your information!")
            else:
                bot.send_message(message.chat.id, "Це чудово! Кожен починає десь. Продовжуйте в тому ж дусі!")
                user_data[message.chat.id]['gym_years'] = 0
                bot.send_message(message.chat.id, "Дякуємо за надану інформацію!")
            show_stats(message)
        elif message.text.lower() in ['no', 'ні']:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "How many years have you been going to the gym?")
            else:
                bot.send_message(message.chat.id, "Скільки років ви ходите в тренажерний зал?")
            user_states[message.chat.id] = UserState.ASKING_GYM_YEARS
        else:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please answer with Yes or No.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, відповідайте Так або Ні.")

    elif state == UserState.ASKING_GYM_YEARS:
        if message.text.isdigit() and int(message.text) >= 0:
            user_data[message.chat.id]['gym_years'] = int(message.text)
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Thank you for providing your information!")
            else:
                bot.send_message(message.chat.id, "Дякуємо за надану інформацію!")
            show_stats(message)
        else:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please enter a valid number of years.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, введіть дійсну кількість років.")

    elif state == UserState.SHOWING_STATS:
        if message.text.lower() in ['yes', 'так']:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Setting up your daily weight update reminder...")
                user_states[message.chat.id] = UserState.SETTING_TIMER
            else:
                bot.send_message(message.chat.id, "Налаштовуємо нагадування про щоденне оновлення ваги...")
                user_states[message.chat.id] = UserState.SETTING_TIMER
        elif message.text.lower() in ['no', 'ні']:
            show_options(message)
        else:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please answer with Yes or No.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, відповідайте Так або Ні.")

    elif state == UserState.SETTING_TIMER:
        try:
            hour, minute = map(int, message.text.split(':'))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                reminder_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                if reminder_time < datetime.now():
                    reminder_time = reminder_time.replace(day=reminder_time.day + 1)
                delay = (reminder_time - datetime.now()).total_seconds()
                user_timers[message.chat.id] = Timer(delay, send_weight_update_reminder, [message.chat.id])
                user_timers[message.chat.id].start()
                if user_data[message.chat.id]['language'] == 'English':
                    bot.send_message(message.chat.id, f"Reminder set for {hour:02d}:{minute:02d} daily.")
                else:
                    bot.send_message(message.chat.id, f"Нагадування встановлено на {hour:02d}:{minute:02d} щодня.")
                user_states[message.chat.id] = UserState.UPDATING_WEIGHT
            else:
                raise ValueError
        except ValueError:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please enter a valid time in the format HH:MM.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, введіть дійсний час у форматі ГГ:ХХ.")

    elif state == UserState.UPDATING_WEIGHT:
        if message.text.isdigit() and int(message.text) > 0:
            user_data[message.chat.id]['weight'] = int(message.text)
            calculate_bmi(message)
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, f"Your weight has been updated to {message.text} kg.")
                bot.send_message(message.chat.id, random.choice(advices))
            else:
                bot.send_message(message.chat.id, f"Вашу вагу оновлено до {message.text} кг.")
                bot.send_message(message.chat.id, random.choice(advices))
            show_options(message)
        else:
            if user_data[message.chat.id]['language'] == 'English':
                bot.send_message(message.chat.id, "Please enter a valid weight in kg.")
            else:
                bot.send_message(message.chat.id, "Будь ласка, введіть дійсну вагу у кг.")

    elif state == UserState.SHOWING_SPLITS:
        handle_gym_splits(message)


# Function to calculate BMI
def calculate_bmi(message):
    height_m = user_data[message.chat.id]['height'] / 100
    weight = user_data[message.chat.id]['weight']
    bmi = weight / (height_m ** 2)
    user_data[message.chat.id]['bmi'] = round(bmi, 2)


# Function to show user stats
def show_stats(message):
    if user_data[message.chat.id]['language'] == 'English':
        stats = (f"Here are your stats:\n"
                 f"Name: {user_data[message.chat.id]['name']}\n"
                 f"Age: {user_data[message.chat.id]['age']}\n"
                 f"Sex: {user_data[message.chat.id]['sex']}\n"
                 f"Height: {user_data[message.chat.id]['height']} cm\n"
                 f"Weight: {user_data[message.chat.id]['weight']} kg\n"
                 f"BMI: {user_data[message.chat.id]['bmi']}\n"
                 f"Years at gym: {user_data[message.chat.id]['gym_years']}")
    else:
        stats = (f"Ось ваші дані:\n"
                 f"Ім'я: {user_data[message.chat.id]['name']}\n"
                 f"Вік: {user_data[message.chat.id]['age']}\n"
                 f"Стать: {user_data[message.chat.id]['sex']}\n"
                 f"Зріст: {user_data[message.chat.id]['height']} см\n"
                 f"Вага: {user_data[message.chat.id]['weight']} кг\n"
                 f"ІМТ: {user_data[message.chat.id]['bmi']}\n"
                 f"Років у залі: {user_data[message.chat.id]['gym_years']}")
    bot.send_message(message.chat.id, stats)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Yes', 'No') if user_data[message.chat.id]['language'] == 'English' else markup.add('Так', 'Ні')
    if user_data[message.chat.id]['language'] == 'English':
        bot.send_message(message.chat.id, "Would you like daily weight update reminders?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Хочете щоденні нагадування про оновлення ваги?", reply_markup=markup)
    user_states[message.chat.id] = UserState.SHOWING_STATS


# Function to send weight update reminder
def send_weight_update_reminder(chat_id):
    if user_data[chat_id]['language'] == 'English':
        bot.send_message(chat_id, "It's time to update your weight. Please enter your current weight in kg.")
    else:
        bot.send_message(chat_id, "Час оновити вашу вагу. Будь ласка, введіть вашу поточну вагу у кг.")
    user_states[chat_id] = UserState.UPDATING_WEIGHT
    # Reschedule the reminder for the next day
    user_timers[chat_id] = Timer(24 * 60 * 60, send_weight_update_reminder, [chat_id])
    user_timers[chat_id].start()


# Function to translate messages
def translate_message(message, language):
    translations = {
        "The Upper-Lower Training Split Workout Routine: This split divides your workouts into upper body and lower body days, allowing for focused training on specific muscle groups.\nWatch this video for more details: https://www.youtube.com/watch?v=3IQVNjWH60A&ab_channel=JeffNippard": {
            "Українська": "Програма тренувань Upper-Lower: Цей розподіл ділить ваші тренування на дні верхньої та нижньої частини тіла, що дозволяє зосередитися на певних групах м'язів.\nДивіться це відео для отримання додаткової інформації: https://www.youtube.com/watch?v=3IQVNjWH60A&ab_channel=JeffNippard"
        },
        "Push/Pull/Legs (PPL) Workout Routine: This split is divided into push (chest, shoulders, triceps), pull (back, biceps), and leg days. It's a versatile routine for balanced training.\nWatch this video for more details: https://www.youtube.com/watch?v=qVek72z3F1U&ab_channel=JeffNippard": {
            "Українська": "Програма тренувань Push/Pull/Legs (PPL): Цей розподіл ділить тренування на дні штовхання (груди, плечі, трицепси), тягнення (спина, біцепси) і ноги. Це універсальна програма для збалансованих тренувань.\nДивіться це відео для отримання додаткової інформації: https://www.youtube.com/watch?v=qVek72z3F1U&ab_channel=JeffNippard"
        },
        "Full Body Split Training Program: This split involves training all major muscle groups in a single workout, which is efficient and great for overall fitness.\nWatch this video for more details: https://www.youtube.com/watch?v=eTxO5ZMxcsc&ab_channel=JeffNippard": {
            "Українська": "Програма тренувань Full Body Split: Цей розподіл включає тренування всіх основних груп м'язів за одне тренування, що є ефективним і чудовим для загальної фізичної форми.\nДивіться це відео для отримання додаткової інформації: https://www.youtube.com/watch?v=eTxO5ZMxcsc&ab_channel=JeffNippard"
        },
        "A helpful video for beginners: Starting your fitness journey? Here's a video to guide you through the basics.\nWatch this video: https://www.youtube.com/watch?v=U9ENCvFf9yQ&ab_channel=trainerwinny": {
            "Українська": "Корисне відео для новачків: Починаєте свою фітнес-подорож? Ось відео, яке допоможе вам освоїти основи.\nДивіться це відео: https://www.youtube.com/watch?v=U9ENCvFf9yQ&ab_channel=trainerwinny"
        }
    }
    return translations.get(message, {}).get(language, message)


# Function to handle gym splits
@bot.callback_query_handler(func=lambda call: True)
def handle_gym_splits(call):
    if call.data == "upper_lower":
        bot.send_message(call.message.chat.id,
                         translate_message(
                             "The Upper-Lower Training Split Workout Routine: This split divides your workouts into upper body and lower body days, allowing for focused training on specific muscle groups.\nWatch this video for more details: https://www.youtube.com/watch?v=3IQVNjWH60A&ab_channel=JeffNippard",
                             user_data[call.message.chat.id]['language']))
    elif call.data == "ppl":
        bot.send_message(call.message.chat.id,
                         translate_message(
                             "Push/Pull/Legs (PPL) Workout Routine: This split is divided into push (chest, shoulders, triceps), pull (back, biceps), and leg days. It's a versatile routine for balanced training.\nWatch this video for more details: https://www.youtube.com/watch?v=qVek72z3F1U&ab_channel=JeffNippard",
                             user_data[call.message.chat.id]['language']))
    elif call.data == "full_body":
        bot.send_message(call.message.chat.id,
                         translate_message(
                             "Full Body Split Training Program: This split involves training all major muscle groups in a single workout, which is efficient and great for overall fitness.\nWatch this video for more details: https://www.youtube.com/watch?v=eTxO5ZMxcsc&ab_channel=JeffNippard",
                             user_data[call.message.chat.id]['language']))
    elif call.data == "beginners":
        bot.send_message(call.message.chat.id,
                         translate_message(
                             "A helpful video for beginners: Starting your fitness journey? Here's a video to guide you through the basics.\nWatch this video: https://www.youtube.com/watch?v=U9ENCvFf9yQ&ab_channel=trainerwinny",
                             user_data[call.message.chat.id]['language']))


# Function to show options for gym splits and other features
def show_options(message):
    markup = types.InlineKeyboardMarkup()
    upper_lower_button = types.InlineKeyboardButton("Upper-Lower Split", callback_data="upper_lower")
    ppl_button = types.InlineKeyboardButton("Push/Pull/Legs Split", callback_data="ppl")
    full_body_button = types.InlineKeyboardButton("Full Body Split", callback_data="full_body")
    beginners_button = types.InlineKeyboardButton("Beginners Guide", callback_data="beginners")
    markup.add(upper_lower_button, ppl_button, full_body_button, beginners_button)
    if user_data[message.chat.id]['language'] == 'English':
        bot.send_message(message.chat.id, "Choose a workout split:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Виберіть програму тренувань:", reply_markup=markup)
    user_states[message.chat.id] = UserState.SHOWING_SPLITS


bot.polling()
