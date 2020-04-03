import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def get_categoty_pages_number(category_url):
    response = requests.get(category_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    if soup.select('p.center a.npage'):
        return int(soup.select('p.center a.npage')[-1].text)
    return 1


def get_ids_from_category_page(page_url):
    ids_for_page = []
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    a = soup.select('table.d_book div.bookimage a')
    for id in a:
        ids_for_page.append(id.get('href').replace('/', ''))
    return ids_for_page


def get_ids_for_category(category_url, start_page, end_page):
    ids_for_category = []
    for category_page_number in range(start_page-1, end_page):
        category_page_url = urljoin(category_url, str(category_page_number+1))
        ids_for_category.extend(get_ids_from_category_page(category_page_url))
    return(ids_for_category)
