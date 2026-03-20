from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QMessageBox, QHeaderView, QDialog, QFormLayout,
    QDialogButtonBox, QDateEdit, QDoubleSpinBox, QSpinBox,
    QComboBox
)
from PyQt5.QtCore import Qt, QDate
from db_connection import get_connection

class TableWindow(QWidget):
    def __init__(self, table_name, columns, window_title):
        super().__init__()
        self.table_name = table_name
        self.columns = columns
        self.setWindowTitle(window_title)
        self.resize(900, 600)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Поиск
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.search_data)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Добавить")
        self.btn_add.clicked.connect(self.on_add)
        buttons_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("✏️ Редактировать")
        self.btn_edit.clicked.connect(self.on_edit)
        buttons_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("🗑️ Удалить")
        self.btn_delete.clicked.connect(self.on_delete)
        buttons_layout.addWidget(self.btn_delete)
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_data)
        buttons_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_data(self):
        """Загрузка данных из таблицы"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY 1")
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
    
    def search_data(self):
        """Поиск по таблице"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def on_double_click(self, index):
        """Двойной клик для редактирования"""
        self.on_edit()
    
    def on_add(self):
        """Добавление новой записи"""
        dialog = EditDialog(self.columns, {}, self)
        if dialog.exec_() == QDialog.Accepted:
            self.insert_data(dialog.get_data())
    
    def on_edit(self):
        """Редактирование выбранной записи"""
        current_row = self.table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return
        
        try:
            dialog = EditDialog(self.columns, self.get_row_data(current_row), self)
            if dialog.exec_() == QDialog.Accepted:
                self.update_data(current_row, dialog.get_data())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии редактора:\n{e}")
    
    def on_delete(self):
        """Удаление выбранной записи"""
        current_row = self.table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return
        
        record_id = self.table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить запись?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_data(record_id)
    
    def get_row_data(self, row):
        """Получение данных строки"""
        data = {}
        for col in range(self.table.columnCount()):
            column_name = self.table.horizontalHeaderItem(col).text()
            item = self.table.item(row, col)
            data[column_name] = item.text() if item else ""
        return data
    
    def update_data(self, row, data):
        """Обновление данных (переопределить в дочерних классах)"""
        print(f"⚠️ WARNING: update_data не переопределен для {self.table_name}")
        QMessageBox.warning(
            self,
            "Метод не реализован",
            f"Метод update_data не реализован для таблицы {self.table_name}"
        )
    
    def insert_data(self, data):
        """Вставка данных (переопределить в дочерних классах)"""
        print(f"⚠️ WARNING: insert_data не переопределен для {self.table_name}")
        QMessageBox.warning(
            self,
            "Метод не реализован",
            f"Метод insert_data не реализован для таблицы {self.table_name}"
        )
    
    def delete_data(self, record_id):
        """Удаление данных (переопределить в дочерних классах)"""
        print(f"⚠️ WARNING: delete_data не переопределен для {self.table_name}")
        QMessageBox.warning(
            self,
            "Метод не реализован",
            f"Метод delete_data не реализован для таблицы {self.table_name}"
        )


class EditDialog(QDialog):
    def __init__(self, columns, data, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.data = data
        self.setWindowTitle("Редактирование записи")
        self.resize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        self.widgets = {}
        
        for column in self.columns:
            if column.lower() in ['id', 'код', 'code', '№']:
                continue
            
            value = self.data.get(column, "")
            
            # Определение типа поля
            if any(word in column.lower() for word in ['date', 'дата']):
                widget = QDateEdit()
                try:
                    if value:
                        if '-' in value:
                            widget.setDate(QDate.fromString(value, "yyyy-MM-dd"))
                        else:
                            widget.setDate(QDate.fromString(value, "dd.MM.yyyy"))
                    else:
                        widget.setDate(QDate.currentDate())
                except:
                    widget.setDate(QDate.currentDate())
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd.MM.yyyy")
            
            elif any(word in column.lower() for word in ['price', 'cost', 'цена', 'сумма']):
                widget = QDoubleSpinBox()
                widget.setMaximum(99999999.99)
                widget.setMinimum(0)
                widget.setDecimals(2)
                try:
                    widget.setValue(float(value) if value else 0)
                except:
                    widget.setValue(0)
            
            elif any(word in column.lower() for word in ['количество', 'number', 'count']):
                widget = QSpinBox()
                widget.setMaximum(999999)
                widget.setMinimum(0)
                try:
                    widget.setValue(int(float(value)) if value else 0)
                except:
                    widget.setValue(0)
            
            elif any(word in column.lower() for word in ['status', 'статус', 'type', 'тип']):
                widget = QComboBox()
                widget.addItems(['активный', 'завершен', 'в работе', 'ожидание'])
                if value:
                    index = widget.findText(value)
                    if index >= 0:
                        widget.setCurrentIndex(index)
            
            else:
                widget = QLineEdit(str(value))
                widget.setPlaceholderText(f"Введите {column.lower()}")
            
            layout.addRow(column + ":", widget)
            self.widgets[column] = widget
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Получение данных из формы"""
        data = {}
        for column, widget in self.widgets.items():
            if isinstance(widget, QDateEdit):
                value = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QDoubleSpinBox):
                value = str(widget.value())
            elif isinstance(widget, QSpinBox):
                value = str(widget.value())
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            else:
                value = widget.text()
            
            data[column] = value
        
        return data