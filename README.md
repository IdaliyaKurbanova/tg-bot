# Общая часть

## Что из себя представляет проект
Проект представляет собой телеграм-бота под названием TicketBot, написанного при помощи библиотеки aiogram 3.
Данный бот осуществляет поиск авиабилетов на сайте Aviasales по заданным пользователем критериям.


## Подключение и запуск бота

1. Создаем у себя на компьютере новую папку для проекта. 
   В директории папки проекта создаем виртуальное окружение и активируем его. 

2. Находясь в директории папки проекта, при помощи команды `git clone` клонируем проект, который находится по следующему адресу => 
    https://gitlab.skillbox.ru/idaliia_kurbanova/python_basic_diploma

3. Находясь в директории проекта выполняем в терминале следующую команду по установке необходимых библиотек:
   `pip install -r requirements.txt`

4. После того как успешно установлены все необходимые библиотеки, в директории проекта на примере файла 
   `.env.template` создаем файл `.env`, в котором указываем ключи для BOT_TOKEN и API_KEY.

5. В файле `database/models.py` в качестве базы данных указана SQlite. 
   В случае, если вы планируете использовать для проекта другую базу данных и DBAPI, укажите их вместо `sqlite`
   в следующем кусочке кода:

   ```
   db_engine = create_engine('sqlite:///bot.db', echo=False) 
   ```
   
6. Находясь в директории проекта запустите файл `db_creation.py`.
   Он создаст в базе данных таблицы с кодами городов и авиалиний. Они необходимы для дальнейшей работы бота.

7. Убедитесь, что в базе данных успешно созданы таблицы `airlines` и `cities`, и запустите файл `bot.py`.
   Запуск данного файла, при успешном выполнении всех предыдущих шагов запустит телеграм-бота TicketBot.


## Документация

   Подробное описание всех функций, команд и классов, представлено в соответствующих файлах-модулях.