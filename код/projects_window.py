from base_table_window import TableWindow
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QVBoxLayout, QFormLayout, QComboBox, QDialogButtonBox, QLabel, QDoubleSpinBox, QLineEdit
from db_connection import get_connection

class ProjectsWindow(TableWindow):
    def __init__(self):
        super().__init__(
            "project",
            ["ID", "Название проекта", "Цена проекта", "Сотрудник"],
            "Управление проектами"
        )
        self.available_employees = []
        self.load_references()
    
    def load_references(self):
        """Загружаем справочники для валидации"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Загружаем сотрудников
            cursor.execute("""
                SELECT employee_code, 
                       CONCAT(last_name, ' ', first_name, ' ', COALESCE(middle_name, '')) as full_name
                FROM employee
            """)
            self.available_employees = [(str(row[0]), row[1].strip()) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Ошибка загрузки справочников: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def load_data(self):
        """Загрузка данных из таблицы project"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.project_code, 
                       p.project_name, 
                       p.price_project,
                       CONCAT(e.last_name, ' ', e.first_name, ' ', COALESCE(e.middle_name, '')) as employee_name
                FROM project p
                LEFT JOIN employee e ON p.employee_code = e.employee_code
                ORDER BY p.project_code
            """)
            data = cursor.fetchall()
            
            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row[1]) if row[1] else ""))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(row[2]) if row[2] else "0"))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(row[3]).strip() if row[3] else ""))
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def validate_foreign_keys(self, employee_code):
        """Проверяем существование внешних ключей"""
        errors = []
        
        if employee_code:
            employee_exists = any(str(eid) == str(employee_code) for eid, _ in self.available_employees)
            if not employee_exists:
                errors.append(f"Сотрудник с кодом {employee_code} не существует")
        
        return errors
    
    def get_row_data(self, row):
        """Получение данных строки"""
        data = {}
        # ID
        item = self.table.item(row, 0)
        if item:
            data['ID'] = item.text()
        
        # Название проекта
        item = self.table.item(row, 1)
        if item:
            data['Название проекта'] = item.text()
        
        # Цена проекта
        item = self.table.item(row, 2)
        if item:
            data['Цена проекта'] = item.text()
        
        # Для сотрудника нужно получить код из БД
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                project_id = data.get('ID', '')
                cursor.execute("SELECT employee_code FROM project WHERE project_code = %s", (project_id,))
                result = cursor.fetchone()
                if result:
                    data['Код сотрудника'] = str(result[0]) if result[0] else ''
            except Exception as e:
                print(f"Ошибка получения кода сотрудника: {e}")
            finally:
                cursor.close()
                conn.close()
        
        return data
    
    def update_data(self, row, data):
        """Обновление данных проекта"""
        record_id = self.table.item(row, 0).text()
        project_name = data.get('Название проекта', '').strip()
        price_project = data.get('Цена проекта', '0').strip()
        employee_code = data.get('Код сотрудника', '').strip()
        
        if not project_name:
            QMessageBox.warning(self, "Ошибка", "Название проекта не может быть пустым!")
            return
        
        validation_errors = self.validate_foreign_keys(employee_code)
        if validation_errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(validation_errors))
            return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE project
                SET project_name = %s, price_project = %s, employee_code = %s
                WHERE project_code = %s
            """, (
                project_name,
                float(price_project) if price_project else 0,
                int(employee_code) if employee_code else None,
                int(record_id)
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", f"Проект #{record_id} обновлен!")
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть числом!")
            conn.rollback()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def insert_data(self, data):
        """Добавление нового проекта"""
        project_name = data.get('Название проекта', '').strip()
        price_project = data.get('Цена проекта', '0').strip()
        employee_code = data.get('Код сотрудника', '').strip()
        
        if not project_name:
            QMessageBox.warning(self, "Ошибка", "Название проекта не может быть пустым!")
            return
        
        validation_errors = self.validate_foreign_keys(employee_code)
        if validation_errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(validation_errors))
            return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO project (project_name, price_project, employee_code)
                VALUES (%s, %s, %s)
                RETURNING project_code
            """, (
                project_name,
                float(price_project) if price_project else 0,
                int(employee_code) if employee_code else None
            ))
            
            new_id = cursor.fetchone()[0]
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", f"Проект #{new_id} добавлен!")
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть числом!")
            conn.rollback()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, record_id):
        """Удаление проекта"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Проверяем, есть ли заказы на этот проект
            cursor.execute("SELECT COUNT(*) FROM orders WHERE project_code = %s", (record_id,))
            order_count = cursor.fetchone()[0]
            
            if order_count > 0:
                reply = QMessageBox.question(
                    self, "Подтверждение",
                    f"На проект есть {order_count} заказов. Удалить проект вместе с заказами?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # Проверяем, есть ли чеки на этот проект
            cursor.execute("SELECT COUNT(*) FROM cheque WHERE project_code = %s", (record_id,))
            cheque_count = cursor.fetchone()[0]
            
            if cheque_count > 0:
                reply = QMessageBox.question(
                    self, "Подтверждение",
                    f"На проект есть {cheque_count} чеков. Удалить проект вместе с чеками?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            cursor.execute("DELETE FROM project WHERE project_code = %s", (record_id,))
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Проект удален!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def on_add(self):
        """Добавление с кастомным диалогом"""
        dialog = ProjectsEditDialog(self.available_employees, {}, self)
        if dialog.exec_() == QDialog.Accepted:
            self.insert_data(dialog.get_data())
    
    def on_edit(self):
        """Редактирование с кастомным диалогом"""
        current_row = self.table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return
        
        row_data = self.get_row_data(current_row)
        dialog = ProjectsEditDialog(self.available_employees, row_data, self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_data(current_row, dialog.get_data())


class ProjectsEditDialog(QDialog):
    """Кастомное диалоговое окно для проектов"""
    def __init__(self, employees, data, parent=None):
        super().__init__(parent)
        self.employees = employees
        self.data = data
        self.setWindowTitle("Редактирование проекта")
        self.resize(400, 250)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Название проекта
        self.name_edit = QLineEdit(self.data.get('Название проекта', ''))
        self.name_edit.setPlaceholderText("Введите название проекта")
        form_layout.addRow("Название проекта:", self.name_edit)
        
        # Цена проекта
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMaximum(99999999.99)
        self.price_spin.setMinimum(0)
        self.price_spin.setDecimals(2)
        try:
            self.price_spin.setValue(float(self.data.get('Цена проекта', 0)))
        except:
            self.price_spin.setValue(0)
        form_layout.addRow("Цена проекта:", self.price_spin)
        
        # Сотрудник
        self.employee_combo = QComboBox()
        self.employee_combo.addItem("-- Не назначен --", "")
        for emp_id, emp_name in self.employees:
            self.employee_combo.addItem(f"{emp_name}", emp_id)
        
        current_employee = self.data.get('Код сотрудника', '')
        if current_employee:
            index = self.employee_combo.findData(current_employee)
            if index >= 0:
                self.employee_combo.setCurrentIndex(index)
        
        form_layout.addRow("Сотрудник:", self.employee_combo)
        
        layout.addLayout(form_layout)
        
        # Информация
        info_label = QLabel(f"Доступно сотрудников: {len(self.employees)}")
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
            'Название проекта': self.name_edit.text(),
            'Цена проекта': str(self.price_spin.value()),
            'Код сотрудника': self.employee_combo.currentData() or ''
        }