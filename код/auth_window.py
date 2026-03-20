import sys
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from db_connection import get_connection
from register_window import RegisterWindow


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация - IT Компания")
        self.resize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("IT Компания - Система управления")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Поле логина
        layout.addWidget(QLabel("Логин:"))
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Введите логин")
        layout.addWidget(self.input_login)
        
        # Поле пароля
        layout.addWidget(QLabel("Пароль:"))
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.check_login)
        buttons_layout.addWidget(self.btn_login)
        
        self.btn_register = QPushButton("Регистрация")
        self.btn_register.clicked.connect(self.show_register)
        buttons_layout.addWidget(self.btn_register)
        layout.addLayout(buttons_layout)
        
        # Тестовые данные
        test_label = QLabel("Тестовые данные: admin / admin")
        test_label.setStyleSheet("color: gray; font-size: 10px; margin: 10px;")
        test_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(test_label)
        
        self.setLayout(layout)
    
    def hash_password(self, password):
        """Хеширование пароля SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_login(self):
        """Проверка учетных данных"""
        username = self.input_login.text().strip()
        password = self.input_password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Ошибка подключения к БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, username, password, role FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()
            
            if not user:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
                return
            
            user_id, db_username, db_password, role = user
            
            # Проверка пароля
            if len(db_password) == 64:  # Хеш
                input_hash = self.hash_password(password)
                if input_hash != db_password:
                    QMessageBox.warning(self, "Ошибка", "Неверный пароль")
                    return
            else:  # Plain text
                if password != db_password:
                    QMessageBox.warning(self, "Ошибка", "Неверный пароль")
                    return
            
            # Успешная авторизация
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!\nРоль: {role}")
            self.open_main_menu(user_id, username, role)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при авторизации:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def show_register(self):
        """Открытие окна регистрации"""
        self.register_window = RegisterWindow()
        self.register_window.show()
    
    def open_main_menu(self, user_id, username, role):
        """Открытие главного меню"""
        from main_menu import MainMenu
        self.main_menu = MainMenu(username, role, user_id)
        self.main_menu.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())