"""cart_logic.py
Simple cart + inventory logic used for unit tests.

Framework-agnostic so it runs without Flask/HTML.
Mirrors behaviors from the demo:
  - add item
  - remove item
  - set quantity
  - compute totals
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: int

Cart = Dict[int, int]  # product_id -> qty

def add_to_cart(cart: Cart, inventory: Dict[int, Product], product_id: int, qty: int = 1) -> None:
    if qty <= 0:
        return
    if product_id not in inventory:
        raise KeyError("Product not found")
    p = inventory[product_id]
    if p.stock < qty:
        raise ValueError("Insufficient stock")
    cart[product_id] = cart.get(product_id, 0) + qty
    p.stock -= qty

def remove_from_cart(cart: Cart, inventory: Dict[int, Product], product_id: int) -> None:
    qty = cart.get(product_id, 0)
    if qty <= 0:
        return
    if product_id in inventory:
        inventory[product_id].stock += qty
    cart.pop(product_id, None)

def set_quantity(cart: Cart, inventory: Dict[int, Product], product_id: int, new_qty: int) -> None:
    if new_qty < 0:
        new_qty = 0
    current = cart.get(product_id, 0)
    if product_id not in inventory:
        raise KeyError("Product not found")
    p = inventory[product_id]

    diff = new_qty - current
    if diff > 0:
        if p.stock < diff:
            raise ValueError("Insufficient stock")
        p.stock -= diff
        cart[product_id] = new_qty
    elif diff < 0:
        p.stock += (-diff)
        if new_qty == 0:
            cart.pop(product_id, None)
        else:
            cart[product_id] = new_qty

def cart_items(cart: Cart, inventory: Dict[int, Product]) -> List[Tuple[Product, int, float]]:
    items = []
    for pid, qty in cart.items():
        if pid in inventory and qty > 0:
            p = inventory[pid]
            items.append((p, qty, round(p.price * qty, 2)))
    return items

def cart_total(cart: Cart, inventory: Dict[int, Product]) -> float:
    return round(sum(subtotal for _, _, subtotal in cart_items(cart, inventory)), 2)
