## InfoHub-TelegramGptBot
![News Image](https://iat.kpi.ua/wp-content/uploads/2019/10/news-3.jpg)
## Overview
InfoHub-TelegramGptBot is an AI-powered chatbot that provides concise and clear summaries of news from various sources. It helps users stay informed efficiently by retrieving information from reliable websites on the Telegram platform. The target audience includes users who want quick and accurate news updates.

## User Manual

### 1. Introduction
InfoHub-TelegramGptBot is designed to assist users in obtaining summarized news efficiently. The program is particularly useful for those who want automated news retrieval and analysis.

### 2. Installation and Launch

#### 2.1 Software Installation
1. Download and install Python: [Python Installer](https://www.python.org/downloads/)
2. Verify Python installation: [Video Tutorial](https://www.youtube.com/watch?v=fJKdIf11GcI)
3. Install required libraries:
   ```sh
   pip install trafilatura tqdm g4f telebot json subprocess beautifulsoup4 lxml
   ```

#### 2.2 Running the Program
1. Create a project directory.
2. Inside the directory, create three `.py` files:
   - **File_1:** Bot initialization script, AI processing script
   - **parser.py:** News parser
3. Copy the required code from section 4.2 into these files.
4. Install Telegram and visit [BotFather](https://t.me/BotFather).
5. Create a new bot with `/newbot` and copy the token.
6. Run `parser.py`:
   ```sh
   python parser.py
   ```
7. Run **File_1**:
   ```sh
   python File_1.py
   ```
8. Open the Telegram bot and start using it.

### 3. Main Functions

#### 3.1 Features
- **"All news"** - Displays all news stored in `news.json`.
- **"Last 5 news"** - Displays the latest five news entries.
- **"Update news"** - Fetches new news updates not recorded in `news.json`.
- **"Summarize (ChatGPT)"** - Uses AI to generate concise summaries.

#### 3.2 Usage Instructions
To use a function, click the corresponding button in the Telegram chat.

#### 3.3 How It Works
1. The bot provides four commands: `/start`, "All news", "Last 5 news", "Refresh news", and one AI-powered function "Summarize (ChatGPT)."
2. News parsing is done via `beautifulsoup4` and `lxml`, extracting HTML elements and forwarding them to **File_1**.
3. The **"Summarize (ChatGPT)"** function:
   - Extracts text using `trafilatura`.
   - Splits text into chunks to comply with API limits.
   - Sends API requests via `g4f`.
   - Summarized results are passed back to **File_1** for display.

### 4. Settings

#### 4.1 Customizable Parameters
- Output language for summaries
- Chunk size for AI processing
- AI model selection
- News category (tag)

#### 4.2 Modifying Settings
- Open **File_1** and update:
  ```python
    self.model = os.environ.get("LLM_MODEL", "gemini-1.5-flash")
    self.lang = os.environ.get("TS_LANG", "Ukrainian")
    self.chunk_size = int(os.environ.get("CHUNK_SIZE", 10000))
  ```
- To change the news tag, edit **parser.py**:
  ```python
  url = 'https://www.unian.ua/techno'  # Example: Change to politics
  ```

## Instructions for Telegram Users
1. Open Telegram.
2. Search for `@infohub_newsbot`.
3. Type `/start`.
4. Use the bot functions as described in sections 3.1 and 3.2.

## Instructions for Telegram Channel Owners & News Sites
To avoid legal issues, use the `openai` library instead of `g4f`:
1. Follow installation steps up to **2.2 Step 7**.
2. Open **File_1**.
3. Install `openai`:
   ```sh
   pip install openai
   ```
4. Modify **File_1**:
   ```python
   from openai import OpenAI
   OPENAI_API_KEY = '<your_api_key>'
   client = OpenAI(api_key=OPENAI_API_KEY)
   ```
5. Continue with step **2.2 Step 8**.

---
This structured README provides clear instructions for installation, usage, and customization of InfoHub-TelegramGptBot.**
