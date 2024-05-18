User
import telebot
from telebot import types
from threading import Timer
import random
from datetime import datetime

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the token you received from BotFather
bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')

# This dictionary will store the user's personal data
user_data = {}
user_timers = {}

# State management
user_states = {}

# Define user states
class UserState:
    ASKING_NAME = 1
    ASKING_AGE = 2
    ASKING_SEX = 3
    ASKING_HEIGHT = 4
    ASKING_WEIGHT = 5
    ASKING_DOB = 6
    ASKING_GYM_NEWBIE = 7
    ASKING_GYM_YEARS = 8
    SHOWING_STATS = 9
    SETTING_TIMER = 10
    UPDATING_WEIGHT = 11

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

# Function to start the bot and ask for the user's name
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome to Coach Sam! Let's get started with some personal information.")
    bot.send_message(message.chat.id, "What's your name?")
    user_states[message.chat.id] = UserState.ASKING_NAME

# Function to handle state transitions and user messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    state = user_states.get(message.chat.id, None)
    
    if state == UserState.ASKING_NAME:
        user_data[message.chat.id] = {'name': message.text}
        bot.send_message(message.chat.id, "How old are you?")
        user_states[message.chat.id] = UserState.ASKING_AGE
    
    elif state == UserState.ASKING_AGE:
        if message.text.isdigit() and int(message.text) > 0:
            user_data[message.chat.id]['age'] = int(message.text)
            bot.send_message(message.chat.id, "What is your sex? (Male/Female)")
            user_states[message.chat.id] = UserState.ASKING_SEX
        else:
            bot.send_message(message.chat.id, "Please enter a valid age.")

    elif state == UserState.ASKING_SEX:
        sex = message.text.lower()
        if sex in ['male', 'female']:
            user_data[message.chat.id]['sex'] = sex.capitalize()
            bot.send_message(message.chat.id, "What is your height in cm?")
            user_states[message.chat.id] = UserState.ASKING_HEIGHT
        else:
            bot.send_message(message.chat.id, "Please enter either Male or Female.")

    elif state == UserState.ASKING_HEIGHT:
        if message.text.isdigit() and int(message.text) > 0:
            user_data[message.chat.id]['height'] = int(message.text)
            bot.send_message(message.chat.id, "What is your weight in kg?")
            user_states[message.chat.id] = UserState.ASKING_WEIGHT
        else:
            bot.send_message(message.chat.id, "Please enter a valid height in cm.")
    
    elif state == UserState.ASKING_WEIGHT:
        if message.text.isdigit() and int(message.text) > 0:
            user_data[message.chat.id]['weight'] = int(message.text)
            bot.send_message(message.chat.id, "What's your date of birth? (YYYY-MM-DD)")
            user_states[message.chat.id] = UserState.ASKING_DOB
        else:
            bot.send_message(message.chat.id, "Please enter a valid weight in kg.")

    elif state == UserState.ASKING_DOB:
        try:
            dob = datetime.strptime(message.text, "%Y-%m-%d")
            user_data[message.chat.id]['dob'] = dob
            calculate_bmi(message)
            calculate_age(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Yes', 'No')
            bot.send_message(message.chat.id, "Are you a newbie to the gym? (Yes/No)", reply_markup=markup)
            user_states[message.chat.id] = UserState.ASKING_GYM_NEWBIE
        except ValueError:
            bot.send_message(message.chat.id, "Please enter your date of birth in the format YYYY-MM-DD.")

    elif state == UserState.ASKING_GYM_NEWBIE:
        if message.text.lower() == 'yes':
            bot.send_message(message.chat.id, "That's awesome! Everyone starts somewhere. Keep it up!")
            user_data[message.chat.id]['gym_years'] = 0
            bot.send_message(message.chat.id, "Thank you for providing your information!")
            show_main_menu(message)
        elif message.text.lower() == 'no':
            bot.send_message(message.chat.id, "How many years have you been active in the gym? You can enter fractions like 0.5 for half a year.")
            user_states[message.chat.id] = UserState.ASKING_GYM_YEARS
        else:
            bot.send_message(message.chat.id, "Please enter Yes or No.")

    elif state == UserState.ASKING_GYM_YEARS:
        try:
            gym_years = float(message.text)
            if gym_years >= 0:
                user_data[message.chat.id]['gym_years'] = gym_years
                bot.send_message(message.chat.id, "Thank you for providing your information!")
                show_main_menu(message)
            else:
                bot.send_message(message.chat.id, "Please enter a valid number of years.")
        except ValueError:
            bot.send_message(message.chat.id, "Please enter a valid number of years.")

    elif state == UserState.SHOWING_STATS:
        if message.text.lower() == 'my stats':
            show_user_stats(message)
        elif message.text.lower() == 'reset':
            reset_user_data(message.chat.id)
            start(message)
        elif message.text.lower() == 'advices':
            give_random_advice(message)
        elif message.text.lower() == 'timer':
            bot.send_message(message.chat.id, "How many hours from now would you like to be reminded to go to the gym?")
            user_states[message.chat.id] = UserState.SETTING_TIMER
        elif message.text.lower() == 'update weight':
            bot.send_message(message.chat.id, "Please enter your new weight in kg.")
            user_states[message.chat.id] = UserState.UPDATING_WEIGHT
        elif message.text.lower() == 'gym splits':
            show_gym_splits(message)

    elif state == UserState.SETTING_TIMER:
        try:
            hours = float(message.text)
            if hours > 0:
                set_gym_reminder(message, hours)
                bot.send_message(message.chat.id, f"I'll remind you to go to the gym in {hours} hours.")
                show_main_menu(message)
            else:
                bot.send_message(message.chat.id, "Please enter a valid number of hours.")
        except ValueError:
            bot.send_message(message.chat.id, "Please enter a valid number of hours.")

    elif state == UserState.UPDATING_WEIGHT:
        try:
            new_weight = float(message.text)
            if new_weight > 0:
                old_weight = user_data[message.chat.id]['weight']
                weight_change = new_weight - old_weight
                weight_change_percentage = (weight_change / old_weight) * 100
                user_data[message.chat.id]['weight'] = new_weight
                user_data[message.chat.id]['weight_change_percentage'] = round(weight_change_percentage, 2)
                calculate_bmi(message)
                bot.send_message(message.chat.id, f"Your weight has been updated. Change: {weight_change_percentage:.2f}%")
                show_main_menu(message)
            else:
                bot.send_message(message.chat.id, "Please enter a valid weight in kg.")
        except ValueError:
            bot.send_message(message.chat.id, "Please enter a valid weight in kg.")

def calculate_bmi(message):
    height_m = user_data[message.chat.id]['height'] / 100
    weight = user_data[message.chat.id]['weight']
    bmi = weight / (height_m ** 2)
    user_data[message.chat.id]['bmi'] = round(bmi, 2)

    if bmi < 18.5:
        bmi_category = "underweight"
    elif 18.5 <= bmi < 24.9:
        bmi_category = "normal weight"
    elif 25 <= bmi < 29.9:
        bmi_category = "overweight"
    else:
        bmi_category = "obese"

    user_data[message.chat.id]['bmi_category'] = bmi_category

def calculate_age(message):
    dob = user_data[message.chat.id]['dob']
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    user_data[message.chat.id]['age'] = age

def show_user_stats(message):
    data = user_data[message.chat.id]
    stats = (f"Name: {data['name']}\n"
             f"Age: {data['age']}\n"
             f"Sex: {data['sex']}\n"
             f"Height: {data['height']} cm\n"
             f"Weight: {data['weight']} kg\n"
             f"BMI: {data['bmi']} ({data['bmi_category']})\n"
             f"Years active in gym: {data['gym_years']}\n"
             f"Weight Change: {data.get('weight_change_percentage', 'N/A')}%")
    bot.send_message(message.chat.id, stats)
    show_main_menu(message)

def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('My Stats', 'Reset', 'Advices', 'Timer', 'Update Weight', 'Gym Splits')
    bot.send_message(message.chat.id, 'Choose an option:', reply_markup=markup)
    user_states[message.chat.id] = UserState.SHOWING_STATS

def reset_user_data(chat_id):
    if chat_id in user_data:
        del user_data[chat_id]
    if chat_id in user_states:
        del user_states[chat_id]

def give_random_advice(message):
    advice = random.choice(advices)
    bot.send_message(message.chat.id, advice)

def set_gym_reminder(message, hours):
    chat_id = message.chat.id
    if chat_id in user_timers:
        user_timers[chat_id].cancel()
    
    user_timers[chat_id] = Timer(hours * 3600, send_gym_reminder, [chat_id])
    user_timers[chat_id].start()

def send_gym_reminder(chat_id):
    bot.send_message(chat_id, "Time to hit the gym! Let's go!")

def show_gym_splits(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Upper-Lower", callback_data="upper_lower"))
    markup.add(types.InlineKeyboardButton("Push/Pull/Legs", callback_data="ppl"))
    markup.add(types.InlineKeyboardButton("Full Body", callback_data="full_body"))
    markup.add(types.InlineKeyboardButton("For Beginners", callback_data="beginners"))
    bot.send_message(message.chat.id, "Choose a gym split to learn more:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "upper_lower":
        bot.send_message(call.message.chat.id, 
            "The Upper-Lower Training Split Workout Routine: This split divides your workouts into upper body and lower body days, allowing for focused training on specific muscle groups.\nWatch this video for more details: https://www.youtube.com/watch?v=3IQVNjWH60A&ab_channel=JeffNippard")
    elif call.data == "ppl":
        bot.send_message(call.message.chat.id, 
            "Push/Pull/Legs (PPL) Workout Routine: This split is divided into push (chest, shoulders, triceps), pull (back, biceps), and leg days. It's a versatile routine for balanced training.\nWatch this video for more details: https://www.youtube.com/watch?v=qVek72z3F1U&ab_channel=JeffNippard")
    elif call.data == "full_body":
        bot.send_message(call.message.chat.id, 
            "Full Body Split Training Program: This split involves training all major muscle groups in a single workout, which is efficient and great for overall fitness.\nWatch this video for more details: https://www.youtube.com/watch?v=eTxO5ZMxcsc&ab_channel=JeffNippard")
    elif call.data == "beginners":
        bot.send_message(call.message.chat.id, 
            "A helpful video for beginners: Starting your fitness journey? Here's a video to guide you through the basics.\nWatch this video: https://www.youtube.com/watch?v=U9ENCvFf9yQ&ab_channel=trainerwinny")

# Start the bot
bot.polling()
