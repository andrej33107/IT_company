import hashlib
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from db_connection import get_connection


class ChangePasswordWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle("Смена пароля")
        self.resize(400, 250)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel(f"Смена пароля для пользователя: {self.username}")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Форма
        form_layout = QFormLayout()
        
        # Текущий пароль
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.Password)
        self.current_password.setPlaceholderText("Введите текущий пароль")
        form_layout.addRow("Текущий пароль:", self.current_password)
        
        # Новый пароль
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Минимум 4 символа")
        form_layout.addRow("Новый пароль:", self.new_password)
        
        # Подтверждение пароля
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Повторите новый пароль")
        form_layout.addRow("Подтверждение:", self.confirm_password)
        
        layout.addLayout(form_layout)
        
        # Информация
        info_label = QLabel("Пароль должен содержать минимум 4 символа")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Кнопки
        self.btn_change = QPushButton("Сменить пароль")
        self.btn_change.clicked.connect(self.change_password)
        self.btn_change.setMinimumHeight(40)
        layout.addWidget(self.btn_change)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.close)
        layout.addWidget(self.btn_cancel)
        
        self.setLayout(layout)
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def change_password(self):
        """Смена пароля"""
        current = self.current_password.text()
        new = self.new_password.text()
        confirm = self.confirm_password.text()
        
        # Валидация
        if not current or not new or not confirm:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        if len(new) < 4:
            QMessageBox.warning(self, "Ошибка", "Новый пароль должен содержать минимум 4 символа!")
            return
        
        if new != confirm:
            QMessageBox.warning(self, "Ошибка", "Новые пароли не совпадают!")
            return
        
        if current == new:
            QMessageBox.warning(self, "Ошибка", "Новый пароль должен отличаться от текущего!")
            return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Ошибка подключения к БД")
            return
        
        cursor = conn.cursor()
        try:
            # Проверяем текущий пароль
            cursor.execute(
                "SELECT password FROM users WHERE id = %s",
                (self.user_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                QMessageBox.critical(self, "Ошибка", "Пользователь не найден!")
                return
            
            db_password = result[0]
            current_hash = self.hash_password(current)
            
            # Проверка пароля (поддерживаем и хеш, и plain text)
            if len(db_password) == 64:  # Хеш
                if current_hash != db_password:
                    QMessageBox.warning(self, "Ошибка", "Неверный текущий пароль!")
                    return
            else:  # Plain text
                if current != db_password:
                    QMessageBox.warning(self, "Ошибка", "Неверный текущий пароль!")
                    return
            
            # Обновляем пароль
            new_hash = self.hash_password(new)
            cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                (new_hash, self.user_id)
            )
            conn.commit()
            
            QMessageBox.information(self, "Успех", "Пароль успешно изменен!")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при смене пароля:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()