from django.db import models, transaction
from django.db.models.signals import pre_save, post_save, m2m_changed


class Item(models.Model):
    name = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} -- {self.price}"


class Order(models.Model):
    order_item = models.ManyToManyField('OrderItem')
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.item} * {self.quantity} = {self.total} "


def pre_save_order_tem_receiver(sender, instance, *args, **kwargs):
    """Receiver for updating total of OrderItem"""
    total = instance.item.price * instance.quantity
    instance.total = total


pre_save.connect(pre_save_order_tem_receiver, sender=OrderItem)


def listen_order_item_change(sender, instance, **kwargs):
    orders = instance.order_set.all()
    for order in orders:
        order.order_item.remove(instance)
        order.order_item.add(instance)
        order.save()


post_save.connect(listen_order_item_change, sender=OrderItem)


def m2m_changed_order_item_receiver(sender, instance, action, *args, **kwargs):
    """Receiver for updating total of Order through OrderItem"""
    if action in ["post_add", "post_remove"]:
        order_items = instance.order_item.all()
        total = 0
        for order_item in order_items:
            total += order_item.item.price * order_item.quantity
        instance.total = total
    instance.save()


m2m_changed.connect(m2m_changed_order_item_receiver, sender=Order.order_item.through)
