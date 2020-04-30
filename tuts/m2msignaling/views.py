from .models import OrderItem, Order
from .serializers import  OrderReadSerializer, OrderWriteSerializer
from rest_framework import generics


class ListCreateOrderView(generics.ListCreateAPIView):
    """List or create a new order"""
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderReadSerializer
        else:
            return OrderWriteSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """List or create a new order"""
    serializer_class = OrderWriteSerializer
    queryset = Order.objects.all()

    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderReadSerializer
        else:
            return OrderWriteSerializer
