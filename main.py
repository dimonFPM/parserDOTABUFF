import bs4
import requests
# import grequests
import json
from tqdm import tqdm
import copy
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 'Chrome/89.0.4389.72 Safari/537.36"}


# session=requests.Session()
# session.headers.update()


def get_content(url) -> requests.models.Response or None:
    '''Получает код страницы по адресу, указанному в url'''
    req = requests.get(url=url, headers=headers)
    if req.ok:
        return req
    else:
        print("программе не удалось совершить запрос к сайту")
        return None


def save_file(req, name: str) -> None:
    '''Записывает переданный в функцию код страницы в текстовый файл'''
    name = "html//" + name
    if req is not None and (name[-4:] == ".txt"):
        req = req.text
        with open(name, "w", encoding="utf-8") as file:
            file.write(req)
    else:
        print("нет данных для записи или не коректное имя файла")


def read_file(name):
    '''Читает код страницы из файла name'''
    with open(name, "r", encoding="utf-8") as file:
        return file.read()


def pars_name_price(pars_file: str) -> dict or None:
    '''Находит цену и название предметов'''
    soup = bs4.BeautifulSoup(pars_file, "lxml")
    item_list = soup.find("table", class_="sortable").find_all("td", class_="cell-xlarge")
    item_href_list = [f"https://ru.dotabuff.com{i.find('a')['href']}" for i in item_list]
    print(*item_href_list[:10], sep="\n")
    item_list = []
    for href in tqdm(item_href_list):
        req = get_content(href)

        if req:
            href_soup = bs4.BeautifulSoup(req.text, "lxml")
            article = href_soup.find("div", class_="embedded-tooltip")
            name = article.find("div", class_="name").text
            price = article.find("div", class_="price").text
            item_list.append({"name": name, "price": price, "href": href})
        else:
            print("не рабочая ссылка")
        #########
        if len(item_list) == 10:
            break
        #########

    # print(item_list)
    if item_list:
        return copy.deepcopy(item_list)
    else:
        return None


def pars_herous(pars_file: str):
    herou_soup = bs4.BeautifulSoup(pars_file, "lxml")
    herous_list = herou_soup.find("div", class_="hero-grid").find_all("a")
    herous_href_list = [f"https://ru.dotabuff.com/heroes{href['href']}" for href in herous_list]
    herous_name = [herou.text for herou in herous_list]
    herous_list.clear()
    if len(herous_name) == len(herous_href_list):
        for i in tqdm(range(len(herous_name))):
            herous_list.append({"name": herous_name[i], "href": herous_href_list[i]})
        return herous_list
    else:
        return None


def write_json(data_dict, name_json) -> None:
    if data_dict:
        with open(name_json, "w") as file:
            json.dump(data_dict, file, indent=4, ensure_ascii=False)
    else:
        print("Нет данных для записи")


def create_item_json(file_name) -> None:
    x = pars_name_price(read_file(file_name))
    write_json(x, "json//item_json.json")


def create_herous_json(file_name):
    x = pars_herous(read_file(file_name))
    write_json(x, "json//herous_json.json")


def check_files():
    if not os.path.exists("picture"):  # проверка наличия папки с изображениями
        os.mkdir("picture")
    if not os.path.exists("json"):
        os.mkdir("json")
    if not os.path.exists("html"):
        os.mkdir("html")

    if not os.path.exists("items_json.json"):  # проверка на наличие item_json
        if not os.path.exists("html//html_item.txt"):
            save_file(get_content("https://ru.dotabuff.com/items"), "html_item.txt")
        create_item_json("html//html_item.txt")

    if not os.path.exists("herous_json.json"):  # проверка на наличие herou_json
        if not os.path.exists("html//html_herous.txt"):
            save_file(get_content("https://ru.dotabuff.com/heroes"), "html_herous.txt")
        create_herous_json("html//html_herous.txt")


def main():
    check_files()


if __name__ == '__main__':
    main()
