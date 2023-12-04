import datetime

from bs4 import BeautifulSoup


# TODO: Добавить обработку исключенйи
async def parse_is_next_page(html_text):
    try:
        soup = BeautifulSoup(html_text, "lxml")
        is_next_page = soup.find(
            "div", class_="sideDiv inlineblock text_align_lang_base_2"
        )
        return bool(is_next_page)
    except Exception:
        return False


def parse_news_links(html_text):
    result = []
    soup = BeautifulSoup(html_text, "lxml")
    left_coolumn = soup.find("section", id="leftColumn")
    articles = left_coolumn.find_all("article")

    for article in articles:
        try:
            if article.find("svg") or article.find("span", class_="sponsoredBadge"):
                continue

            link = article.find("a", class_="title")
            url = link["href"]
            title = link.text

            details = article.find("span", class_="articleDetails")
            name_span, time_span = details.find_all("span")
            source_name = name_span.text
            time = time_span.text.replace(
                "\xa0", " "
            )  # Формат " - Sep 03, 2017" или " - Jan 06, 2022"

            if time:
                # Создай datetime object
                datetime_object = parse_date(time)
            else:
                datetime_object = None

            result.append([source_name, title, datetime_object, url])

        except Exception:
            pass

    return result


def parse_date(time_span):
    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    # Разделяем строку времени на части
    _, month, day, year = time_span.split()

    # Преобразуем месяц в число
    month_number = months.get(month)

    day = day.rstrip(",")

    # Создаем объект datetime
    datetime_object = datetime.datetime(int(year), month_number, int(day))

    return datetime_object


def parse_news_content(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    body = soup.find("div", class_="articlePage")
    content = body.find_all(["p", "h2"], recursive=False)

    result_content = " ".join(tag.get_text(strip=True) for tag in content)
    return result_content
