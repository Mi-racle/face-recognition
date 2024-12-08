import mysql.connector
from mysql.connector import Error

from db.config import DB_CONFIG


def insert_feature(name, feature):
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG, buffered=True)
        if connection.is_connected():
            cursor = connection.cursor()

            insert_query = """
                INSERT INTO tbl_feature (
                name, feature
                ) VALUES (
                %s, %s
                )
            """

            feature_str = f'[{",".join(feature.astype(str))}]'
            cursor.execute(insert_query, (name, feature_str))
            connection.commit()
            print(f'Entry successfully inserted into tbl_feature')

    except Error as e:
        connection = None
        print(f'Error: {e}')

    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()
            print('MySQL connection closed')


def get_all_features():
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG, buffered=True)
        if connection.is_connected():
            cursor = connection.cursor()

            insert_query = """
                SELECT * FROM tbl_feature
            """

            cursor.execute(insert_query)
            print(f'Entry successfully selected from tbl_feature')

            return cursor.fetchall()

    except Error as e:
        connection = None
        print(f'Error: {e}')

    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()
            print('MySQL connection closed')


def feature_exists(name):
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG, buffered=True)
        if connection.is_connected():
            cursor = connection.cursor()

            select_query = """
                SELECT * FROM tbl_feature WHERE name = %s 
            """

            cursor.execute(select_query, (name, ))

            res = cursor.fetchall()
            if res:
                print(f'Feature exists in tbl_feature')
                return True
            else:
                print(f'Feature does not exist in tbl_feature')
                return False

    except Error as e:
        connection = None
        print(f'Error: {e}')

    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()
            print('MySQL connection closed')