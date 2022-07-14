import requests
from bs4 import BeautifulSoup

import time

from threading import Thread

import os
try:
    from config import token, id, price
except ModuleNotFoundError:
    if not os.path.exists('config.log'):
        with open('config.py', 'wt') as file:
            token = str(input('Введите токен от телеграм бота (Его можно получить у Bot Father):'))
            id = str(input('Введите id вашего аккаунта (ищите в интернете, как получить id telegram аккаунта) :'))
            price = str(input('Введите максимальную цену заказа, например 2000 :'))
            file.write(f'token = "{token}"\nid = "{id}"\nprice = "{prise}"')
        print('File config created!')



def getSoupWithWrite(url):
    req = requests.get(url)
    with open('index.html', 'wt', encoding='utf-8') as file:
        file.write(req.text)
    soup = BeautifulSoup(req.text, 'lxml')
    return soup


def get_last_call():
    with open('lastOrder.log', 'rt') as file:
        last_call = file.read()
    return last_call


def getSoup(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')
    return soup


def sendNotification(message):
    url = "https://api.telegram.org/bot" + f'{token}'
    method = url + "/sendMessage"

    requests.post(method, data={
        "chat_id": int(id),
        "text": str(message)
    })


def parsHabr():
    url = 'https://freelance.habr.com/tasks?q=%D0%BF%D0%B0%D1%80%D1%81%D0%B5%D1%80&only_with_price=true&fields=title'
    soup = getSoup(url)
    find_all_table_with_order = soup.find_all(class_='task task_list')
    for item in find_all_table_with_order:
        nameOrder = item.find(class_='task__title').find('a').get_text()
        urlOrder = 'https://freelance.habr.com' + item.find(class_='task__title').find('a').get('href')
        priceOrder = item.find(class_='count').get_text()
        priceNumber = int(priceOrder.replace(' руб. за проект', '').replace(' ', ''))
        if priceNumber <= int(price):
            log = get_last_call()
            if nameOrder not in log:
                text = f"""На Habr появилась новая задача!\n\nНазвание: {nameOrder};\n\nЦена: {priceOrder};\n\nСсылка: {urlOrder}
                """
                sendNotification(text)

                with open('lastOrder.log', 'a') as file:
                    file.write(nameOrder + "\n")


def startHabr():
    print('Модуль парсинга Habr запускается!')

    while True:
        try:
            parsHabr()
            time.sleep(60)
        except requests.exceptions.ConnectionError:
            print('Не удалось подключиться к сессии. Проверьте подключение с интернетом.')
            continue


def parsKwork():
    url = 'https://kwork.ru/projects?fc=41&attr=211'
    soup = getSoup(url)
    find_all_table_with_order = soup.find_all(class_='card__content pb5')
    for item in find_all_table_with_order:
        nameOrder = item.find(class_='wants-card__header-title first-letter breakwords pr250').find('a').get_text()
        urlOrder = item.find(class_='wants-card__header-title first-letter breakwords pr250').find('a').get('href')
        priceOrder = item.find(class_='wants-card__header-price wants-card__price m-hidden').get_text()
        priceNumber = int(priceOrder.replace('Желаемый бюджет: до', '').replace(' ', '').replace('₽', ''))
        if priceNumber <= int(price):
            log = get_last_call()
            if nameOrder not in log:
                text = f"""На Kwork появилась новая задача!\n\nНазвание: {nameOrder};\n\nЦена: {priceOrder};\n\nСсылка: {urlOrder}
                """
                sendNotification(text)

                with open('lastOrder.log', 'a') as file:
                    file.write(nameOrder + "\n")


def startKwork():
    print('Модуль парсинга Kwork запускается!')

    while True:
        try:
            parsKwork()
            time.sleep(60)
        except requests.exceptions.ConnectionError:
            print('Не удалось подключиться к сессии. Проверьте подключение с интернетом.')
            continue


def main():
    print('Бот запускается')

    if not os.path.exists('lastOrder.log'):
        with open('lastOrder.log', 'wt') as file:
            file.write('Start\n')
        print('File log created!')

    threadHabr = Thread(target=startHabr)
    threadKwork = Thread(target=startKwork)
    threadHabr.start()
    threadKwork.start()


if __name__ == "__main__":
    main()