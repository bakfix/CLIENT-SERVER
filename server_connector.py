import requests


class ServerConnector:

    def __init__(self, address, port, user_id):
        self.url = f"{address}:{port}"
        self.user_id = user_id
        self.views = set()

    def add_view(self, view):
        self.views.add(view)

    def update_data(self):
        for view in self.views:
            view.update_data()

    def get_orders(self):
        content = requests.get(f"{self.url}/orders").json()
        return content

    def get_orders_for_worker(self):
        content = requests.get(f"{self.url}/worker/{self.user_id}/orders").json()
        return content

    def add_orders(self, location, description, price: int):
        result = requests.post(f"{self.url}/orders",
                               json={
                                   'location': location,
                                   'description': description,
                                   'price': price
                               }).json()
        self.update_data()
        return result['status'] == 'ok'

    def take_orders(self, orders_id):
        result = requests.post(f"{self.url}/orders/{orders_id}/take",
                               json={
                                   'worker_id': self.user_id
                               }).json()
        self.update_data()
        return result['status'] == 'ok'

    def finish_orders(self, orders_id):
        requests.post(f"{self.url}/orders/{orders_id}/finish")
        self.update_data()
        return True
