import argparse
import json
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


def scroll_page(driver, max_time=40):
    # Автоматическая прокрутка страницы
    scroll_pause_time = 1
    start_time = time.time()
    while (time.time() - start_time) < max_time:  # Прокручиваем в течение 5 минут
        # Прокрутка вниз
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(scroll_pause_time)


def parse_page(driver, hyper_param, hyper_param_name="ticker"):
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    items = soup.find_all("li", class_="js-stream-content Pos(r)")

    data = []
    for item in items:
        source_span = item.find("div", class_="C(#959595)")
        source_name = source_span.find("span") if source_span else None
        source_name = source_name.get_text() if source_name else None

        news_link = (
            item.find("a", class_="js-content-viewer")
            if item.find("a", class_="js-content-viewer")
            else None
        )

        if source_name and news_link:
            link = news_link.get("href")
            title = news_link.text
            data.append(
                {
                    "source_name": source_name,
                    hyper_param_name: hyper_param,
                    "title": title,
                    "link": f"https://finance.yahoo.com{link}",
                }
            )

    return data


def process_url(url, hyper_param, driver, hyper_param_name="ticker", max_time=40):
    # Открываем веб-сайт
    driver.get(url)
    # Прокручиваем страницу
    scroll_page(driver, max_time=max_time)
    # Парсим страницу
    data = parse_page(
        driver, hyper_param=hyper_param, hyper_param_name=hyper_param_name
    )

    return data


# python3 parse_news_links.py yahoo_categories.txt -t 60 -s yahoo_categories.json -hp category
def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="Web scraping script")
    parser.add_argument("file_path", type=str, help="Path to the file with URLs")
    parser.add_argument(
        "-t",
        "--max_time",
        type=int,
        default=40,
        help="Maximum time for scrolling (default: 40 seconds)",
    )
    parser.add_argument(
        "-hp",
        "--hyper_param",
        type=str,
        default="ticker",
        help="First parameter in urls file (default: ticker, maybe category or sth else)",
    )
    parser.add_argument(
        "-s",
        "--save_file_path",
        type=str,
        default="data.json",
        help="Path to save the output JSON file (default: data.json)",
    )
    args = parser.parse_args()

    # with open('test/selenium/yahoo_urls.txt', 'r') as f:
    with open(args.file_path, "r") as f:
        urls = [url.split() for url in f.readlines()]

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # Список для хранения данных
    all_data = []

    for hyper_param, url in urls:
        data = process_url(
            url,
            hyper_param,
            driver,
            hyper_param_name=args.hyper_param,
            max_time=args.max_time,
        )
        all_data.extend(data)

    # Записываем все данные в JSON файл
    # with open('data.json', "w", encoding="utf-8") as file:
    with open(args.save_file_path, "w", encoding="utf-8") as file:
        json.dump(all_data, file, ensure_ascii=False, indent=4)

    # Завершаем работу браузера
    driver.quit()


if __name__ == "__main__":
    main()
