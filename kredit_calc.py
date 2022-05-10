from typing import Tuple, List, Any

import telebot
from telebot import types

token = '5274041775:AAHaFTcRVCw0oSswXhqlHK2NftwA6hYiqgE'   #создаю бот
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, {0.first_name}! Введите сумму кредита'.format(message.from_user))
     #когда бот получает команду старт, то приветствует и спрашивает сумму кредита

@bot.message_handler(func=lambda m: True)
def reg_sum(message):
    global summ                    #то, что получил бот выше в качестве суммы, записываем в переменную глобальную
    summ = message.text            #проверяем введена ли сумма цифрами
    if summ.isdigit():
        bot.send_message(message.chat.id, "Введите проценты по кредиту")    #если цифрами переходим к след шагу
        bot.register_next_step_handler(message, reg_proc)
    else:
        bot.send_message(message.chat.id, "Введите сумму кредита цифрами!")    #если не цифры, то просим ввести заново
        start(message)


@bot.message_handler(func=lambda m: True)
def reg_proc(message):
    global proc                    #аналогично обрабатываем новое сообщение от человека
    proc = message.text
    if proc.isdigit():
        bot.send_message(message.chat.id, "Количество лет, на которое берете кредит?")
        bot.register_next_step_handler(message, reg_age)
    else:
        bot.send_message(message.chat.id, "Вводите цифрами! Попробуйте заново!")
        start(message)


@bot.message_handler(func=lambda m: True)
def reg_age(message):
    global age                      #и здесь тоже самое
    age = message.text
    if age.isdigit():                #если введены 3 сообщения цифрами, вызываем окошко с ответами да/нет
        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)        #дальше уточняем данные и спрашиваем верны ли они
        question = 'Сумма кредита ' + str(summ) + ' ? Проценты ' + str(proc) + '? Количество лет ' + str(age) + '?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Вводите цифрами! Попробуйте заново!")
        start(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes':      #если верны, то уточняем вид платежей (даем возможность выбрать с клавиатуры)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        key_dif = types.KeyboardButton('дифференциальный')
        key_ann = types.KeyboardButton('аннуитетный')
        keyboard.add(key_dif, key_ann)
        question = 'Выберите порядок платежей'
        bot.send_message(call.message.chat.id, text=question, reply_markup=keyboard)
        bot.register_next_step_handler(call.message, bot_message)
    elif call.data == 'no':
        bot.send_message(call.message.chat.id, "Попробуем еще раз!")
        bot.send_message(call.message.chat.id, "Введите сумму кредита")
        bot.register_next_step_handler(call.message, reg_sum)
    else:
        bot.send_message(call.message.chat.id, "Попробуем еще раз!")
        bot.send_message(call.message.chat.id, "Введите сумму кредита")
        bot.register_next_step_handler(call.message, reg_sum)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.text == 'дифференциальный':   #если выбран данный вид, то рассчитываем исходя из введенных цифр
        def diff_int(summ, proc, age):
            arr = []
            n = int(age) * 12          #количество месяцев
            rest = int(summ)           #сумма, которая будет уменьшаться
            telo = int(summ) / n       #тело кредита
            while n != 0:               #пока количество месяцев не будет равно ноль
                mp = telo + (rest * (float(int(proc) / 1200)*int(age)))    #месячный платеж
                arr.append(round(mp, 2))    #добавляем месячный платеж в переменную, чтобы потом все показать человеку
                rest = rest - telo          #уменьшаем сумму, с которой будет процент
                n = n - 1                   #уменьшаем количество месяцев
            return arr                       #фугкция возвращает список

        diff = diff_int(summ, proc, age)       #здесь передаем в функцию наши полученные значения от человека
        d=str(diff)                       #делаем список строкой, чтобы смогли отправить ее боту
        it=round(sum(diff),2)             #считаю сумму значений списка и округляю его до 2 цифр после запятой
        per=round(it-int(summ),2)         #считаю переплату по кредиту и округляю до 2 цифр после запятой
        bot.send_message(message.chat.id, "Платежи будут следующими" + d)    #отправляю человек
        bot.send_message(message.chat.id, "Всего будет выплачено " + str(it) + " переплата составит "+ str(per))
        bot.send_message(message.chat.id, "Введите сумму кредита", reply_markup=types.ReplyKeyboardRemove())
        start(message)
                                            #спрашиваю заново сумму кредиты и удаляю клавиатуру


    if message.text == 'аннуитетный':        #если выбран ответ аннуитетный, то делаем рассчет для него, выдаем и спрашиваем заново
        n = int(int(age) * 12)  # количество месяцев
        m= (int(summ)*float(int(proc)/100))*int(age) #сумма процентов
        total = int(summ)+m
        ak = total/n
        p=round(total-int(summ), 2)
        bot.send_message(message.chat.id, 'ежемесячный платеж равен ' + str(ak) + " \nвсего будет выплачено " +
                         str(total) + ' \nпереплата составит '+ str(p))
        bot.send_message(message.chat.id, "Введите сумму кредита", reply_markup=types.ReplyKeyboardRemove())
        start(message)

    if message.text!= 'дифференциальный' and message.text!='аннуитетный': #если ввели любой другой ответ по поводу вида платежей
        bot.send_message(message.chat.id, "Попробуем еще раз!", reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, "Введите сумму кредита")
        bot.register_next_step_handler(message, reg_sum)
        start(message)

bot.polling()   #постоянно "спрашиваем" у бота нет ли новых сообщений от пользователя
