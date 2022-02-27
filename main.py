from handlers import bot  # Как должные происходить импорты?
# по цепочке или из каждого модуля на прямую, из loader в handlers или наоборот?

if __name__ == '__main__':  # Что тут должно быть кроме старта?
    bot.infinity_polling()

