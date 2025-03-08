import telebot
import json
import tkinter as tk
from tkinter import scrolledtext
from telebot import types
import subprocess
import os
import sys
import threading
from parser import check_news_update, get_first_news # додаємо імпорт get_first_news

class TelegramNewsBot:
    def __init__(self, token, log_callback=None):
        self.bot = telebot.TeleBot(token, parse_mode='HTML')
        self.log_callback = log_callback
        self.running = False
        self.register_handlers()

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def run(self):
        self.running = True

        # Перевірка наявності news.json і створення, якщо його немає
        if not os.path.exists("news.json"):  # Імпортуйте os на початку файлу: import os
            self.log("Файл news.json не знайдено. Створення початкового файлу...")
            get_first_news()  # Викликаємо функцію для створення news.json
            self.log("Файл news.json успішно створено.")
        else:
            self.log("Файл news.json знайдено.")

        self.log("Бот запущено!")
        self.bot.polling(none_stop=True)

    def stop(self):
        self.running = False
        self.log("Бот зупинено!")
        self.bot.stop_polling()

    def generate_news_message(self, news_data):
        return (f"<u>{news_data['thumb_date']}</u>\n\n"
                f"<b>{news_data['thumb_title']}</b>\n\n"
                f"{news_data['thumb_url']}")

    def get_all_news(self, message):
        with open("news.json", "r", encoding="utf-8") as file:
            news_dict = json.load(file)
        for k, v in sorted(news_dict.items()):
            self.send_news(message, v)

    def get_last_five_news(self, message):
        with open("news.json", "r", encoding="utf-8") as file:
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

    def truncate_text(self, text, limit=4096):
        """Обрізає текст до допустимого ліміту"""
        return text[:limit] + '...' if len(text) > limit else text

    def handle_button_click(self, call):
        text1 = call.message.text
        last_line = text1.split('\n')[-1]
        print(last_line)
        self.log(f"\nОбробка: {last_line}")

        new_text = text1 + '\n' + '================================' + '\n' + 'Триває обробка!'
        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text)

        # Отримуємо поточний шлях до директорії, де знаходиться скрипт
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "oop_summary.py")

        # Використовуємо sys.executable, щоб запускати скрипт у правильному середовищі
        process = subprocess.Popen([sys.executable, script_path, last_line], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, _ = process.communicate()

        new_text2 = text1 + '\n' + '================================' + '\n' + stdout.decode('cp1251')

        if len(new_text2) > 4096:
            new_text2 = self.truncate_text(new_text2)

        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   text=new_text2[:-3])

        self.log("Обробку завершено\n")

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

class BotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram News Bot")

        # Відступи для елементів
        self.root.padx = 10
        self.root.pady = 10

        self.bot_instance = None
        self.bot_thread = None

        self.token_label = tk.Label(root, text="Введіть токен:")
        self.token_label.pack(pady=(self.root.pady, 0))

        self.token_entry = tk.Entry(root, width=50)
        self.token_entry.pack(pady=(0, self.root.pady))

        self.accept_button = tk.Button(root, text="Прийняти", command=self.set_token)
        self.accept_button.pack(pady=(0, self.root.pady))

        # Змінено: додано fill=tk.BOTH, expand=True
        self.log_console = scrolledtext.ScrolledText(root, width=60, height=20)
        self.log_console.pack(pady=(0, self.root.pady), fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(root, text="Старт", command=self.toggle_bot)
        self.start_button.pack(pady=(0, self.root.pady))

        self.token = None

        # Встановлюємо мінімальні розміри вікна
        self.set_min_size()

    def set_min_size(self):
        # Отримуємо необхідні розміри віджетів
        min_width = 400
        min_height = (self.token_label.winfo_reqheight() +
                      self.token_entry.winfo_reqheight() +
                      self.accept_button.winfo_reqheight() +
                      self.log_console.winfo_reqheight() +
                      self.start_button.winfo_reqheight() +
                      6 * self.root.pady)

        # Встановлюємо мінімальні розміри вікна
        self.root.minsize(min_width, min_height)

    def log(self, message):
        self.log_console.insert(tk.END, message + '\n')
        self.log_console.yview(tk.END)

    def set_token(self):
        self.token = self.token_entry.get()
        self.log(f"Токен прийнято: {self.token}")

    def toggle_bot(self):
        if self.bot_instance and self.bot_instance.running:
            self.bot_instance.stop()
            self.bot_thread = None
            self.start_button.config(text="Старт")
        else:
            if not self.token:
                self.log("Помилка: введіть токен!")
                return

            self.bot_instance = TelegramNewsBot(self.token, log_callback=self.log)
            self.bot_thread = threading.Thread(target=self.bot_instance.run, daemon=True)
            self.bot_thread.start()
            self.start_button.config(text="Стоп")

if __name__ == '__main__':
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()