import bs4
import parser_config
import grequests
import requests
import json
from tqdm import tqdm
import copy
import os
from loguru import logger

debug_logger = logger.add("..//..//logs//debug_log.log", level="DEBUG")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 'Chrome/89.0.4389.72 Safari/537.36"}

session = requests.Session()
session.headers.update(headers)
g_session = grequests.Session()
g_session.headers.update(headers)


def get_content_requests(url) -> requests.models.Response or None:
    '''Получает код страницы по адресу, указанному в url'''
    response = session.get(url=url, headers=headers, timeout=50)
    # print(response.status_code)
    # print(response.headers)
    if response.ok:
        return response
    else:
        # print("программе не удалось совершить запрос к сайту")
        return None


def get_content_grequests(url_list: tuple):
    req_list = (g_session.get(url, headers=headers, timeout=10) for url in url_list)
    response = grequests.map(req_list)
    if len(response) == response.count(None):
        return None
    else:
        return response


def save_file(req, name: str) -> None:
    '''Записывает переданный в функцию код страницы в текстовый файл'''
    name = f"{parser_config.html_path}//" + name
    # name = "html//" + name
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


def get_item_href_list(pars_file: str):
    '''получает на вход имя файла с html кодом страницы
    return список ссылок на страницы предметов'''
    try:
        soup = bs4.BeautifulSoup(pars_file, "lxml")
        item_list = soup.find("table", class_="sortable").find_all("td", class_="cell-xlarge")
        item_href_list = [f"https://ru.dotabuff.com{i.find('a')['href']}" for i in item_list]
        # print(*item_href_list[:10], sep="\n")
        return copy.deepcopy(item_href_list)
    except TypeError:
        return None
    # except:
    #     return None


def pars_items_name_price(pars_file: str) -> dict or None:
    '''Находит цену и название предметов'''
    item_href_list = get_item_href_list(pars_file)
    # print("res", get_content_requests(item_href_list[0]))

    # region grequests
    # greq_list = (grequests.get(url, headers=headers) for url in item_href_list)
    # response = grequests.map(greq_list)
    #
    # # print(response)
    # # print(response[0].headers)
    # # exit()
    # item_list = []
    # for i, herou in tqdm(enumerate(response)):
    #     if herou is not None:
    #         herou_soup = bs4.BeautifulSoup(herou.text, "lxml")
    #         article = herou_soup.find("div", class_="embedded-tooltip")
    #         name = article.find("div", class_="name").text
    #         price = article.find("div", class_="price").text
    #         item_list.append({"name": name, "price": price, "href": item_href_list[i]})
    # print(*item_list, sep="\n")
    # endregion

    # region requests

    item_list = []
    for href in tqdm(item_href_list):
        req = get_content_requests(href)

        if req.ok:
            href_soup = bs4.BeautifulSoup(req.text, "lxml")
            article = href_soup.find("div", class_="embedded-tooltip")
            name = article.find("div", class_="name").text
            price = article.find("div", class_="price").text
            item_list.append({"name": name, "price": price, "href": href})
        else:
            print("не рабочая ссылка")

        #########
        if len(item_list) == 10 and parser_config.test_config is True:
            break
        #########
    # endregion

    if item_list:
        return copy.deepcopy(item_list)
    else:
        return None


def pars_herou_page(herou_href: str = "https://ru.dotabuff.com/heroes/abaddon") -> list or None:
    '''Принимает на вход ссылку на страницу героя'''
    output = []
    req = get_content_requests(herou_href)
    # print(req)
    # print(*req.headers.items(), sep="\n")
    if req:  # если None то значит не прошел запрос(get_content вернул None)
        soup = bs4.BeautifulSoup(req.text, "lxml")  # кладём страницу героя в объект bs4
        table_html = soup.find_all("table")  # получаем все таблицы со стрницы

        ####
        # for i in range(len(table_html)):
        #     with open(f"table_html_{i}.txt", "w", encoding="utf-8") as file:
        #         file.write(f"{table_html[i]}")
        ####

        # парсинг необходимых данных(здесь можно добавить в output парсинг других таблиц или других структур со страницы героя
        output.append(pars_herou_favorit_items_table(table_html[2]))  # 2-номер таблицы с предметами
        output.append(pars_herou_skils(soup))
        ########

        # print(output)
        return output
    else:
        print("не рабочая ссылка")
        return None


