from base_table_window import TableWindow
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QVBoxLayout, QFormLayout, QComboBox, QDialogButtonBox, QLabel, QDoubleSpinBox, QDateEdit
from PyQt5.QtCore import QDate
from db_connection import get_connection

class ChequesWindow(TableWindow):
    def __init__(self):
        super().__init__(
            "cheque",
            ["ID", "Проект", "Цена проекта", "Способ оплаты", "Дата"],
            "Управление чеками"
        )
        self.available_projects = []
        self.load_references()
    
    def load_references(self):
        """Загружаем справочники для валидации"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Загружаем проекты
            cursor.execute("SELECT project_code, project_name, price_project FROM project")
            self.available_projects = [(str(row[0]), row[1], row[2]) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Ошибка загрузки справочников: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def load_data(self):
        """Загрузка данных из таблицы cheque"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT ch.cheque_code, 
                       p.project_name, 
                       ch.price_project,
                       ch.payment_method,
                       ch.cheque_date
                FROM cheque ch
                LEFT JOIN project p ON ch.project_code = p.project_code
                ORDER BY ch.cheque_code
            """)
            data = cursor.fetchall()
            
            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row[1]) if row[1] else ""))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(row[2])))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(row[3]) if row[3] else ""))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(row[4]) if row[4] else ""))
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{e}")
        finally:
            cursor.close()
            conn.close()
    
    def validate_foreign_keys(self, project_code):
        """Проверяем существование внешних ключей"""
        if project_code:
            project_exists = any(str(pid) == str(project_code) for pid, _, _ in self.available_projects)
            if not project_exists:
                return [f"Проект с кодом {project_code} не существует"]
        return []
    
    def get_row_data(self, row):
        """Получение данных строки"""
        data = {}
        # ID
        item = self.table.item(row, 0)
        if item:
            data['ID'] = item.text()
        
        # Цена
        item = self.table.item(row, 2)
        if item:
            data['Цена проекта'] = item.text()
        
        # Способ оплаты
        item = self.table.item(row, 3)
        if item:
            data['Способ оплаты'] = item.text()
        
        # Дата
        item = self.table.item(row, 4)
        if item:
            data['Дата'] = item.text()
        
        # Для проекта нужно получить код из БД
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cheque_id = data.get('ID', '')
                cursor.execute("SELECT project_code FROM cheque WHERE cheque_code = %s", (cheque_id,))
                result = cursor.fetchone()
                if result:
                    data['Код проекта'] = str(result[0]) if result[0] else ''
            except Exception as e:
                print(f"Ошибка получения кода проекта: {e}")
            finally:
                cursor.close()
                conn.close()
        
        return data
    
    def update_data(self, row, data):
        """Обновление данных чека"""
        record_id = self.table.item(row, 0).text()
        project_code = data.get('Код проекта', '').strip()
        price_project = data.get('Цена проекта', '0').strip()
        payment_method = data.get('Способ оплаты', 'наличные').strip()
        cheque_date = data.get('Дата', QDate.currentDate().toString("yyyy-MM-dd")).strip()
        
        if not project_code:
            QMessageBox.warning(self, "Ошибка", "Проект должен быть выбран!")
            return
        
        validation_errors = self.validate_foreign_keys(project_code)
        if validation_errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(validation_errors))
            return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE cheque
                SET project_code = %s, price_project = %s, payment_method = %s, cheque_date = %s
                WHERE cheque_code = %s
            """, (
                int(project_code),
                float(price_project),
                payment_method,
                cheque_date,
                int(record_id)
            ))
            
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", f"Чек #{record_id} обновлен!")
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Код проекта должен быть числом, цена - числом с плавающей точкой")
            conn.rollback()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def insert_data(self, data):
        """Добавление нового чека"""
        project_code = data.get('Код проекта', '').strip()
        price_project = data.get('Цена проекта', '0').strip()
        payment_method = data.get('Способ оплаты', 'наличные').strip()
        cheque_date = data.get('Дата', QDate.currentDate().toString("yyyy-MM-dd")).strip()
        
        if not project_code:
            QMessageBox.warning(self, "Ошибка", "Проект должен быть выбран!")
            return
        
        validation_errors = self.validate_foreign_keys(project_code)
        if validation_errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(validation_errors))
            return
        
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO cheque (project_code, price_project, payment_method, cheque_date)
                VALUES (%s, %s, %s, %s)
                RETURNING cheque_code
            """, (
                int(project_code),
                float(price_project),
                payment_method,
                cheque_date
            ))
            
            new_id = cursor.fetchone()[0]
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", f"Чек #{new_id} добавлен!")
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Код проекта должен быть числом, цена - числом с плавающей точкой")
            conn.rollback()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, record_id):
        """Удаление чека"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cheque WHERE cheque_code = %s", (int(record_id),))
            conn.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Чек удален!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления:\n{e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def on_add(self):
        """Добавление с кастомным диалогом"""
        dialog = ChequesEditDialog(self.available_projects, {}, self)
        if dialog.exec_() == QDialog.Accepted:
            self.insert_data(dialog.get_data())
    
    def on_edit(self):
        """Редактирование с кастомным диалогом"""
        current_row = self.table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return
        
        row_data = self.get_row_data(current_row)
        dialog = ChequesEditDialog(self.available_projects, row_data, self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_data(current_row, dialog.get_data())


class ChequesEditDialog(QDialog):
    """Кастомное диалоговое окно для чеков"""
    def __init__(self, projects, data, parent=None):
        super().__init__(parent)
        self.projects = projects
        self.data = data
        self.setWindowTitle("Редактирование чека")
        self.resize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Проект
        self.project_combo = QComboBox()
        self.project_combo.addItem("-- Выберите проект --", "")
        for proj_id, proj_name, proj_price in self.projects:
            self.project_combo.addItem(f"{proj_name} (цена: {proj_price})", proj_id)
        
        current_project = self.data.get('Код проекта', '')
        if current_project:
            index = self.project_combo.findData(current_project)
            if index >= 0:
                self.project_combo.setCurrentIndex(index)
        
        form_layout.addRow("Проект:", self.project_combo)
        
        # Цена
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMaximum(99999999.99)
        self.price_spin.setMinimum(0)
        self.price_spin.setDecimals(2)
        
        try:
            self.price_spin.setValue(float(self.data.get('Цена проекта', 0)))
        except:
            self.price_spin.setValue(0)
        
        form_layout.addRow("Цена проекта:", self.price_spin)
        
        # Способ оплаты
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(['наличные', 'карта', 'криптовалюта'])
        
        current_payment = self.data.get('Способ оплаты', 'наличные')
        index = self.payment_combo.findText(current_payment)
        if index >= 0:
            self.payment_combo.setCurrentIndex(index)
        
        form_layout.addRow("Способ оплаты:", self.payment_combo)
        
        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        try:
            date_str = self.data.get('Дата', QDate.currentDate().toString("yyyy-MM-dd"))
            if date_str:
                self.date_edit.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
            else:
                self.date_edit.setDate(QDate.currentDate())
        except:
            self.date_edit.setDate(QDate.currentDate())
        
        form_layout.addRow("Дата:", self.date_edit)
        
        # Обновление цены при выборе проекта
        self.project_combo.currentIndexChanged.connect(self.update_price_from_project)
        
        layout.addLayout(form_layout)
        
        # Информация
        info_label = QLabel(f"Доступно проектов: {len(self.projects)}")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def update_price_from_project(self):
        """Обновление цены при выборе проекта"""
        project_id = self.project_combo.currentData()
        if project_id:
            for proj_id, _, proj_price in self.projects:
                if str(proj_id) == str(project_id):
                    try:
                        self.price_spin.setValue(float(proj_price))
                    except:
                        pass
                    break
    
    def get_data(self):
        return {
            'Код проекта': self.project_combo.currentData() or '',
            'Цена проекта': str(self.price_spin.value()),
            'Способ оплаты': self.payment_combo.currentText(),
            'Дата': self.date_edit.date().toString("yyyy-MM-dd")
        }