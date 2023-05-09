import requests
from bs4 import BeautifulSoup

urlx = 'https://auto.ru/cars/used/sale/vaz/largus/1115376493-04de7809/'
responsex = requests.get(urlx)
responsex.encoding = 'utf8'
soupx = BeautifulSoup(responsex.text, 'lxml')
name = soupx.find('h1', class_='CardHead__title').text
price = soupx.find('span', class_='OfferPriceCaption PriceUsedOffer__caption').text
rannge = soupx.find('li', class_='CardInfoRow CardInfoRow_kmAge').text[6::]
body_type = soupx.find('li', class_='CardInfoRow CardInfoRow_bodytype').text[5::]
colour = soupx.find('li', class_='CardInfoRow CardInfoRow_color').text[4::]
volume, power, fuel_type = map(str, soupx.find('li', class_='CardInfoRow CardInfoRow_engine').text[9::].split(' / '))
engine_box = soupx.find('li', class_='CardInfoRow CardInfoRow_transmission').text[7::]
drive_unit = soupx.find('li', class_='CardInfoRow CardInfoRow_drive').text[6::]
print(drive_unit)