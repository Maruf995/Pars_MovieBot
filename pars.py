import requests
import json
from bs4 import BeautifulSoup 
import os

#Создаем переменную в которой есть число, которое каждый раз будет увеличиваться на 1
page = 1
URL = ('https://vip.x-film.sbs/page/' + str(page)) #Используем эту переменную, чтобы скрипт автоматом парсил не 1 страницу

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}


def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params).text
    return r

#Создаем главную функцию, где находится сам парсер
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.findAll("div", class_="short clearfix with-mask") #Класс блока на сайте, с фильмами
    result = []
    movie_id = max_movie_id + 1 #Обьявляем id к фильму

    for item in main: #Тут парсим отдельные классы, Название, описание, лого и т.д.
        title_element = item.find('a', class_='short-title')
        image_element = item.find('div', class_='short-img img-box').find('img')
        description_element = item.find('div', class_='sd-line sd-text')
        sd_line_elements = item.find_all('div', class_='sd-line') #Т.К несколько элементов имеют один и тот же класс, мы парсим все
        grade_elenents = item.find('div', class_='m-meta m-kp')

        if len(sd_line_elements) >= 2: #Тут мы уже парсим определеные элементы, по id 
            year_element = sd_line_elements[0]
            original_element = sd_line_elements[1]
            time_element = sd_line_elements[2]
            contries_element = sd_line_elements[3]
            translate_element = sd_line_elements[4]

        if grade_elenents: #Парсим оценку, и даем проверку, есть нет оценки
            grade = grade_elenents.get_text(strip=True)
        else:
            grade = 'Not Found'

        if description_element: # Тут мы наш спарсеный класс (Описание фильмов), переводим в текст
            description = description_element.get_text(strip=True)
            year = year_element.get_text(strip=True)
            original = original_element.get_text(strip=True)
            time = time_element.get_text(strip=True)
            contries = contries_element.get_text(strip=True)
            translate = translate_element.get_text(strip=True)

        if title_element: # Наш класс с названием, переводим в обычный текст, и берем ссылку
            title = title_element.get_text(strip=True)

            link_element = item.find('a', class_='short-title')
            if link_element:
                link = link_element.get('href')
            else:
                link = 'Link not found' 
            

            if image_element: # Тут мы парсим нашу картинку, виде ссылки
                image_url = image_element.get('src')
            else:
                image_url = 'Image not found'

            #Инициализируем наши спарсенные данные
            result.append({'id': movie_id,'title': title, 'description ': description, 'year': year, 'original': original, 
                           'time': time, 'contries': contries, 'translate': translate, 'grade':grade, 'link': link, 'image': image_url})
            movie_id += 1 #К каждому спарсенному фильму, мы добваляем +1 i

    return result

# Проверяем, чтобы при след парсинге, он не удалял старые, а прибавлял к новым
def load_existing_data(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
    return data

existing_data = load_existing_data('result.json')
max_movie_id = max(existing_data, key=lambda x: x['id'])['id'] if existing_data else 0

result = load_existing_data('result.json')


html = get_html(URL)
max_movie_id = max(existing_data, key=lambda x: x['id'])['id'] if existing_data else 0
new_data = get_content(html)
result.extend(new_data)

# Записываем наши данные в json
with open('result.json', 'w', encoding='utf-8') as file:
    json.dump(result, file, indent=4, ensure_ascii=False)

print("Спарсено")
