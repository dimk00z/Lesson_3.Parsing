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
    books_dir_path = Path.joinpath(directory_for_save, 'books')
    Path(books_dir_path).mkdir(parents=True, exist_ok=True)
    response = requests.get(book_url)
    response.raise_for_status()
    path_for_saving = Path.joinpath(
        books_dir_path, f'{book_id}.{book_name}.txt')
    with open(path_for_saving, 'wb') as file:
        file.write(response.content)
    return str(path_for_saving)


def download_image(image_url, book_id,
                   directory_for_save):
    images_dir_path = Path.joinpath(directory_for_save, 'images')
    Path(images_dir_path).mkdir(parents=True, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()
    path_for_saving = Path.joinpath(
        images_dir_path, f'{book_id}.jpg')
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
    for url in soup.select('table.d_book td a'):
        if url.text == 'скачать txt':
            book_info['book_url'] = f'http://tululu.org{url.get("href")}'
            break
    img_url = soup.select_one('div.bookimage img').get('src')
    if img_url != '/images/nopic.gif':
        book_info['book_image_url'] = f'http://tululu.org{img_url}'
    comments = soup.select('div.texts span.black')
    book_info['comments'] = [comment.text for comment in comments]
    genres = soup.select_one('div#content span.d_book').select('a')
    book_info['genres'] = [genre.text for genre in genres]
    return book_info


def get_books(ids_for_category, args):
    books_info = []
    for book_id in ids_for_category:
        book_url = urljoin('http://tululu.org/', book_id)
        book_info = parse_book_url(book_url)
        book_info['book_id'] = book_id
        if ('book_url' not in book_info):
            continue
        try:
            if ('book_image_url' in book_info) and (not args.skip_imgs):
                book_info['img_src'] = download_image(book_info['book_image_url'],
                                                      book_info['book_id'],
                                                      args.dest_folder)
            if (not args.skip_txt):
                book_info['book_path'] = download_txt(book_info['book_url'],
                                                      book_info['book_id'],
                                                      remove_invalid_symbols_from_filename(
                    book_info['book_title']),
                    args.dest_folder)
                print(
                    f'''Downloaded '{book_info["book_title"]}' - {book_info["book_author"]} '''
                    f'''from http://tululu.org/{book_info["book_id"]}''')
            books_info.append(book_info)
        except requests.exceptions.HTTPError as ex:
            print(
                f'Connection error {ex} while dowloading {book_info["book_title"]}')
    return books_info


def remove_invalid_symbols_from_filename(filename):
    return re.sub(r'[\\\\/*?:"<>|]', "", filename)


def save_books_json(books_info, json_file_name, dest_folder):
    json_file_name = Path.joinpath(
        dest_folder, json_file_name)
    with open(json_file_name, "w", encoding='utf8') as json_file:
        json.dump(books_info, json_file, ensure_ascii=False)


def get_arg(parser):
    parser.add_argument('--start_page', type=int, default=1,
                        help="input start page for parsing")
    parser.add_argument('--end_page', type=int, default=2,
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
    args = get_arg(argparse.ArgumentParser())
    categoty_pages_number = get_categoty_pages_number(args.category_url)
    # минимальное значение используется, если пользователь ввел страницу большую, чем есть в категории
    end_page = min(
        args.end_page, categoty_pages_number) if args.end_page else categoty_pages_number
    ids_for_category = get_ids_for_category(
        args.category_url, args.start_page, end_page)
    books_info = get_books(ids_for_category, args)
    save_books_json(books_info, args.json_path, args.dest_folder)


if __name__ == '__main__':
    main()
