import os
import re
import trafilatura
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from g4f.client import Client
import sys

class TextSummarizer:
    def __init__(self):
        self.client = Client()
        self.model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
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
            {"role": "system", "content": "You are an expert in creating summaries that capture the main points and key details in 3000 characters."},
            {"role": "system", "content": f"You will show the bulleted list content without translating any technical terms."},
            {"role": "system", "content": f"You will print all the content in {self.lang}."},
        ]
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.call_gpt_api, f"Summary keypoints for the following text:\n{chunk}", system_messages) for chunk in text_chunks]
            for future in tqdm(futures, total=len(text_chunks), desc="Summarizing"):
                summaries.append(future.result())
        return ' '.join(summaries) if len(summaries) <= 5 else self.summarize(summaries)

    def process_user_input(self, user_input):
        url_pattern = re.compile(r"https?://")
        return self.scrape_text_from_url(user_input) if url_pattern.match(user_input) else self.split_user_input(user_input)

def main():
    summarizer = TextSummarizer()
    argument = sys.argv[1]
    text_array = summarizer.process_user_input(argument)
    summary = summarizer.summarize(text_array) if text_array else "Error: Unable to process the input."
    print(summary)

if __name__ == '__main__':
    main()