import telebot
from telebot import types

# Replace YOUR_TELEGRAM_BOT_TOKEN with the token you received from BotFather
bot = telebot.TeleBot('7155412471:AAF75oq4TiyWcVd3i5I1XghiSRdFxmCsaMU')

# This is a dictionary that will store the user's gym progress
gym_progress = {}

# State management
user_states = {}
current_exercise_info = {}


# Define user states
class UserState:
    ASKING_DAYS = 1
    ASKING_EXERCISES = 2
    ASKING_SETS_REPS = 3
    ASKING_WEIGHTS = 4
    SHOWING_PROGRESS = 5
    RESTART_DAY_SELECTION = 6
    VIEWING_PROGRESS = 7
    ADD_MORE_DAYS = 8


# This is a function that will be called whenever the user starts the bot
@bot.message_handler(commands=['start'])
def start(message):
    reset_user_data(message.chat.id)
    ask_days_per_week(message)


# Function to handle state transitions and user messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    state = user_states.get(message.chat.id, None)

    if state == UserState.ASKING_DAYS:
        handle_asking_days(message)
    elif state == UserState.ASKING_EXERCISES:
        handle_asking_exercises(message)
    elif state == UserState.ASKING_SETS_REPS:
        handle_asking_sets_reps(message)
    elif state == UserState.ASKING_WEIGHTS:
        handle_asking_weights(message)
    elif state == UserState.RESTART_DAY_SELECTION:
        handle_restart_day_selection(message)
    elif state == UserState.VIEWING_PROGRESS:
        handle_viewing_progress(message)
    elif state == UserState.ADD_MORE_DAYS:
        handle_add_more_days(message)


def handle_asking_days(message):
    days_per_week = message.text
    if days_per_week.split()[0].isdigit() and 1 <= int(days_per_week.split()[0]) <= 7:
        gym_progress[message.chat.id] = {'days_per_week': days_per_week, 'exercises': {}}
        bot.send_message(message.chat.id,
                         'Great! Please list your exercises for the first day, separated by commas.\nExample: Squat, Bench Press, Deadlift',
                         reply_markup=types.ReplyKeyboardRemove())
        user_states[message.chat.id] = UserState.ASKING_EXERCISES
    else:
        bot.send_message(message.chat.id, 'Please select a valid number of days from the keyboard.')


def handle_asking_exercises(message):
    day_number = len(gym_progress[message.chat.id]['exercises']) + 1
    exercises = [exercise.strip() for exercise in message.text.split(',')]
    gym_progress[message.chat.id]['exercises'][day_number] = {'exercises': {exercise: [] for exercise in exercises}}
    current_exercise_info[message.chat.id] = {'day': day_number, 'exercise_index': 0}
    exercise_list = ', '.join(exercises)
    bot.send_message(message.chat.id, f'You have listed the following exercises for day {day_number}: {exercise_list}')
    user_states[message.chat.id] = UserState.ASKING_SETS_REPS
    ask_for_sets_reps(message, exercises[0], day_number)


def handle_asking_sets_reps(message):
    user_info = current_exercise_info[message.chat.id]
    day_number = user_info['day']
    current_exercise = list(gym_progress[message.chat.id]['exercises'][day_number]['exercises'].keys())[
        user_info['exercise_index']]

    try:
        sets, reps = map(int, message.text.split('x'))
        gym_progress[message.chat.id]['exercises'][day_number]['exercises'][current_exercise] = [
            {'reps': reps, 'weight': None} for _ in range(sets)]
        user_states[message.chat.id] = UserState.ASKING_WEIGHTS
        ask_for_weights(message, current_exercise, 1, sets)
    except ValueError:
        bot.send_message(message.chat.id, 'Please enter the sets and reps in the correct format. Example: 3x12')


def handle_asking_weights(message):
    user_info = current_exercise_info[message.chat.id]
    day_number = user_info['day']
    current_exercise = list(gym_progress[message.chat.id]['exercises'][day_number]['exercises'].keys())[
        user_info['exercise_index']]
    sets = len(gym_progress[message.chat.id]['exercises'][day_number]['exercises'][current_exercise])

    try:
        weight = int(message.text)
        for set_info in gym_progress[message.chat.id]['exercises'][day_number]['exercises'][current_exercise]:
            if set_info['weight'] is None:
                set_info['weight'] = weight
                break

        remaining_sets = any(set_info['weight'] is None for set_info in
                             gym_progress[message.chat.id]['exercises'][day_number]['exercises'][current_exercise])
        if remaining_sets:
            set_number = sets - sum(set_info['weight'] is not None for set_info in
                                    gym_progress[message.chat.id]['exercises'][day_number]['exercises'][
                                        current_exercise])
            ask_for_weights(message, current_exercise, set_number, sets)
        else:
            next_exercise_index = user_info['exercise_index'] + 1
            if next_exercise_index < len(gym_progress[message.chat.id]['exercises'][day_number]['exercises']):
                user_info['exercise_index'] = next_exercise_index
                next_exercise = list(gym_progress[message.chat.id]['exercises'][day_number]['exercises'].keys())[
                    next_exercise_index]
                ask_for_sets_reps(message, next_exercise, day_number)
                user_states[message.chat.id] = UserState.ASKING_SETS_REPS
            else:
                if day_number < int(gym_progress[message.chat.id]['days_per_week'].split()[0]):
                    bot.send_message(message.chat.id,
                                     f'Please list your exercises for day {day_number + 1}, separated by commas.\nExample: Squat, Bench Press, Deadlift')
                    user_states[message.chat.id] = UserState.ASKING_EXERCISES
                else:
                    show_progress(message)
                    ask_restart_or_add_days(message)
    except ValueError:
        bot.send_message(message.chat.id, 'Please enter a valid weight.')


