from ..models import  Item, OrderItem, Order
from django.test import TestCase


def create_sample_item(name, price, data_only):
    """Create sample item for tests"""
    item_info = {
        'name': name,
        'price': price
    }
    if data_only:
        return item_info

    else:
        item_obj = Item.objects.create(**item_info)
        return item_obj, item_info


def create_sample_order_item(item, quantity, data_only):
    """Create sample order item for tests"""
    order_item_info = {
        'item': item.pk,
        'quantity': quantity
    }
    if data_only:
        return order_item_info

    else:
        order_item_obj = OrderItem.objects.create(
            item=item,
            quantity=quantity
        )
        order_item_info["id"] = order_item_obj.id
        return order_item_obj, order_item_info


def create_sample_order(order_items, data_only):
    """Create sample order"""
    order_info = {
        'order_item': order_items
    }

    if data_only:
        return order_items
    else:
        order_obj = Order.objects.create(total=0.00)
        order_obj.save()
        for order_item_info in order_info.get('order_item'):
            order_item_obj = OrderItem.objects.get(id=order_item_info["id"])
            order_obj.order_item.add(order_item_obj)
        return order_obj, order_info


class TestModel(TestCase):

    def setUp(self):
        # Items for tests
        self.item1, self.item1_info = create_sample_item("Burger", 250.00, False)
        self.item2, self.item1_info = create_sample_item("Chicken Chilly", 150.00, False)
        self.item3, self.item1_info = create_sample_item("Dumpling", 100.00, False)

    def test_create_new_order(self):
        """Test creating new order"""
        order_item1, order_item1_data = create_sample_order_item(
            item=self.item1,
            quantity=2,
            data_only=False
        )

        order_item2, order_item2_data = create_sample_order_item(
            item=self.item2,
            quantity=2,
            data_only=False
        )

        # triggers post_create m2m
        order, _ = create_sample_order(
            order_items=[order_item1_data, order_item2_data],
            data_only=False
        )

        order_item1_total = order_item1.item.price*order_item1.quantity
        order_item2_total = order_item2.item.price*order_item2.quantity

        self.assertEqual(order_item1.total, order_item1_total)
        self.assertEqual(order_item2.total, order_item2_total)
        self.assertEqual(order.total, order_item1_total + order_item2_total)

    def test_removing_order_item_from_order(self):
        order_item1, order_item1_data = create_sample_order_item(
            item=self.item1,
            quantity=2,
            data_only=False
        )

        order_item2, order_item2_data = create_sample_order_item(
            item=self.item2,
            quantity=2,
            data_only=False
        )

        order, _ = create_sample_order(
            order_items=[order_item1_data, order_item2_data],
            data_only=False
        )

        # triggers post_remove m2m
        order.order_item.remove(order_item1)

        order.refresh_from_db()

        self.assertEqual(order.total, order_item2.total)

    def test_updating_order_item_items_in_order(self):
        order_item1, order_item1_data = create_sample_order_item(
            item=self.item1,
            quantity=2,
            data_only=False
        )

        order_item2, order_item2_data = create_sample_order_item(
            item=self.item2,
            quantity=2,
            data_only=False
        )

        order, _ = create_sample_order(
            order_items=[order_item1_data, order_item2_data],
            data_only=False
        )

        order_items = order.order_item.all()

        for order_item in order_items:
            if order_item == order_item2:
                order_item2.item = self.item3
                order_item2.save()
        order.save()

        # updated total to be checked
        order_item2_total = order_item2.quantity * self.item3.price

        # possibility for code ducplication here
        order.order_item.remove(order_item2)
        order.order_item.add(order_item2)

        # refresh lazy queryset :P
        order.refresh_from_db()
        order_item1.refresh_from_db()
        order_item2.refresh_from_db()

        # check weather OrderItem total is updated or not
        self.assertEqual(order_item2.total, order_item2_total)

        self.assertEqual(order.total, order_item1.total + order_item2.total)

    def test_updating_order_item_quantity_in_order(self):
        order_item1, order_item1_data = create_sample_order_item(
            item=self.item1,
            quantity=2,
            data_only=False
        )

        order_item2, order_item2_data = create_sample_order_item(
            item=self.item2,
            quantity=2,
            data_only=False
        )

        order, _ = create_sample_order(
            order_items=[order_item1_data, order_item2_data],
            data_only=False
        )

        order_items = order.order_item.all()

        for order_item in order_items:
            if order_item == order_item2:
                order_item2.quantity = 10
                order_item2.save()
        order.save()

        # update
        order_item2_total = order_item2.item.price * 10

        # below approach might cause code duplication
        order.order_item.remove(order_item2)
        order.order_item.add(order_item2)

        # refresh lazy queryset :P
        order_item1.refresh_from_db()
        order_item2.refresh_from_db()

        # check weather OrderItem total is updated or not
        self.assertEqual(order_item2.total, order_item2_total)

        order.refresh_from_db()

        self.assertEqual(order.total, order_item1.total + order_item2.total)
