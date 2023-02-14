from __future__ import print_function
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import aiogram
import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sql import base,cur
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


#Создание ссылки авторизации
async def auth_url(chat_id,user_id):
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = flow._OOB_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        promt='consent'
         )
    await settings.bot.send_message(user_id, f'<a href="{authorization_url}">Подключить Google аккаунт</a>', parse_mode=aiogram.types.ParseMode.HTML)

#Авторизация пользователя
async def auth(chat_id,code,user_id):
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        flow.redirect_uri = flow._OOB_REDIRECT_URI
        flow.fetch_token(code=code)
        cur.execute('INSERT INTO users VALUES(?,?)',(chat_id,flow.credentials.to_json()))
        base.commit()
            # tokens[str(id)] = flow.credentials.to_json()

    except:
        await settings.bot.send_message(user_id,'Некорретный код, введите действительный код')
        return False
    return True


#Извлечение токена доступа к календарю пользователя
def check_token(id):
    token = cur.execute('SELECT token FROM users WHERE id == ?', (id,)).fetchone()[0]
    creds = Credentials.from_authorized_user_info(eval(token),SCOPES)
    if not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            cur.execute('UPDATE users SET token = ? WHERE id == ?',(creds.to_json(),id))
            base.commit()
    return creds

#Получение событий календаря пользователя
async def events_information(id):
    event_list = {}
    creds = check_token(id)
    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=100, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            name =''
            if 'summary' in event:
                name = event['summary']
            event_data = [start.split('T')[0].split('-'),start.split('T')[1].split(':')]
            datee = datetime.datetime.strptime(start,"%Y-%m-%dT%H:%M:%S+03:00")
            event_list[start] = [name,datee,datee.day]
    except HttpError as error:
            print('An error occurred: %s' % error)

    return event_list

#Создание события
async def events_create(chat_id,name,date,time,user_id):
    creds = check_token(chat_id)
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {'summary': name,
                 'start':{
                    'dateTime':f'{date}T{time}:00+03:00',
                    'timeZone': 'Europe/Moscow'
                        },
                 'end': {
                     'dateTime': f'{date}T{time}:00+03:00',
                     'timeZone': 'Europe/Moscow'
                 }

                }
        events =  service.events().insert(calendarId='primary',body=event).execute()

    except:
        await settings.bot.send_message(user_id,'Не корректное время, введите время в необходимом формате')
        return False

    return True

