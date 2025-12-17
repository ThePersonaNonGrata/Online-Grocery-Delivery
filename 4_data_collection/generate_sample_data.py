"""generate_sample_data.py
Data collection / sample data generator for the demo system.

Creates:
  - sample_products.json
  - sample_users.json
  - sample_orders.json
"""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

sample_products = [
    {"id": 1, "name": "Apples", "price": 2.99, "stock": 10, "category": "Produce"},
    {"id": 2, "name": "Bread", "price": 1.99, "stock": 15, "category": "Bakery"},
    {"id": 3, "name": "Milk", "price": 3.49, "stock": 8, "category": "Dairy"},
    {"id": 4, "name": "Chicken Breast", "price": 6.99, "stock": 12, "category": "Meat"},
    {"id": 5, "name": "Rice", "price": 4.49, "stock": 20, "category": "Pantry"},
    {"id": 6, "name": "Orange Juice", "price": 3.99, "stock": 9, "category": "Beverages"},
]

sample_users = [
    {"email": "customer@example.com", "role": "customer"},
    {"email": "manager@example.com", "role": "manager"},
    {"email": "delivery@example.com", "role": "delivery_staff"},
]

sample_orders = [
    {
        "order_id": 1,
        "customer_email": "customer@example.com",
        "items": [{"id": 1, "name": "Apples", "qty": 2}, {"id": 3, "name": "Milk", "qty": 1}],
        "status": "Packed"
    }
]

def write(name: str, data):
    (OUT / name).write_text(json.dumps(data, indent=2), encoding="utf-8")

def main():
    write("sample_products.json", sample_products)
    write("sample_users.json", sample_users)
    write("sample_orders.json", sample_orders)
    print("Generated sample_products.json, sample_users.json, sample_orders.json")

if __name__ == "__main__":
    main()
