import telebot
from telebot import types

# Bot's API Token
bot = telebot.TeleBot('1707868667:AAHC17XDgOBdIUQwAGJr_Q-ha9NcOhJHWbM')
post = ''
author = ''
admin_id = ''
admin_checker = False
password = '421'


# -- Commands handler --
@bot.message_handler(commands=['start', 'admin'])
def get_command_messages(message):
	# Start
	if message.text == "/start":
		bot.send_message(message.chat.id, '''
Привет! Хочешь написать пост?''', reply_markup=keyboard_menu())
	if message.text == "/admin":
		global admin_checker
		bot.send_message(message.from_user.id, "Введите пароль 🔐")
		admin_checker = True


# -- Messages Handler --
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	global post
	global author
	global admin_checker
	global admin_id
	# Some text
	if message.text == password and admin_checker:
		bot.send_message(message.chat.id, "Новый id админа успешно установлен! 🔓")
		admin_id = message.from_user.id
		admin_checker = False
		print("Новый админ:", message.from_user.id)
	elif message.text != password and admin_checker:
		bot.send_message(message.chat.id, "Пароль неверный! 🔒")
		admin_checker = False
		print("Зафиксирована попытка входа в админку, от пользователя:", message.from_user.username, message.from_user.id)
	else:
		bot.forward_message(message.chat.id, message.chat.id, message.message_id)
		bot.send_message(message.chat.id, "Отправить?", reply_markup=keyboard_create())
		post = message.text
		author = message.chat.username


# -- Content Handler --
@bot.message_handler(content_types=['photo', 'video', 'audio'])
def get_photo_messages(message):
	global admin_id
	try:
		bot.forward_message(admin_id, message.chat.id, message.message_id)
		bot.send_message(admin_id, str("*Файл прислал: *" + message.from_user.username), parse_mode="Markdown")
		bot.send_message(message.from_user.id, "Файл успешно отправлен!")
	except:
		bot.send_message(message.chat.id, 'К сожалению сейчас нет админа!')


# -- Callback --
@bot.callback_query_handler(func=lambda call: True)
def get_callback(call):
	global post
	global author
	if call.data == "new_post":
		bot.send_message(call.message.chat.id, 'Отправьте пост после этого сообщения ⏬')
	if call.data == "info":
		bot.send_message(call.message.chat.id, '''
Вы можете написать боту что угодно после чего он предложит отправить это на проверку админу, расценивая это как пост. \n
Если Вы хотите разместить картинку, аудио или видео файл, просто отправьте его после поста.\n
Если Вы хотите оставить ссылку на файл - напишите ее вместе с постом.\n

**Текст** – комбинация делает шрифт жирным.\n
__Текст__ – комбинация наклоняет шрифт.''')
	if call.data == "send_post":
		try:
			get_new_post(post, author)
			bot.send_message(call.message.chat.id, 'Ваш пост успешно отправлен и будет опубликован после проверки! ✅')
		except:
			bot.send_message(call.message.chat.id, 'К сожалению сейчас нет админа!')
	if call.data == "send_img":
		bot.send_message(call.message.chat.id, 'Пришлите файл. 📄\nМожно прикрепить только 1 файл')
	if call.data == "cancel_post":
		post = ''
		author = ''
		bot.send_message(call.message.chat.id, 'Пост успешно удален!')


# -- Sending Post --
def get_new_post(text, user):
	global admin_id
	bot.send_message(admin_id, f"*Новый пост:*\n{text} \n*Автор:* {user}", parse_mode="Markdown")


# -- Keyboards --
def keyboard_menu():
	markup = types.InlineKeyboardMarkup()
	button_nav = types.InlineKeyboardButton("Написать пост 📝", callback_data='new_post')
	button_check = types.InlineKeyboardButton("Подробнее 🔍", callback_data='info')
	markup.add(button_nav, button_check)
	return markup


def keyboard_create():
	markup = types.InlineKeyboardMarkup()
	button_done = types.InlineKeyboardButton("Отправить ✉", callback_data='send_post')
	button_img = types.InlineKeyboardButton("Прикрепить файл 📎", callback_data='send_img')
	button_cancel = types.InlineKeyboardButton("Отмена 🚫", callback_data='cancel_post')
	markup.add(button_done, button_img)
	markup.add(button_cancel)
	return markup


# -- Polling --
bot.polling(none_stop=False, interval=0, timeout=20)