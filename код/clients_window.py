from base_table_window import TableWindow
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from db_connection import get_connection

class ClientsWindow(TableWindow):
    def __init__(self):
        super().__init__(
            "clients",
            ["ID", "Фамилия", "Имя", "Отчество", "Телефон"],
            "Управление клиентами"
        )
    
    def load_data(self):
        """Загрузка данных из таблицы clients"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT client_code, last_name, first_name, middle_name, telephone
                FROM clients
                ORDER BY client_code
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
        """Обновление данных клиента"""
        record_id = self.table.item(row, 0).text()
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE clients
                SET last_name = %s, first_name = %s, middle_name = %s, telephone = %s
                WHERE client_code = %s
            """, (
                data.get('Фамилия', ''),
                data.get('Имя', ''),
                data.get('Отчество', ''),
                data.get('Телефон', ''),
                record_id
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Данные клиента обновлены!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def insert_data(self, data):
        """Добавление нового клиента"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO clients (last_name, first_name, middle_name, telephone)
                VALUES (%s, %s, %s, %s)
            """, (
                data.get('Фамилия', ''),
                data.get('Имя', ''),
                data.get('Отчество', ''),
                data.get('Телефон', '')
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Клиент добавлен!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, record_id):
        """Удаление клиента"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Проверяем, есть ли у клиента заказы
            cursor.execute("SELECT COUNT(*) FROM orders WHERE client_code = %s", (record_id,))
            order_count = cursor.fetchone()[0]
            
            if order_count > 0:
                reply = QMessageBox.question(
                    self, "Подтверждение",
                    f"У клиента есть {order_count} заказов. Удалить клиента вместе с заказами?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            cursor.execute("DELETE FROM clients WHERE client_code = %s", (record_id,))
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Клиент удален!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления:\n{e}")
        finally:
            cursor.close()
            conn.close()