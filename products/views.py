from rest_framework import viewsets
from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer

# Create your views here.

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)