import requests
from bs4 import BeautifulSoup

url = 'https://auto.ru/cars/all/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
for i in soup.find_all('div', class_='ListingItem'):
    print(i.find('h3').a.get('href'))