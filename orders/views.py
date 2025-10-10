# orders/views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet (not ModelViewSet) - we define all actions manually.
    This gives us full control over the API behavior.
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/cart/
        Get user's cart with all items.
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        """
        POST /api/cart/
        Add item to cart.
        Body: {"product_id": 1, "quantity": 2}
        """
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id, defaults={"quantity": quantity}
        )

        if not created:
            # Item exists, update quantity
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        """
        DELETE /api/cart/clear/
        Clear all items from cart.
        """
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["patch"], url_path="items/(?P<item_id>[^/.]+)")
    def update_item(self, request, item_id=None):
        """
        PATCH /api/cart/items/{item_id}/
        Update quantity of a cart item.
        Body: {"quantity": 3}
        """
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get("quantity")
        if not quantity or quantity < 1:
            return Response(
                {"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST
            )

        if cart_item.product.stock < quantity:
            return Response(
                {"error": f"Only {cart_item.product.stock} items available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response(CartItemSerializer(cart_item).data)

    @action(detail=False, methods=["delete"], url_path="items/(?P<item_id>[^/.]+)")
    def remove_item(self, request, item_id=None):
        """
        DELETE /api/cart/items/{item_id}/
        Remove item from cart.
        """
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response(
                {"message": "Item removed"}, status=status.HTTP_204_NO_CONTENT
            )
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND
            )


# orders/views.py (continued)
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderListSerializer, OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    Full order management.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see their own orders.
        Staff can see all orders.
        """
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """
        Create order from user's cart.
        POST /api/orders/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # The serializer's create() method handles all the logic
        order = serializer.save()

        # Return full order details
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel an order (if not shipped yet).
        POST /api/orders/{id}/cancel/
        """
        order = self.get_object()

        if order.status in ["shipped", "delivered"]:
            return Response(
                {"error": "Cannot cancel shipped or delivered orders"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Restore stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        order.status = "cancelled"
        order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """
        Update order status (staff only in production).
        PATCH /api/orders/{id}/update_status/
        Body: {"status": "shipped"}
        """
        order = self.get_object()
        new_status = request.data.get("status")

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        return Response(OrderSerializer(order).data)
