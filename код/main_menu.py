from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt


class MainMenu(QWidget):
    def __init__(self, username, role, user_id):
        super().__init__()
        self.username = username
        self.role = role
        self.user_id = user_id
        self.setWindowTitle(f"Главное меню - IT Компания ({username} - {role})")
        self.resize(700, 650)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("IT Компания - Управление базой данных")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Информация о пользователе с цветом в зависимости от роли
        role_color = "#FF0000" if self.role == 'admin' else "#0000FF"
        user_info = QLabel(f"Пользователь: <b>{self.username}</b> | Роль: <span style='color:{role_color};'><b>{self.role}</b></span>")
        user_info.setAlignment(Qt.AlignCenter)
        user_info.setStyleSheet("font-size: 14px; margin: 10px;")
        user_info.setTextFormat(Qt.RichText)
        layout.addWidget(user_info)
        
        # Сетка для кнопок (3 колонки)
        grid_layout = QGridLayout()
        
        # Определяем доступные функции в зависимости от роли
        if self.role == 'admin':
            menu_buttons = [
                ("👥 Управление клиентами", self.show_clients, 0, 0),
                ("💼 Управление сотрудниками", self.show_employees, 0, 1),
                ("💻 Управление проектами", self.show_projects, 0, 2),
                ("📦 Управление заказами", self.show_orders, 1, 0),
                ("💰 Управление чеками", self.show_cheques, 1, 1),
                ("👤 Управление пользователями", self.show_users, 1, 2),
            ]
            
        else:  # role == 'user'
            menu_buttons = [
                ("👥 Просмотр клиентов", self.show_clients_view, 0, 0),
                ("💼 Просмотр сотрудников", self.show_employees_view, 0, 1),
                ("💻 Просмотр проектов", self.show_projects_view, 0, 2),
                ("📦 Просмотр заказов", self.show_orders_view, 1, 0),
                ("💰 Просмотр чеков", self.show_cheques_view, 1, 1),
            ]
            
            # Заполняем пустые ячейки пустыми виджетами для выравнивания
            from PyQt5.QtWidgets import QWidget
            empty_widget = QWidget()
            grid_layout.addWidget(empty_widget, 1, 2)
        
        for text, handler, row, col in menu_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(180)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px;
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    background-color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #E8F5E9;
                }
                QPushButton:disabled {
                    border: 2px solid #CCCCCC;
                    color: #999999;
                    background-color: #F5F5F5;
                }
            """)
            btn.clicked.connect(handler)
            grid_layout.addWidget(btn, row, col)
        
        layout.addLayout(grid_layout)
        
        # Кнопка смены пароля (доступна всем)
        change_password_btn = QPushButton("🔐 Сменить пароль")
        change_password_btn.clicked.connect(self.change_password)
        change_password_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                background-color: white;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
        """)
        layout.addWidget(change_password_btn)
        
        # Кнопка выхода
        logout_btn = QPushButton("🚪 Выйти из системы")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                border: 2px solid #FF5252;
                border-radius: 5px;
                background-color: white;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #FFEBEE;
            }
        """)
        layout.addWidget(logout_btn)
        
        self.setLayout(layout)
    
    def change_password(self):
        """Открыть окно смены пароля"""
        from change_password_window import ChangePasswordWindow
        self.change_pass_window = ChangePasswordWindow(self.user_id, self.username)
        self.change_pass_window.show()
    
    # === ФУНКЦИИ ДЛЯ ADMIN ===
    def show_clients(self):
        from clients_window import ClientsWindow
        self.clients_window = ClientsWindow()
        self.clients_window.show()
    
    def show_employees(self):
        from employees_window import EmployeesWindow
        self.employees_window = EmployeesWindow()
        self.employees_window.show()
    
    def show_projects(self):
        from projects_window import ProjectsWindow
        self.projects_window = ProjectsWindow()
        self.projects_window.show()
    
    def show_orders(self):
        from orders_window import OrdersWindow
        self.orders_window = OrdersWindow()
        self.orders_window.show()
    
    def show_cheques(self):
        from cheques_window import ChequesWindow
        self.cheques_window = ChequesWindow()
        self.cheques_window.show()
    
    def show_users(self):
        try:
            from users_window import UsersWindow
            self.users_window = UsersWindow()
            self.users_window.show()
        except ImportError:
            QMessageBox.critical(self, "Ошибка", "Модуль users_window.py не найден!")
    
    # === ФУНКЦИИ ДЛЯ USER ===
    def show_clients_view(self):
        from clients_window import ClientsWindow
        self.clients_window = ClientsWindow()
        
        # Отключаем кнопки редактирования для user
        self.clients_window.btn_add.setEnabled(False)
        self.clients_window.btn_edit.setEnabled(False)
        self.clients_window.btn_delete.setEnabled(False)
        
        # Меняем заголовок
        self.clients_window.setWindowTitle("Просмотр клиентов (режим просмотра)")
        self.clients_window.show()
    
    def show_employees_view(self):
        from employees_window import EmployeesWindow
        self.employees_window = EmployeesWindow()
        
        # Отключаем кнопки редактирования для user
        self.employees_window.btn_add.setEnabled(False)
        self.employees_window.btn_edit.setEnabled(False)
        self.employees_window.btn_delete.setEnabled(False)
        
        # Меняем заголовок
        self.employees_window.setWindowTitle("Просмотр сотрудников (режим просмотра)")
        self.employees_window.show()
    
    def show_projects_view(self):
        from projects_window import ProjectsWindow
        self.projects_window = ProjectsWindow()
        
        # Отключаем кнопки редактирования для user
        self.projects_window.btn_add.setEnabled(False)
        self.projects_window.btn_edit.setEnabled(False)
        self.projects_window.btn_delete.setEnabled(False)
        
        # Меняем заголовок
        self.projects_window.setWindowTitle("Просмотр проектов (режим просмотра)")
        self.projects_window.show()
    
    def show_orders_view(self):
        from orders_window import OrdersWindow
        self.orders_window = OrdersWindow()
        
        # Отключаем кнопки редактирования для user
        self.orders_window.btn_add.setEnabled(False)
        self.orders_window.btn_edit.setEnabled(False)
        self.orders_window.btn_delete.setEnabled(False)
        
        # Меняем заголовок
        self.orders_window.setWindowTitle("Просмотр заказов (режим просмотра)")
        self.orders_window.show()
    
    def show_cheques_view(self):
        from cheques_window import ChequesWindow
        self.cheques_window = ChequesWindow()
        
        # Отключаем кнопки редактирования для user
        self.cheques_window.btn_add.setEnabled(False)
        self.cheques_window.btn_edit.setEnabled(False)
        self.cheques_window.btn_delete.setEnabled(False)
        
        # Меняем заголовок
        self.cheques_window.setWindowTitle("Просмотр чеков (режим просмотра)")
        self.cheques_window.show()
    
    def logout(self):
        """Выход из системы"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите выйти из системы?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from auth_window import AuthWindow
            self.close()
            self.auth_window = AuthWindow()
            self.auth_window.show()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainMenu("test_user", "user", 1)
    window.show()
    sys.exit(app.exec_())