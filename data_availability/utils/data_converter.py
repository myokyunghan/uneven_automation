import os
import psycopg2
import xml.etree.cElementTree as ET
from dotenv import load_dotenv
from utils.data_loader import DataLoader
from constants import CONSTANTS


def indexed_file_path(dir_, index):
    """

    Args:
        dir_: a str
        index: an int

    Returns:
        a str
    """
    file_name = str(index) + ".json"
    to_return = os.path.join(dir_, file_name)
    return to_return


class DBConverter:
    def __init__(self):
        self.batch_size = 200000
        self.fetch_size = 100
        self.loop_limit = 1000000000
        self.data_loader = DataLoader()

    @staticmethod
    def construct_query(post_type=1, tag=None, time_start=None, time_end=None):
        """

        Args:
            post_type: an int, default=1
            tag: a str (optional)
            time_start: a str with YYYY.MM.DD format (optional)
            time_end: a str with YYYY.MM.DD format (optional)

        Returns:
            a query str
        """
        to_return = (
            "SELECT posts.id, posts.creationdate, posts.title,"
            "posts.tags, posts.viewcount, posts.answercount, "
            "posts.commentcount "
            "FROM posts "
            f"WHERE posts.posttypeid = '{post_type}'"
        )
        if tag is not None:
            to_return += f" AND posts.tags LIKE '%<{tag}>%'"
        if time_start is not None:
            to_return += (f" AND posts.creationdate "
                          f">= TO_TIMESTAMP('{time_start}', 'YYYY.MM.DD')")
        if time_end is not None:
            to_return += (f" AND posts.creationdate "
                          f"< TO_TIMESTAMP('{time_end}', 'YYYY.MM.DD')")
        return to_return

    def open_connection(self):
        """

        Returns:
            an open connection and its cursor
        """
        load_dotenv()
        password = os.environ.get("POSTGRES_PASSWORD")
        print("[Postgres] Connecting to Postgres")
        conn = psycopg2.connect(dbname=CONSTANTS.db_name,
                                host=CONSTANTS.db_host,
                                user=CONSTANTS.db_user,
                                port=CONSTANTS.db_port,
                                password=password)
        cursor = conn.cursor()
        return conn, cursor

    def close_connection(self, conn, cursor):
        """

        Args:
            conn: an open postgres connection
            cursor: an open cursor from conn

        Returns:
            None
        """
        print("[Postgres] Closing Postgres connection")
        cursor.close()
        conn.close()

    def save_indexed_json(self, dir_, index, data_):
        """

        Args:
            dir_: a str
            index: an int
            data_: a dict or a list of dict

        Returns:
            None
        """
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        self.data_loader.save_json(indexed_file_path(dir_, index), data_)

    def prepare_dicts_to_save(self, column_names, contents):
        """

        Args:
            column_names: a list of str
            contents: a list of lists of various types

        Returns:
            a list of dict

        """
        for kdx, content in enumerate(contents):
            contents[kdx] = [str(x) for x in content]
        to_return = [dict(zip(column_names, content)) for content in contents]
        return to_return

    @staticmethod
    def check_dir_exists(dir_):
        """

        Args:
            dir_: a str

        Returns:
            a bool
        """
        if os.path.exists(dir_):
            print(f"WARNING: directory {dir_} already exists")
            return True
        return False

    def execute_and_fetch_all(self, cursor, query):
        """

        Args:
            cursor: a cursor object
            query: a query str

        Returns:
            a dict
        """
        # conn, cursor = self.open_connection()
        cursor.execute(query)
        column_names = [column[0] for column in cursor.description]
        contents = cursor.fetchall()
        to_return = self.prepare_dicts_to_save(column_names, contents)
        # self.close_connection(conn, cursor)
        return to_return

    def execute_and_save(self, query, dir_):
        """

        Args:
            query: a query str to execute
            dir_: a str

        Returns:
            None
        """
        self.check_dir_exists(dir_)
        conn, cursor = self.open_connection()
        cursor.execute(query)
        column_names = [column[0] for column in cursor.description]
        idx, loop_count = 0, 0
        to_save = []
        contents = cursor.fetchmany(self.fetch_size)
        while len(contents) > 0 and loop_count < self.loop_limit:
            contents = self.prepare_dicts_to_save(column_names, contents)
            to_save += contents
            if len(to_save) >= self.batch_size:
                self.save_indexed_json(dir_, idx, to_save)
                idx += 1
                to_save = []
            contents = cursor.fetchmany(self.fetch_size)
            loop_count += 1
        if to_save:
            self.save_indexed_json(dir_, idx, to_save)
        self.close_connection(conn, cursor)


class XMLConverter:
    def __init__(self):
        self.batch_size = 1000
        self.loop_limit = 5000
        self.data_loader = DataLoader()

    def __call__(self, xml_path, dir_, default_keys):
        self.iterparse_and_save(xml_path, dir_, default_keys)

    def save_indexed_json(self, dir_, index, data_):
        """

        Args:
            dir_: a str
            index: an int
            data_: a dict or a list of dict

        Returns:
            None
        """
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        self.data_loader.save_json(indexed_file_path(dir_, index), data_)

    @staticmethod
    def check_dir_exists(dir_):
        """

        Args:
            dir_: a str

        Returns:
            a bool
        """
        if os.path.exists(dir_):
            print(f"WARNING: directory {dir_} already exists")
            return True
        return False

    @staticmethod
    def check_keys(default_keys, attrib_keys):
        """

        Args:
            default_keys: a list of str
            attrib_keys: a list of str

        Returns:
            a bool
        """
        if not set(attrib_keys).issubset(default_keys):
            print(f"WARNING: default keys are {default_keys},"
                  f"but got {attrib_keys}")
            return False
        return True

    def iterparse_and_save(self, xml_path, dir_, default_keys=None):
        """

        Args:
            xml_path: a str
            dir_: a str
            default_keys: a list of str

        Returns:
            None
        """
        idx, loop_count = 0, 0
        to_save = []
        for _, elem in ET.iterparse(xml_path):
            if elem.tag != 'row':
                continue
            loop_count += 1
            if loop_count > self.loop_limit:
                break
            if default_keys is not None:
                self.check_keys(default_keys, elem.attrib.keys())
            to_save.append(elem.attrib)
            if len(to_save) >= self.batch_size:
                self.save_indexed_json(dir_, idx, to_save)
                idx += 1
                to_save = []
        if to_save:
            self.save_indexed_json(dir_, idx, to_save)


if __name__ == '__main__':
    TIMESTAMPS = CONSTANTS.monthly_timestamps
    save_dir = "../data/questions_with_statistics"
    os.makedirs(save_dir, exist_ok=True)
    db_converter = DBConverter()
    conn, cursor = db_converter.open_connection()
    for i in range(len(TIMESTAMPS)-1):
        time_start = TIMESTAMPS[i]
        time_end = TIMESTAMPS[i+1]
        query_ = db_converter.construct_query(time_start=time_start,
                                              time_end=time_end)
        print(query_)
        to_save = db_converter.execute_and_fetch_all(cursor, query_)
        DataLoader.save_json(f'{save_dir}/{i}.json', to_save)


