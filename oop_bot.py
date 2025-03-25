import multiprocessing
import telebot
import json
import tkinter as tk
from tkinter import scrolledtext
from telebot import types
import os
import threading
import re
import trafilatura
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from g4f.client import Client
from multiprocessing import Pool
import datetime

from parser import check_news_update, get_first_news


class TextSummarizer:
    def __init__(self):
        self.client = Client()
        self.model = os.environ.get("LLM_MODEL", "gemini-1.5-flash")
        self.lang = os.environ.get("TS_LANG", "Ukrainian")
        self.chunk_size = int(os.environ.get("CHUNK_SIZE", 10000))

    def split_user_input(self, text):
        paragraphs = text.split('\n')
        return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]

    def scrape_text_from_url(self, url):
        try:
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded, include_formatting=True)
            return [text.strip() for text in text.split("\n") if text.strip()] if text else []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def create_chunks(self, paragraphs):
        chunks, chunk = [], ''
        for paragraph in paragraphs:
            if len(chunk) + len(paragraph) < self.chunk_size:
                chunk += paragraph + ' '
            else:
                chunks.append(chunk.strip())
                chunk = paragraph + ' '
        if chunk:
            chunks.append(chunk.strip())
        return chunks

    def call_gpt_api(self, prompt, additional_messages=[]):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=additional_messages + [{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error: {e}")
            return ""

    def summarize(self, text_array):
        text_chunks = self.create_chunks(text_array)
        summaries = []
        system_messages = [
            {"role": "system",
             "content": "You are an expert in creating summaries that capture the main points and key details in 300 characters."},
            {"role": "system",
             "content": f"You will show the bulleted list content without translating any technical terms."},
            {"role": "system", "content": f"You will print all the content in {self.lang}."},
        ]
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.call_gpt_api, f"Summary keypoints for the following text:\n{chunk}",
                                       system_messages) for chunk in text_chunks]
            for future in tqdm(futures, total=len(text_chunks), desc="Summarizing"):
                summaries.append(future.result())
        return ' '.join(summaries) if len(summaries) <= 5 else self.summarize(summaries)

    def process_user_input(self, user_input):
        url_pattern = re.compile(r"https?://")
        return self.scrape_text_from_url(user_input) if url_pattern.match(user_input) else self.split_user_input(
            user_input)


def summarize_article(arg):
    try:
        summarizer = TextSummarizer()
        text_array = summarizer.process_user_input(arg)
        if not text_array:
            return "Error: Unable to process the input."
        summary = summarizer.summarize(text_array)
        return summary
    except Exception as e:
        return f"Error during summarization: {str(e)}"


class TelegramNewsBot:
    def __init__(self, token, log_callback=None):
        self.bot = telebot.TeleBot(token, parse_mode='HTML')
        self.log_callback = log_callback
        self.running = False
        self.register_handlers()

    def log(self, message):
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        timestamped_message = f"[{current_time}] {message}"
        if self.log_callback:
            self.log_callback(timestamped_message)

    def run(self):
        self.running = True
        if not os.path.exists("news.json"):
            self.log("Файл news.json не знайдено. Створення початкового файлу...")
            get_first_news()
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
        return text[:limit] + '...' if len(text) > limit else text

    def handle_button_click(self, call):
        text1 = call.message.text
        last_line = text1.split('\n')[-1]
        self.log(f"Обробка: {last_line}")

        new_text = text1 + '\n================================\nТриває обробка!'
        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text)

        with Pool(1) as pool:
            summary = pool.apply(summarize_article, (last_line,))

        new_text2 = text1 + '\n================================\n' + summary
        if len(new_text2) > 4096:
            new_text2 = self.truncate_text(new_text2)

        self.bot.edit_message_text(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id,
                                   text=new_text2[:-3] if new_text2.endswith('...') else new_text2)
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
        self.root.configure(bg="#18222d")  # Telegram dark theme background
        self.root.padx = 10
        self.root.pady = 10
        self.bot_instance = None
        self.bot_thread = None

        # Configure custom fonts
        self.title_font = ("Segoe UI", 12, "bold")
        self.base_font = ("Segoe UI", 10)
        self.button_font = ("Segoe UI", 10, "bold")
        self.console_font = ("Consolas", 9)

        # Telegram color scheme
        self.colors = {
            "bg": "#18222d",
            "fg": "#ffffff",
            "secondary_bg": "#2a3b4d",
            "accent": "#0088cc",
            "text_entry_bg": "#2a3b4d",
            "console_bg": "#1a2634",
            "console_fg": "#c5cbd4"
        }

        # Token input section
        self.token_frame = tk.Frame(root, bg=self.colors["bg"])
        self.token_frame.pack(pady=10, fill=tk.X, padx=20)  # Add horizontal padding

        self.token_label = tk.Label(self.token_frame,
                                    text="Введіть токен:",
                                    font=self.base_font,
                                    bg=self.colors["bg"],
                                    fg=self.colors["fg"])
        self.token_label.pack(side=tk.LEFT, padx=(0, 10))

        self.token_entry = tk.Entry(self.token_frame,
                                    width=40,  # Fixed character width
                                    font=self.base_font,
                                    bg=self.colors["text_entry_bg"],
                                    fg=self.colors["fg"],
                                    insertbackground=self.colors["fg"],
                                    relief=tk.FLAT)
        self.token_entry.pack(side=tk.LEFT)

        self.accept_button = tk.Button(self.token_frame,
                                       text="Прийняти",
                                       font=self.button_font,
                                       bg=self.colors["accent"],
                                       fg=self.colors["fg"],
                                       activebackground="#006699",
                                       activeforeground=self.colors["fg"],
                                       relief=tk.FLAT,
                                       command=self.set_token)
        self.accept_button.pack(side=tk.LEFT, padx=(10, 0))

        # Log console
        self.log_console = scrolledtext.ScrolledText(root,
                                                     width=60,
                                                     height=20,
                                                     font=self.console_font,
                                                     bg=self.colors["console_bg"],
                                                     fg=self.colors["console_fg"],
                                                     insertbackground=self.colors["console_fg"],
                                                     relief=tk.FLAT)
        self.log_console.pack(pady=10, fill=tk.BOTH, expand=True)

        # Control buttons
        self.control_frame = tk.Frame(root, bg=self.colors["bg"])
        self.control_frame.pack(pady=10)

        self.start_button = tk.Button(self.control_frame,
                                      text="Старт",
                                      font=self.button_font,
                                      bg=self.colors["accent"],
                                      fg=self.colors["fg"],
                                      activebackground="#006699",
                                      activeforeground=self.colors["fg"],
                                      relief=tk.FLAT,
                                      command=self.toggle_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Configure button hover effects
        self.setup_hover_effects()
        self.set_min_size()

    def setup_hover_effects(self):
        # Add hover effects for buttons
        def on_enter(e):
            e.widget.config(bg="#006699" if e.widget == self.start_button else self.colors["accent"])

        def on_leave(e):
            e.widget.config(bg=self.colors["accent"])

        for btn in [self.accept_button, self.start_button]:
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def set_min_size(self):
        min_width = 500
        min_height = (self.token_label.winfo_reqheight() +
                      self.token_entry.winfo_reqheight() +
                      self.accept_button.winfo_reqheight() +
                      self.log_console.winfo_reqheight() +
                      self.start_button.winfo_reqheight() +
                      6 * self.root.pady)
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
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()