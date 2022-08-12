import parser_config
import grequests
import requests
import json


class Parser():

    def __init__(self):
        # self.result_json = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 'Chrome/89.0.4389.72 Safari/537.36"}

        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.g_session = grequests.Session()
        self.g_session.headers.update(self.headers)

    def get_content_requests(self, url) -> requests.models.Response or None:
        '''Получает код страницы по адресу, указанному в url'''
        response = self.session.get(url=url, headers=self.headers, timeout=50)
        # print(response.status_code)
        # print(response.headers)
        if response.ok:
            return response
        else:
            # print("программе не удалось совершить запрос к сайту")
            return None

    def get_content_grequests(self, url_list: tuple):
        req_list = (self.g_session.get(url, headers=self.headers, timeout=10) for url in url_list)
        response = grequests.map(req_list)
        if len(response) == response.count(None):
            return None
        else:
            return response

    @staticmethod
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

    @staticmethod
    def read_file(name):
        '''Читает код страницы из файла name'''
        with open(name, "r", encoding="utf-8") as file:
            return file.read()

    def picture_save(self, picture_url: str, name) -> None:
        name = name.replace("/", "_")
        # name=picture_url.replace("https://ru.dotabuff.com/heroes/assets/heroes/","")
        req = requests.get(picture_url, headers=self.headers, stream=True, timeout=10)
        if req.ok:
            # print(req.ok)
            with open(f"{parser_config.picture_path}//{name}.jpg", "wb") as file:
                for chunk in req.iter_content(chunk_size=1000):
                    if chunk:
                        file.write(chunk)
            return f"{parser_config.picture_path}//{name}.jpg"
        else:
            None

    @staticmethod
    def write_json(data_dict, name_json) -> None:
        if data_dict:
            with open(name_json, "w") as file:
                json.dump(data_dict, file, indent=4, ensure_ascii=False)
        else:
            print("Нет данных для записи")
