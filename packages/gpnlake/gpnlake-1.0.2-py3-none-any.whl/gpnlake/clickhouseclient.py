import clickhouse_connect

class CliсkHouseClient:
    def __init__(self, host, port, user, password):
        """
        Подключение к ClikHouse
        """
         
        try: 

            self.conn = clickhouse_connect.get_client(
                host=host,
                port=port,                
                user=user,
                password=password,
                verify=False
            )
        except Exception as err:
            raise ConnectionError(f"Ошибка подключения к базе данных: {err}")
    
    def read(self, query):
        """
        Выполняет SQL-запрос для возврата результатов
        :param query: SQL-запрос
        """
        try:
            self.conn.command(query) 
        except Exception as err:
            raise RuntimeError(f"Ошибка выполнения запроса: {err}")

    

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()