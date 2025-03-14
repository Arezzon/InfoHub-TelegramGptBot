import telebot
import json
from telebot import types
from parser import check_news_update
import subprocess
import os
import sys

class TelegramNewsBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token, parse_mode='HTML')
        self.register_handlers()

    def run(self):
        self.bot.polling(none_stop=True)

    def generate_news_message(self, news_data):
        return (f"<u>{news_data['thumb_date']}</u>\n\n"
                f"<b>{news_data['thumb_title']}</b>\n\n"
                f"{news_data['thumb_url']}")

    def get_all_news(self, message):
        with open("news.json", "r") as file:
            news_dict = json.load(file)
        for k, v in sorted(news_dict.items()):
            self.send_news(message, v)

    def get_last_five_news(self, message):
        with open("news.json", "r") as file:
            news_dict = json.load(file)
        for k, v in sorted(news_dict.items())[-5:]:
            self.send_news(message, v)

    def get_fresh_news(self, message):
        fresh_news = check_news_update()
        if fresh_news:
            for k, v in sorted(fresh_news.items()):
                self.send_news(message, v)
        else:
            self.bot.send_message(message.chat.id, "Оновлення на сайті відсутні ...")

    def send_news(self, message, news_data):
        news = self.generate_news_message(news_data)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Зробити підсумки (ChatGPT)", callback_data="edit"))
        self.bot.send_message(message.chat.id, news, reply_markup=markup)

    def truncate_text(text, limit=4096):
        """Обрізає текст до допустимого ліміту"""
        return text[:limit] + '...' if len(text) > limit else text

    def handle_button_click(self, call):
        text1 = call.message.text
        last_line = text1.split('\n')[-1]
        print(last_line)

        new_text = text1 + '\n' + '================================' + '\n' + 'Триває обробка!'
        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text)

        # Отримуємо поточний шлях до директорії, де знаходиться скрипт
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "oop_summary.py")

        # Використовуємо sys.executable, щоб запускати скрипт у правильному середовищі
        process = subprocess.Popen([sys.executable, script_path, last_line], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, _ = process.communicate()

        new_text2 = text1 + '\n' + '================================' + '\n' + stdout.decode('cp1251')

        if len(new_text2) > 4096:
            new_text2 = self.truncate_text(new_text2)

        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   text=new_text2[:-3])

    def register_handlers(self):
        self.bot.message_handler(commands=['start'])(self.start)
        self.bot.message_handler(commands=['all_news'])(self.get_all_news)
        self.bot.message_handler(commands=['last_five'])(self.get_last_five_news)
        self.bot.message_handler(commands=['fresh_news'])(self.get_fresh_news)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('edit'))(self.handle_button_click)

    def start(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton('Всі новини'))
        markup.row(types.KeyboardButton('Останні 5 новин'), types.KeyboardButton('Оновити новини'))
        self.bot.send_message(message.chat.id, f'Привіт, {message.from_user.first_name}', reply_markup=markup)
        self.bot.register_next_step_handler(message, self.on_click)

    def on_click(self, message):
        if message.text == 'Всі новини':
            self.get_all_news(message)
        elif message.text == 'Останні 5 новин':
            self.get_last_five_news(message)
        elif message.text == 'Оновити новини':
            self.get_fresh_news(message)
        self.bot.register_next_step_handler(message, self.on_click)

if __name__ == '__main__':
    TOKEN = 'TOKEN'
    news_bot = TelegramNewsBot(TOKEN)
    news_bot.run()
