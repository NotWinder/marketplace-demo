# orders/serializers.py
from rest_framework import serializers

from products.models import Product
from products.serializers import ProductListSerializer

from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Shows items in cart with product details.
    """

    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)  # For adding items
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "subtotal", "added_at"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, data):
        """Check if product has enough stock"""
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

        if product.stock < quantity:
            raise serializers.ValidationError(
                f"Only {product.stock} items available in stock"
            )

        if not product.is_active:
            raise serializers.ValidationError("This product is not available")

        return data


class CartSerializer(serializers.ModelSerializer):
    """
    Full cart with all items.
    """

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "total_items", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Order item with product snapshot (price at time of order).
    """

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.ImageField(source="product.image", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "price",
            "subtotal",
        ]
        read_only_fields = ["price", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    """
    Full order details.
    Used in: GET /api/orders/<id>/
    """

    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_email",
            "items",
            "total_price",
            "status",
            "payment_method",
            "shipping_address",
            "phone_number",
            "notes",
            "is_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "total_price", "created_at"]


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Creating an order from cart.
    Used in: POST /api/orders/
    """

    class Meta:
        model = Order
        fields = ["payment_method", "shipping_address", "phone_number", "notes"]

    def validate_payment_method(self, value):
        """Ensure payment method is valid"""
        valid_methods = [choice[0] for choice in Order.PAYMENT_METHOD_CHOICES]
        if value not in valid_methods:
            raise serializers.ValidationError("Invalid payment method")
        return value

    def create(self, validated_data):
        """
        Custom create logic:
        1. Get user's cart
        2. Create order
        3. Create order items from cart
        4. Clear cart
        """
        user = self.context["request"].user
        cart = Cart.objects.get(user=user)

        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty")

        # Calculate total
        total = cart.total_price

        # Create order
        order = Order.objects.create(user=user, total_price=total, **validated_data)

        # Create order items from cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )

            # Reduce stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()

        # Clear cart
        cart.items.all().delete()

        return order


class OrderListSerializer(serializers.ModelSerializer):
    """
    Minimal order info for listing.
    Used in: GET /api/orders/
    """

    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "total_price", "status", "items_count", "created_at"]

    def get_items_count(self, obj):
        return obj.items.count()
