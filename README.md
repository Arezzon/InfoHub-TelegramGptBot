# InfoHub-TelegramGptBot
This is an AI-powered chatbot program that helps Internet users get short and clear summaries of news from various sources, saving time and finding information based on reliable websites on the Telegram platform. The app's target audience is users who are looking for a way to get up-to-date news efficiently


1.	Introduction
     1.2. Brief description of the program and its purpose. 
     This is an artificial intelligence-based chatbot program that helps Internet users to get short and clear summaries of news from various sources, saving time and finding information based on reliable websites on the Telegram platform. The app's target audience is users looking for a way to get up-to-date news efficiently.
     1.3. Clarification of the target audience for which the manual is intended. 
     The app manual is intended for developers who want to automate news search and analysis.

2.	Installation and launch
     2.1. Software installation instructions. 
     Download and install Python on your computer. Link to the python installer: https://www.python.org/downloads/. 
Check the performance of python. Link to the video tutorial: https://www.youtube.com/watch?v=fJKdIf11GcI
Install the necessary libraries to run the program:
pip install trafilatura tqdm g4f telebot json subprocess beautifulsoup4 lxml
     2.2. Steps to run the program after installation.
     Steps to run the program:
1. Create a directory for the project
2. In the created directory, create 3 files with the extension .py with the following names
   File_1. Any name for the bot's telegrams
   File_2. Any name for the file with artificial intelligence
   File_3. parser
3. Copy the code from section 4.2 and paste it into the required files.
4. Open File_1 and in the line 
process = subprocess.Popen(['Specify the path to python.exe', Specify the path to File_2', last_line], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, _ = process.communicate()
5. Install Telegram and go to https://t.me/BotFather.
6. Create a new bot using the /newbot command and copy the created bot token
7. Open File_1 and in the variable TOKEN = 'Paste your token here'
8. Run parser.py
9. Run File_1
10. Open your Telegram bot and use it

3.	Main functions
    3.1. Detailed description of the main functions of the program.
- "All news" - Displays all news from the news.json file in a chat with the user
- "Last 5 news" - Displays the last 5 news from the news.json file in a chat with the user
- "Update news" - Displays in the chat with the user the news that has not yet been recorded in the news.json file, the code is carried out using the check_news_update() function.
- "Summarize (ChatGPT)" - Changes the current message by adding summaries from the site using artificial intelligence.
    3.2. Step-by-step instructions on how to use each function.
     To use any function, you need to click on the corresponding button in the chat.
     3.3 Description of the program After launching the Telegram bot, the user will have access to 4 commands "/start", "All news", "Last 5 news", "Refresh news" and 1 function for all news "Summarize (ChatGPT)". News parsing is done using the beautifulsoup4 and lxml libraries, where information is searched for by HTML classes and passed directly to File_1, where the news is displayed in the chat. The "/start" command sends a welcome message to the user and provides access to the buttons. Each of the buttons works according to the same algorithm, only the news output changes. Unlike the other buttons, the "Summarize (ChatGPT)" button, when activated, sends a processing request to File_1, where it then calls File_2, which takes the link to the site from the bot message and goes to the site where the main text of the site is collected using the trafilatura library and divided into parts (chunks). The chunking is necessary because the ChatGPT api (or any other api with artificial intelligence) contains a query limit. After dividing the text into chunks, the code makes a call using the g4f library to the ChatGPT api with the model parameters specified in the code, and after the AI call, the text is summarized by chunks. Then, the result is transferred to File_1 using the subprocess library, where the current news is edited with the addition of the result from ChatGPT.

4.	Settings
     4.1 Overview of the available program settings.
     Among the program settings, you can change the language of the text summary output, the size of the chunk, the artificial intelligence model, and the news tag.
     4.2 Instructions on how to customize the app to suit your preferences.
     To change the parameters of the text summarization output language, chunk size, and artificial intelligence model, open File_2 and change the values of the model, chunk_size, and lang attributes in the constructor. To change the news tag, go to parser.py and change the url variable to the desired tag. For example: https://www.unian.ua/techno ➔ https://www.unian.ua/politics.



Instructions for Telegram bot users
1.	Open the Telegram application
2.	Enter @infohub_newsbot in the search
3.	Enter the command /start
4.	Use the functions of the bot. Description of the functions in the instructions for developers of bundles 3.1 and 3.2.

Instructions for owners of Telegram channels and news sites
 In order to avoid problems with rights, I recommend using the openai library for using artificial intelligence.
1. Repeat the steps from the instructions for developers up to point 2.2, step 7.
2. Open File_2.
3. Install the openai library.
4. Delete the line with the connection of the g4f library and type from openai import OpenAI.
5. Add the line OPEN_API_KEY = "Your api key from the OpenAI website".
6. In the client variable, change the value from Client() to OpenAI(api_key=OPEN_API_KEY).
7. Continue with the instructions for developers from point 2.2, step 8.
