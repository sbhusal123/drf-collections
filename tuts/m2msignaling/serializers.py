from .models import Order, OrderItem, Item
from rest_framework import serializers


# For OrderWrite
class OrderItemSerializer(serializers.ModelSerializer):
    """Serializers for OrderItem in Order"""
    action = serializers.CharField(required=False)  # action can be update or delete
    id = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ('id', 'item', 'quantity', 'action')
        extra_kwargs = {
            'action': {'validators': []}
        }


class OrderWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating new order"""
    order_item = OrderItemSerializer(many=True, required=True)

    class Meta:
        model = Order
        fields = ('order_item', )


    def create(self, validated_data):
        order_items_data = validated_data.pop('order_item')
        order = Order.objects.create()

        # add order_item in the order
        for order_item_data in order_items_data:
            order_item = OrderItem.objects.create(**order_item_data)
            order.order_item.add(order_item)
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_item')

        for order_item_data in order_items_data:
            action = order_item_data.pop('action', None)
            order_item_id = order_item_data.get('id', None)

            if action is not None and order_item_id is None:
                """If OrderItem id is not passed cannot update it"""
                raise serializers.ValidationError("Please pass id to update order item")

            """If updating or deleting order item"""
            if action:
                order_item_obj = OrderItem.objects.get(pk=order_item_id)

                if action == "update":
                    """ Action field validation:
                        For updating first remove object update it and at last add it,
                        otherwise signal to update order total wont be executed.
                    """
                    # remove
                    instance.order_item.remove(order_item_obj)
                    # update
                    order_item_obj.quantity = order_item_data.pop('quantity', order_item_obj.quantity)
                    order_item_obj.item = order_item_data.pop('item', order_item_obj.item)
                    order_item_obj.save()
                    # add back
                    instance.order_item.add(order_item_obj)

                elif action == "remove":
                    """First remove and delete object"""
                    instance.order_item.remove(order_item_obj)
                    order_item_obj.delete()
            else:
                """If adding new order item"""
                try:
                    order_item = OrderItem.objects.create(**order_item_data)
                except Exception as e:
                    raise serializers.ValidationError(e)
                instance.order_item.add(order_item)

        instance.save()
        return instance


# For OrderRead
class ItemSerializer(serializers.ModelSerializer):
    """Serializer for reading Item in OrderItem"""

    class Meta:
        model = Item
        fields = '__all__'


class NestedOrderItemSerializer(serializers.ModelSerializer):
    """Serializers for reading OrderItem in Order"""
    item = ItemSerializer(many=False)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderReadSerializer(serializers.ModelSerializer):
    """Serializer for reading order object"""
    order_item = NestedOrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'

