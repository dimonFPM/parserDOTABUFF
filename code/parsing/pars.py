import parser_config
import os
from loguru import logger
import Parser_herous_class
import Parser_items_class

debug_logger = logger.add("..//..//logs//debug_log.log", level="DEBUG")


def check_files():
    try:
        herous_parser = Parser_herous_class.Parser_Herous_Class()
        items_parser = Parser_items_class.Parser_Item_Class()

        '''Проверка нужных директорий'''
        if not os.path.exists(parser_config.picture_path):  # проверка наличия папки с изображениями
            os.mkdir(parser_config.picture_path)
        if not os.path.exists(parser_config.json_path):  # проверка наличия папки с json
            os.mkdir(parser_config.json_path)
        if not os.path.exists(parser_config.html_path):  # проверка наличия папки с html
            os.mkdir(parser_config.html_path)
        if not os.path.exists(parser_config.logs_path):  # проверка наличия папки с изображениями
            os.mkdir(parser_config.logs_path)

        items_parser.check()
        herous_parser.check()

        if all([os.path.exists(parser_config.logs_path),
                os.path.exists(parser_config.html_path),
                os.path.exists(parser_config.json_path),
                os.path.exists(parser_config.picture_path)]):
            print("успешная проверка")
        else:
            print("нет одной из необходимых директорий")
    except Exception as error:

        print("не получилось проверить наличий нужных деректория и файлов")


def main():
    check_files()
    # pars_herou_page()
    # get_content_grequests(("https://ru.dotabuff.com/heroes", 0, 1, "afeaf", "https://ru.dotabuff.com/heroes"))
    # pars_items_name_price(read_file("html//html_item.txt"))
    # pars_herous(read_file("html//html_herous.txt"))
    pass


if __name__ == '__main__':
    main()
