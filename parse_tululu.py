import requests
import time
import re
import json
import argparse
from urllib.parse import urljoin
from random import randrange
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename

CONECTIONS_ATTEMPTS = 3


def tululu_response(url):
    headers = {"User-Agent": 'Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    for connection_attempt in range(CONECTIONS_ATTEMPTS):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if response.status_code not in [301, 302]:
                return response
            time.sleep(randrange(1, 3))
        except Exception:
            print(f"Cann't connect to {url}")


def get_category_pages_number(category_url):
    response = tululu_response(category_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    category_pages_number = soup.select('p.center a.npage')
    return int(category_pages_number[-1].text) if category_pages_number else 1


def get_book_ids(category_url, start_page, end_page):
    ids_for_category = []
    for category_page_number in range(start_page, end_page+1):
        category_page_url = urljoin(category_url, str(category_page_number))
        response = tululu_response(category_page_url)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        books_links = soup.select('table.d_book div.bookimage a')
    # .replace('/', '') испольщутся, чтобы от адреса абсолютного адреса вида /id/ отсечь слеши для получения "чистого" id
    # далее они используются в имени файлов и генерации пути
        ids_for_category.extend(
            [book_link.get('href').replace('/', '') for book_link in books_links])
    return ids_for_category


def download_txt(book_url, book_id, book_name,
                 directory_for_save):
    books_dir_path = Path.joinpath(directory_for_save, 'books')
    Path(books_dir_path).mkdir(parents=True, exist_ok=True)
    response = tululu_response(book_url)
    if response is None:
        return
    path_for_saving = Path.joinpath(
        books_dir_path, f'{book_id}.{book_name}.txt')
    with open(path_for_saving, 'wb') as file:
        file.write(response.content)
    return str(path_for_saving)


def download_image(image_url, book_id,
                   directory_for_save):
    images_dir_path = Path.joinpath(directory_for_save, 'images')
    Path(images_dir_path).mkdir(parents=True, exist_ok=True)
    response = tululu_response(image_url)
    if response is None:
        return
    path_for_saving = Path.joinpath(
        images_dir_path, f'{book_id}.jpg')
    with open(path_for_saving, 'wb') as file:
        file.write(response.content)
    return str(path_for_saving)


def parse_book_url(url):
    book_info = {}
    response = tululu_response(url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        book_info['book_title'], book_info['book_author'] = soup.select_one(
            'h1').text.split(" \xa0 :: \xa0 ")
        book_info['book_url'] = urljoin(url, soup.find(
            'a', title=f'{book_info["book_title"]} - скачать книгу txt')['href'])
        img_url = soup.select_one('div.bookimage img').get('src')
        if 'nopic.gif' not in img_url:
            book_info['book_image_url'] = urljoin(url, img_url)
        comments = soup.select('div.texts span.black')
        book_info['comments'] = [comment.text for comment in comments]
        genres = soup.select_one('div#content span.d_book').select('a')
        book_info['genres'] = [genre.text for genre in genres]
    except Exception:
        return
    return book_info


def download_books(book_ids, args):
    downloaded_books_info = []
    for book_id in book_ids:
        book_url = urljoin('http://tululu.org/', book_id)
        book_info = parse_book_url(book_url)
        if book_info is None:
            continue
        book_info['book_id'] = book_id
        if not args.skip_txt:
            book_info['book_path'] = download_txt(book_info['book_url'],
                                                  book_info['book_id'],
                                                  sanitize_filename(
                book_info['book_title']),
                args.dest_folder)
            print(
                f'''Downloaded '{book_info["book_title"]}' - {book_info["book_author"]} '''
                f'''from http://tululu.org/{book_info["book_id"]}''')

        if 'book_image_url' in book_info and not args.skip_imgs:
            book_info['img_src'] = download_image(book_info['book_image_url'],
                                                  book_info['book_id'],
                                                  args.dest_folder)
        downloaded_books_info.append(book_info)
    return downloaded_books_info


def save_books_json(books_info, json_file_name, dest_folder):
    json_file_name = Path.joinpath(
        dest_folder, json_file_name)
    with open(json_file_name, "w", encoding='utf8') as json_file:
        json.dump(books_info, json_file, ensure_ascii=False)


def get_arguments(parser):
    parser.add_argument('--start_page', type=int, default=1,
                        help="input start page for parsing")
    parser.add_argument('--end_page', type=int, default=1,
                        help="input last page for parsing")
    parser.add_argument('--skip_imgs', type=bool, default=False,
                        help="don't download images")
    parser.add_argument('--skip_txt', type=bool, default=False,
                        help="don't download books texts")
    parser.add_argument('--json_path', type=str, default='books.json',
                        help="path for json putput file")
    parser.add_argument('--dest_folder', type=str, default=Path.cwd(),
                        help="path for savings")
    parser.add_argument('--category_url', type=str, default='http://tululu.org/l55/',
                        help="url for your category")
    args = parser.parse_args()
    return args


def main():
    args = get_arguments(argparse.ArgumentParser())
    category_pages_number = get_category_pages_number(args.category_url)
    # минимальное значение используется, если пользователь ввел страницу большую, чем есть в категории
    end_page = min(
        args.end_page, category_pages_number) if args.end_page else category_pages_number
    book_ids = get_book_ids(
        args.category_url, args.start_page, end_page)
    downloaded_books = download_books(book_ids, args)
    save_books_json(downloaded_books, args.json_path, args.dest_folder)
    print(f'Total {len(downloaded_books)} books downloaded')


if __name__ == '__main__':
    main()
