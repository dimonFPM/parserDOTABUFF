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
        return список ссылок на страницы всех предметов'''
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

    def pars_item_page(self, url):
        # print(f"{url=}")
        output = {}
        stats_list = []
        req = self.get_content_requests(url)
        if req.ok:
            soup = bs4.BeautifulSoup(req.text, "lxml")
            article = soup.find("div", class_="embedded-tooltip")
            name = article.find("div", class_="name").text
            price = article.find("div", class_="price").text
            img_url = article.find("a").find("img")["src"]
            img_path = self.picture_save(f"https://ru.dotabuff.com{img_url}", name)
            # print(article)
            stats = article.find("div", class_="stats")
            if stats:
                stats = stats.find_all("div", class_="stat attribute")
                for st in stats:
                    stats_list.append(st.text)
            # print(stats)
            # exit()

            descriptions_activ = article.find("div", class_="description-block активное")
            descriptions_pasiv = article.find("div", class_="description-block пассивное")
            order = article.find("div", class_="item-build item-builds-from")
            if order:
                order= order.find("div", class_="order").find_all("img")
                # order = order.find_all("img")
                order = tuple(i["alt"] for i in order)
            else:
                order = None
            if descriptions_pasiv:
                descriptions_pasiv = descriptions_pasiv.text.replace("Пассивное: ", "")
            else:
                descriptions_pasiv = None
            if descriptions_activ:
                descriptions_activ = descriptions_activ.text.replace("Активное: ", "")
            else:
                descriptions_activ = None

            output["name"] = name
            output["price"] = price
            output["href"] = url
            output["img_path"] = img_path
            output["stats"] = tuple(stats_list)
            output["description"] = {"Активное": descriptions_activ, "Пасивное": descriptions_pasiv}
            output["order:"] = order
            # print(output)
        if output:
            return output
        else:
            None

    def pars_data_about_items(self, pars_file: str) -> dict or None:
        '''получает на вход переменную с html кодом страницы'''
        item_href_list = self.get_item_href_list(pars_file)
        # print("res", get_content_requests(item_href_list[0]))

        # region grequests
        # greq_list = (grequests.get(url, headers=headers) for url in item_href_list)
        # response = grequests.map(greq_list)
        #
        # # print(response)
        # # print(response[0].headers)
        # # exit()
        # items_list = []
        # for i, herou in tqdm(enumerate(response)):
        #     if herou is not None:
        #         herou_soup = bs4.BeautifulSoup(herou.text, "lxml")
        #         article = herou_soup.find("div", class_="embedded-tooltip")
        #         name = article.find("div", class_="name").text
        #         price = article.find("div", class_="price").text
        #         items_list.append({"name": name, "price": price, "href": item_href_list[i]})
        # print(*items_list, sep="\n")
        # endregion

        # region requests

        items_list = []
        for href in tqdm(item_href_list):
            items_list.append(self.pars_item_page(href))

            #########
            if len(items_list) == 10 and parser_config.test_config is True:
                break
            #########
        # endregion

        if items_list:
            return copy.deepcopy(items_list)
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
    # c.pars_item_page("https://ru.dotabuff.com/items/aghanims-shard")
    c.pars_item_page("https://ru.dotabuff.com/items/silver-edge")

    # print(c.pars_data_about_items(c.read_file("..//..//html//html_item.txt")))
