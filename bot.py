import telebot
from main import CurrencyFind
from datetime import datetime
import pytz
import re

bot = telebot.TeleBot("6451864423:AAEe6Cu5nWVzoNLg8iDLLBVVE8tcVUOnQLE")

user_number = 0
data_for_bot = {}
dt = datetime.now().timestamp()

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

markup = telebot.types.InlineKeyboardMarkup(row_width=2)
itembtn1 = telebot.types.InlineKeyboardButton(text='USD', callback_data='USD')
itembtn2 = telebot.types.InlineKeyboardButton(text='EUR', callback_data='EUR')
itembtn3 = telebot.types.InlineKeyboardButton(text='Enter your', callback_data='user_currency')
markup.add(itembtn1, itembtn2, itembtn3)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "йо, вводить спочатку суму потім валюту і я все конвертну \n"
                                      "Якщо введеш щось не наше, тобі конвертну в гривню. \n"
                                      "Якшо введеш гривню, я тобі запропоную варіанти в що конвертнуть")


def save_convert(convert):
    s = CurrencyFind()
    s.save_convert_to_file(convert)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    currency = call.data
    s = CurrencyFind()


    if call.data == "user_currency":
        markup_user = telebot.types.InlineKeyboardMarkup(row_width=8)
        buttons = []

        for item in data_for_bot:
            currency = s.find_currency_by_code(item["currencyCodeA"])
            buttons.append(
                telebot.types.InlineKeyboardButton(text=f'{currency.upper()}', callback_data=f'{currency.upper()}'))

        markup_user.add(*buttons)
        bot.send_message(call.message.chat.id, "Вибери в що конвертувати:", reply_markup=markup_user)
    else:
        s = s.find_currency_by_name(currency.lower())
        for item in data_for_bot:
            if item["currencyCodeA"] == s and item["currencyCodeB"] != 840:
                print("a", item)
                bot.send_message(call.message.chat.id, f'{user_number} UAH в {currency}:\n'
                                                       f'{round(user_number / item["rateBuy"] if item["rateBuy"] != 0 else user_number / item["rateCross"])}')
                save_convert({dt: f"user: {call.message.chat.id} -> {user_number} uah to {currency}"})


@bot.message_handler(func=lambda message: True)
def action(message: telebot.types.Message):
    global user_number
    global data_for_bot

    c = CurrencyFind()
    data = c.show(message.text)
    data_for_bot = data
    user_summ = re.search(r"\d+", message.text)

    if user_summ:
        user_summ = int(user_summ.group(0))
        user_number = user_summ
        if data == "Number was received":
            bot.send_message(message.chat.id, "Вкінці треба ввести валюту")
        elif data == "no such currency":
            bot.send_message(message.chat.id, "Відсутня така валюта в базі, або її не існує")
        elif "uah" in message.text.lower():
            bot.send_message(message.chat.id, "Вибери в що конвертувати:", reply_markup=markup)
            # bot.register_next_step_handler(message, uah_to_smth, user_summ)
        elif "usd" in message.text.lower() or "eur" in message.text.lower():
            date = datetime.fromtimestamp(data[0]['date'], pytz.timezone('Europe/Kiev'))
            convert = f"На момент: {date} \n" \
                      f"Курс продажу: {round(data[0]['rateSell'] * user_summ, 2)}, \n" \
                      f"Курс купівлі: {round(data[0]['rateBuy'] * user_summ, 2)}"
            bot.send_message(message.chat.id, convert)
            save_convert({dt: f"user: {message.chat.id} -> {user_summ} {c.find_currency_by_code(data[0]['currencyCodeA'])} to uah"})
        else:
            date = datetime.fromtimestamp(data[0]['date'], pytz.timezone('Europe/Kiev'))
            bot.send_message(message.chat.id, f"На момент: {date} \n"
                                              f"Курс в гривні: {round(data[0]['rateCross'] * user_summ, 2)}")
            save_convert({dt: f"user: {message.chat.id} -> {user_summ} {c.find_currency_by_code(data[0]['currencyCodeA'])} to uah"})
    else:
        bot.send_message(message.chat.id, "Введіть суму, яку хочете конвертувати:")


while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=9999)
    except Exception as e:
        print(e)