def pars_herou_skils(soup):
    skils_data = soup.find("article", class_="skill-choices smaller")
    # print(skils_data)
    skils_dict = {}
    for skil in skils_data.find_all("div", class_="skill"):
        img = skil.find("a").find("img")
        name = img["alt"]
        skil_learn = skil.find_all("div", class_="entry choice")
        # print(skil_learn)
        skil_learn = tuple(int(i.text) for i in skil_learn)
        picture = picture_save(f"https://ru.dotabuff.com{img['src']}", name)
        skils_dict[name] = {"Прокачка": skil_learn, "img_path": picture}
    # print(skils_dict)
    return skils_dict


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

# @logger.catch()
def picture_save(picture_url: str, name) -> None:
    name = name.replace("/", "_")
    # name=picture_url.replace("https://ru.dotabuff.com/heroes/assets/heroes/","")
    req = requests.get(picture_url, headers=headers, stream=True, timeout=10)
    if req.ok:
        # print(req.ok)
        with open(f"{parser_config.picture_path}//{name}.jpg", "wb") as file:
            for chunk in req.iter_content(chunk_size=1000):
                if chunk:
                    file.write(chunk)
        return f"{parser_config.picture_path}//{name}.jpg"
    else:
        None


# def get_herous_href_list():
#     pass

def pars_herous(pars_file: str):
    '''return список словарей, в которых храниться информация о герое(имя,
                                                                      ссылка на страницу героя)'''
    herou_soup = bs4.BeautifulSoup(pars_file, "lxml")
    herous_list = herou_soup.find("div", class_="hero-grid").find_all("a")
    # print(herous_list)
    herous_href_list = [f"https://ru.dotabuff.com{href['href']}" for href in
                        herous_list]  # поулучаем ссылки для всех героев
    herous_name_list = [herou.text for herou in herous_list]

    # print(herous_href_list)

    herous_list.clear()
    if len(herous_name_list) == len(herous_href_list):
        for i in tqdm(range(len(herous_name_list))):
            herou_data_list = pars_herou_page(herous_href_list[i])
            ##########
            if i > 5 and parser_config.test_config is True:
                break
            ###########
            if herou_data_list:
                herous_list.append(
                    {"name": herous_name_list[i], "href": herous_href_list[i], "Предметы": herou_data_list[0], "Скилы":
                        herou_data_list[1]})
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
    write_json(x, f"{parser_config.json_path}//item_json.json")


def create_herous_json(file_name):
    x = pars_herous(read_file(file_name))
    write_json(x, f"{parser_config.json_path}//herous_json.json")


def check_files():
    '''Проверка нужных директорий и файлов'''
    if not os.path.exists(parser_config.picture_path):  # проверка наличия папки с изображениями
        os.mkdir(parser_config.picture_path)
    if not os.path.exists(parser_config.json_path):  # проверка наличия папки с json
        os.mkdir(parser_config.json_path)
    if not os.path.exists(parser_config.html_path):  # проверка наличия папки с html
        os.mkdir(parser_config.html_path)
    if not os.path.exists(parser_config.logs_path):  # проверка наличия папки с изображениями
        os.mkdir(parser_config.logs_path)

    if not os.path.exists(f"{parser_config.json_path}//items_json.json"):  # проверка на наличие item_json
        if not os.path.exists(f"{parser_config.html_path}//html_item.txt"):
            save_file(get_content_requests("https://ru.dotabuff.com/items"), "html_item.txt")
        create_item_json(f"{parser_config.html_path}//html_item.txt")

    if not os.path.exists(f"{parser_config.json_path}//herous_json.json"):  # проверка на наличие herou_json
        if not os.path.exists(f"{parser_config.html_path}//html_herous.txt"):
            save_file(get_content_requests("https://ru.dotabuff.com/heroes"), "html_herous.txt")
        create_herous_json(f"{parser_config.html_path}//html_herous.txt")
    if all([os.path.exists(parser_config.logs_path),
            os.path.exists(parser_config.html_path),
            os.path.exists(parser_config.json_path),
            os.path.exists(parser_config.picture_path)]):
        print("успешная проверка")
    else:
        print("нет одной из необходимых директорий")


def main():
    check_files()
    # pars_herou_page()
    # get_content_grequests(("https://ru.dotabuff.com/heroes", 0, 1, "afeaf", "https://ru.dotabuff.com/heroes"))
    # pars_items_name_price(read_file("html//html_item.txt"))
    # pars_herous(read_file("html//html_herous.txt"))
    pass


def test():
    pass


if __name__ == '__main__':
    main()
