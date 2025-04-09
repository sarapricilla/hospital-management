import pymysql
import sys
from util.property_util import PropertyUtil

class DBConnection:
    connection = None

    @staticmethod
    def get_connection():
        if DBConnection.connection is None:
            try:
                props = PropertyUtil.get_property_string('db.properties')
                DBConnection.connection = pymysql.connect(
                    host=props['host'],
                    user=props['user'],
                    password=props['password'],
                    database=props['database'],
                    port=props['port']
                )
            except pymysql.MySQLError as e:
                print(f"Database Connection Error: {e}")
                sys.exit(1)
        return DBConnection.connection
