import os

import Parser_Class
import bs4
import copy
from tqdm import tqdm
import parser_config


class Parser_Item_Class(Parser_Class.Parser):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_item_href_list(pars_file: str):
        '''получает на вход переменную с html кодом страницы
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

    def pars_data_about_items(self, pars_file: str) -> dict or None:
        '''Находит цену и название предметов
        получает на вход переменную с html кодом страницы'''
        item_href_list = self.get_item_href_list(pars_file)
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
            req = self.get_content_requests(href)

            if req.ok:
                href_soup = bs4.BeautifulSoup(req.text, "lxml")
                article = href_soup.find("div", class_="embedded-tooltip")
                name = article.find("div", class_="name").text
                price = article.find("div", class_="price").text
                item_list.append({"name": name, "price": float(price.replace(",", ".")), "href": href})
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

    def create_item_json(self, file_name) -> None:
        x = self.pars_data_about_items(self.read_file(file_name))
        self.write_json(x, f"{parser_config.json_path}//item_json.json")

    def check(self):
        if not os.path.exists(f"{parser_config.json_path}//items_json.json"):  # проверка на наличие item_json
            if not os.path.exists(f"{parser_config.html_path}//html_item.txt"):
                self.save_file(self.get_content_requests("https://ru.dotabuff.com/items"), "html_item.txt")
            self.create_item_json(f"{parser_config.html_path}//html_item.txt")


if __name__ == '__main__':
    c = Parser_Item_Class()
    print(c.pars_data_about_items(c.read_file("..//..//html//html_item.txt")))
