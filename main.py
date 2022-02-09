import telebot
from telebot import types

token = "5174156677:AAEn5Y6gN5EKHjoqZton8pdM7XEgx5Y4YAo"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['hello-world'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет ✌️ ")


@bot.message_handler(func=lambda message: message.text == 'Привет')
def button_message(message):
    bot.send_message(message.chat.id, 'Hi!')


bot.polling(none_stop=True, interval=0)
