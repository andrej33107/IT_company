import sys
import hashlib
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from db_connection import get_connection

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация пользователя")
        self.resize(300, 250)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Поле логина
        layout.addWidget(QLabel("Логин:"))
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("минимум 3 символа")
        layout.addWidget(self.input_login)
        
        # Поле пароля
        layout.addWidget(QLabel("Пароль:"))
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("минимум 4 символа")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)
        
        # Подтверждение пароля
        layout.addWidget(QLabel("Подтвердите пароль:"))
        self.input_password_confirm = QLineEdit()
        self.input_password_confirm.setPlaceholderText("повторите пароль")
        self.input_password_confirm.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password_confirm)
        
        # Информация о роли
        role_info = QLabel("Все новые пользователи получают роль 'user'")
        role_info.setStyleSheet("color: gray; font-size: 10px;")
        role_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(role_info)
        
        # Кнопка регистрации
        self.btn_register = QPushButton("Зарегистрироваться")
        self.btn_register.clicked.connect(self.register_user)
        layout.addWidget(self.btn_register)
        
        self.setLayout(layout)
    
    def register_user(self):
        """Регистрация нового пользователя"""
        username = self.input_login.text().strip()
        password = self.input_password.text().strip()
        password_confirm = self.input_password_confirm.text().strip()
        
        # Валидация
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "Ошибка", "Логин минимум 3 символа!")
            return
        
        if len(password) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль минимум 4 символа!")
            return
        
        if password != password_confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Ошибка подключения к БД")
            return
        
        cursor = conn.cursor()
        try:
            # Проверка существующего пользователя
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь уже существует!")
                return
            
            # Хеширование пароля
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Запрос с указанием роли (все новые пользователи - 'user')
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_password, 'user')
            )
            conn.commit()
            
            QMessageBox.information(self, "Успех",
                                  "Регистрация успешна!\nВы получили роль 'user'.")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка регистрации:\n{e}")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_())