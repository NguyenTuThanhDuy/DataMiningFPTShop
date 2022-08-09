import psycopg2
class Database:
    db_name = "postgres"
    host = "127.0.0.1"
    username = "postgres"
    password = "chemgiono1"
    port = '5432'

    def __init__(self):
        self.connection = psycopg2.connect( host = self.host,
                                            user = self.username,
                                            password = self.password,
                                            dbname = self.db_name,
                                            port = self.port )
        self.cursor = self.connection.cursor()

    def execute_query(self,query):
        cursor = self.cursor
        cursor.execute(query)
        self.connection.commit()
    
    def __del__(self):
        self.connection.close()