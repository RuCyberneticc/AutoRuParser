# -*- encoding: utf8 -*-
# Импортируем нужные библиотеки
from unicodedata import normalize # бибилиотека нормализации данных
import requests # библиотека запросов
from bs4 import BeautifulSoup # суп
import pandas as pd # библиотека для создания датафрейма

all_data = {} # Словарик для всех данных
for k in range(1, 99): # Перебираем страницы на auto.ru
    url = f'https://auto.ru/cars/all/?page={k}'  # Получившийся юрл
    response = requests.get(url) # Запрашиваем данные
    response.encoding = 'utf8' # декодируем запрос
    soup = BeautifulSoup(response.text, 'lxml') # Составляем супчик
    for i in soup.find_all('div', class_ = 'ListingItem'):  # Ищем блоки с данными по автомобилям
        name = i.h3.text  # Название ищется легко
        url2 = i.find('h3').a.get('href') # Ссылка на страницу каждой машины
        # Дальше идет проверка на то, работает ли страница
        # Проблема в том, что почему-то при парсинге не все ссылки на страницу являеются
        # верными и некторые могут выдавать страницу которой нет (404)
        # Поэтому мы будем отсеивать такие страницы через try - except
        # Если страница есть, то мы парсим ее, если ссылка неправильная, то берем из карточки машины
        try: # если страница не 404
            responsex = requests.get(url2)  # Запрашиваем данные со страницы
            responsex.encoding = 'utf8'  # Кодировка для полученных данных
            soupx = BeautifulSoup(responsex.text, 'lxml') # получаем суп
            namex = soupx.find('h1', class_='CardHead__title').text # название
            pricex = soupx.find('span', class_='OfferPriceCaption PriceUsedOffer__caption')  # цена
            ranngex = soupx.find('li', class_='CardInfoRow CardInfoRow_kmAge').text[6::] # пробег
            body_typex = soupx.find('li', class_='CardInfoRow CardInfoRow_bodytype').text[5::] # тип кузова
            colourx = soupx.find('li', class_='CardInfoRow CardInfoRow_color').text[4::] # цвет
            volumex, powerx, fuel_typex = map(str, soupx.find('li', class_='CardInfoRow CardInfoRow_engine').text[9::].split(' / ')) # тут все про двигатель: объем, мощность и топливо
            engine_boxx = soupx.find('li', class_='CardInfoRow CardInfoRow_transmission').text[7::] # тип коробюки передач
            drive_unitx = soupx.find('li', class_='CardInfoRow CardInfoRow_drive').text[6::] # привод
            if ranngex == 'Новый': # Если вместо пробега написано новый - значит новый, а пробег = 0
                new = 'Да'
                ranngex = '0 км'
            else:
                new = 'Нет'
            year = i.find_all('div', class_='CardInfoRow CardInfoRow_year').split(' ')[1].text # Год выпуска
            region = i.find_all('span', class_='MetroList__station')[0].text # место машины
            using_updates = i.find_all('div', class_='InfoPopup InfoPopup_theme_plain InfoPopup_withChildren CardBenefits__item-info-popup') # Использование срнедств продвижения
            nice_diler = i.find_all('div', class_='CardSellerNamePlace__avatar HoveredTooltip__trigger') # Хороший диллер или нет
            if using_updates != []: # проверка на использование средств
                use_upd = 'Да'
            else:
                use_upd = 'Нет'
            if nice_diler == []:#  проверка на диллера
                nd = 'Нет'
            else:
                nd = 'Да'
            datax = [namex, engine_boxx, body_typex, drive_unitx, colourx, volumex, powerx, fuel_typex, pricex, ranngex, year, region, use_upd, new, nd] # составляем итоговый список
        except BaseException: # иначе данных нет
            datax = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        data = [j.text for j in i.find_all('div', class_ = 'ListingItemTechSummaryDesktop__cell')]  # Данные в отедьном блоке (там коробка передач, тип кузова, привод, хар-ки двигателя)
        for j in range(len(data)):  # В этом цикле мы нормализуем данные, полученные ранее, потому что там были всякие ненужные символы
            data[j] = normalize('NFKD', data[j]) # Сам процесс нормализации
        for j in data[0].split(' / '):  # В первом наборе данных одновременно есть объем двигателя, мощность и тип топлива, поэтому их надо разделить
            data.append(j) # Ну и потом добавляем в конец списка
        price = normalize('NFKD', i.find_all('div', class_='ListingItemPrice__content')[0].text)  # Также добавляем цену, нормализованную и только цифры, потому что пробелы и значок рубля нам не нужен

        dist = normalize('NFKD', i.find_all('div', class_='ListingItem__kmAge')[0].text)# То же самое с пробегом
        if dist == 'Новый':# проверка на новизну автомобиля
            new = 'Да'
            dist = '0 км'
        else:
            new = 'Нет'
        year = i.find_all('div', class_='ListingItem__year')[0].text# год выпуска
        region = i.find_all('span', class_='MetroListPlace__regionName MetroListPlace_nbsp')[0].text# регион
        using_updates = i.find_all('div', class_='ListingItemServices ListingItem__services')# использование средств выделения
        nice_diler = i.find_all('div', class_='InfoPopup InfoPopup_theme_plain InfoPopup_withChildren SalonVerifiedLabelWithPopup__popup')
        data.append(price)  # Добавляем все в список
        data.append(dist)
        data.append(year)
        data.append(region)
        if using_updates != []:# проверка использования средств
            data.append('Да')
        else:
            data.append('Нет')
        data.append(new)
        if nice_diler == []:# проверка хорошего диллера
            data.append('Нет')
        else:
            data.append('Да')
        data = data[1::]  # Убираем первый набор даннных, потому что мы его раскрыли в строке 40
        print(data)
        data.insert(0, name)  # добавляем название машины сначала
        result = [] # список который должен получиться в итоге
        for i in range(1, min(len(data), len(datax))): # проходимся по спискам и сравниваем, если совпадает, то нормально
            if data[i] != datax[i]: # если не совпадает (получается None, то есть страница 404), то берем с карточки
                result.append(data[i])
            else: # иначе берем со странички
                result.append(datax[i])
        all_data[name] = result  #Добавляем в наш словарик данные

df = pd.DataFrame([[i, all_data[i][0], all_data[i][1], all_data[i][2], all_data[i][3], all_data[i][4], all_data[i][5], all_data[i][6], all_data[i][7], all_data[i][8], all_data[i][9], all_data[i][10], all_data[i][11], all_data[i][12], all_data[i][13]] for i in all_data], columns=['Машина', 'Тип коробки передач', 'Тип машины', 'Привод', 'Цвет', 'Объем двигателя', 'Мощность двигателя', 'Тип топлива', 'Цена', 'Пробег', 'Год выпуска машины', 'Город местонахождения машины', 'Использует ли влдаелец средства продвижения', 'Новая ли машина', 'Проверенный диллер'])  # Создаем датафрейм из наших данных и необходимых полей
print(df)  # Выводим для проверки
df.to_csv('file.csv')  # Сохраняем в файлик