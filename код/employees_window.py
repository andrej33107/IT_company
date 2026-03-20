from base_table_window import TableWindow
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from db_connection import get_connection

class EmployeesWindow(TableWindow):
    def __init__(self):
        super().__init__(
            "employee",
            ["ID", "Фамилия", "Имя", "Отчество"],
            "Управление сотрудниками"
        )
    
    def load_data(self):
        """Загрузка данных из таблицы employee"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT employee_code, last_name, first_name, middle_name
                FROM employee
                ORDER BY employee_code
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
        """Обновление данных сотрудника"""
        record_id = self.table.item(row, 0).text()
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE employee
                SET last_name = %s, first_name = %s, middle_name = %s
                WHERE employee_code = %s
            """, (
                data.get('Фамилия', ''),
                data.get('Имя', ''),
                data.get('Отчество', ''),
                record_id
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Данные сотрудника обновлены!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def insert_data(self, data):
        """Добавление нового сотрудника"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO employee (last_name, first_name, middle_name)
                VALUES (%s, %s, %s)
            """, (
                data.get('Фамилия', ''),
                data.get('Имя', ''),
                data.get('Отчество', '')
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Сотрудник добавлен!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, record_id):
        """Удаление сотрудника"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM employee WHERE employee_code = %s", (record_id,))
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Сотрудник удален!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления:\n{e}")
        finally:
            cursor.close()
            conn.close()