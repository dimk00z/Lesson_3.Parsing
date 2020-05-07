import requests
import time
import json
import argparse
import sys
import re
from urllib.parse import urljoin
from random import randrange
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename


def send_request_to_tululu(url, allow_redirects=True):
    headers = {"User-Agent": 'Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    response = requests.get(
        url, headers=headers,
        allow_redirects=allow_redirects)
    response.raise_for_status()
    if response.status_code in [301, 302]:
        raise requests.exceptions.HTTPError
    return response


def get_category_pages_number(response):
    soup = BeautifulSoup(response.text, 'lxml')
    category_page_numbers = soup.select('p.center a.npage')
    return int(category_page_numbers[-1].text) if category_page_numbers else 1


def get_book_ids(response):
    soup = BeautifulSoup(response.text, 'lxml')
    books_links = soup.select('table.d_book div.bookimage a')
    return [book_link.get('href').rsplit('/')[-2] for book_link in books_links]


def download_txt(response, book_id, book_name,
                 directory_for_save):
    books_dir_path = Path.joinpath(directory_for_save, 'books')
    Path(books_dir_path).mkdir(parents=True, exist_ok=True)
    path_for_saving = Path.joinpath(
        books_dir_path, f'{book_id}.{book_name}.txt')
    with open(path_for_saving, 'wb') as file:
        file.write(response.content)
    return str(path_for_saving)


def download_image(response, book_id,
                   directory_for_save):
    images_dir_path = Path.joinpath(directory_for_save, 'images')
    Path(images_dir_path).mkdir(parents=True, exist_ok=True)
    path_for_saving = Path.joinpath(
        images_dir_path, f'{book_id}.jpg')
    with open(path_for_saving, 'wb') as file:
        file.write(response.content)
    return str(path_for_saving)


def parse_book_url(response, url, book_id):
    parsed_book = {}
    parsed_book['book_id'] = re.sub('\D', '', book_id)
    soup = BeautifulSoup(response.text, 'lxml')
    parsed_book['book_title'], parsed_book['book_author'] = soup.select_one(
        'h1').text.split(" \xa0 :: \xa0 ")
    parsed_book['book_url'] = f"http://tululu.org/txt.php?id={parsed_book['book_id']}"
    img_url = soup.select_one('div.bookimage img').get('src')
    if 'nopic.gif' not in img_url:
        parsed_book['book_image_url'] = urljoin(url, img_url)
    comments = soup.select('div.texts span.black')
    parsed_book['comments'] = [comment.text for comment in comments]
    genres = soup.select_one('div#content span.d_book').select('a')
    parsed_book['genres'] = [genre.text for genre in genres]
    return parsed_book


def save_books_json(downloaded_books, json_file_name, dest_folder):
    json_file_name = Path.joinpath(
        dest_folder, json_file_name)
    with open(json_file_name, "w", encoding='utf8') as json_file:
        json.dump(downloaded_books, json_file, ensure_ascii=False)


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
    try:
        category_response = send_request_to_tululu(
            args.category_url, False)
    except requests.exceptions.HTTPError:
        print(
            f'Can not connect to category url {args.category_url}')
        sys.exit()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
        print("Connection error:", error)

    category_pages_number = get_category_pages_number(category_response)
    end_page = min(
        args.end_page, category_pages_number) if args.end_page else category_pages_number

    book_ids = []

    for category_page_number in range(args.start_page, end_page+1):
        category_page_url = urljoin(
            args.category_url, str(category_page_number))
        try:
            response = send_request_to_tululu(category_page_url)
            book_ids.extend(get_book_ids(response))
        except (requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as error:
            print("Connection error: ", error)

    downloaded_books = []
    for book_id in book_ids:
        book_url = urljoin('http://tululu.org/b', book_id)
        try:
            book_response = send_request_to_tululu(book_url)
            parsed_book = parse_book_url(book_response, book_url, book_id)
            if not args.skip_txt:
                txt_response = send_request_to_tululu(
                    parsed_book['book_url'], False)
                parsed_book['book_path'] = download_txt(txt_response,
                                                        parsed_book['book_id'],
                                                        sanitize_filename(
                                                            parsed_book['book_title']),
                                                        args.dest_folder)
                print(
                    f'''Downloaded '{parsed_book["book_title"]}' - {parsed_book["book_author"]} '''
                    f'''from http://tululu.org/{parsed_book["book_id"]}''')
            if 'book_image_url' in parsed_book and not args.skip_imgs:
                image_response = send_request_to_tululu(
                    parsed_book['book_image_url'])
                parsed_book['img_src'] = download_image(image_response,
                                                        parsed_book['book_id'],
                                                        args.dest_folder)
            downloaded_books.append(parsed_book)
        except requests.exceptions.HTTPError as error:
            print(f"{book_url} doesn't have downloadable book", error)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as error:
            print(f"Connection error with :  {book_url}", error)

    save_books_json(downloaded_books, args.json_path, args.dest_folder)
    print(f'Total {len(downloaded_books)} books downloaded')


if __name__ == '__main__':
    main()
