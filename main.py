import time

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


def pars_items_name_price(pars_file: str) -> dict or None:
    '''Находит цену и название предметов'''
    soup = bs4.BeautifulSoup(pars_file, "lxml")
    item_list = soup.find("table", class_="sortable").find_all("td", class_="cell-xlarge")
    item_href_list = [f"https://ru.dotabuff.com{i.find('a')['href']}" for i in item_list]
    # print(*item_href_list[:10], sep="\n")
    item_list = []
    for href in tqdm(item_href_list):
        req = get_content(href)

        if req.ok:
            href_soup = bs4.BeautifulSoup(req.text, "lxml")
            article = href_soup.find("div", class_="embedded-tooltip")
            name = article.find("div", class_="name").text
            price = article.find("div", class_="price").text
            item_list.append({"name": name, "price": price, "href": href})
        else:
            print("не рабочая ссылка")

        #########
        # if len(item_list) == 10:
        #     break
        #########

    # print(item_list)
    if item_list:
        return copy.deepcopy(item_list)
    else:
        return None


def pars_herou_page_tables(herou_href: str = "https://ru.dotabuff.com/heroes/abaddon") -> list or None:
    '''Принемает на вход ссылку на страницу героя'''
    output = []
    req = get_content(herou_href)
    if req:  # если None то значит не прошел запрос(get_content вернул None)
        soup = bs4.BeautifulSoup(req.text, "lxml")  # получаем страницу героя
        table_html = soup.find_all("table")
        output.append(pars_herou_favorit_items_table(table_html[2]))  # 2-номер таблицы с предметами
        # print(output)
        return output
    else:
        print("не рабочая ссылка")
        return None


def pars_herou_favorit_items_table(table: bs4.element.Tag) -> dict:
    '''Получает на вход 'результат поиска bs4 по тегу <table>
    return  dict вида {"название предмета":{"Матчи": int, "Победы": int, "Доля побед": float}}'''
    dict_item = {}
    # Phase Boots48,48024,23950.00
    soup = bs4.BeautifulSoup(table.text, "lxml")
    items = soup.find("p").text.replace("ПредметМатчиПобедыДоля побед", "").split("%")
    items.pop()
    for i in range(len(items)):
        # print(items[i])
        name = "".join([j for j in items[i] if not j.isnumeric() and j not in (".", ",")])
        x = items[i].replace(name, "")
        # params_item = list(map(float, [x[0:6].replace(",", "."), x[6:12].replace(",", "."), x[12:]]))
        # print(params_item)
        dict_item[name] = {"Матчи": "", "Победы": "", "Доля побед(%)": ""}
    # print(dict_item)
    # exit()
    return dict_item


# def pars_all_table_from_html():
#     pass


def picture_save(picture_url: str) -> None:
    # name=picture_url.replace("https://ru.dotabuff.com/heroes/assets/heroes/","")
    req = requests.get(picture_url, headers=headers, stream=True)
    if req.ok:
        print(req.ok)
        with open("picture//111.jpg", "wb") as file:
            for chunk in req.iter_content(chunk_size=1000):
                if chunk:
                    file.write(chunk)
    else:
        print(req.ok)


def pars_herous(pars_file: str):
    '''return список словарей, в которых храниться информация о герое(имя,
                                                                      ссылка на страницу героя)'''
    herou_soup = bs4.BeautifulSoup(pars_file, "lxml")
    herous_list = herou_soup.find("div", class_="hero-grid").find_all("a")
    herous_href_list = [f"https://ru.dotabuff.com/{href['href']}" for href in
                        herous_list]  # поулучаем ссылки для всех героев
    herous_name_list = [herou.text for herou in herous_list]

    # for herou_href in herous_href_list:
    #     print(herou_href)
    #     res = requests.get(herou_href, headers=headers)
    #     if res.ok:
    #         pass
    #     else:
    #         print("Не удаётся получить топ предметы для героя, ссылка не работает")

    # herous_imag_href = [
    #     f'https://ru.dotabuff.com/heroes{herou.find("div", class_="hero")["style"].replace("background: url(", "").replace(")", "")}'
    #     for herou in herous_list]
    # print("imag:\n", *herous_imag_href,sep="\n")
    # print(herous_imag_href[0])
    # picture_save(herous_imag_href[0])
    # # exit()

    herous_list.clear()
    if len(herous_name_list) == len(herous_href_list):
        for i in tqdm(range(len(herous_name_list))):
            herou_data_list = pars_herou_page_tables(herous_href_list[i])
            ##########
            # if i > 5:
            #     break
            ###########
            if herou_data_list:
                herous_list.append(
                    {"name": herous_name_list[i], "href": herous_href_list[i], "Предметы": herou_data_list[0]})
            else:
                herous_list.append({"name": herous_name_list[i], "href": herous_href_list[i]})
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
    x = pars_items_name_price(read_file(file_name))
    write_json(x, "json//item_json.json")


def create_herous_json(file_name):
    x = pars_herous(read_file(file_name))
    write_json(x, "json//herous_json.json")


def check_files():
    '''Проверка нужных директорий и файлов'''
    if not os.path.exists("picture"):  # проверка наличия папки с изображениями
        os.mkdir("picture")
    if not os.path.exists("json"):  # проверка наличия папки с json
        os.mkdir("json")
    if not os.path.exists("html"):  # проверка наличия папки с html
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
    # pars_herou_page()


if __name__ == '__main__':
    main()
