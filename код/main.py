import sys

try:
    from PyQt5.QtWidgets import QApplication
    from auth_window import AuthWindow
    from db_connection import get_connection, init_database
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Установите зависимости: pip install psycopg2-binary PyQt5")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

def check_and_init_roles():
    """
    Проверка и инициализация ролей при запуске
    """
    conn = get_connection()
    if not conn:
        print("❌ Не удалось подключиться к БД для проверки ролей")
        return False
    
    cursor = conn.cursor()
    try:
        # Проверяем, существует ли колонка role
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='users' AND column_name='role'
        """)
        
        if not cursor.fetchone():
            print("🔧 Обнаружено отсутствие колонки 'role'. Инициализация...")
            
            # Добавляем колонку role
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            print("   ✓ Колонка 'role' добавлена")
            
            # Проверяем существование пользователя admin
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count > 0:
                # Устанавливаем роль admin для существующего пользователя admin
                cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                print("   ✓ Роль 'admin' назначена для пользователя admin")
            else:
                # Создаем пользователя admin
                import hashlib
                hashed_password = hashlib.sha256("admin".encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    ('admin', hashed_password, 'admin')
                )
                print("   ✓ Пользователь 'admin' создан с паролем 'admin'")
            
            # Устанавливаем роль user для остальных пользователей
            cursor.execute("UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''")
            
            conn.commit()
            print("✅ Система ролей успешно инициализирована")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации ролей: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """
    Основная функция запуска приложения
    """
    print("=" * 50)
    print("IT Компания - Система управления")
    print("=" * 50)
    
    # Проверка подключения к БД
    print("\n🔍 Проверка подключения к базе данных...")
    if not init_database():
        print("❌ ОШИБКА: Не удалось подключиться к базе данных!")
        print("\nПроверьте:")
        print("1. Запущен ли PostgreSQL")
        print("2. Существует ли база данных 'it_company'")
        print("3. Правильность параметров в db_connection.py")
        input("\nНажмите Enter для выхода...")
        return 1
    
    print("✅ Подключение к БД успешно")
    
    # Проверка и инициализация системы ролей
    print("\n🔍 Проверка системы ролей...")
    check_and_init_roles()
    
    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("IT Компания")
    app.setApplicationDisplayName("IT Компания - Система управления")
    
    # Создание и отображение окна авторизации
    print("\n🚀 Запуск приложения...")
    window = AuthWindow()
    window.show()
    
    # Запуск основного цикла
    return app.exec_()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)