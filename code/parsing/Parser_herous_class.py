import os
import bs4
from tqdm import tqdm
import Parser_Class
import parser_config


class Parser_Herous_Class(Parser_Class.Parser):
    def __init__(self):
        super().__init__()

    def pars_herou_page(self, herou_href: str = "https://ru.dotabuff.com/heroes/abaddon") -> list or None:
        '''Принимает на вход ссылку на страницу героя'''
        output = []
        req = self.get_content_requests(herou_href)
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
            output.append(self.pars_herou_favorit_items_table(table_html[2]))  # 2-номер таблицы с предметами
            output.append(self.pars_herou_skils(soup))
            ########

            # print(output)
            return output
        else:
            print("не рабочая ссылка")
            return None

    def pars_herou_skils(self, soup):
        skils_data = soup.find("article", class_="skill-choices smaller")
        # print(skils_data)
        skils_dict = {}
        for skil in skils_data.find_all("div", class_="skill"):
            img = skil.find("a").find("img")
            name = img["alt"]
            skil_learn = skil.find_all("div", class_="entry choice")
            # print(skil_learn)
            skil_learn = tuple(int(i.text) for i in skil_learn)
            picture = self.picture_save(f"https://ru.dotabuff.com{img['src']}", name)
            skils_dict[name] = {"Прокачка": skil_learn, "img_path": picture}
        # print(skils_dict)
        return skils_dict

    @staticmethod
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

    def pars_data_about_herous(self, pars_file: str):
        '''return список словарей, в которых храниться вся полученная информация о героях(имя,
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
                herou_data_list = self.pars_herou_page(herous_href_list[i])
                ##########
                if i > 5 and parser_config.test_config is True:
                    break
                ###########
                if herou_data_list:
                    herous_list.append(
                        {"name": herous_name_list[i], "href": herous_href_list[i], "Предметы": herou_data_list[0],
                         "Скилы":
                             herou_data_list[1]})
                else:
                    herous_list.append({"name": herous_name_list[i], "href": herous_href_list[i]})
            return herous_list
        else:
            return None

    def create_herous_json(self, file_name):
        x = self.pars_data_about_herous(self.read_file(file_name))
        self.write_json(x, f"{parser_config.json_path}//herous_json.json")

    def check(self):
        if not os.path.exists(f"{parser_config.json_path}//herous_json.json"):  # проверка на наличие herou_json
            if not os.path.exists(f"{parser_config.html_path}//html_herous.txt"):
                self.save_file(self.get_content_requests("https://ru.dotabuff.com/heroes"), "html_herous.txt")
            self.create_herous_json(f"{parser_config.html_path}//html_herous.txt")
