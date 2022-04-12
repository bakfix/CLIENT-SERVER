import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTabWidget, QListWidget, \
    QListWidgetItem, QDialog, QFormLayout, QLineEdit, QTextEdit

from server_connector import ServerConnector


class OrdersWindow(QDialog):

    def __init__(self, data, server: ServerConnector):
        super().__init__()
        self.setWindowTitle(f"Заказ по месту {data['location']}")
        self.resize(350, 150)
        self.id = data['id']

        self.server = server

        self.setLayout(QVBoxLayout())

        self.layout().addWidget(QLabel(f"Место: {data['location']}"))
        self.layout().addWidget(QLabel(f"Описание: {data['description']}"))
        self.layout().addWidget(QLabel(f"Цена: {data['price']}"))

        if data in server.get_orders():
            take_button = QPushButton("Взять заказ в работу")
            take_button.clicked.connect(self.take)
            self.layout().addWidget(take_button)
        else:
            finish_button = QPushButton("Заказ выполнен")
            finish_button.clicked.connect(self.take)
            self.layout().addWidget(finish_button)

    def take(self):
        self.server.take_orders(self.id)
        self.close()

    def finish(self):
        self.server.finish_orders(self.id)
        self.close()


class OrdersListItem(QListWidgetItem):

    def __init__(self, orders_dict):
        super().__init__()
        self.id = orders_dict['id']
        self.data = orders_dict
        self.setText(f"{orders_dict['location']}\n{orders_dict['description']}")


class OrdersPanel(QTabWidget):

    def __init__(self, get_orders, get_user_orders, server):
        super().__init__()

        self.server = server

        self.get_orders = get_orders
        self.get_user_orders = get_user_orders

        self.orders_widget = QListWidget()
        self.orders_widget.itemDoubleClicked.connect(self.openOrdersWindow)
        self.addTab(self.orders_widget, "Свободные заказы")

        self.my_orders_widget = QListWidget()
        self.my_orders_widget.itemDoubleClicked.connect(self.openOrdersWindow)
        self.addTab(self.my_orders_widget, "Мои заказы")

        self.update_data()

    def update_data(self):
        self.orders_widget.clear()
        self.my_orders_widget.clear()
        for orders in self.get_orders():
            self.orders_widget.addItem(OrdersListItem(orders))
        for orders in self.get_user_orders():
            self.my_orders_widget.addItem(OrdersListItem(orders))

    def openOrdersWindow(self):
        window = OrdersWindow(self.sender().selectedItems()[0].data, self.server)
        window.exec()


class NewOrdersDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.is_accepted = False

        self.setLayout(QFormLayout())

        self.location_field = QLineEdit()
        self.layout().addRow("Место", self.location_field)

        self.price_field = QLineEdit()
        self.layout().addRow("Цена", self.price_field)

        self.description_field = QTextEdit()
        self.layout().addRow("Описание", self.description_field)

        accept_button = QPushButton("Ok")
        accept_button.clicked.connect(self.confirm)
        self.layout().addRow("Принять", accept_button)

    def confirm(self):
        self.is_accepted = True
        self.close()

    @property
    def location(self):
        return self.location_field.text()

    @property
    def price(self):
        return self.price_field.text()

    @property
    def description(self):
        return self.description_field.toPlainText()


class MainWindow(QWidget):

    def __init__(self, server: ServerConnector):
        super().__init__()

        self.server = server

        self.setWindowTitle("Программа контроля заказов")
        self.setGeometry(700, 200, 500, 600)
        self.setLayout(QVBoxLayout())

        add_orders_button = QPushButton("Добавить заказ")
        add_orders_button.clicked.connect(self.addOrders)
        self.layout().addWidget(add_orders_button)

        # TODO: создать две вкладки со списками заказов
        self.orders_panel = OrdersPanel(self.server.get_orders,
                                        self.server.get_orders_for_worker,
                                        self.server)
        self.server.add_view(self.orders_panel)
        self.layout().addWidget(self.orders_panel)

        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.refresh)
        self.layout().addWidget(refresh_button)

        self.status_bar = QLabel()
        self.layout().addWidget(self.status_bar)

        self.showStatus("Готово к работе")

    def showStatus(self, status_message):
        self.status_bar.setText(status_message)

    def addOrders(self):
        adding_dialog = NewOrdersDialog()
        adding_dialog.exec()
        if adding_dialog.is_accepted:
            self.server.add_orders(adding_dialog.location,
                                   adding_dialog.price,
                                   adding_dialog.description)

    def refresh(self):
        self.orders_panel.update_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    connector = ServerConnector("http://localhost", 5000, 1)
    window = MainWindow(connector)
    window.show()
    sys.exit(app.exec())
