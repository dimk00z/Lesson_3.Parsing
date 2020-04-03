# Парсер книг с сайта tululu.org

Программа скачивает книги заданной категории с tululu.org.

### Как установить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Для запуска в консоли:

`$ python main.py`

Для программы доступны следующие параметры:

`--start_page` - номер стартовой страницы, по умолчанию = 1

`--end_page` - номер последней страницы, по умолчанию=1

`--skip_imgs` - пропускать/не скачивать изображения книг , по умолчанию=False

`--skip_txt`- пропускать/не скачивать тексты книг, по умолчанию=False

`--json_path`- имя файла json, по умолчанию='books.json'

`--dest_folder`- путь папки для сохранения, по умолчанию - текущее расположение

`--category_url`- путь к категории, по умолчанию='http://tululu.org/l55/'

Пример использования:
```
$ python main.py 
Downloaded 'Алиби' - ИВАНОВ Сергей from http://tululu.org/b239
Downloaded 'Бич небесный' - Стерлинг Брюс from http://tululu.org/b550
Downloaded 'Цена посвящения: Серый Ангел' - Маркеев Олег Георгиевич from http://tululu.org/b768
Downloaded 'Цена посвящения: Время Зверя' - Маркеев Олег Георгиевич from http://tululu.org/b769
Downloaded 'Дело Джен, или Эйра немилосердия' - Fforde Jasper from http://tululu.org/b1131
Downloaded 'Фабрика дьявола' - Мар Курт from http://tululu.org/b1715
Downloaded 'Говорящий камень' - Азимов Айзек from http://tululu.org/b1987
Downloaded 'И Он пришел... ИТ-роман' - Аджалов Владимир from http://tululu.org/b2043
Downloaded 'Казнить нельзя помиловать' - Чертанов Максим from http://tululu.org/b2531
Downloaded 'Ночь, которая умирает' - Азимов Айзек from http://tululu.org/b4024
Downloaded 'Нырок в забвение' - Хенрик Ричард from http://tululu.org/b4102
Downloaded 'Поющий колокольчик' - Азимов Айзек from http://tululu.org/b4876
Downloaded 'Продается тело Христа' - Аджалов Владимир Исфандеярович from http://tululu.org/b5299
Downloaded 'Роковой поцелуй' - Патрацкая Наталья from http://tululu.org/b5648
Downloaded 'Те, кто против нас' - Руденко Борис from http://tululu.org/b6758
Downloaded 'Телепортеры, внимание!' - Мар Курт from http://tululu.org/b6766
Downloaded 'Зодиак' - Стивенсон Нил from http://tululu.org/b8283
Downloaded 'Justitia - est Часть 1' - Картман Эрика from http://tululu.org/b8559
Downloaded 'Астронавт Джонс' - Хайнлайн Роберт from http://tululu.org/b8902
Downloaded 'Будет скафандр - будут и путешествия' - Хайнлайн Роберт from http://tululu.org/b9080
Downloaded 'Дочь Нефертити' - Семенова Татьяна from http://tululu.org/b9402
Downloaded 'Наложница императора' - Семенова Татьяна from http://tululu.org/b10768
Downloaded 'Общая теория Доминант' - Белохвостов Денис from http://tululu.org/b10923

```
### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
