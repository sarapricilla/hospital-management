import configparser

class PropertyUtil:
    @staticmethod
    def get_property_string(filename):
        config = configparser.ConfigParser()
        config.read(filename)

        host = config.get('database', 'host')
        dbname = config.get('database', 'dbname')
        user = config.get('database', 'user')
        password = config.get('database', 'password')
        port = config.get('database', 'port')

        return {
            'host': host,
            'user': user,
            'password': password,
            'database': dbname,
            'port': int(port)
        }
