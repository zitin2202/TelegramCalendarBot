На данный момент бот не работает. 
После внесения Google изменений, пользователь больше не может после авторизации получить токен доступа к данным аккаунта, который после, можно было бы передать боту. 
Внести изменения и сделать проект работоспособным возможно только при наличии подходящего домена и сервера, 
В таком случае, это должно быть веб приложения а не декстоп, как в данном случае, которое будет принимать токены авторизации

Запуск происходит через TelegramCalendarBot.bat
Для изменения времени уведомления в файле main.py переименовать значения start_hour и start_minutes. Они находяться внизу файла в разделе if __name__ = '__main__'

Тестовый бот - @BotForEventNotificationsBot
Чтобы изменить бота на другого в TelegramCalendarBot.bat изменить TOKEN на токен своего бота

Данный бот управляется со стороннего google аккаунта
Для управления API приложением в Google Cloud Platform с собственного аккаунта:
Создать проект -  для этого прейти по ссылке https://console.developers.google.com/ - поставить галочку под Terms of Service - Create Project - Ввести имя проекта - Create
Теперь нужно создать окно авторизации.Для этого в боковой панели поднести мышку к APIs & Service - открыть OAuth consent screen - Выбрал External - Create.
В поле App name ввести желаемое имя проекта - В поле User support email написать почту для поддержки(можете ввести собственную почту)
Мотаем вниз и добовляем почту для контактов(можно добавить ту же почту) - нажать на Save and Continue - потом еще раз на Save and Continue -  и еще раз
далее на Back to dashboard - опубликовать приложение нажав Publsih App - Confirm
Теперь нужно создать Dekstop приложение. Для этого На боковой панели перейти на Credentials - наверху кликаем на  +Create credentials - OAuth client ID
В Application type выбираем Desktop app - в Name имя клиента(можно оставить) - Create.
В открывашимся окне нажимаем на Downloads Json
Данный файл нужно переминовать на credentials и поместить в папку проекта, предварительно удалив оттуда одноименный файл (credentials)
Добавить Google Calendar API - https://console.developers.google.com/marketplace/product/google/calendar-json.googleapis.com


Установка важных модулей в консоли:
pip install aiogram
pip install aiogram-calendar
