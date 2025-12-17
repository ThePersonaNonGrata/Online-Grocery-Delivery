import unittest
from cart_logic import Product, add_to_cart, remove_from_cart, set_quantity, cart_total

class TestCartLogic(unittest.TestCase):
    def setUp(self):
        self.inventory = {
            1: Product(1, "Apples", 2.99, 10),
            2: Product(2, "Bread", 1.99, 15),
            3: Product(3, "Milk", 3.49, 8),
        }
        self.cart = {}

    def test_add_to_cart_decrements_stock(self):
        add_to_cart(self.cart, self.inventory, 1, qty=2)
        self.assertEqual(self.cart[1], 2)
        self.assertEqual(self.inventory[1].stock, 8)

    def test_remove_restores_stock(self):
        add_to_cart(self.cart, self.inventory, 2, qty=3)
        remove_from_cart(self.cart, self.inventory, 2)
        self.assertNotIn(2, self.cart)
        self.assertEqual(self.inventory[2].stock, 15)

    def test_set_quantity_increase_and_decrease(self):
        add_to_cart(self.cart, self.inventory, 3, qty=1)
        set_quantity(self.cart, self.inventory, 3, 4)
        self.assertEqual(self.cart[3], 4)
        self.assertEqual(self.inventory[3].stock, 4)

        set_quantity(self.cart, self.inventory, 3, 2)
        self.assertEqual(self.cart[3], 2)
        self.assertEqual(self.inventory[3].stock, 6)

    def test_total(self):
        add_to_cart(self.cart, self.inventory, 1, qty=2)  # 5.98
        add_to_cart(self.cart, self.inventory, 2, qty=1)  # 1.99
        self.assertEqual(cart_total(self.cart, self.inventory), 7.97)

    def test_insufficient_stock_raises(self):
        with self.assertRaises(ValueError):
            add_to_cart(self.cart, self.inventory, 1, qty=999)

if __name__ == "__main__":
    unittest.main()
