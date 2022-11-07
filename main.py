import tkinter as tk
from vk_api import VkApi
import pyperclip

import datetime
from random import choice
import requests
import threading
import time

user_agents = [
    'Mozilla/5.0 (Linux; Android 11; 21061179AG Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/361.0.0.39.115;]',
    'Mozilla/5.0 (Linux; Android 11; 22011169UY Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.97 Mobile Safari/537.36 [FB_IAB/Orca-Android;FBAV/376.1.0.25.106;]',
    'Mozilla/5.0 (Linux; Android 11; 21121159SG Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/381.0.0.29.105;]',
    'Mozilla/5.0 (Linux; Android 11; 21061149AG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; 21121139SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
]

flag = True
try:
    file = open('group.txt', mode='r', encoding='utf-8')
    group = file.read()
    print(group)
except:
    group = '7777777\n8888888\n9999999' # Если файла group.txt нету, группы возьмутся от сюда

def touch_password(event):
    input_password.insert(0, pyperclip.paste())

def touch_list_group(event):
    input_list_group.insert(1.0, pyperclip.paste() + '\n')

def touch_text(event):
    input_text.insert(1.0, pyperclip.paste())

def touch_photo(event):
    input_photo.insert(0, pyperclip.paste())

def get_token(login, password):
    session = requests.Session()
    user_agent = choice(user_agents) # выбераем рандомный ЮА из нашего списка
    session.headers.update({'User-agent': user_agent}) # перезаписываем дефолтный ЮА
    response = requests.get(
        f'https://oauth.vk.com/token?grant_type=password&client_id=2274003&client_secret=hHbZxrka2uZ6jB1inYsH&username={login}&password={password}&v=5.131&2fa_supported=1'
    )
    if 'error_description' in response.json():
        return False # если логин и пароль неверные возвращаем False

    token = response.json()['access_token']
    vk_session = VkApi(token=token)
    vk_session.http.headers['User-agent'] = user_agent
    return vk_session # возвращаем авторизованную сессию

def start_action():
    btn_start.config(state=tk.DISABLED) # делаем кнопку неактивной
    thread = threading.Thread(target=started) # поток
    print(threading.main_thread().name)
    print(thread.name) # выводим имя потока
    thread.start()

def stop_action():
    global flag
    flag = False

def cleaner():
    input_logs.delete(1.0, tk.END) # эта функция очищения всех полей, я поленился её делать

def started():
    account = input_password.get() # получаем аккаунт
    list_group = input_list_group.get(1.0, tk.END) # получаем список групп
    text = input_text.get(1.0, tk.END) # получаем текст рассылки
    attachment = input_photo.get() # вложение

    login, password = account.split(':')
    vk_session = get_token(login, password)
    time.sleep(2)

    check_list_group = {} # создаём пустой словарь

    for group in list_group.rstrip().split('\n'):
        print(group)
        result = vk_session.method('wall.get', {'owner_id': f'-{group.strip()}', 'count': 1})
        print(result)
        id_group = result["items"][0]["id"]
        input_logs.insert(1.0, f'Группа {group}, ид последней записи {id_group}\nВремя {datetime.datetime.fromtimestamp(result["items"][0]["date"])}' + '\n' + ' ******* ' + '\n')
        check_list_group[group] = id_group
        time.sleep(6)
        root.update()

    time.sleep(5)

    while True:
        for group in check_list_group:
            print(group)
            check_id = vk_session.method('wall.get', {'owner_id': f'-{group}', 'count': 1})
            id_post = check_id["items"][0]["id"]
            time.sleep(7)
            if check_list_group[group] != id_post:
                vk_session.method('wall.createComment', {'owner_id': f'-{group}', 'post_id': id_post,
                                                         'message': text.strip(), 'attachments': attachment})
                check_list_group[group] = id_post
                input_logs.insert(1.0, f'Комментарий в группе\nhttps://vk.com/club{group}\nуспешно оставлен!!\n ******* \n')
                root.update()
                time.sleep(7)

            time.sleep(6)

        if flag == False:
            break # брикаем функцию
    btn_start.config(state=tk.NORMAL) # нормализуем кнопку

root = tk.Tk()

root.geometry('280x550+350+50') # создаём геометрию окна
root.title('TG: @listopadd') # не трогай бл..ть!!!

label = tk.Label(text='Введите логин и пароль через разделитель : ')
label_2 = tk.Label(text='Введите список id групп')

input_password = tk.Entry(width=35)
input_password.bind("<ButtonPress-3>", touch_password)
input_list_group = tk.Text(height=5)
input_list_group.bind("<ButtonPress-3>", touch_list_group)
input_list_group.insert(1.0, group)

label_text = tk.Label(text='Введите текст рассылки ')
input_text = tk.Text(height=2)
input_text.bind("<ButtonPress-3>", touch_text)

label_photo = tk.Label(text='Вложение photo-123456_123456')
input_photo = tk.Entry(width=35)
input_photo.bind("<ButtonPress-3>", touch_photo)

frame_btn = tk.Frame()
btn_start = tk.Button(master=frame_btn, text='Старт', command=start_action)
btn_stop = tk.Button(master=frame_btn, text='Стоп', padx=4, command=stop_action)

label_logs = tk.Label(text='LOGS')
input_logs = tk.Text(height=11, wrap=tk.WORD)

label.pack(pady=7)
input_password.pack()

label_2.pack(pady=7)
input_list_group.pack(padx=6)

label_text.pack(pady=7)
input_text.pack(padx=6)

label_photo.pack(pady=7)
input_photo.pack()

frame_btn.pack(pady=5)
btn_start.pack(side=tk.LEFT, pady=5, padx=5, ipadx=8)
btn_stop.pack(side=tk.RIGHT, pady=5, padx=5, ipadx=8)

label_logs.pack(pady=7)
input_logs.pack(padx=6)

root.mainloop()



