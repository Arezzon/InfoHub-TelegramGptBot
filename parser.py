import requests
from bs4 import BeautifulSoup
import json

def get_first_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    url = "https://www.unian.ua/techno"

    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")
    list_thumb_items = soup.find_all("div", class_="list-thumbs__item")

    news_dict = {}

    for thumb__item in list_thumb_items:
        thumb_title = thumb__item.find("a", class_="list-thumbs__title").text.strip()
        thumb_url = thumb__item.find("a").get("href")
        thumb_date = thumb__item.find("div", class_="list-thumbs__time time").text.strip()

        thumb_id = thumb_url.split("-")[-1]
        thumb_id = thumb_id[:-5]

        news_dict[thumb_id] = {
            "thumb_date": thumb_date,
            "thumb_title": thumb_title,
            "thumb_url": thumb_url
        }

    # Trim news_dict to keep only the latest 50 news
    news_dict = dict(sorted(news_dict.items(), key=lambda x: x[1]['thumb_date'], reverse=True)[:50])

    with open("news.json", "w") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)

def check_news_update():
    with open("news.json") as file:
        news_dict = json.load(file)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    url = "https://www.unian.ua/techno"

    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")
    list_thumb_items = soup.find_all("div", class_="list-thumbs__item")

    fresh_news = {}

    for thumb__item in list_thumb_items:
        thumb_url = thumb__item.find("a").get("href")
        thumb_id = thumb_url.split("-")[-1]
        thumb_id = thumb_id[:-5]

        if thumb_id in news_dict:
            continue
        else:
            thumb_title = thumb__item.find("a", class_="list-thumbs__title").text.strip()
            thumb_date = thumb__item.find("div", class_="list-thumbs__time time").text.strip()

            news_dict[thumb_id] = {
                "thumb_date": thumb_date,
                "thumb_title": thumb_title,
                "thumb_url": thumb_url
            }

            fresh_news[thumb_id] = {
                "thumb_date": thumb_date,
                "thumb_title": thumb_title,
                "thumb_url": thumb_url
            }

    # Trim news_dict to keep only the latest 15 news
    news_dict = dict(sorted(news_dict.items(), key=lambda x: x[1]['thumb_date'], reverse=True)[:20])

    with open("news.json", "w") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)

    return fresh_news

def main():
    get_first_news()
    print(check_news_update())

if __name__ == "__main__":
    main()