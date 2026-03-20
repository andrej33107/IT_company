from base_table_window import TableWindow
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QVBoxLayout, QFormLayout, QComboBox, QDialogButtonBox, QLabel
from db_connection import get_connection

class OrdersWindow(TableWindow):
    def __init__(self):
        super().__init__(
            "orders",
            ["ID", "Проект", "Клиент", "Статус готовности"],
            "Управление заказами"
        )
        self.available_projects = []
        self.available_clients = []
        self.load_references()
    
    def load_references(self):
        """Загружаем справочники для валидации"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Загружаем проекты
            cursor.execute("SELECT project_code, project_name FROM project")
            self.available_projects = [(str(row[0]), row[1]) for row in cursor.fetchall()]
            
            # Загружаем клиентов (ФИО полностью)
            cursor.execute("""
                SELECT client_code, 
                       CONCAT(last_name, ' ', first_name, ' ', COALESCE(middle_name, '')) as full_name
                FROM clients
            """)
            self.available_clients = [(str(row[0]), row[1].strip()) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Ошибка загрузки справочников: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def load_data(self):
        """Загрузка данных из таблицы orders"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT o.order_code, 
                       p.project_name, 
                       CONCAT(c.last_name, ' ', c.first_name, ' ', COALESCE(c.middle_name, '')) as client_name,
                       o.readiness_status
                FROM orders o
                LEFT JOIN project p ON o.project_code = p.project_code
                LEFT JOIN clients c ON o.client_code = c.client_code
                ORDER BY o.order_code
            """)
            data = cursor.fetchall()
            
            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row[1]) if row[1] else ""))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(row[2]).strip() if row[2] else ""))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(row[3])))
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def validate_foreign_keys(self, project_code, client_code):
        """Проверяем существование внешних ключей"""
        errors = []
        
        if project_code:
            project_exists = any(str(pid) == str(project_code) for pid, _ in self.available_projects)
            if not project_exists:
                errors.append(f"Проект с кодом {project_code} не существует")
        
        if client_code:
            client_exists = any(str(cid) == str(client_code) for cid, _ in self.available_clients)
            if not client_exists:
                errors.append(f"Клиент с кодом {client_code} не существует")
        
        return errors
    
    def get_row_data(self, row):
        """Получение данных строки"""
        data = {}
        # ID
        item = self.table.item(row, 0)
        if item:
            data['ID'] = item.text()
        
        # Статус готовности
        item = self.table.item(row, 3)
        if item:
            data['Статус готовности'] = item.text()
        
        # Для проекта и клиента нужно получить их коды из БД
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                order_id = data.get('ID', '')
                cursor.execute("SELECT project_code, client_code FROM orders WHERE order_code = %s", (order_id,))
                result = cursor.fetchone()
                if result:
                    data['Код проекта'] = str(result[0]) if result[0] else ''
                    data['Код клиента'] = str(result[1]) if result[1] else ''
            except Exception as e:
                print(f"Ошибка получения кодов: {e}")
            finally:
                cursor.close()
                conn.close()
        
        return data
    
    def update_data(self, row, data):
        """Обновление данных заказа"""
        record_id = self.table.item(row, 0).text()
        project_code = data.get('Код проекта', '').strip()
        client_code = data.get('Код клиента', '').strip()
        readiness_status = data.get('Статус готовности', 'в разработке').strip()
        
        if not project_code or not client_code:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return
        
        validation_errors = self.validate_foreign_keys(project_code, client_code)
        if validation_errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(validation_errors))
            return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE orders
                SET project_code = %s, client_code = %s, readiness_status = %s
                WHERE order_code = %s
            """, (
                int(project_code),
                int(client_code),
                readiness_status,
                int(record_id)
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", f"Заказ #{record_id} обновлен!")
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Коды должны быть числами!")
            conn.rollback()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def insert_data(self, data):
        """Добавление нового заказа"""
        project_code = data.get('Код проекта', '').strip()
        client_code = data.get('Код клиента', '').strip()
        readiness_status = data.get('Статус готовности', 'в разработке').strip()
        
        if not project_code or not client_code:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return
        
        validation_errors = self.validate_foreign_keys(project_code, client_code)
        if validation_errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(validation_errors))
            return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO orders (project_code, client_code, readiness_status)
                VALUES (%s, %s, %s)
                RETURNING order_code
            """, (
                int(project_code),
                int(client_code),
                readiness_status
            ))
            
            new_id = cursor.fetchone()[0]
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", f"Заказ #{new_id} добавлен!")
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Коды должны быть числами!")
            conn.rollback()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, record_id):
        """Удаление заказа"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM orders WHERE order_code = %s", (int(record_id),))
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Заказ удален!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def on_add(self):
        """Добавление с кастомным диалогом"""
        dialog = OrdersEditDialog(self.available_projects, self.available_clients, {}, self)
        if dialog.exec_() == QDialog.Accepted:
            self.insert_data(dialog.get_data())
    
    def on_edit(self):
        """Редактирование с кастомным диалогом"""
        current_row = self.table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return
        
        row_data = self.get_row_data(current_row)
        dialog = OrdersEditDialog(self.available_projects, self.available_clients, row_data, self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_data(current_row, dialog.get_data())


class OrdersEditDialog(QDialog):
    """Кастомное диалоговое окно для заказов"""
    def __init__(self, projects, clients, data, parent=None):
        super().__init__(parent)
        self.projects = projects
        self.clients = clients
        self.data = data
        self.setWindowTitle("Редактирование заказа")
        self.resize(400, 250)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Проект
        self.project_combo = QComboBox()
        self.project_combo.addItem("-- Выберите проект --", "")
        for proj_id, proj_name in self.projects:
            self.project_combo.addItem(f"{proj_name}", proj_id)
        
        current_project = self.data.get('Код проекта', '')
        if current_project:
            index = self.project_combo.findData(current_project)
            if index >= 0:
                self.project_combo.setCurrentIndex(index)
        
        form_layout.addRow("Проект:", self.project_combo)
        
        # Клиент
        self.client_combo = QComboBox()
        self.client_combo.addItem("-- Выберите клиента --", "")
        for client_id, client_name in self.clients:
            self.client_combo.addItem(f"{client_name}", client_id)
        
        current_client = self.data.get('Код клиента', '')
        if current_client:
            index = self.client_combo.findData(current_client)
            if index >= 0:
                self.client_combo.setCurrentIndex(index)
        
        form_layout.addRow("Клиент:", self.client_combo)
        
        # Статус готовности
        self.status_combo = QComboBox()
        self.status_combo.addItems(['в разработке', 'готов', 'тестирование'])
        
        current_status = self.data.get('Статус готовности', 'в разработке')
        index = self.status_combo.findText(current_status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        form_layout.addRow("Статус готовности:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Информация
        info_label = QLabel(f"Доступно: {len(self.projects)} проектов, {len(self.clients)} клиентов")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'Код проекта': self.project_combo.currentData() or '',
            'Код клиента': self.client_combo.currentData() or '',
            'Статус готовности': self.status_combo.currentText()
        }