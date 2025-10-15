# products/views.py
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Category, Product
from .permissions import IsSellerOrReadOnly
from .serializers import (
    CategorySerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnlyModelViewSet provides:
    - list() -> GET /api/categories/
    - retrieve() -> GET /api/categories/{id}/

    No create, update, or delete.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"  # Use slug instead of id in URLs

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):
        """
        Custom action: Get all products in a category
        URL: GET /api/categories/{slug}/products/

        @action parameters:
        - detail=True: Works on a single object (requires ID/slug)
        - detail=False: Works on the entire collection
        - methods: HTTP methods allowed
        """
        category = self.get_object()
        products = category.products.filter(is_active=True)

        # Pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet provides:
    - list() -> GET /api/products/
    - retrieve() -> GET /api/products/{id}/
    - create() -> POST /api/products/
    - update() -> PUT /api/products/{id}/
    - partial_update() -> PATCH /api/products/{id}/
    - destroy() -> DELETE /api/products/{id}/
    """

    queryset = Product.objects.filter(is_active=True).select_related(
        "category", "seller"
    )

    permission_classes = [IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]
    lookup_field = "slug"

    # Filtering, searching, ordering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "seller"]  # Filter by: ?category=1&seller=2
    search_fields = ["name", "description"]  # Search: ?search=laptop
    ordering_fields = ["price", "created_at", "stock"]  # Order: ?ordering=-price
    ordering = ["-created_at"]  # Default ordering

    def get_serializer_class(self):
        """
        Return different serializers based on action.
        This is called automatically by DRF.
        """
        if self.action == "list":
            return ProductListSerializer
        elif self.action == "retrieve":
            return ProductDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ProductCreateSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        """
        Customize queryset based on user or request parameters.
        This is called for every request.
        """
        queryset = super().get_queryset()

        # Filter by price range if provided
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Show only user's products if 'my_products' param is present
        if (
            self.request.query_params.get("my_products")
            and self.request.user.is_authenticated
        ):
            queryset = queryset.filter(seller=self.request.user)

        return queryset

    def perform_create(self, serializer):
        """
        Called when creating a new object.
        Automatically sets the seller to current user.
        """
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        """
        Called when updating an object.
        You can add custom logic here.
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Soft delete: Set is_active to False instead of actually deleting.
        """
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_to_cart(self, request, slug=None):
        """
        Add product to user's cart.
        URL: POST /api/products/{slug}/add_to_cart/
        Body: {"quantity": 2}
        """
        product = self.get_object()
        quantity = request.data.get("quantity", 1)

        # Validate quantity
        if quantity < 1:
            return Response(
                {"error": "Quantity must be at least 1"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if product.stock < quantity:
            return Response(
                {"error": f"Only {product.stock} items available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create cart
        from orders.models import Cart, CartItem

        cart, created = Cart.objects.get_or_create(user=request.user)

        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            {"message": "Product added to cart", "cart_total": str(cart.total_price)},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """
        Get featured products (e.g., top selling or high stock).
        URL: GET /api/products/featured/

        detail=False means it works on the collection, not a single object.
        """
        # Example: Products with stock > 10, ordered by creation date
        featured_products = self.get_queryset().filter(stock__gt=10)[:10]
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_products(self, request):
        """
        Get all products created by the current user.
        URL: GET /api/products/my_products/
        """
        products = self.get_queryset().filter(seller=request.user)

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