def handle_restart_day_selection(message):
    if message.text.startswith('Day'):
        try:
            day_number = int(message.text.split()[1])
            if day_number in gym_progress[message.chat.id]['exercises']:
                bot.send_message(message.chat.id,
                                 f'Please list your exercises for day {day_number}, separated by commas.\nExample: Squat, Bench Press, Deadlift',
                                 reply_markup=types.ReplyKeyboardRemove())
                gym_progress[message.chat.id]['exercises'].pop(day_number)  # Remove old data for this day
                user_states[message.chat.id] = UserState.ASKING_EXERCISES
            else:
                bot.send_message(message.chat.id, 'Please select a valid day.')
        except:
            bot.send_message(message.chat.id, 'Please select a valid day.')
    elif message.text.lower() == 'view progress':
        show_progress(message)
        ask_restart_or_add_days(message)
    else:
        bot.send_message(message.chat.id, 'Please choose a valid option.')


def handle_viewing_progress(message):
    if message.text.lower() == 'view progress':
        show_progress(message)
        ask_restart_or_add_days(message)


def handle_add_more_days(message):
    if message.text.lower() == 'add more days':
        ask_days_per_week(message)
    elif message.text.lower() == 'start over':
        start(message)
    else:
        bot.send_message(message.chat.id, 'Please choose a valid option.')


def ask_days_per_week(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('1 day', '2 days', '3 days', '4 days', '5 days', '6 days', '7 days')
    bot.send_message(message.chat.id, 'Hi there! How many days are you training per week?', reply_markup=markup)
    user_states[message.chat.id] = UserState.ASKING_DAYS


def ask_for_sets_reps(message, exercise, day):
    bot.send_message(message.chat.id,
                     f'How many sets and reps do you perform for {exercise} on day {day}? Please enter in the format setsxreps. Example: 3x12')


def ask_for_weights(message, exercise, set_number, total_sets):
    bot.send_message(message.chat.id,
                     f'Enter the weight for {exercise}, set {set_number} of {total_sets}. Example: 100')


def show_progress(message):
    bot.send_message(message.chat.id, 'Here is your gym progress:')
    for day, details in gym_progress[message.chat.id]['exercises'].items():
        bot.send_message(message.chat.id, f'Day {day}:')
        for exercise, sets in details['exercises'].items():
            bot.send_message(message.chat.id, f'{exercise}:')
            for set_number, set_info in enumerate(sets, 1):
                bot.send_message(message.chat.id,
                                 f'Set {set_number}: {set_info["reps"]} reps - {set_info["weight"]} kg')


def ask_restart_or_add_days(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Yes', 'No')
    bot.send_message(message.chat.id, 'Would you like to set exercises for any day again?', reply_markup=markup)
    user_states[message.chat.id] = UserState.RESTART_DAY_SELECTION


def handle_restart_day_selection(message):
    if message.text.lower() == 'yes':
        days = list(gym_progress[message.chat.id]['exercises'].keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for day in days:
            markup.add(f'Day {day}')
        bot.send_message(message.chat.id, 'Which day would you like to set again?', reply_markup=markup)
    elif message.text.lower() == 'no':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Add More Days', 'Start Over', 'View Progress')
        bot.send_message(message.chat.id, 'Would you like to add more days, start over, or view progress?',
                         reply_markup=markup)
        user_states[message.chat.id] = UserState.ADD_MORE_DAYS
    else:
        bot.send_message(message.chat.id, 'Please choose "Yes" or "No".')


def reset_user_data(chat_id):
    if chat_id in gym_progress:
        del gym_progress[chat_id]
    if chat_id in user_states:
        del user_states[chat_id]
    if chat_id in current_exercise_info:
        del current_exercise_info[chat_id]


# Start the bot
bot.polling()
