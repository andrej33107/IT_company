import psycopg2

def get_connection():
    """
    Установка соединения с базой данных IT компании
    """
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='it_company',
            user='postgres',
            password='12345',
            port='5432'
        )
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к БД it_company: {e}")
        return None

def init_database():
    """
    Проверка подключения к базе данных
    """
    conn = get_connection()
    if conn:
        print("✅ Успешное подключение к базе данных it_company")
        conn.close()
        return True
    else:
        print("❌ Не удалось подключиться к базе данных it_company")
        return False


if __name__ == "__main__":
    init_database()