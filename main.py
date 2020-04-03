import requests
import re
import json
import argparse
from urllib.parse import urljoin
from parse_tululu_category import get_ids_for_category, get_categoty_pages_number
from bs4 import BeautifulSoup
from pathlib import Path


def download_txt(book_url, book_id, book_name,
                 directory_for_save):
    Path(f'{directory_for_save}').mkdir(parents=True, exist_ok=True)
    book_file_name = Path(book_url).name
    response = requests.get(book_url)
    response.raise_for_status()
    path_for_saving = Path.joinpath(
        directory_for_save, 'books', f'{book_id}.{book_name}.txt')
    if not Path.is_file(path_for_saving):
        with open(path_for_saving, 'wb') as file:
            file.write(response.content)
    return str(path_for_saving)


def download_image(image_url, book_id,
                   directory_for_save):
    Path(f'{directory_for_save}').mkdir(parents=True, exist_ok=True)
    image_file_name = Path(image_url).name
    response = requests.get(image_url)
    response.raise_for_status()
    path_for_saving = Path.joinpath(
        directory_for_save, 'images', f'{book_id}.jpg')
    if not Path.is_file(path_for_saving):
        with open(path_for_saving, 'wb') as file:
            file.write(response.content)
    return str(path_for_saving)


def parse_book_url(url):
    book_info = {}
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_info['book_title'], book_info['book_author'] = soup.select_one(
        'h1').text.split(" \xa0 :: \xa0 ")
    for url in soup.select('a'):
        if url.text == 'скачать txt':
            book_info['book_url'] = f'http://tululu.org{url.get("href")}'
    img_url = soup.select_one('div.bookimage img').get('src')
    if img_url != '/images/nopic.gif':
        book_info['book_image_url'] = f'http://tululu.org{img_url}'
    comments = soup.select('div.texts span.black')
    book_info['comments'] = []
    for comment in comments:
        book_info['comments'].append(comment.text)
    genres = soup.select_one('div#content span.d_book').select('a')
    book_info['genres'] = []
    for genre in genres:
        book_info['genres'].append(genre.text)
    return book_info


def get_books_info(ids_for_category):
    books_info = []
    for book_id in ids_for_category:
        book_url = urljoin('http://tululu.org/', book_id)
        book_info = parse_book_url(book_url)
        book_info['book_id'] = book_id
        if ('book_url' not in book_info):
            continue
        books_info.append(book_info)
    return books_info


def remove_invalid_symbols_from_filename(filename):
    return re.sub(r'[\\\\/*?:"<>|]', "", filename)


def save_books_json(books_info, json_file_name, dest_folder):
    json_file_name = Path.joinpath(
        dest_folder, json_file_name)
    with open(json_file_name, "w", encoding='utf8') as json_file:
        json.dump(books_info, json_file, ensure_ascii=False)


def get_arg():
    parser = argparse.ArgumentParser()
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
                        help="path for savings")
    args = parser.parse_args()
    return args


def main():
    args = get_arg()
    category_url = args.category_url
    start_page = args.start_page
    dest_folder = args.dest_folder
    categoty_pages_number = get_categoty_pages_number(category_url)
    # минимальное значение используется, если пользователь ввел страницу большую, чем есть в категории
    end_page = min(
        args.end_page, categoty_pages_number) if args.end_page else categoty_pages_number
    ids_for_category = get_ids_for_category(
        category_url, start_page, end_page)
    books_info = get_books_info(ids_for_category)
    for book_index, book_info in enumerate(books_info):
        if ('book_image_url' in book_info) and (not args.skip_imgs):
            books_info[book_index]['img_src'] = download_image(book_info['book_image_url'],
                                                               book_info['book_id'],
                                                               dest_folder)
        if (not args.skip_txt):
            books_info[book_index]['book_path'] = download_txt(book_info['book_url'],
                                                               book_info['book_id'],
                                                               remove_invalid_symbols_from_filename(
                book_info['book_title']),
                dest_folder)
            print(
                f'''Downloaded '{book_info["book_title"]}' - {book_info["book_author"]} '''
                f'''from http://tululu.org/{book_info["book_id"]}''')
    save_books_json(books_info, args.json_path, dest_folder)


if __name__ == '__main__':
    main()
