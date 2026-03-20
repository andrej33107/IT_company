from base_table_window import TableWindow
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QComboBox
from db_connection import get_connection
import hashlib

class UsersWindow(TableWindow):
    def __init__(self):
        super().__init__(
            "users",
            ["ID", "Логин", "Роль"],
            "Управление пользователями (только для admin)"
        )
    
    def load_data(self):
        """Загрузка данных из таблицы users"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, username, role
                FROM users
                ORDER BY id
            """)
            data = cursor.fetchall()
            
            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.table.setItem(row_idx, col_idx, item)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def update_data(self, row, data):
        """Обновление данных пользователя"""
        record_id = self.table.item(row, 0).text()
        username = data.get('Логин', '').strip()
        role = data.get('Роль', 'user').strip()
        
        # Нельзя изменять логин admin
        current_username = self.table.item(row, 1).text()
        if current_username == 'admin' and username != 'admin':
            QMessageBox.warning(self, "Ошибка", "Нельзя изменить логин администратора!")
            return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users
                SET username = %s, role = %s
                WHERE id = %s
            """, (
                username,
                role,
                record_id
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Данные пользователя обновлены!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def insert_data(self, data):
        """Добавление нового пользователя"""
        username = data.get('Логин', '').strip()
        role = data.get('Роль', 'user').strip()
        password = "123456"  # Пароль по умолчанию
        
        if not username:
            QMessageBox.warning(self, "Ошибка", "Введите логин!")
            return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Проверка существующего пользователя
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь уже существует!")
                return
            
            # Хеширование пароля по умолчанию
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s)
            """, (
                username,
                hashed_password,
                role
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех",
                                  f"Пользователь {username} добавлен!\nПароль по умолчанию: 123456")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, record_id):
        """Удаление пользователя"""
        # Нельзя удалить администратора
        current_row = self.table.currentRow()
        if current_row != -1:
            username = self.table.item(current_row, 1).text()
            if username == 'admin':
                QMessageBox.warning(self, "Ошибка", "Нельзя удалить администратора!")
                return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (record_id,))
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Пользователь удален!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def on_add(self):
        """Кастомный диалог для добавления пользователя"""
        dialog = UsersEditDialog({}, self)
        if dialog.exec_() == QDialog.Accepted:
            self.insert_data(dialog.get_data())
    
    def on_edit(self):
        """Кастомный диалог для редактирования пользователя"""
        current_row = self.table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return
        
        row_data = {}
        for col in range(self.table.columnCount()):
            column_name = self.table.horizontalHeaderItem(col).text()
            item = self.table.item(current_row, col)
            if item:
                row_data[column_name] = item.text()
        
        dialog = UsersEditDialog(row_data, self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_data(current_row, dialog.get_data())


class UsersEditDialog(QDialog):
    """Кастомный диалог для пользователей"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Редактирование пользователя")
        self.resize(400, 200)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        # Логин
        self.username_edit = QLineEdit(str(self.data.get('Логин', '')))
        self.username_edit.setPlaceholderText("Введите логин")
        layout.addRow("Логин:", self.username_edit)
        
        # Роль - ComboBox
        self.role_combo = QComboBox()
        self.role_combo.addItems(['admin', 'user'])
        
        current_role = self.data.get('Роль', 'user')
        index = self.role_combo.findText(current_role)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)
        layout.addRow("Роль:", self.role_combo)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'Логин': self.username_edit.text(),
            'Роль': self.role_combo.currentText()
        }