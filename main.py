from aiogram import Bot,types
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.utils import executor
import quickstart as quick
import settings
from settings import kb_menu
from datetime import datetime
import asyncio
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from sql import base,cur


bot = settings.bot
dp = settings.dp

#Класс машины состояния для авторизации
class ConnectingAccount(StatesGroup):
    token = State()

#Класс машины состояния для создания события
class CreateEvents(StatesGroup):
    name = State()
    date = State()
    time = State()

#Ожидание определенного времени, перед началам цыкла оповещений
async def waiting(need_hour,need_minutes):
    now_time = datetime.now()
    if (need_hour*60+need_minutes)*60>(now_time.hour*60+now_time.minute)*60+now_time.second:
        sleep_time = (((need_hour - now_time.hour) * 60) + (need_minutes - now_time.minute)) * 60 - now_time.second
    else:
        sleep_time = 24*60*60 + (((need_hour - now_time.hour) * 60) + (need_minutes - now_time.minute)) * 60 - now_time.second
    print(f'Бот оповестит о событиях в календарях в {need_hour}:{need_minutes}, осталось {sleep_time} секунд')
    await asyncio.sleep(sleep_time)


#Оповещение о событиях в календаре пользователя, которые произойдут через неделю, 3 или 1 день
async def monitoring():
    await waiting(start_hour,start_minutes)
    while True:
        users = cur.execute('SELECT id FROM users').fetchall()
        for id in users:
                id = id[0]
                events = await quick.events_information(id)
                for i in events.values():
                    now = datetime.now()
                    between = i[1] - now
                    days = between.days
                    if now.hour*60+now.minute>i[1].hour*60+i[1].minute:
                        days+=1
                    # print('{} - {} = {}'.format(datetime.now(),i[1],days))
                    if days in (7, 3, 1):
                       # print('дней до события "{0}" - {1},\nдата события: {2}'.format(i[0], days, i[1]))
                       await bot.send_message( chat_id=id, text='дней до события "{0}" - {1},\nдата события: {2}'.format(i[0], days, i[1]))
        await asyncio.sleep(24*60*60)



#Справочная информация
@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    help_message = """Использование бота для управления календарем:

/start и /help - получение справочной информации

/connect - подключение телеграм аккаунта к своему Google каленадрю:
   - При вводе команды присылается гипперсылка на авторизацию.
   - Если при попытке авторизоваться высвечивается сообщение - "Google hasn’t verified this app"
     нажмите на "Advanced", а после на "Go to Calendar (unsafe)" и продолжайте авторизацию.
   - По окончанию авторизации скопируйте сгенерированный код и отправьте его боту.
     На этом подключение Google календаря заканчивается

/create - Создание события в календаре:
   - Поочередно введите название, дату и время события
/cancel - Используйте для отмены определенных действий, например, подключения аккаунта или создания события

Работа с группами:
    При использовании бота в группе,все команды, кроме /cancel, пишутся в чате группы, но все дальшейшие
    процессы этих команд необходимо проходить в личном чате с ботом, например подключение Google аккаунта или 
    создания событий.
    Для использования бота в группе,сначало необходимо его запустить в личном чате."""

    await bot.send_message(message.from_user.id, help_message, reply_markup=kb_menu)
#Отмена машин состояния
@dp.message_handler(state="*",commands='cancel')
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()

#Событие, отпровляющее пользователю ссылку авторизации
@dp.message_handler(commands=['connect'], state=None)
async def connect_google_account(message: types.Message):
        if cur.execute('SELECT * FROM users WHERE id == ?',(message.chat.id,)).fetchone() != None:
            await bot.send_message(message.from_user.id, 'Ваш каленадрь уже подключен')
        else:
            await quick.auth_url(message.chat.id,message.from_user.id)
            await bot.send_message(message.from_user.id, 'Авторизуйтесь и введите полученный код')
            chat_id = message.chat.id
            chat_name = message.chat.full_name
            message.chat.id = message.from_user.id
            await ConnectingAccount.token.set()
            state = FSMContext(settings.storage,message.from_user.id,message.from_user.id)
            async with state.proxy() as data:
                data['chat_id'] = chat_id
                data['chat_name']  = chat_name

#Событие, принимающее код, полученный при авторизации
@dp.message_handler(state=ConnectingAccount.token)
async def connect_google_account(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        chat_id = data['chat_id']
        chat_name = data['chat_name']
    succ = await quick.auth(chat_id, message.text,message.from_user.id)
    if succ:
        await message.answer(f'Календарь для {chat_name} успешно подключен!')
        await state.finish()

#Запуск машины состояния создания событий
@dp.message_handler(commands='create',state=None)
async def create_event_start(message: types.Message):
    if cur.execute('SELECT * FROM users WHERE id == ?',(message.chat.id,)).fetchone() == None:
        await bot.send_message(message.from_user.id,f'У {message.chat.full_name} не подключен календарь')
        return
    state = FSMContext(settings.storage, message.from_user.id, message.from_user.id)
    async with state.proxy() as data:
        data['chat_id'] =  message.chat.id
    message.chat.id = message.from_user.id
    await CreateEvents.name.set()
    await message.answer("Название события: ")

#Ввод имени события
@dp.message_handler(state=CreateEvents.name)
async def create_event_name(message: types.Message, state: FSMContext):
    # print(state.storage,state.user,state.chat,settings.storage)
    # print(message.from_user,message.from_user.id)
    async with state.proxy() as data:
        data['name'] = message.text
    await CreateEvents.next()
    await message.answer("Please select a date: ", reply_markup=await SimpleCalendar().start_calendar())

#Ввод даты события в интерактивном календаре
@dp.callback_query_handler(simple_cal_callback.filter(), state=CreateEvents.date)
async def process_create_event_date(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['date'] = date.strftime("%Y-%m-%d")
            await CreateEvents.next()
            await bot.send_message(callback_query.from_user.id,"Введите время (в формате 00:00): ")

#Ввод времени события и и его создание
@dp.message_handler(state=CreateEvents.time)
async def create_event_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
        succ  = await quick.events_create(data['chat_id'],data["name"], data["date"],data["time"],message.from_user.id)
        if succ:
            await message.answer(f'событие "{data["name"]}" установлено на {data["date"]} {data["time"]}')
            await state.finish()










if __name__ == '__main__':
  #Асинхронный запуск оповещения о событиях и бота
  start_hour =12
  start_minutes = 00
  loop = asyncio.get_event_loop()
  loop.create_task(monitoring())
  executor.start_polling(dp, skip_updates=True)








