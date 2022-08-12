import datetime
import sqlite3 as sqlite
import parser_config as config
import json


class Parser_db():
    def __init__(self, db_name: str):
        self.db_name = db_name
        # db = self.db_connect(self.db_name)
        self.db_insert_all()
        # print(self.db_select(db, "herou", "max(name) , min(name)","href='https://ru.dotabuff.com/heroes/abaddon'"))

    def db_connect(self, db_name: str, timeout=10):
        '''возвращает экземпляр sqlite.Connection  если получилось подключиться к базе данных, иначе false'''
        try:
            result_connect = sqlite.connect(db_name, timeout=timeout)
            print(result_connect)
        except sqlite.Error as error:
            print(error)
            result_connect = False
        finally:
            return result_connect

    def db_insert_all(self):
        db = self.db_connect(self.db_name)
        if db:

            with open("..//..//json//herous_json.json", "r") as file:
                json_file = json.load(file)
                # print(json_file)
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for herou in json_file:  # проходим по списку героев
                print("herou=", herou)

                try:
                    self.db_insert_with_cursor(db, "herou", "name, date, href",
                                               (herou["name"], date, herou["href"]))  # заполняем таблицу herou

                    print(f"{herou['Скилы']=}")

                    skils_list = list(herou["Скилы"].items())
                    print(skils_list)

                    for i, skil in enumerate(skils_list):
                        print(f"{skil=}")
                        self.db_insert_with_cursor(db, "skils_name", "name, date",
                                                   (skil[0], date))  # заполнение таблицы skils_name

                        self.db_insert_with_cursor(db, "skils",
                                                   "skils_name, date, img_path, skil_num, id_herou",
                                                   (skil[0], date, skil[1]["img_path"], i + 1,
                                                    herou["name"]))  # заполнение таблицы skils

                        for lvl_up in skil[1]["Прокачка"]:
                            self.db_insert_with_cursor(db, "skils_up", " id_skil, date, lvl_up", (
                                self.db_select(db, "skils", "max(id)")[0][0], date,
                                lvl_up))  # заполнение таблицы skils_up


                # except ZeroDivisionError:
                #     pass
                except sqlite.IntegrityError:
                    continue

        else:

            print("база данных не подключена")
        if db:
            db.close()

    def db_insert_with_cursor(self, db: sqlite.Connection, table_name: str, columns: str, data_list: tuple):
        '''пример insert запроса:
        self.db_insert(db, "herou", ("name", "href", "type"), (1, 2, 3))'''
        cursor = db.cursor()
        cursor.execute('''pragma foreign_key=on;''')
        x = f"insert into {table_name} ({columns}) values {data_list};"
        # x = x.replace("'", "")
        print(x)
        cursor.execute(x)
        db.commit()
        cursor.close()

    def db_select(self, db: sqlite.Connection, table_name: str, columns: str, where: str = ""):
        cursor = db.cursor()
        cursor.execute('''pragma foreign_key=on;''')
        if where != "":
            query = f"select {columns} from {table_name} where {where};"
        else:
            query = f"select {columns} from {table_name}"
        print(query)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        print(f"{result=}")
        return result

    # def insert_herou(self, db: sqlite.Connection, ):
    #     # with db.cursor() as cursor:
    #     #     cursor.execute('''''')
    #     #     # self.db_insert(db, "herou", ("name", "date", "href"),
    #     #     #                (herou["name"], date, herou["href"]))  # заполняем таблицу herou
    #     pass
    #
    # def insert_skils(self):
    #     pass
    #
    # def insert_skils_name(self):
    #     pass
    #
    # def insert_skils_up(self):
    #     pass
    #
    # def insert_herou_item_top12(self):
    #     pass
    #
    # def insert_items(self):
    #     pass
    #
    # def insert_items_name(self):
    #     pass
    #
    # def insert_order(self):
    #     pass


if __name__ == '__main__':
    db = Parser_db(config.db_name)
