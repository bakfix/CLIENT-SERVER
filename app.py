import json

from flask import Flask, request, jsonify
from database import DataOrders

app = Flask(__name__)
db = DataOrders()


@app.route('/orders', methods=['GET'])
def get_orders():
    result = [{'id': id_, 'location': location, 'description': description, 'price': price}
              for id_, location, description, price in db.get_orders()]
    return jsonify(result)


@app.route('/worker/<int:worker_id>/orders', methods=['GET'])
def get_orders_for_worker(worker_id):
    result = [{'id': id_, 'location': location, 'description': description, 'price': price}
              for id_, location, description, price in db.get_worker_orders(worker_id)]
    return jsonify(result)


@app.route('/orders', methods=['POST'])
def add_new_order():
    if not request.is_json:
        return {"status": "error", "message": "no json sent"}
    data = json.loads(request.data)
    db.add_new_orders(data['location'], data['description'], data['price'])
    return {"status": "ok"}


@app.route('/orders/<int:orders_id>/take', methods=['POST'])
def take_orders(orders_id):
    if not request.is_json:
        return {"status": "error", "message": "no json sent"}
    data = json.loads(request.data)
    result = db.take_orders(orders_id, data['worker_id'])
    return {'status': "ok" if result else "failed"}


@app.route('/orders/<int:orders_id>/finish', methods=['POST'])
def report_about_orders(orders_id):
    db.report_about_orders(orders_id)
    return {'status': "ok"}


if __name__ == '__main__':
    app.run(debug=True)
