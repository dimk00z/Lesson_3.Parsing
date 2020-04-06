import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def get_categoty_pages_number(category_url):
    response = requests.get(category_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    max_page_number = soup.select('p.center a.npage')
    category_pages_number = int(
        max_page_number[-1].text) if max_page_number else 1
    return category_pages_number


def get_ids_from_category_page(page_url):
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    books_links = soup.select('table.d_book div.bookimage a')
    return [book_link.get('href').replace('/', '') for book_link in books_links]


def get_ids_for_category(category_url, start_page, end_page):
    ids_for_category = []
    for category_page_number in range(start_page, end_page+1):
        category_page_url = urljoin(category_url, str(category_page_number))
        ids_for_category.extend(get_ids_from_category_page(category_page_url))
    return(ids_for_category)
