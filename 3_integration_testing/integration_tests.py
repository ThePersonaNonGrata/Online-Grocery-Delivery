"""integration_tests.py
Lightweight integration tests (simulation) that verify an end-to-end flow:
  - add items / change quantities
  - checkout creates an order
  - track order progresses through delivery statuses

Runs WITHOUT a server.
"""

import unittest
from dataclasses import dataclass
from typing import Dict

from cart_logic import Product, add_to_cart, set_quantity, cart_total

DELIVERY_STAGES = ["Confirmed", "Packed", "Out for Delivery", "Delivered"]

@dataclass
class Order:
    order_id: int
    full_name: str
    email: str
    phone: str
    address: str
    total: float
    stage_index: int = 0

class SystemSimulator:
    def __init__(self):
        self.inventory: Dict[int, Product] = {
            1: Product(1, "Apples", 2.99, 10),
            2: Product(2, "Bread", 1.99, 15),
            3: Product(3, "Milk", 3.49, 8),
        }
        self.cart: Dict[int, int] = {}
        self.orders: Dict[int, Order] = {}
        self._next_order_id = 1

    def checkout(self, full_name: str, email: str, phone: str, address: str) -> Order:
        if not full_name or not email or not phone or not address:
            raise ValueError("Missing customer info")
        if not self.cart:
            raise ValueError("Empty cart")

        total = cart_total(self.cart, self.inventory)
        oid = self._next_order_id
        self._next_order_id += 1
        order = Order(oid, full_name, email, phone, address, total, 0)
        self.orders[oid] = order
        self.cart = {}
        return order

    def track(self, order_id: int) -> str:
        if order_id not in self.orders:
            raise KeyError("Order not found")
        o = self.orders[order_id]
        if o.stage_index < len(DELIVERY_STAGES) - 1:
            o.stage_index += 1
        return DELIVERY_STAGES[o.stage_index]

class TestIntegrationFlow(unittest.TestCase):
    def test_end_to_end_flow(self):
        sim = SystemSimulator()
        add_to_cart(sim.cart, sim.inventory, 1, qty=1)
        add_to_cart(sim.cart, sim.inventory, 2, qty=2)
        set_quantity(sim.cart, sim.inventory, 1, 3)

        order = sim.checkout("Test User", "test@example.com", "555-555-5555", "123 Main St")
        self.assertGreater(order.total, 0)

        s1 = sim.track(order.order_id)
        s2 = sim.track(order.order_id)
        self.assertIn(s1, DELIVERY_STAGES)
        self.assertIn(s2, DELIVERY_STAGES)

    def test_checkout_requires_info(self):
        sim = SystemSimulator()
        add_to_cart(sim.cart, sim.inventory, 1, qty=1)
        with self.assertRaises(ValueError):
            sim.checkout("", "a@b.com", "1", "x")

if __name__ == "__main__":
    unittest.main()
