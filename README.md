запуск из корневой папки, содержащей mai_schedule_parser:

py -m mai_schedule_parser (номер группы, ctrlC+ctrlV с сайта маи) (номер недели)

аргументы не обязательные, по умолчанию (М8О-102БВ-24) (10)

e.g.

py -m mai_schedule_parser М8О-102БВ-24 10
и
py -m mai_schedule_parser

выдаст один и тот же результат



склонить репу:

git clone https://github.com/Aflipov/mai_schedule_parser.git


установка после git clone:

py -m venv venv
.\venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install sqlalchemy click requests_html cachetools bs4 lxml_html_clean